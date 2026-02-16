from lowest_price_buyer.providers.amazon import parse_amazon_html
from lowest_price_buyer.providers.rakuten import parse_rakuten_response


def test_parse_amazon_html_extracts_price_and_points():
    html = """
    <div class='s-result-item' data-component-type='s-search-result'>
      <h2><a href='/dp/B0001'><span>Sample Product</span></a></h2>
      <span class='a-price'><span class='a-offscreen'>￥12,800</span></span>
      <span>128ポイント(1%)</span>
    </div>
    """
    offers = parse_amazon_html(html, max_results=5)

    assert len(offers) == 1
    assert offers[0].title == "Sample Product"
    assert offers[0].price_yen == 12800
    assert offers[0].point_amount_yen == 128


def test_parse_rakuten_response_extracts_items():
    payload = {
        "Items": [
            {
                "Item": {
                    "itemName": "Rakuten Product",
                    "itemPrice": 5000,
                    "pointRate": 5,
                    "itemUrl": "https://example.com/item",
                }
            }
        ]
    }

    offers = parse_rakuten_response(payload, max_results=5)
    assert len(offers) == 1
    assert offers[0].provider == "rakuten"
    assert offers[0].price_yen == 5000
    assert offers[0].point_rate == 5.0
