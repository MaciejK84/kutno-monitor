from __future__ import annotations

import hashlib
import re
from typing import List

from scrapers.common import clean_text, extract_links

ENTRY_RE = re.compile(
    r"(?P<location>[A-ZĄĆĘŁŃÓŚŹŻ0-9 ,./-]{5,}?,\s*KUTNO,\s*KUTNOWSKI|[A-ZĄĆĘŁŃÓŚŹŻa-ząćęłńóśźż0-9 ,./-]{5,}?,\s*Kutno,\s*k\w+)"
    r"\s+(?P<price>[0-9\s]+)\s*zł"
    r"(?:\s+(?P<price_per_sqm>[0-9\s]+)\s*zł/m²)?"
    r"\s+(?P<area>[0-9]+(?:[.,][0-9]+)?)\s*m²"
    r"(?P<rest>.*?)"
    r"Dodane\s+(?P<date>[0-9]{4}\.[0-9]{2}\.[0-9]{2})",
    re.IGNORECASE,
)


def parse(payload, meta: dict) -> List[dict]:
    matches = list(ENTRY_RE.finditer(payload.text))
    links = extract_links(payload.html, domain_filter="morizon.pl")
    url_candidates = [l for l in links if "/oferta/" in l["href"] or "/mieszkanie/" in l["href"] or "/dzialka/" in l["href"] or "/hala" in l["href"]]
    results = []
    for idx, m in enumerate(matches):
        title = _guess_title_near_match(payload.text, m.start())
        url = url_candidates[idx]["href"] if idx < len(url_candidates) else ""
        location = clean_text(m.group("location"))
        if "kutno" not in location.lower():
            continue
        price = _to_float(m.group("price"))
        area = _to_float(m.group("area"))
        ppsqm = _to_float(m.group("price_per_sqm"))
        if not ppsqm and price and area:
            ppsqm = round(price / area, 2)
        results.append(
            {
                **meta,
                "listing_id": _listing_id(url, title, price, area),
                "title": title,
                "location": location,
                "price": price,
                "price_per_sqm": ppsqm,
                "area_sqm": area,
                "advertiser_type": _advertiser_type(m.group("rest")),
                "publication_date": m.group("date").replace(".", "-"),
                "reduced_price": 1 if _reduced(m.group("rest")) else 0,
                "url": url,
                "status": "active",
                "extracted_text": clean_text(m.group(0))[:1500],
            }
        )
    return results


def _guess_title_near_match(text: str, start: int) -> str:
    prefix = text[max(0, start - 180):start]
    chunks = [c.strip(" •-–—") for c in prefix.split("Dodane")[-1].split(" Zobacz opis ")]
    candidate = clean_text(chunks[-1]) if chunks else ""
    return candidate[-120:] if candidate else "Oferta Morizon"


def _advertiser_type(text: str) -> str:
    lowered = text.lower()
    if any(x in lowered for x in ["biuro", "agencja", "nieruchomo", "pośrednik"]):
        return "biuro"
    return "nieustalone"


def _reduced(text: str) -> bool:
    lowered = text.lower()
    return any(x in lowered for x in ["obni", "promocj", "taniej"])


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
