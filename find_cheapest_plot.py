#!/usr/bin/env python3
"""Find the cheapest Splinterlands plots for sale using the live market API.

Important: the live Splinterlands VAPI listing endpoint exposes generic LAND/PLOT
listings, not a fully enriched plot object with region/resource/rarity metadata.
This script uses the real live endpoint and keeps the optional filters working
when the metadata is present in the payload; otherwise it reports that the filter
cannot be applied to the live data.

Examples:
    python find_cheapest_plot.py --plot-type normal --top 10
    python find_cheapest_plot.py --region water --top 10
    python find_cheapest_plot.py --resource wood --rarity common
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from typing import Any, Iterable

import requests


BASE_URL = "https://vapi.splinterlands.com"

VALID_PLOT_TYPES = {"normal", "magic", "occupied", "castle", "keep"}
VALID_RESOURCES = {"grain", "ore", "stone", "wood"}
TARGET_CATEGORIES = ("normal", "rare", "magic", "occupied", "grain")
CACHE_PATH = "/tmp/splinterlands-land-deeds.json"
CACHE_TTL_SECONDS = 60
TARGET_REGIONS = {
    "xiang pho 85": {"xiang pho 85", "xian pho 85", "xiangpho 85", "xianpho 85", "xiang pho", "xian pho", "xiangpho", "xianpho", "85"},
    "ravenwood 133": {"ravenwood 133", "raven wood 133", "ravenwood133", "raven wood133", "ravenwood", "raven wood", "133"},
}
RARITY_ALIASES = {
    "common": {"common", "c"},
    "rare": {"rare", "r"},
    "epic": {"epic", "e"},
    "legendary": {"legendary", "legend", "l"},
    "mythic": {"mythic", "m"},
}


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip().lower().replace("_", " ").replace("-", " ")
    text = re.sub(r"\s+", " ", text)
    return text


def normalize_rarity(value: Any) -> str:
    text = normalize_text(value)
    if not text:
        return ""
    for canonical, aliases in RARITY_ALIASES.items():
        if text in aliases or text == canonical:
            return canonical
    if text.isdigit():
        mapping = {"1": "common", "2": "rare", "3": "epic", "4": "legendary", "5": "mythic"}
        return mapping.get(text, text)
    return text


def _get_first(mapping: dict[str, Any], keys: Iterable[str]) -> Any:
    if not isinstance(mapping, dict):
        return None
    for key in keys:
        if key in mapping:
            return mapping[key]
        alt = key.lower()
        for actual_key in mapping:
            if isinstance(actual_key, str) and actual_key.lower() == alt:
                return mapping[actual_key]
    return None


def _deep_get(data: Any, keys: Iterable[str]) -> Any:
    if isinstance(data, dict):
        value = _get_first(data, keys)
        if value is not None:
            return value
        for nested in data.values():
            found = _deep_get(nested, keys)
            if found is not None:
                return found
    elif isinstance(data, list):
        for item in data:
            found = _deep_get(item, keys)
            if found is not None:
                return found
    return None


def clean_price(value: Any) -> float:
    if value is None:
        return float("inf")
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = value.replace("$", "").replace(",", "").strip()
        if not cleaned or cleaned.lower() in {"null", "none", "n/a"}:
            return float("inf")
        try:
            return float(cleaned)
        except ValueError:
            pass
        match = re.search(r"[-+]?\d*\.?\d+", cleaned)
        if match:
            return float(match.group(0))
    return float("inf")


def normalize_plot(raw_plot: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(raw_plot, dict):
        return {}

    merged = raw_plot.copy()
    nested = raw_plot.get("details") or raw_plot.get("plot") or raw_plot.get("data") or {}
    if isinstance(nested, dict):
        merged.update(nested)

    region = (
        _get_first(merged, ("region_name", "region", "land_region", "name"))
        or _deep_get(merged, ("region_name", "region", "land_region"))
    )

    plot_type = _get_first(merged, ("plot_type", "plotType", "land_type", "type", "plot type"))
    if plot_type is None and isinstance(merged.get("type"), dict):
        plot_type = merged["type"].get("name") or merged["type"].get("plot_type")

    resource = _get_first(merged, ("resource_type", "resource", "resource_name", "resourceType", "resource type"))
    if resource is None and isinstance(merged.get("tile"), dict):
        resource = merged["tile"].get("type") or merged["tile"].get("resource")

    rarity = _get_first(merged, ("rarity", "rarity_name", "quality", "tier", "chance"))
    price = _get_first(merged, ("price", "buy_price", "market_price", "sell_price", "cost"))
    plot_id = _get_first(merged, ("plot_id", "id", "uid", "plotId"))

    region_name = normalize_text(region) if region is not None else ""
    plot_name = normalize_text(plot_type) if plot_type is not None else ""
    resource_name = normalize_text(resource) if resource is not None else ""
    rarity_name = normalize_rarity(rarity) if rarity is not None else ""
    price_value = clean_price(price)

    # Some payloads encode plot type as a nested dict or a very generic value; keep it tolerant.
    if plot_name and plot_name not in VALID_PLOT_TYPES:
        aliases = {
            "normal": "normal",
            "basic": "normal",
            "magic": "magic",
            "occupied": "occupied",
            "castle": "castle",
            "keep": "keep",
        }
        plot_name = aliases.get(plot_name, plot_name)

    if resource_name in {"grain", "ore", "stone", "wood"}:
        pass
    elif resource_name in {"food", "grain resource"}:
        resource_name = "grain"
    elif resource_name in {"metal", "ore resource"}:
        resource_name = "ore"
    elif resource_name in {"rock", "stone resource"}:
        resource_name = "stone"
    elif resource_name in {"timber", "wood resource"}:
        resource_name = "wood"

    return {
        "id": plot_id,
        "region": region_name,
        "plot_type": plot_name,
        "resource": resource_name,
        "rarity": rarity_name,
        "price": price_value,
        "raw": raw_plot,
    }


def extract_items(response_json: Any) -> list[dict[str, Any]]:
    if isinstance(response_json, list):
        return [item for item in response_json if isinstance(item, dict)]

    if not isinstance(response_json, dict):
        return []

    for key in ("plots", "lands", "items", "data", "results", "for_sale", "market"):
        value = response_json.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
        if isinstance(value, dict):
            nested_items = extract_items(value)
            if nested_items:
                return nested_items

    # Some APIs return a dict keyed by plot id.
    if any(isinstance(v, dict) for v in response_json.values()):
        items = []
        for value in response_json.values():
            if isinstance(value, dict):
                items.append(value)
        return items

    return []


def fetch_lands_market() -> list[dict[str, Any]]:
    """Fetch live Splinterlands land deeds from the VAPI land endpoint."""
    try:
        cache_age = time.time() - os.path.getmtime(CACHE_PATH)
        if cache_age <= CACHE_TTL_SECONDS:
            with open(CACHE_PATH, "r", encoding="utf-8") as cache_file:
                cached = json.load(cache_file)
            if isinstance(cached, list):
                return cached
    except (OSError, ValueError, TypeError):
        pass

    endpoint = f"{BASE_URL}/land/deeds"
    try:
        response = requests.get(endpoint, timeout=30)
        response.raise_for_status()
    except Exception:
        return []

    try:
        payload = response.json()
    except ValueError:
        return []

    if payload.get("status") != "success":
        return []

    data = payload.get("data") or {}
    deeds = data.get("deeds") or []
    normalized = []
    for deed in deeds:
        if not isinstance(deed, dict):
            continue
        if not deed.get("listed"):
            continue
        plot = normalize_live_item(deed)
        if plot.get("price") != float("inf"):
            normalized.append(plot)

    try:
        with open(CACHE_PATH, "w", encoding="utf-8") as cache_file:
            json.dump(normalized, cache_file)
    except OSError:
        pass

    return normalized


def normalize_live_item(raw_item: dict[str, Any]) -> dict[str, Any]:
    """Normalize a live Splinterlands land deed record from the land/deeds API."""
    if not isinstance(raw_item, dict):
        return {}

    region = raw_item.get("region_name") or raw_item.get("territory") or raw_item.get("region") or ""
    plot_status = raw_item.get("plot_status") or raw_item.get("status") or ""
    plot_name = normalize_text(plot_status)
    if plot_name == "natural":
        plot_type = "normal"
    elif plot_name == "magical":
        plot_type = "magic"
    elif plot_name == "occupied":
        plot_type = "occupied"
    else:
        plot_type = plot_name

    resource = parse_land_resource(raw_item)
    rarity = normalize_rarity(raw_item.get("rarity"))
    price = clean_price(raw_item.get("listing_price"))

    return {
        "id": raw_item.get("market_listing_id") or raw_item.get("deed_uid") or raw_item.get("plot_id"),
        "region": normalize_region_name(region),
        "plot_type": plot_type,
        "resource": resource,
        "rarity": rarity,
        "price": price,
        "raw": raw_item,
    }


def build_demo_plots() -> list[dict[str, Any]]:
    return [
        {"id": "xian-85-normal-plain-1", "region": "xian pho 85", "plot_type": "normal", "resource": "wood", "rarity": "common", "price": 12},
        {"id": "xian-85-normal-plain-2", "region": "xian pho 85", "plot_type": "normal", "resource": "grain", "rarity": "common", "price": 9},
        {"id": "xian-85-normal-plain-3", "region": "xian pho 85", "plot_type": "normal", "resource": "stone", "rarity": "rare", "price": 17},
        {"id": "xian-85-rare-1", "region": "xian pho 85", "plot_type": "normal", "resource": "ore", "rarity": "rare", "price": 22},
        {"id": "xian-85-magic-1", "region": "xian pho 85", "plot_type": "magic", "resource": "wood", "rarity": "common", "price": 28},
        {"id": "xian-85-occupied-1", "region": "xian pho 85", "plot_type": "occupied", "resource": "stone", "rarity": "epic", "price": 44},
        {"id": "raven-133-normal-1", "region": "ravenwood 133", "plot_type": "normal", "resource": "grain", "rarity": "common", "price": 10},
        {"id": "raven-133-normal-2", "region": "ravenwood 133", "plot_type": "normal", "resource": "wood", "rarity": "rare", "price": 16},
        {"id": "raven-133-magic-1", "region": "ravenwood 133", "plot_type": "magic", "resource": "stone", "rarity": "common", "price": 26},
        {"id": "raven-133-occupied-1", "region": "ravenwood 133", "plot_type": "occupied", "resource": "ore", "rarity": "rare", "price": 41},
        {"id": "raven-133-rare-1", "region": "ravenwood 133", "plot_type": "normal", "resource": "wood", "rarity": "rare", "price": 18},
        {"id": "other-1", "region": "other region", "plot_type": "normal", "resource": "grain", "rarity": "common", "price": 8},
    ]


def normalize_region_name(value: Any) -> str:
    text = normalize_text(value)
    for canonical, aliases in TARGET_REGIONS.items():
        if text in aliases:
            return canonical
    return text


def matches_region(plot_region: Any, requested_region: Any) -> bool:
    requested = normalize_region_name(requested_region)
    actual = normalize_region_name(plot_region)
    return requested == actual


def parse_land_resource(raw_deed: dict[str, Any]) -> str:
    resource = raw_deed.get("resource_symbol") or raw_deed.get("resource") or raw_deed.get("resource_id")
    if resource is not None:
        resource_text = normalize_text(resource)
        if resource_text in {"wood", "ore", "stone", "grain"}:
            return resource_text
        if resource_text in {"wood_ore", "ore_wood", "orewood"}:
            return "ore"
    stats = raw_deed.get("land_stats")
    if isinstance(stats, str):
        match = re.search(r'"resources"\s*:\s*\[(.*?)\]', stats, re.I)
        if match:
            names = match.group(1)
            for candidate in ("wood", "ore", "stone", "grain"):
                if candidate in names.lower():
                    return candidate
    return ""


def parse_region_list(value: str | None) -> list[str]:
    if not value:
        return []
    regions = []
    for raw in value.split(","):
        name = normalize_region_name(raw)
        if name:
            regions.append(name)
    return regions


def matches_filters(plot: dict[str, Any], region: str | list[str] | tuple[str, ...] | set[str] | None, plot_type: str | None, resource: str | None, rarity: str | None) -> bool:
    if region is not None:
        if isinstance(region, (list, tuple, set)):
            allowed = {normalize_region_name(item) for item in region if item}
            plot_region = normalize_text(plot.get("region"))
            if not plot_region or normalize_region_name(plot_region) not in allowed:
                return False
        else:
            region_name = normalize_region_name(region)
            plot_region = normalize_text(plot.get("region"))
            if not plot_region:
                return False
            if not matches_region(plot_region, region_name):
                return False

    if plot_type is not None:
        requested = normalize_text(plot_type)
        actual = normalize_text(plot.get("plot_type"))
        if not actual:
            return False
        if requested != actual:
            return False

    if resource is not None:
        requested = normalize_text(resource)
        actual = normalize_text(plot.get("resource"))
        if not actual:
            return False
        if requested != actual:
            return False

    if rarity is not None:
        requested = normalize_rarity(rarity)
        actual = normalize_rarity(plot.get("rarity"))
        if not actual:
            return False
        if requested != actual:
            return False

    return True


def find_cheapest_plots(plots: list[dict[str, Any]], region: str | list[str] | tuple[str, ...] | set[str] | None = None, plot_type: str | None = None, resource: str | None = None, rarity: str | None = None, limit: int = 5) -> list[dict[str, Any]]:
    filtered = []
    for item in plots:
        plot = normalize_plot(item)
        if not plot:
            continue
        if not matches_filters(plot, region, plot_type, resource, rarity):
            continue
        price = plot.get("price")
        if isinstance(price, (int, float)) and price != float("inf"):
            filtered.append(plot)

    filtered.sort(key=lambda item: item.get("price", float("inf")))
    return filtered[:limit]


def find_category_matches(plots: list[dict[str, Any]], regions: list[str] | None, categories: list[str], limit: int = 2) -> list[tuple[str, list[dict[str, Any]]]]:
    buckets: list[tuple[str, list[dict[str, Any]]]] = []
    requested = [normalize_text(category) for category in categories if category]
    region_filter = list(regions) if regions else None
    for category in requested:
        if category in {"normal", "plain"}:
            matches = find_cheapest_plots(plots, region=region_filter, plot_type="normal", limit=limit)
        elif category == "rare":
            matches = find_cheapest_plots(plots, region=region_filter, rarity="rare", limit=limit)
        elif category == "magic":
            matches = find_cheapest_plots(plots, region=region_filter, plot_type="magic", limit=limit)
        elif category == "occupied":
            matches = find_cheapest_plots(plots, region=region_filter, plot_type="occupied", limit=limit)
        else:
            matches = []
        buckets.append((category, matches))
    return buckets


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Find the cheapest Splinterlands plot for sale.")
    parser.add_argument("--region", help="Region name, for example: water, fire, earth, life, neutral")
    parser.add_argument("--regions", help="Comma-separated region names to search, such as 'Xian Pho 85,Ravenwood 133'")
    parser.add_argument("--plot-type", choices=sorted(VALID_PLOT_TYPES), help="Plot type: normal, magic, occupied, castle, keep")
    parser.add_argument("--resource", choices=sorted(VALID_RESOURCES), help="Resource: grain, ore, stone, wood")
    parser.add_argument("--rarity", help="Rarity name or numeric tier, such as common, rare, epic, legendary, mythic, or 1-5")
    parser.add_argument("--categories", help="Comma-separated targeted categories: normal, rare, magic, occupied")
    parser.add_argument("--top", type=int, default=5, help="Number of results to display (default: 5)")
    parser.add_argument("--demo", action="store_true", help="Use local sample data instead of the live market API.")
    return parser.parse_args()


def pretty_print(plot: dict[str, Any]) -> None:
    print(
        f"id={plot.get('id') or 'n/a'} | "
        f"region={plot.get('region') or 'n/a'} | "
        f"plot_type={plot.get('plot_type') or 'n/a'} | "
        f"resource={plot.get('resource') or 'n/a'} | "
        f"rarity={plot.get('rarity') or 'n/a'} | "
        f"price={plot.get('price', 'n/a')}"
    )


def main() -> int:
    args = parse_args()

    if args.demo:
        plots = build_demo_plots()
        print("Using demo plot data because demo mode was requested.")
    else:
        plots = fetch_lands_market()
        if not plots:
            print("Live market query returned no land listings; falling back to demo data.")
            plots = build_demo_plots()

    if not args.demo and plots and all(not plot.get("region") and not plot.get("resource") and not plot.get("rarity") for plot in plots[:3]):
        print("Live Splinterlands market data currently exposes generic LAND/PLOT listings only; region/resource/rarity filters are applied only when the payload includes that metadata.")

    requested_regions = parse_region_list(args.regions) if args.regions else []
    if args.region:
        requested_regions = [normalize_region_name(args.region)]
    requested_categories = []
    if args.categories:
        requested_categories = [normalize_text(category).replace("plain", "normal") for category in args.categories.split(",") if category]
    elif args.plot_type and args.rarity:
        requested_categories = [normalize_text(args.plot_type), normalize_text(args.rarity)]
    elif args.plot_type:
        requested_categories = [normalize_text(args.plot_type)]
    elif args.rarity:
        requested_categories = [normalize_text(args.rarity)]

    if requested_regions or requested_categories:
        categories = requested_categories or list(TARGET_CATEGORIES)
        if not requested_regions:
            requested_regions = ["xiang pho 85", "ravenwood 133"]
        print(f"Lowest {args.top} matches by region and category for: {', '.join(requested_regions)}\n")
        for region in requested_regions:
            print(f"Region: {region}")
            region_matches = []
            for category in categories:
                category_matches = []
                if category in {"normal", "plain"}:
                    category_matches = find_cheapest_plots(plots, region=region, plot_type="normal", limit=args.top)
                elif category == "rare":
                    category_matches = find_cheapest_plots(plots, region=region, rarity="rare", limit=args.top)
                elif category == "magic":
                    category_matches = find_cheapest_plots(plots, region=region, plot_type="magic", limit=args.top)
                elif category == "occupied":
                    category_matches = find_cheapest_plots(plots, region=region, plot_type="occupied", limit=args.top)
                elif category == "grain":
                    category_matches = find_cheapest_plots(plots, region=region, resource="grain", limit=args.top)
                region_matches.append((category, category_matches))
            if not any(matches for _, matches in region_matches):
                print("  no matches")
                print()
                continue
            for category, matches in region_matches:
                print(f"  Category: {category}")
                if not matches:
                    print("    no matches")
                    continue
                for plot in matches:
                    pretty_print(plot)
                print()
            print()
        return 0

    matches = find_cheapest_plots(
        plots,
        region=args.region,
        plot_type=args.plot_type,
        resource=args.resource,
        rarity=args.rarity,
        limit=args.top,
    )

    if not matches:
        if not args.demo:
            print("No live plot listings matched the requested filters. The current market endpoint only exposes generic LAND/PLOT listing rows; if you need richer filters, use a payload that includes region/resource/rarity metadata.")
        else:
            print("No plots matched the requested filters.")
        return 0

    print(f"Top {len(matches)} cheapest matching plots:\n")
    for plot in matches:
        pretty_print(plot)
    return 0


if __name__ == "__main__":
    sys.exit(main())
