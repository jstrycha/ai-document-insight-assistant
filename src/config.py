import os  # importuje moduł os, który pozwala czytać zmienne środowiskowe
from pathlib import Path  # importuje klasę Path do pracy ze ścieżkami plików

from dotenv import load_dotenv # ładowanie zmiennych z pliku .env


# Ładuje zmienne środowiskowe z pliku .env (jeśli istnieje)
# Plik .env powinien być w katalogu głównym projektu.
load_dotenv()

# === KONFIGURACJA AZURE ===

# Endpoint usługi Azure Form Recognizer (Document Intelligence)
AZURE_FORM_RECOGNIZER_ENDPOINT = os.getenv("AZURE_FORM_RECOGNIZER_ENDPOINT")  # pobiera adres endpointu z zmiennej środowiskowej

# Klucz dostępu do Azure Form Recognizer
AZURE_FORM_RECOGNIZER_KEY = os.getenv("AZURE_FORM_RECOGNIZER_KEY")  # pobiera klucz API z zmiennej środowiskowej

# Endpoint usługi Azure OpenAI
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")  # pobiera adres endpointu Azure OpenAI z env

# Klucz dostępu do Azure OpenAI
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")  # pobiera klucz API z env

# Nazwa deploymentu (modelu) skonfigurowanego w Azure OpenAI, np. "gpt-4o-mini"
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")  # pobiera nazwę deploymentu

# Wersja API dla Azure OpenAI
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")


# === PARAMETRY PROGRAMU ===

# Limit znaków tekstu dokumentu, który przekażemy do modelu (chroni przed zbyt długim inputem)
MAX_CHARS_FOR_SUMMARY = 15000  # ustawia maksymalną liczbę znaków tekstu przekazywanego do streszczania

# Folder z dokumentami testowymi — domyślnie data/test_docs,
# ale można go nadpisać w pliku .env przez REPO_DOCS_DIR=data/inne_miejsce
repo_docs_env = os.getenv("REPO_DOCS_DIR", "data/test_docs")
REPO_DOCS_DIR = Path(__file__).resolve().parents[1] / repo_docs_env
# ^ resolve() – przekształca ścieżkę na absolutną
# ^ parents[1] – przechodzi dwa poziomy wyżej (src/config.py -> src -> ROOT)
# ^ / "docs" – dokleja folder "docs" na końcu
