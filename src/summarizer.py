from typing import List, Tuple

from .services import call_openai


def generate_insights(document_text: str) -> dict:
    """
    Główna funkcja: przyjmuje tekst dokumentu,
    wywołuje model Azure OpenAI i zwraca słownik:
    {
        "summary": "...",
        "key_points": ["...", "..."]
    }
    """
    if not document_text or not document_text.strip():
        return {"summary": "Brak tekstu do analizy.", "key_points": []}

    # Budujemy prompt dla modelu
    prompt = (
        "Przeczytaj poniższy tekst i przygotuj dwie sekcje (w języku polskim):\n\n"
        "STRESZCZENIE:\n"
        "- krótki opis najważniejszych informacji (3–5 zdań)\n\n"
        "KLUCZOWE PUNKTY:\n"
        "- wypunktowana lista najważniejszych tez/faktów\n\n"
        "Zachowaj dokładnie taki format:\n"
        "STRESZCZENIE:\n"
        "<tekst>\n\n"
        "KLUCZOWE PUNKTY:\n"
        "- punkt 1\n"
        "- punkt 2\n"
        "- ...\n\n"
        "=== TEKST DO ANALIZY ===\n"
        f"{document_text.strip()}\n"
    )

    print("[INFO] Wysyłam dokument do Azure OpenAI...")

    try:
        raw_output = call_openai(prompt)
    except Exception as e:
        print(f"[ERROR] Błąd komunikacji z Azure OpenAI: {e}")
        # Zwracamy pusty wynik, ale w poprawnym formacie
        return {"summary": "", "key_points": []}

    summary, key_points = parse_model_output(raw_output)

    return {
        "summary": summary,
        "key_points": key_points,
    }


def parse_model_output(model_output: object) -> Tuple[str, List[str]]:
    """
    Parsuje odpowiedź modelu, oczekując sekcji:

    STRESZCZENIE:
    ...
    
    KLUCZOWE PUNKTY:
    - ...
    - ...

    Zwraca zawsze krotkę (summary: str, key_points: List[str]).
    Nigdy nie zwraca None.
    """
    # Zabezpieczenie: jeśli model_output jest None lub nie-string, konwertujemy na string
    if model_output is None:
        return "", []

    if not isinstance(model_output, str):
        model_output = str(model_output)

    lines = model_output.splitlines()

    summary_lines: List[str] = []
    key_points: List[str] = []

    current_section = None  # None, "summary", "points"

    for line in lines:
        stripped = line.strip()

        # Wykrycie nagłówków sekcji
        if stripped.upper().startswith("STRESZCZENIE"):
            current_section = "summary"
            continue

        if stripped.upper().startswith("KLUCZOWE PUNKTY"):
            current_section = "points"
            continue

        # Zbieramy treść w zależności od sekcji
        if current_section == "summary":
            if stripped:
                summary_lines.append(stripped)

        elif current_section == "points":
            if not stripped:
                continue
            # Linia zaczyna się od myślnika lub punktorów
            if stripped.startswith("-") or stripped.startswith("•") or stripped.startswith("*"):
                point = stripped.lstrip("-•*").strip()
                if point:
                    key_points.append(point)
            else:
                # Jeśli model nie dodał myślnika, a jesteśmy w sekcji punktów
                key_points.append(stripped)

    summary_text = " ".join(summary_lines).strip()

    # Dodatkowe zabezpieczenie: zawsze zwracamy coś (nawet puste)
    if summary_text is None:
        summary_text = ""
    if key_points is None:
        key_points = []

    return summary_text, key_points