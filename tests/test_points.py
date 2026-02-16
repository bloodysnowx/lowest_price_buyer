from lowest_price_buyer.models import Offer
from lowest_price_buyer.points import calculate_points


def test_point_amount_has_priority_over_rate():
    offer = Offer(
        provider="test",
        title="test",
        price_yen=1000,
        shipping_yen=0,
        point_rate=10,
        point_amount_yen=50,
    )
    assert calculate_points(offer) == 50


def test_rate_based_point_calc():
    offer = Offer(
        provider="test",
        title="test",
        price_yen=1234,
        shipping_yen=66,
        point_rate=5,
    )
    assert calculate_points(offer) == 65
