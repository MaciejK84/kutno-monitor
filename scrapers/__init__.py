from scrapers.morizon import parse as parse_morizon
from scrapers.olx import parse as parse_olx
from scrapers.otodom import parse as parse_otodom

PARSERS = {
    "morizon": parse_morizon,
    "olx": parse_olx,
    "otodom": parse_otodom,
}
