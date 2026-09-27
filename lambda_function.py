"""AWS Lambda entry point for the Splinterlands land check."""

from __future__ import annotations

import json
import os

import boto3

from find_cheapest_plot import fetch_lands_market, find_category_matches, normalize_region_name


ssm = boto3.client("ssm")


def get_parameter(name: str, with_decryption: bool = False) -> str:
    response = ssm.get_parameter(Name=name, WithDecryption=with_decryption)
    return response["Parameter"]["Value"]


def lambda_handler(event, context):
    username = get_parameter(
        os.getenv("ACCOUNT_PARAMETER", "SplinterlandsAccount"),
        with_decryption=False,
    )
    posting_key = get_parameter(
        os.getenv("POSTING_KEY_PARAMETER", "HivePostingKey"),
        with_decryption=True,
    )

    regions = [
        normalize_region_name(region)
        for region in event.get("regions", ["85", "133"])
    ]
    categories = event.get(
        "categories",
        ["normal", "rare", "magic", "occupied", "grain"],
    )
    limit = int(event.get("top", 2))

    listings = fetch_lands_market()
    results = {}
    for region in regions:
        category_results = {}
        for requested_category in categories:
            category, matches = find_category_matches(
                listings,
                [region],
                [requested_category],
                limit=limit,
            )[0]
            category_results[category] = matches
        results[region] = category_results

    # The secret is intentionally used only to prove it was retrieved. It is
    # never returned or written to CloudWatch logs.
    _ = posting_key
    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "account": username,
                "regions": results,
                "listing_count": len(listings),
            },
            default=str,
        ),
    }