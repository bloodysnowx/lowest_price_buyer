from __future__ import annotations

from typing import Any

from lowest_price_buyer.models import Offer
from lowest_price_buyer.providers.base import BaseProvider, ProviderError, fetch_json


ENDPOINT = "https://app.rakuten.co.jp/services/api/IchibaItem/Search/20220601"


class RakutenProvider(BaseProvider):
    name = "rakuten"

    def __init__(self, app_id: str):
        if not app_id:
            raise ValueError("Rakuten app_id is required")
        self.app_id = app_id

    def fetch(self, keyword: str, max_results: int = 5) -> list[Offer]:
        payload = fetch_json(
            ENDPOINT,
            {
                "format": "json",
                "applicationId": self.app_id,
                "keyword": keyword,
                "hits": max_results,
                "sort": "+itemPrice",
            },
        )
        return parse_rakuten_response(payload, max_results=max_results)


def parse_rakuten_response(payload: dict[str, Any], max_results: int = 5) -> list[Offer]:
    offers: list[Offer] = []
    for wrapped in payload.get("Items", []):
        item = wrapped.get("Item") or wrapped
        if not isinstance(item, dict):
            continue

        title = str(item.get("itemName") or "").strip()
        if not title:
            continue

        try:
            price = int(float(item.get("itemPrice", 0)))
        except (TypeError, ValueError):
            continue

        point_rate = _to_float(item.get("pointRate"))
        shipping = 0
        offers.append(
            Offer(
                provider="rakuten",
                title=title,
                price_yen=price,
                shipping_yen=shipping,
                point_rate=point_rate,
                point_amount_yen=None,
                url=item.get("itemUrl"),
            )
        )
        if len(offers) >= max_results:
            break

    if not offers:
        raise ProviderError("Rakuten response did not contain usable items")
    return offers


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
