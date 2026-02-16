from lowest_price_buyer.comparator import evaluate_offers
from lowest_price_buyer.models import Offer


def test_evaluate_offers_sort_by_effective_price():
    offers = [
        Offer(provider="a", title="A", price_yen=10000, point_rate=10),
        Offer(provider="b", title="B", price_yen=9800, point_amount_yen=100),
        Offer(provider="c", title="C", price_yen=9900, shipping_yen=500, point_rate=5),
    ]

    ranked = evaluate_offers(offers)

    assert ranked[0].offer.provider == "a"  # 10000 - 1000 = 9000
    assert ranked[0].effective_price_yen == 9000
    assert ranked[1].offer.provider == "b"  # 9800 - 100 = 9700
    assert ranked[2].offer.provider == "c"  # (9900+500) - 520 = 9880
