from pathlib import Path
from typing import List, Dict, Tuple

import requests
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI
from docx import Document as DocxDocument  # lokalny odczyt DOCX

from .config import (
    AZURE_FORM_RECOGNIZER_ENDPOINT,
    AZURE_FORM_RECOGNIZER_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_DEPLOYMENT,
    AZURE_OPENAI_API_VERSION,
    REPO_DOCS_DIR,
)


def get_form_recognizer_client() -> DocumentAnalysisClient:
    """
    Tworzy i zwraca klienta Azure Form Recognizer (Document Intelligence).
    Używany głównie do analizy plików PDF.
    """
    credential = AzureKeyCredential(AZURE_FORM_RECOGNIZER_KEY)
    client = DocumentAnalysisClient(
        endpoint=AZURE_FORM_RECOGNIZER_ENDPOINT,
        credential=credential,
    )
    return client


def extract_text_from_pdf_via_form_recognizer(file_path: str) -> Dict[str, object]:
    """
    Analizuje plik PDF używając Azure Form Recognizer (model 'prebuilt-document').
    Zwraca słownik z tekstem i liczbą stron.
    """
    client = get_form_recognizer_client()

    with open(file_path, "rb") as f:
        poller = client.begin_analyze_document(
            model_id="prebuilt-document",
            document=f,
        )
        result = poller.result()

    # Jeśli usługa zwraca gotowy content – używamy go
    if getattr(result, "content", None):
        text = result.content
    else:
        # Ręczne sklejenie linii ze stron
        all_lines: List[str] = []
        for page in result.pages:
            for line in page.lines:
                all_lines.append(line.content)
        text = "\n".join(all_lines) if all_lines else "Brak odczytanego tekstu."

    page_count = len(result.pages) if hasattr(result, "pages") else None

    return {
        "text": text,
        "page_count": page_count,
    }


def extract_text_from_docx_local(file_path: str) -> Dict[str, object]:
    """
    Lokalny odczyt DOCX bez użycia Form Recognizer.
    Dzięki temu dokumenty DOCX działają nawet, jeśli usługa Azure ich nie lubi.
    """
    doc = DocxDocument(file_path)
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    text = "\n".join(paragraphs) if paragraphs else "Brak odczytanego tekstu."
    # Nie mamy informacji o liczbie stron – zostawiamy None
    return {
        "text": text,
        "page_count": None,
    }


def get_openai_client() -> AzureOpenAI:
    """
    Tworzy i zwraca klienta Azure OpenAI.
    Wersja API jest pobierana z .env (AZURE_OPENAI_API_VERSION).
    """
    client = AzureOpenAI(
        api_key=AZURE_OPENAI_API_KEY,
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_version=AZURE_OPENAI_API_VERSION,
    )
    return client


def call_openai(prompt: str, max_tokens: int = 800) -> str:
    """
    Wysyła prompt do Azure OpenAI (model typu chat)
    i zwraca wygenerowaną odpowiedź jako string.
    """
    client = get_openai_client()

    response = client.chat.completions.create(
        model=AZURE_OPENAI_DEPLOYMENT,
        messages=[
            {
                "role": "system",
                "content": "Jesteś asystentem biurowym, który tworzy streszczenia dokumentów.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        max_tokens=max_tokens,
        temperature=0.2,
    )

    first_choice = response.choices[0]
    content = first_choice.message.content
    return content


def normalize_github_url(url: str) -> str:
    """
    Jeśli URL jest w formie:
      https://github.com/uzytkownik/repo/blob/main/ścieżka/plik.pdf
    to zamienia go na:
      https://raw.githubusercontent.com/uzytkownik/repo/main/ścieżka/plik.pdf

    Dzięki temu pobieramy prawdziwy plik, a nie stronę HTML.
    """
    if "github.com" in url and "/blob/" in url:
        url = url.replace("github.com", "raw.githubusercontent.com")
        url = url.replace("/blob/", "/")
    return url


def download_file_from_github(url: str, local_dir: str = "temp_files") -> str:
    """
    Pobiera dokument (PDF/DOCX) bezpośrednio z URL (np. GitHub raw)
    i zapisuje go lokalnie w folderze tymczasowym.

    Zwraca ścieżkę do pobranego pliku jako string.
    """
    # Automatycznie naprawiamy "zwykły" link GitHuba na link RAW
    url = normalize_github_url(url)

    local_dir_path = Path(local_dir)
    local_dir_path.mkdir(parents=True, exist_ok=True)

    response = requests.get(url, timeout=15)
    if response.status_code != 200:
        raise ValueError(f"Nie udało się pobrać pliku: {url} (HTTP {response.status_code})")

    filename_from_url = url.split("/")[-1].strip()
    if not filename_from_url:
        filename_from_url = "document_from_url.pdf"

    local_path = local_dir_path / filename_from_url

    with open(local_path, "wb") as f:
        f.write(response.content)

    print(f"[INFO] Pobrano plik do: {local_path}")
    return str(local_path)


def resolve_document_path(file_path_or_url: str) -> Tuple[str, bool]:
    """
    Zamienia URL lub ścieżkę względną/absolutną na lokalną ścieżkę do pliku.

    Zwraca krotkę (local_path, remove_after), gdzie:
      - local_path: lokalna ścieżka do pliku,
      - remove_after: True, jeśli plik powinien być usunięty po analizie (pobrany z URL),
                      False, jeśli plik jest lokalny.
    """
    # URL (np. GitHub raw)
    if file_path_or_url.startswith("http"):
        local_path = download_file_from_github(file_path_or_url)
        return local_path, True

    # Ścieżka lokalna – może być względna lub absolutna
    p = Path(file_path_or_url)

    # Jeśli ścieżka nie jest absolutna, traktujemy ją jako nazwę pliku w REPO_DOCS_DIR
    if not p.is_absolute():
        p = REPO_DOCS_DIR / p

    return str(p), False


def analyze_document(file_path_or_url: str) -> Dict[str, object]:
    """
    Główna funkcja analizująca dokument:
    - obsługuje URL (np. GitHub) oraz lokalne ścieżki względne/absolutne,
    - dla PDF używa Form Recognizer,
    - dla DOCX korzysta z lokalnego parsera python-docx,
    - zwraca dict: { "text", "page_count", "source" }.
    """
    file_path, remove_after = resolve_document_path(file_path_or_url)

    path_obj = Path(file_path)
    if not path_obj.exists():
        raise FileNotFoundError(f"Plik nie istnieje: {file_path}")

    suffix = path_obj.suffix.lower()

    try:
        if suffix == ".pdf":
            # Analiza PDF przez Form Recognizer
            print("[INFO] Analiza PDF przez Azure Form Recognizer...")
            result = extract_text_from_pdf_via_form_recognizer(file_path)
            return {
                "text": result["text"],
                "page_count": result["page_count"],
                "source": file_path,
            }

        elif suffix == ".docx":
            # DOCX – lokalny odczyt, bo Form Recognizer czasem zgłasza InvalidContent
            print("[INFO] Analiza DOCX lokalnie (python-docx)...")
            result = extract_text_from_docx_local(file_path)
            return {
                "text": result["text"],
                "page_count": result["page_count"],
                "source": file_path,
            }

        else:
            raise ValueError(f"Nieobsługiwane rozszerzenie pliku: {suffix}")

    finally:
        # Usunięcie pliku tymczasowego, jeśli pochodził z URL
        if remove_after:
            try:
                if path_obj.exists():
                    path_obj.unlink()
            except Exception as e:
                print(f"[WARN] Nie udało się usunąć pliku tymczasowego: {e}")
