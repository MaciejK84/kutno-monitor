from __future__ import annotations

import hashlib
import json
import re
from typing import List

from bs4 import BeautifulSoup

from scrapers.common import clean_text, extract_links


def parse(payload, meta: dict) -> List[dict]:
    results = _parse_json_ld(payload.html, meta)
    if results:
        return [r for r in results if "kutno" in (r.get("location") or "").lower()]
    return _parse_fallback_text(payload, meta)



def _parse_json_ld(html: str, meta: dict) -> List[dict]:
    soup = BeautifulSoup(html, "lxml")
    scripts = soup.find_all("script", type="application/ld+json")
    output = []
    for script in scripts:
        text = script.string or script.get_text(" ", strip=True)
        if not text:
            continue
        try:
            data = json.loads(text)
        except Exception:
            continue
        items = data if isinstance(data, list) else [data]
        for item in items:
            output.extend(_extract_from_json_item(item, meta))
    return output



def _extract_from_json_item(item: dict, meta: dict) -> List[dict]:
    results = []
    if not isinstance(item, dict):
        return results
    if item.get("@type") == "ItemList":
        for x in item.get("itemListElement", []):
            target = x.get("item") if isinstance(x, dict) else None
            if isinstance(target, dict):
                results.extend(_extract_from_json_item(target, meta))
        return results
    if item.get("@type") not in {"Offer", "Product", "Residence", "Apartment", "House"}:
        for v in item.values():
            if isinstance(v, dict):
                results.extend(_extract_from_json_item(v, meta))
            elif isinstance(v, list):
                for element in v:
                    if isinstance(element, dict):
                        results.extend(_extract_from_json_item(element, meta))
        return results

    title = clean_text(str(item.get("name") or item.get("headline") or "Oferta Otodom"))
    url = item.get("url") or ""
    offers = item.get("offers") if isinstance(item.get("offers"), dict) else {}
    price = _to_float(offers.get("price") or item.get("price"))
    area = _to_float(item.get("floorSize", {}).get("value") if isinstance(item.get("floorSize"), dict) else item.get("floorSize"))
    location = _extract_location(item)
    price_per_sqm = round(price / area, 2) if price and area else None
    results.append(
        {
            **meta,
            "listing_id": _listing_id(url, title, price, area),
            "title": title,
            "location": location,
            "price": price,
            "price_per_sqm": price_per_sqm,
            "area_sqm": area,
            "advertiser_type": "nieustalone",
            "publication_date": None,
            "reduced_price": 0,
            "url": url,
            "status": "active",
            "extracted_text": clean_text(json.dumps(item, ensure_ascii=False))[:1500],
        }
    )
    return results


FALLBACK_RE = re.compile(
    r"(?P<title>[A-ZĄĆĘŁŃÓŚŹŻa-ząćęłńóśźż0-9 ,./()|+-]{8,120}?)\s+"
    r"(?P<price>[0-9\s]+)\s*zł\s+"
    r"(?:[A-Za-ząćęłńóśźż ]*?)\s*"
    r"(?P<area>[0-9]+(?:[.,][0-9]+)?)\s*mkw|m²",
    re.IGNORECASE,
)


def _parse_fallback_text(payload, meta: dict) -> List[dict]:
    links = extract_links(payload.html, domain_filter="otodom.pl")
    offer_links = [l for l in links if "/oferta/" in l["href"] or "/pl/oferta/" in l["href"]]
    results = []
    for idx, m in enumerate(FALLBACK_RE.finditer(payload.text)):
        title = clean_text(m.group("title"))
        if len(title) < 8:
            continue
        url = offer_links[idx]["href"] if idx < len(offer_links) else ""
        price = _to_float(m.group("price"))
        area = _to_float(m.group("area"))
        results.append(
            {
                **meta,
                "listing_id": _listing_id(url, title, price, area),
                "title": title,
                "location": "Kutno",
                "price": price,
                "price_per_sqm": round(price / area, 2) if price and area else None,
                "area_sqm": area,
                "advertiser_type": "nieustalone",
                "publication_date": None,
                "reduced_price": 0,
                "url": url,
                "status": "active",
                "extracted_text": clean_text(m.group(0))[:1500],
            }
        )
    return results


def _extract_location(item: dict) -> str:
    addr = item.get("address") if isinstance(item.get("address"), dict) else {}
    bits = []
    for key in ["streetAddress", "addressLocality", "addressRegion"]:
        val = addr.get(key)
        if val:
            bits.append(str(val))
    if bits:
        return ", ".join(bits)
    text = clean_text(json.dumps(item, ensure_ascii=False))
    if "kutno" in text.lower():
        return "Kutno"
    return ""


def _listing_id(url: str, title: str, price: float, area: float) -> str:
    base = url or f"{title}|{price}|{area}"
    return hashlib.md5(base.encode("utf-8")).hexdigest()


def _to_float(value) -> float | None:
    if value is None:
        return None
    value = str(value).replace("zł", "").replace("m²", "").replace("mkw", "").replace(" ", "").replace(",", ".")
    try:
        return float(value)
    except ValueError:
        return None
