from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
REPORTS_DIR = DATA_DIR / "reports"
DB_DIR = DATA_DIR / "database"
DB_PATH = DB_DIR / "kutno_monitor.db"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
)

HEADLESS = True
PAGE_TIMEOUT_MS = 45000
MAX_PAGES_PER_SEARCH = 3
SCROLL_STEPS = 3
SCROLL_PAUSE_MS = 1200

DEDUP_TITLE_THRESHOLD = 78
DEDUP_PRICE_TOLERANCE = 0.07
DEDUP_AREA_TOLERANCE = 0.05

SEARCHES = [
    {
        "portal": "otodom",
        "segment": "mieszkania",
        "transaction": "sprzedaz",
        "url": "https://www.otodom.pl/pl/wyniki/sprzedaz/mieszkanie/lodzkie/kutnowski/gmina-miejska--kutno/kutno",
    },
    {
        "portal": "otodom",
        "segment": "mieszkania",
        "transaction": "wynajem",
        "url": "https://www.otodom.pl/pl/wyniki/wynajem/mieszkanie/lodzkie/kutnowski/gmina-miejska--kutno/kutno",
    },
    {
        "portal": "otodom",
        "segment": "dzialki",
        "transaction": "sprzedaz",
        "url": "https://www.otodom.pl/pl/wyniki/sprzedaz/dzialka/lodzkie/kutnowski/gmina-miejska--kutno/kutno",
    },
    {
        "portal": "otodom",
        "segment": "przemysl_magazyny",
        "transaction": "sprzedaz",
        "url": "https://www.otodom.pl/pl/wyniki/sprzedaz/hala-magazyn/lodzkie/kutnowski/gmina-miejska--kutno/kutno",
    },
    {
        "portal": "otodom",
        "segment": "przemysl_magazyny",
        "transaction": "wynajem",
        "url": "https://www.otodom.pl/pl/wyniki/wynajem/hala-magazyn/lodzkie/kutnowski/gmina-miejska--kutno/kutno",
    },
    {
        "portal": "morizon",
        "segment": "mieszkania",
        "transaction": "sprzedaz",
        "url": "https://www.morizon.pl/mieszkania/kutnowski/miasto-kutno/",
    },
    {
        "portal": "morizon",
        "segment": "mieszkania",
        "transaction": "wynajem",
        "url": "https://www.morizon.pl/do-wynajecia/mieszkania/kutnowski/miasto-kutno/",
    },
    {
        "portal": "morizon",
        "segment": "dzialki",
        "transaction": "sprzedaz",
        "url": "https://www.morizon.pl/dzialki/kutnowski/miasto-kutno/",
    },
    {
        "portal": "morizon",
        "segment": "przemysl_magazyny",
        "transaction": "sprzedaz",
        "url": "https://www.morizon.pl/komercyjne/hale-magazyny/kutnowski/miasto-kutno/",
    },
    {
        "portal": "morizon",
        "segment": "przemysl_magazyny",
        "transaction": "wynajem",
        "url": "https://www.morizon.pl/do-wynajecia/komercyjne/hale-magazyny/kutnowski/miasto-kutno/",
    },
    {
        "portal": "olx",
        "segment": "mieszkania",
        "transaction": "sprzedaz",
        "url": "https://www.olx.pl/nieruchomosci/mieszkania/sprzedaz/kutno/",
    },
    {
        "portal": "olx",
        "segment": "mieszkania",
        "transaction": "wynajem",
        "url": "https://www.olx.pl/nieruchomosci/mieszkania/wynajem/kutno/",
    },
    {
        "portal": "olx",
        "segment": "dzialki",
        "transaction": "sprzedaz",
        "url": "https://www.olx.pl/nieruchomosci/dzialki/sprzedaz/kutno/",
    },
    {
        "portal": "olx",
        "segment": "przemysl_magazyny",
        "transaction": "sprzedaz",
        "url": "https://www.olx.pl/nieruchomosci/hale-i-magazyny/sprzedaz/kutno/",
    },
    {
        "portal": "olx",
        "segment": "przemysl_magazyny",
        "transaction": "wynajem",
        "url": "https://www.olx.pl/nieruchomosci/hale-i-magazyny/wynajem/kutno/",
    },
]
