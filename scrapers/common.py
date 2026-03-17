from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import List

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from config import (
    HEADLESS,
    PAGE_TIMEOUT_MS,
    SCROLL_PAUSE_MS,
    SCROLL_STEPS,
    USER_AGENT,
)


@dataclass
class PagePayload:
    html: str
    text: str
    final_url: str


SPACE_RE = re.compile(r"\s+")


def clean_text(value: str) -> str:
    value = value or ""
    return SPACE_RE.sub(" ", value).strip()


def fetch_page(url: str) -> PagePayload:
    logging.info("Pobieranie: %s", url)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        page = browser.new_page(user_agent=USER_AGENT)
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=PAGE_TIMEOUT_MS)
            _accept_cookies_if_present(page)
            for _ in range(SCROLL_STEPS):
                page.mouse.wheel(0, 3000)
                page.wait_for_timeout(SCROLL_PAUSE_MS)
            html = page.content()
            text = clean_text(page.locator("body").inner_text())
            return PagePayload(html=html, text=text, final_url=page.url)
        finally:
            browser.close()


def _accept_cookies_if_present(page) -> None:
    labels = [
        "Zaakceptuj",
        "Akceptuję",
        "Akceptuj",
        "Accept",
        "Zgadzam się",
        "Przejdź do serwisu",
    ]
    for label in labels:
        try:
            locator = page.get_by_role("button", name=label)
            if locator.count() > 0:
                locator.first.click(timeout=1500)
                page.wait_for_timeout(500)
                return
        except Exception:
            continue


def extract_links(html: str, domain_filter: str | None = None) -> List[dict]:
    soup = BeautifulSoup(html, "lxml")
    links = []
    seen = set()
    for a in soup.find_all("a", href=True):
        href = a.get("href", "")
        text = clean_text(a.get_text(" ", strip=True))
        if not href or href.startswith("#"):
            continue
        if domain_filter and domain_filter not in href:
            continue
        key = (href, text)
        if key in seen:
            continue
        seen.add(key)
        links.append({"href": href, "text": text})
    return links
