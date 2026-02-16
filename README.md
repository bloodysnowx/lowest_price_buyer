# lowest_price_buyer

Yahoo Shopping, Rakuten, Amazon, and Yodobashi offers can be compared with an effective price metric:

`effective_price = listed_price + shipping - earned_points`

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

## Required credentials

- Yahoo Shopping API: `YAHOO_APP_ID`
- Rakuten Ichiba API: `RAKUTEN_APP_ID`
- Amazon and Yodobashi: scraped from search result pages (no API key)

```bash
export YAHOO_APP_ID='your_yahoo_app_id'
export RAKUTEN_APP_ID='your_rakuten_app_id'
```

## Usage

```bash
lowest-price-buyer "Nintendo Switch 本体" --max-results 5
```

Only specific providers:

```bash
lowest-price-buyer "Nintendo Switch 本体" --providers yahoo,rakuten
```

JSON output:

```bash
lowest-price-buyer "Nintendo Switch 本体" --as-json
```

## Manual offer merge

You can merge local offers (for campaign point assumptions or fixed shipping) with fetched results:

```json
[
  {
    "provider": "manual_rakuten",
    "title": "Switch sample",
    "price_yen": 32000,
    "shipping_yen": 0,
    "point_rate": 15,
    "point_amount_yen": null,
    "url": "https://example.com"
  }
]
```

Run with:

```bash
lowest-price-buyer "Nintendo Switch 本体" --manual-offers /path/to/offers.json
```

## Notes

- The same product matching quality depends on keyword precision. Include model number for better accuracy.
- Marketplace HTML/API response formats can change. If parsing fails, provider warnings are printed and other providers continue.
- Point conditions vary by account status and campaign. Adjust with `--manual-offers` when exact campaign assumptions are needed.

## Test

```bash
pytest
```
