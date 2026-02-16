from __future__ import annotations

from .models import EvaluatedOffer, Offer
from .points import calculate_points


def evaluate_offers(offers: list[Offer]) -> list[EvaluatedOffer]:
    evaluated: list[EvaluatedOffer] = []
    for offer in offers:
        gross = max(offer.price_yen + offer.shipping_yen, 0)
        points = calculate_points(offer)
        effective = max(gross - points, 0)
        evaluated.append(
            EvaluatedOffer(
                offer=offer,
                gross_price_yen=gross,
                earned_points_yen=points,
                effective_price_yen=effective,
            )
        )

    return sorted(
        evaluated,
        key=lambda item: (
            item.effective_price_yen,
            item.gross_price_yen,
            item.offer.provider,
        ),
    )
