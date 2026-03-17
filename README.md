# Kutno Monitor Nieruchomości — MVP lokalny

Lokalny skrypt do monitorowania ofert nieruchomości w Kutnie z portali:
- Otodom
- Morizon
- OLX

Zakres MVP:
- sprzedaż i wynajem mieszkań,
- sprzedaż działek,
- sprzedaż i wynajem hal/magazynów oraz obiektów przemysłowych,
- tylko oferty z lokalizacją `Kutno`,
- eksport do Excela,
- historia kolejnych pomiarów,
- porównanie z poprzednim uruchomieniem,
- podstawowa deduplikacja między portalami.

## Ważne
To jest **starter, który da się uruchomić lokalnie**, ale portale potrafią zmieniać układ stron. Najbardziej wrażliwe są pliki w katalogu `scrapers/`. Po pierwszym uruchomieniu może być potrzebne dostrojenie parserów.

## Instalacja

1. Zainstaluj Python 3.11 lub 3.12.
2. Otwórz terminal w folderze projektu.
3. Utwórz środowisko i zainstaluj zależności:

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
python -m playwright install chromium
```

## Uruchomienie

```bash
python main.py
```

Po uruchomieniu powstaną:
- baza SQLite: `data/database/kutno_monitor.db`
- raport Excel: `data/reports/kutno_monitor_YYYYMMDD_HHMMSS.xlsx`
- pliki CSV pomocnicze w `data/processed/`

## Automatyzacja co 14 dni w Windows
1. Otwórz **Harmonogram zadań**.
2. Utwórz nowe zadanie.
3. Wyzwalacz: co 14 dni.
4. Akcja: uruchom program:
   - Program/skrypt: ścieżka do `python.exe` w `.venv`
   - Argumenty: `main.py`
   - Rozpocznij w: folder projektu

## Co robi raport
Arkusze Excela:
- `aggregates` — agregaty wg segmentu i transakcji
- `history` — historia wszystkich snapshotów
- `unique_listings` — oferty po deduplikacji
- `raw_listings` — oferty przed deduplikacją
- `new_listings` — oferty nowe względem poprzedniego uruchomienia
- `price_changes` — zmiany cen względem poprzedniego uruchomienia

## Gdzie edytować zakres
W pliku `config.py`:
- liczba stron wyników,
- zestaw wyszukiwań,
- adresy URL,
- progi deduplikacji.

## Ograniczenia MVP
- Otodom, OLX i Morizon mogą zmieniać HTML lub tekst na stronach wyników.
- Wskaźnik „oferta z obniżką” działa na dwa sposoby:
  - z etykiet widocznych na portalu, jeśli parser je wykryje,
  - przez porównanie ceny z poprzednim pomiarem.
- Deduplikacja między portalami jest heurystyczna, nie idealna.
