# AI document insight assistant
Asystent AI do analizy dokumentów (PDF, DOCX), który automatycznie generuje streszczenia i listy kluczowych punktów.  

Projekt wykorzystuje:
- **Azure Form Recognizer (Document Intelligence)** – do ekstrakcji tekstu z dokumentów,
- **Azure OpenAI** – do generowania streszczeń i punktów.

Program działa jako **prosta aplikacja CLI** (z linii komend) i może pracować:
- na **dokumentach lokalnych** (podanych ścieżką),
- na **dokumentach przykładowych** przechowywanych w repozytorium (folder `docs/`).

### Zakres prac
1. Przygotowanie zestawu dokumentów testowych (wykorzystane zostały doc z https://www.kaggle.com/datasets) 
2. Konfiguracja i użycie **Azure Form Recognizer SDK**
3. Integracja z **Azure OpenAI SDK** (generacja streszczeń i kluczowych punktów)
4. Testy jakości (trafność, kompletność streszczeń)
5. Stworzenie interfejsu demo (upload PDF → streszczenie) z użyciem **Gradio**
6. Dokumentacja i prezentacja

### Przykładowe zastosowania

1. Streszczanie raportów
2. Analiza umów i dokumentów prawnych
3. Podsumowanie dokumentacji projektowej
4. Skracanie długich dokumentów wewnętrznych
5. Przygotowanie do spotkań

---

## Spis treści

1. [Struktura projektu](#struktura-projektu)
2. [Przebieg działania programu](#przebieg-działania-programu)
3. [Lista wymagań](#lista-wymagań)
4. [Konfiguracja środowiska](#konfiguracja-środowiska)
5. [Uruchamianie programu](#uruchamianie-programu)
6. [Technologie i biblioteki](#technologie-i-biblioteki)
7. [Rozwiązywanie najczęstszych problemów](#rozwiązywanie-najczęstszych-problemów)
8. [Licencja](#licencja)
9. [Lista autorów](#lista-autorów)

---
## Struktura projektu

```text
ai-document-insight/
├─ data/
│  └─ test_docs/             # folder z przykładowymi dokumentami PDF/DOCX
├─ src/
│  ├─ main.py                # punkt wejściowy, logika uruchomienia aplikacji (CLI)
│  ├─ config.py              # konfiguracja projektu, ładowanie zmiennych z .env
│  ├─ services.py            # integracja z Azure, analiza dokumentów, obsługa źródeł
│  └─ summarizer.py          # budowanie promptów, generowanie streszczeń
├─ requirements.txt          # lista wymaganych bibliotek Pythona
├─ .env.sample               # dane konfiguracyjne (endpointy, klucze, wersje API)
└─ README.md                 # plik z opisem projektu
```

### Opis plików

- **`docs/`**
  - Folder z przykładowymi dokumentami (PDF, DOCX), które można szybko przetestować bez szukania plików na dysku.
  - Program potrafi wyświetlić listę plików z tego folderu i pozwala użytkownikowi wybrać jeden z nich.

- **`src/config.py`**
  - Zawiera konfigurację aplikacji:
    - endpointy i klucze do usług Azure,
    - nazwę deploymentu modelu Azure OpenAI,
    - limit długości tekstu dokumentu przekazywanego do modelu,
    - ścieżkę do folderu `docs/`.
  - Wszystkie dane wrażliwe (klucze, endpointy) wczytywane są ze zmiennych środowiskowych.

- **`src/services.py`**
  - Warstwa integracji z zewnętrznymi usługami:
    - tworzenie klienta **Form Recognizer**,  
    - ekstrakcja tekstu z dokumentu,
    - tworzenie klienta **Azure OpenAI**,
    - wywołanie modelu (chat completions) z promptem.

- **`src/summarizer.py`**
  - Logika przetwarzania tekstu:
    - buduje prompt dla modelu (instrukcje, co ma zrobić z tekstem dokumentu),
    - parsuje odpowiedź modelu do prostego słownika,
    - udostępnia funkcję `generate_insights(document_text)`, która zwraca streszczenie oraz listę punktów.

- **`src/main.py`**
  - Główny punkt wejściowy programu:
    - obsługuje argumenty linii komend,
    - w trybie interaktywnym pozwala wybrać:
      - dokument z folderu `docs/`, albo  
      - własny dokument z dysku,
    - uruchamia pipeline:
      - ekstrakcja tekstu → streszczenie + punkty → zapis do pliku `.summary.json`,
    - wypisuje wynik w konsoli.

- **`requirements.txt`**
  - Lista bibliotek Pythona używanych w projekcie (do instalacji via `pip`).

- **`.env.sample`**
  - Wzór do stworzenia własnego pliku `.env` (endpointy, API key potrzebne do działania programu).

---

## Przebieg działania programu

1. Użytkownik wybiera źródło dokumentu:
   - dokument z folderu `data/test_docs/`,
   - własny plik z dysku,
   - lub URL (np. plik z GitHuba).

2. Program rozpoznaje tekst w dokumencie za pomocą **Azure Form Recognizer**:
   - model `prebuilt-document`,
   - wyodrębnia pełny tekst i liczbę stron.

3. Następnie tekst trafia do **Azure OpenAI**, który generuje:
   - streszczenie,
   - listę kluczowych punktów.

4. Wynik zapisywany jest do pliku JSON (`.summary.json`) oraz wypisywany w konsoli.

---

## Lista wymagań

- **Python 3.9+**
- Aktywne konto w **Microsoft Azure**
- Usługi:
  - **Azure AI Document Intelligence (Form Recognizer)**
  - **Azure OpenAI** (z wdrożonym modelem)
- Plik `.env` z odpowiednimi zmiennymi środowiskowymi

---

## Konfiguracja środowiska

1. Sklonuj repozytorium
```bash
   git clone https://github.com/EmiliaM-hub/AI-document-insight
   cd AI-document-insight
```

2. Utwórz środowisko wirtualne:

```bash
  python -m venv .venv
  source .venv/bin/activate  # macOS/Linux
  .venv\Scripts\activate   # Windows
 ```

3. Zainstaluj zależności:

```bash
   pip install -r requirements.txt
```

4. Utwórz plik `.env` w głównym katalogu i ustaw niezbędne zmienne środowiskowe, zgodnie z przykładem umieszczonym  w pliku `.env.sample`.
   **Uwaga:** 
  > Zmienne muszą odpowiadać rzeczywistym nazwom i konfiguracjom w portalu Azure AI (nie zapomnij o wcześniejszym skonfigurowaniu Form Recognizer i OpenAI).
  > Nie publikuj pliku `.env` w repozytorium – dodaj go do `.gitignore`.
 
---

## Uruchamianie programu

Program możesz uruchomić na trzy główne sposoby:
1. Tryb interaktywny – bez argumentów.
2. Tryb „lokalny plik” – podajesz ścieżkę do pliku.
3. Tryb „URL (GitHub / internet)” – podajesz adres URL dokumentu.

### Tryb interaktywny (bez argumentów)

Najprostszy sposób uruchomienia — nie trzeba podawać żadnych argumentów.  
Program sam poprowadzi Cię przez proces wyboru dokumentu.

```bash
python -m src.main
```

Po uruchomieniu zobaczysz menu:

```text
[INFO] Nie podano ścieżki/URL jako argumentu.
[INFO] Uruchamiam interaktywny wybór dokumentu...
Wybierz źródło dokumentu:
1) Dokument z folderu testowego (data/test_docs/)
2) Podaj własną ścieżkę do pliku (PDF/DOCX)
3) Podaj URL do pliku (np. GitHub)
Twój wybór (1/2/3):
```

#### Opcje:

- **1)** Wybierz dokument z folderu `data/test_docs/`.  
  Program pokaże listę wszystkich plików `.pdf` i `.docx` w tym katalogu:
  ```text
  Dostępne dokumenty:
  1) raport.pdf
  2) umowa.docx
  ```
  Wpisz numer, np. `1`, aby przeanalizować wybrany plik.

- **2)** Podaj własną ścieżkę do dokumentu z dysku:
  ```text
  Podaj ścieżkę do pliku (PDF/DOCX):
  ```
  Możesz wpisać np.:
  ```text
  C:\Users\Jan\Documents\raport.pdf
  ```
  lub (na Linux/macOS):
  ```text
  /home/jan/dokumenty/umowa.docx
  ```

- **3)** Podaj **URL** do pliku (np. z GitHuba):
  ```text
  Podaj URL do pliku (np. z GitHuba):
  ```
  Przykład:
  ```text
  https://raw.githubusercontent.com/uzytkownik/repo/main/docs/przyklad.pdf
  ```
  Program pobierze dokument tymczasowo, przeanalizuje go i **usunie po zakończeniu**.

---

### Tryb z lokalnym plikiem (bez interakcji)

Jeśli wiesz dokładnie, który plik chcesz przeanalizować,  
możesz przekazać jego ścieżkę od razu jako argument przy uruchomieniu.

```bash
python -m src.main data/test_docs/raport.pdf
```

lub (ścieżka absolutna):

```bash
python -m src.main "C:/Users/Jan/Documents/umowa.docx"
```

**Działanie:**
- Program **nie zadaje pytań** – od razu analizuje wskazany dokument.
- Następnie automatycznie:
  - wysyła plik do **Azure Form Recognizer**,  
  - generuje streszczenie i punkty kluczowe przez **Azure OpenAI**,  
  - zapisuje wynik w pliku JSON obok oryginału (np. `umowa.summary.json`).

---

### Tryb zdalny (URL / GitHub / Internet)

Możesz też przekazać **adres URL** do dokumentu PDF lub DOCX —  
np. do pliku opublikowanego w GitHubie lub innym repozytorium.

```bash
python -m src.main "https://raw.githubusercontent.com/uzytkownik/repo/main/docs/umowa.pdf"
```

**Działanie krok po kroku:**
1. Program rozpoznaje, że ścieżka zaczyna się od `http`.  
2. Pobiera dokument za pomocą `requests` do lokalnego folderu `temp_files/`.  
3. Wysyła plik do **Azure Form Recognizer** (model `prebuilt-document`).  
4. Po zakończeniu analizy:
   - plik tymczasowy jest **usuwany**,  
   - wynik (tekst, streszczenie, punkty) jest zapisywany lokalnie.  

Przykład komunikatu:

```text
[INFO] Analiza dokumentu: https://raw.githubusercontent.com/uzytkownik/repo/main/docs/umowa.pdf
[INFO] Pobrano plik do: temp_files/umowa.pdf
[INFO] Generowanie streszczenia i kluczowych punktów...
[INFO] Streszczenie zapisane do: umowa.summary.json
```

---

### Gdzie pojawia się wynik?

Niezależnie od trybu uruchomienia, program zapisze wynik w pliku `.summary.json`.

| Źródło dokumentu | Przykładowy wynik |
|------------------|------------------|
| `data/test_docs/raport.pdf` | `data/test_docs/raport.summary.json` |
| `C:/Users/Jan/Documents/umowa.docx` | `C:/Users/Jan/Documents/umowa.summary.json` |
| `https://.../przyklad.pdf` | `przyklad.summary.json` (w bieżącym katalogu) |

Plik JSON zawiera m.in.:

```json
{
  "summary": "Tutaj tekst streszczenia dokumentu...",
  "key_points": [
    "Pierwszy punkt...",
    "Drugi punkt...",
    "Trzeci punkt..."
  ]
}
```

---

## Technologie i biblioteki

### Język
- **Python**

---

### Azure Form Recognizer / Azure AI Document Intelligence
- **Zadanie:** rozpoznawanie tekstu z dokumentów PDF/DOCX.  
- **Używany model:** `prebuilt-document`.

---

### Azure OpenAI
- **Zadanie:** generowanie streszczeń i listy kluczowych punktów.  
- **API:** `chat completions`.

---

### Biblioteki Python

| Biblioteka | Opis |
|-------------|------|
| `azure-ai-formrecognizer` | Klient usługi Azure Form Recognizer |
| `azure-core` | Podstawowe klasy Azure (poświadczenia, obsługa błędów) |
| `openai` | Klient Azure OpenAI |
| `pathlib` *(standardowa biblioteka)* | Praca ze ścieżkami plików |
| `json`, `sys` *(standardowe moduły)* | Przetwarzanie danych i argumentów programu |

---
## Rozwiązywanie najczęstszych problemów

### 1. Błąd uwierzytelniania (401, 403)

**Objawy:**
- Komunikaty typu:
  - `401 Unauthorized`
  - `403 Forbidden`

**Możliwe przyczyny i rozwiązania:**
- **Klucz (KEY) nie pasuje do endpointu:**
  - Upewnij się, że endpoint i klucz pochodzą z tego samego zasobu Azure.
- **Klucz wygasł / został zresetowany:**
  - Wygeneruj nowy klucz w panelu Azure i zaktualizuj zmienne środowiskowe.
- **Subskrypcja nie ma uprawnień do danej usługi:**
  - Sprawdź w Azure Portal, czy zasoby są aktywne i dostępne.

---

### 2. Błąd modelu / niepoprawna nazwa deploymentu

**Objawy:**
- Błąd po stronie Azure OpenAI, np.:
  - `The model does not exist`
  - `Deployment not found`

**Rozwiązanie:**
- Sprawdź nazwę deploymentu w **Azure Portal**.  
- Upewnij się, że wartość `AZURE_OPENAI_DEPLOYMENT` **dokładnie odpowiada nazwie deploymentu** (wielkość liter może mieć znaczenie).

---

### 3. Brak dokumentów w folderze `docs/`

**Objawy:**
- W trybie `1) Dokument z folderu 'docs'…` widzisz komunikat:

```text
[WARN] Brak dokumentów w katalogu: ...
```
*Rozwiązanie:**
- Upewnij się, że:
- folder `docs/` istnieje w katalogu głównym repozytorium,
- w folderze są pliki `.pdf` lub `.docx`.

---

### 4. „Plik nie istnieje” przy opcji podania ścieżki

**Objawy:**
- Po wpisaniu ścieżki do pliku dostajesz komunikat:
```text
[WARN] Podany plik nie istnieje. Spróbuj ponownie.
```
**Rozwiązanie:**
- Sprawdź, czy:
- ścieżka jest poprawna,
- używasz odpowiednich ukośników (`/` vs `\`),
- plik nie został przeniesiony lub usunięty.
- Spróbuj użyć **ścieżki bezwzględnej**, np.  
`C:\Users\...\plik.pdf` zamiast `.\plik.pdf`.

---

### 5. Model zwraca nieuporządkowaną odpowiedź (parser nie wyciąga punktów)

**Objawy:**
- JSON zawiera puste `key_points`, mimo że odpowiedź modelu w logach wygląda poprawnie.

**Możliwe przyczyny i rozwiązania:**
- **Model nie trzyma się oczekiwanej struktury:**
- Upewnij się, że prompt wymaga sekcji:
  - `STRESZCZENIE:`
  - `KLUCZOWE PUNKTY:`
- Możesz zmniejszyć `temperature` do `0.0–0.2`, żeby odpowiedzi były bardziej deterministyczne.
- **Parser nie rozpoznaje nagłówków:**
- Sprawdź, czy model nie dodaje np. `**STRESZCZENIE**` zamiast `STRESZCZENIE:`.
- W razie potrzeby dopasuj funkcję `parse_model_output()`.

---

### 6. Zbyt długi dokument (błąd limitu tokenów)

**Objawy:**
- Błędy związane z limitem tokenów w Azure OpenAI.
- Dzieje się to dla bardzo dużych dokumentów.

**Rozwiązanie:**
- Zweryfikuj wartość `MAX_CHARS_FOR_SUMMARY` w `config.py`:
- Możesz ją **zmniejszyć** (bezpieczniej),  
- lub zaimplementować **dzielenie dokumentu na fragmenty** i streszczanie sekcjami (bardziej zaawansowane rozwiązanie).

---

## Licencja

Projekt grupowy wykonany w ramach **Programu LevelUP – Generative AI**.  
Może być swobodnie modyfikowany i wykorzystywany w celach nauki lub testów.

---

## Lista autorów
- Dominika Liszkiewicz
- Emilia Murawska
- Aleksandra Rostkowska
- Emilia Stacherczak
- Judyta Strychalska-Nowak
