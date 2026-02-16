from __future__ import annotations

import re
from urllib.parse import quote_plus, urljoin

import requests
from bs4 import BeautifulSoup

from lowest_price_buyer.models import Offer
from lowest_price_buyer.providers.base import BaseProvider, ProviderError


SEARCH_URL = "https://www.amazon.co.jp/s"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)


class AmazonProvider(BaseProvider):
    name = "amazon"

    def fetch(self, keyword: str, max_results: int = 5) -> list[Offer]:
        url = f"{SEARCH_URL}?k={quote_plus(keyword)}"
        response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=20)
        response.raise_for_status()
        return parse_amazon_html(response.text, max_results=max_results)


def parse_amazon_html(html: str, max_results: int = 5) -> list[Offer]:
    soup = BeautifulSoup(html, "html.parser")
    offers: list[Offer] = []

    for node in soup.select("div.s-result-item[data-component-type='s-search-result']"):
        title_node = node.select_one("h2 span")
        price_node = node.select_one("span.a-price span.a-offscreen")
        link_node = node.select_one("h2 a")
        if not title_node or not price_node:
            continue

        title = title_node.get_text(strip=True)
        price = _extract_yen(price_node.get_text())
        if price is None:
            continue

        text = node.get_text(" ", strip=True)
        point_amount = _extract_points(text)
        url = None
        if link_node and link_node.get("href"):
            url = urljoin("https://www.amazon.co.jp", link_node["href"])

        offers.append(
            Offer(
                provider="amazon",
                title=title,
                price_yen=price,
                point_amount_yen=point_amount,
                point_rate=None,
                shipping_yen=0,
                url=url,
            )
        )
        if len(offers) >= max_results:
            break

    if not offers:
        raise ProviderError("Amazon HTML did not contain usable items")
    return offers


def _extract_yen(text: str) -> int | None:
    match = re.search(r"([0-9][0-9,]*)", text)
    if not match:
        return None
    return int(match.group(1).replace(",", ""))


def _extract_points(text: str) -> int | None:
    match = re.search(r"([0-9][0-9,]*)\s*ポイント", text)
    if not match:
        return None
    return int(match.group(1).replace(",", ""))
