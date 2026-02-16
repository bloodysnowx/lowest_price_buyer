from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from lowest_price_buyer.comparator import evaluate_offers
from lowest_price_buyer.models import Offer


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare effective price (price - points) across marketplaces"
    )
    parser.add_argument("keyword", help="Search keyword (e.g. model name)")
    parser.add_argument(
        "--providers",
        default="yahoo,rakuten,amazon,yodobashi",
        help="Comma separated providers. available: yahoo,rakuten,amazon,yodobashi",
    )
    parser.add_argument("--max-results", type=int, default=5)
    parser.add_argument("--rakuten-app-id", default=os.getenv("RAKUTEN_APP_ID"))
    parser.add_argument("--yahoo-app-id", default=os.getenv("YAHOO_APP_ID"))
    parser.add_argument(
        "--manual-offers",
        type=Path,
        help="Optional JSON file of offers to merge. Format: list[Offer-like dict]",
    )
    parser.add_argument("--as-json", action="store_true", help="Output as JSON")
    return parser


def _build_provider(provider_name: str, args: argparse.Namespace):
    if provider_name == "yahoo":
        if not args.yahoo_app_id:
            print("[skip] yahoo: set YAHOO_APP_ID or --yahoo-app-id")
            return None
        from lowest_price_buyer.providers.yahoo import YahooShoppingProvider

        return YahooShoppingProvider(app_id=args.yahoo_app_id)

    if provider_name == "rakuten":
        if not args.rakuten_app_id:
            print("[skip] rakuten: set RAKUTEN_APP_ID or --rakuten-app-id")
            return None
        from lowest_price_buyer.providers.rakuten import RakutenProvider

        return RakutenProvider(app_id=args.rakuten_app_id)

    if provider_name == "amazon":
        from lowest_price_buyer.providers.amazon import AmazonProvider

        return AmazonProvider()

    if provider_name == "yodobashi":
        from lowest_price_buyer.providers.yodobashi import YodobashiProvider

        return YodobashiProvider()

    print(f"[skip] unknown provider: {provider_name}")
    return None


def _load_manual_offers(path: Path | None) -> list[Offer]:
    if path is None:
        return []

    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("manual offers must be a list")

    offers: list[Offer] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        offers.append(Offer.from_dict(item))
    return offers


def _print_table(rows: list[dict]) -> None:
    if not rows:
        print("No offers found")
        return

    headers = ["provider", "title", "gross_yen", "points_yen", "effective_yen", "url"]
    widths = {header: len(header) for header in headers}
    for row in rows:
        for header in headers:
            widths[header] = max(widths[header], len(str(row[header])))

    line = " | ".join(header.ljust(widths[header]) for header in headers)
    print(line)
    print("-+-".join("-" * widths[header] for header in headers))
    for row in rows:
        print(" | ".join(str(row[h]).ljust(widths[h]) for h in headers))


def main() -> int:
    args = build_parser().parse_args()

    providers = [p.strip().lower() for p in args.providers.split(",") if p.strip()]
    offers: list[Offer] = _load_manual_offers(args.manual_offers)

    for provider_name in providers:
        provider = _build_provider(provider_name, args)
        if provider is None:
            continue

        try:
            offers.extend(provider.fetch(args.keyword, max_results=args.max_results))
        except Exception as exc:
            print(f"[warn] {provider_name}: {exc}")

    ranked = evaluate_offers(offers)
    rows = [
        {
            "provider": item.offer.provider,
            "title": item.offer.title,
            "gross_yen": item.gross_price_yen,
            "points_yen": item.earned_points_yen,
            "effective_yen": item.effective_price_yen,
            "url": item.offer.url or "",
        }
        for item in ranked
    ]

    if args.as_json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
    else:
        _print_table(rows)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
