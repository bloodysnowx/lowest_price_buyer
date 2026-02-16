from __future__ import annotations

from typing import Any

from lowest_price_buyer.models import Offer
from lowest_price_buyer.providers.base import BaseProvider, ProviderError, fetch_json


ENDPOINT = "https://shopping.yahooapis.jp/ShoppingWebService/V3/itemSearch"


class YahooShoppingProvider(BaseProvider):
    name = "yahoo"

    def __init__(self, app_id: str):
        if not app_id:
            raise ValueError("Yahoo Shopping app_id is required")
        self.app_id = app_id

    def fetch(self, keyword: str, max_results: int = 5) -> list[Offer]:
        payload = fetch_json(
            ENDPOINT,
            {
                "appid": self.app_id,
                "query": keyword,
                "results": max_results,
            },
        )
        return parse_yahoo_response(payload, max_results=max_results)


def parse_yahoo_response(payload: dict[str, Any], max_results: int = 5) -> list[Offer]:
    offers: list[Offer] = []
    for item in payload.get("hits", []):
        if not isinstance(item, dict):
            continue

        title = str(item.get("name") or "").strip()
        if not title:
            continue

        price = _extract_int(item.get("price"))
        if price is None:
            continue

        shipping = _extract_shipping(item.get("shipping"))
        point_amount, point_rate = _extract_points(item.get("point"))

        offers.append(
            Offer(
                provider="yahoo",
                title=title,
                price_yen=price,
                shipping_yen=shipping,
                point_rate=point_rate,
                point_amount_yen=point_amount,
                url=item.get("url"),
            )
        )
        if len(offers) >= max_results:
            break

    if not offers:
        raise ProviderError("Yahoo Shopping response did not contain usable items")
    return offers


def _extract_int(value: Any) -> int | None:
    if isinstance(value, dict):
        for key in ("value", "amount", "price"):
            if key in value:
                return _extract_int(value[key])
        return None
    try:
        return int(float(str(value).replace(",", "")))
    except (TypeError, ValueError):
        return None


def _extract_shipping(value: Any) -> int:
    if isinstance(value, dict):
        for key in ("fee", "price", "amount"):
            if key in value:
                parsed = _extract_int(value[key])
                if parsed is not None:
                    return max(parsed, 0)
    return 0


def _extract_points(value: Any) -> tuple[int | None, float | None]:
    if not isinstance(value, dict):
        return None, None

    amount = None
    rate = None
    for key in ("amount", "value"):
        if key in value:
            amount = _extract_int(value[key])
            if amount is not None:
                break

    for key in ("rate", "times"):
        if key in value:
            try:
                rate = float(value[key])
                break
            except (TypeError, ValueError):
                continue

    return amount, rate
