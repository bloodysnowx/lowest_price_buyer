from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Offer:
    provider: str
    title: str
    price_yen: int
    shipping_yen: int = 0
    point_rate: float | None = None
    point_amount_yen: int | None = None
    url: str | None = None

    @classmethod
    def from_dict(cls, data: dict) -> "Offer":
        return cls(
            provider=str(data["provider"]),
            title=str(data["title"]),
            price_yen=int(data["price_yen"]),
            shipping_yen=int(data.get("shipping_yen", 0) or 0),
            point_rate=float(data["point_rate"]) if data.get("point_rate") is not None else None,
            point_amount_yen=(
                int(data["point_amount_yen"])
                if data.get("point_amount_yen") is not None
                else None
            ),
            url=data.get("url"),
        )


@dataclass
class EvaluatedOffer:
    offer: Offer
    gross_price_yen: int
    earned_points_yen: int
    effective_price_yen: int
