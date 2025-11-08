import sys
import json
from pathlib import Path

from .config import MAX_CHARS_FOR_SUMMARY, REPO_DOCS_DIR
from .services import analyze_document
from .summarizer import generate_insights


def list_repo_documents() -> list[Path]:
    """
    Zwraca listę plików PDF/DOCX dostępnych w katalogu testowym.
    """
    docs: list[Path] = []
    if REPO_DOCS_DIR.exists() and REPO_DOCS_DIR.is_dir():
        docs.extend(REPO_DOCS_DIR.glob("*.pdf"))
        docs.extend(REPO_DOCS_DIR.glob("*.docx"))
    docs = sorted(docs, key=lambda p: p.name)
    return docs


def choose_document_interactively() -> str:
    """
    Interaktywne menu wyboru źródła dokumentu:
    1) dokument z folderu testowego (np. data/test_docs/),
    2) własna ścieżka na dysku,
    3) URL (np. GitHub raw).

    Zwraca string będący ścieżką do pliku lub URL.
    """
    print("Wybierz źródło dokumentu:")
    print("1) Dokument z folderu testowego (data/test_docs/)")
    print("2) Podaj własną ścieżkę do pliku (PDF/DOCX)")
    print("3) Podaj URL do pliku (np. GitHub)")

    while True:
        choice = input("Twój wybór (1/2/3): ").strip()

        if choice == "1":
            docs = list_repo_documents()
            if not docs:
                print(f"[WARN] Brak dokumentów w katalogu: {REPO_DOCS_DIR}")
                continue

            print("\nDostępne dokumenty:")
            for idx, path in enumerate(docs, start=1):
                print(f"{idx}) {path.name}")

            while True:
                selected = input("Wybierz numer dokumentu: ").strip()
                try:
                    num = int(selected)
                    if 1 <= num <= len(docs):
                        return str(docs[num - 1])
                    else:
                        print("[WARN] Nieprawidłowy numer. Spróbuj ponownie.")
                except ValueError:
                    print("[WARN] Podaj poprawny numer (liczbę).")

        elif choice == "2":
            path_str = input("Podaj ścieżkę do pliku (PDF/DOCX): ").strip()
            return path_str

        elif choice == "3":
            url = input("Podaj URL do pliku (np. z GitHuba): ").strip()
            return url

        else:
            print("[WARN] Niepoprawny wybór. Wpisz 1, 2 lub 3.")


def main():
    """
    Główna funkcja programu – wybiera dokument, analizuje go i generuje streszczenie.
    """

    print("kopytko")

    # Jeśli użytkownik podał argument (ścieżka lub URL) – używamy go bez pytania
    if len(sys.argv) >= 2:
        target = sys.argv[1]
    else:
        print("[INFO] Nie podano ścieżki/URL jako argumentu.")
        print("[INFO] Uruchamiam interaktywny wybór dokumentu...")
        target = choose_document_interactively()

    print(f"[INFO] Analiza dokumentu: {target}")
    doc_info = analyze_document(target)
    document_text = doc_info["text"]

    if len(document_text) > MAX_CHARS_FOR_SUMMARY:
        document_text = document_text[:MAX_CHARS_FOR_SUMMARY]
        print(f"[INFO] Tekst został przycięty do {MAX_CHARS_FOR_SUMMARY} znaków.")

    print("[INFO] Generowanie streszczenia i kluczowych punktów...")
    insights = generate_insights(document_text)

    source_path = Path(doc_info["source"])
    output_path = source_path.with_suffix(".summary.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(insights, f, ensure_ascii=False, indent=2)

    print(f"[INFO] Streszczenie zapisane do: {output_path}")

    print("\n=== STRESZCZENIE ===\n")
    print(insights.get("summary", ""))

    print("\n=== KLUCZOWE PUNKTY ===\n")
    for point in insights.get("key_points", []):
        print(f"- {point}")


if __name__ == "__main__":
    main()
