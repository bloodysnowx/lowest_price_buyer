from __future__ import annotations

import re
from urllib.parse import quote_plus, urljoin

import requests
from bs4 import BeautifulSoup

from lowest_price_buyer.models import Offer
from lowest_price_buyer.providers.base import BaseProvider, ProviderError


SEARCH_URL = "https://www.yodobashi.com/?word="
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)


class YodobashiProvider(BaseProvider):
    name = "yodobashi"

    def fetch(self, keyword: str, max_results: int = 5) -> list[Offer]:
        url = f"{SEARCH_URL}{quote_plus(keyword)}"
        response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=20)
        response.raise_for_status()
        return parse_yodobashi_html(response.text, max_results=max_results)


def parse_yodobashi_html(html: str, max_results: int = 5) -> list[Offer]:
    soup = BeautifulSoup(html, "html.parser")
    offers: list[Offer] = []
    seen_urls: set[str] = set()

    for link in soup.select("a[href*='/product/']"):
        href = link.get("href")
        if not href:
            continue
        url = urljoin("https://www.yodobashi.com", href)
        if url in seen_urls:
            continue

        container = link.find_parent(["li", "div", "article"]) or link
        text = container.get_text(" ", strip=True)
        title = link.get_text(" ", strip=True)
        if not title:
            continue

        price = _extract_first_int(r"([0-9][0-9,]*)\s*円", text)
        if price is None:
            continue

        points = _extract_first_int(r"([0-9][0-9,]*)\s*ポイント", text)
        point_rate = None
        if points is None:
            raw_rate = _extract_first_int(r"([0-9]{1,2})\s*%\s*還元", text)
            point_rate = float(raw_rate) if raw_rate is not None else None

        offers.append(
            Offer(
                provider="yodobashi",
                title=title,
                price_yen=price,
                shipping_yen=0,
                point_rate=point_rate,
                point_amount_yen=points,
                url=url,
            )
        )
        seen_urls.add(url)
        if len(offers) >= max_results:
            break

    if not offers:
        raise ProviderError("Yodobashi HTML did not contain usable items")
    return offers


def _extract_first_int(pattern: str, text: str) -> int | None:
    match = re.search(pattern, text)
    if not match:
        return None
    return int(match.group(1).replace(",", ""))
