from __future__ import annotations

import hashlib
import re
from typing import List

from scrapers.common import clean_text, extract_links

ENTRY_RE = re.compile(
    r'(?P<title>[^"\n]{5,120}?)\s+'
    r"(?P<price>[0-9\s]+)\s*zł(?:do negocjacji)?\s+"
    r"(?P<location>Kutno)\s+-\s+(?P<date>(?:Dzisiaj o [0-9:]{4,5})|(?:Odświeżono dnia [0-9]{1,2} [a-ząćęłńóśźż]+ [0-9]{4})|(?:[0-9]{1,2} [a-ząćęłńóśźż]+ [0-9]{4}))\s+"
    r"(?P<area>[0-9]+(?:,[0-9]+)?)\s*m²\s+-\s+(?P<price_per_sqm>[0-9]+(?:[.,][0-9]+)?)\s*zł/m²",
    re.IGNORECASE,
)


def parse(payload, meta: dict) -> List[dict]:
    links = extract_links(payload.html, domain_filter="olx.pl")
    offer_links = [
        l for l in links
        if "/d/oferta/" in l["href"] or "/oferta/" in l["href"]
    ]
    matches = list(ENTRY_RE.finditer(payload.text))
    results = []
    for idx, m in enumerate(matches):
        title = clean_text(m.group("title"))
        if len(title) < 6 or title.lower().startswith("image"):
            continue
        url = offer_links[idx]["href"] if idx < len(offer_links) else ""
        price = _to_float(m.group("price"))
        area = _to_float(m.group("area"))
        ppsqm = _to_float(m.group("price_per_sqm"))
        results.append(
            {
                **meta,
                "listing_id": _listing_id(url, title, price, area),
                "title": title,
                "location": "Kutno",
                "price": price,
                "price_per_sqm": ppsqm,
                "area_sqm": area,
                "advertiser_type": "nieustalone",
                "publication_date": None,
                "reduced_price": 1 if "odświeżono" in m.group("date").lower() else 0,
                "url": url,
                "status": "active",
                "extracted_text": clean_text(m.group(0))[:1500],
            }
        )
    return results


def _listing_id(url: str, title: str, price: float, area: float) -> str:
    base = url or f"{title}|{price}|{area}"
    return hashlib.md5(base.encode("utf-8")).hexdigest()


def _to_float(value: str | None) -> float | None:
    if not value:
        return None
    value = value.replace("zł", "").replace("m²", "").replace(" ", "").replace(",", ".")
    try:
        return float(value)
    except ValueError:
        return None
