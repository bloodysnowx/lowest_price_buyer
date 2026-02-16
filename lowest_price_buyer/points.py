from __future__ import annotations

from .models import Offer


def calculate_points(offer: Offer) -> int:
    if offer.point_amount_yen is not None:
        return max(offer.point_amount_yen, 0)

    if offer.point_rate is None:
        return 0

    gross = max(offer.price_yen + offer.shipping_yen, 0)
    return int(gross * (offer.point_rate / 100.0))
