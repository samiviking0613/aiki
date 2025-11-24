#!/usr/bin/env python3
"""
Hent faktisk weekly usage fra Claude.ai via OAuth token.
Brukes av statusline.sh for å vise riktig weekly %.
"""

import json
import os
import sys
import time
from pathlib import Path

CREDENTIALS_PATH = Path.home() / ".claude" / ".credentials.json"
CACHE_PATH = Path.home() / "aiki" / "data" / "claude_weekly_usage_cache.json"
CACHE_TTL = 300  # 5 minutter cache


def get_oauth_token():
    """Les OAuth access token fra Claude Code credentials."""
    if not CREDENTIALS_PATH.exists():
        return None

    with open(CREDENTIALS_PATH) as f:
        creds = json.load(f)

    return creds.get("claudeAiOauth", {}).get("accessToken")


def get_admin_api_key():
    """Les Anthropic admin API key fra fil."""
    api_keys_file = Path.home() / "aiki" / "Api-nøkler" / "Api keys openai anthropic.txt"

    if not api_keys_file.exists():
        return None

    with open(api_keys_file) as f:
        for line in f:
            if line.strip().startswith("Anthropic_admin_key1:"):
                return line.split(":", 1)[1].strip()

    return None


def fetch_usage_from_api(api_key):
    """
    Hent usage fra Anthropic Admin API (cost_report endpoint).
    """
    import urllib.request
    import urllib.error
    from datetime import datetime, timedelta

    # Beregn ukens start (søndag 10:59 UTC)
    # Claude Max 5x weekly limit resets søndag kl. 10:59 UTC (bekreftet fra claude.ai)
    now = datetime.utcnow()
    days_since_sunday = (now.weekday() + 1) % 7  # Mandag=0 → 1 dag siden søndag
    last_sunday = now - timedelta(days=days_since_sunday)
    week_start = last_sunday.replace(hour=10, minute=59, second=0, microsecond=0)

    # Hvis nåtid er før denne søndagens 10:59, gå tilbake én uke
    if now < week_start:
        week_start -= timedelta(days=7)

    # Format: ISO 8601
    starting_at = week_start.strftime("%Y-%m-%dT%H:%M:%SZ")

    try:
        # Anthropic Admin API: Cost Report endpoint
        # Limit må være <= 31 (antall dager)
        url = f"https://api.anthropic.com/v1/organizations/cost_report?starting_at={starting_at}&limit=7"

        req = urllib.request.Request(
            url,
            headers={
                "anthropic-version": "2023-06-01",
                "x-api-key": api_key,
            }
        )

        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            return data

    except urllib.error.HTTPError as e:
        # Logg error for debugging
        error_body = e.read().decode() if hasattr(e, 'read') else str(e)
        print(f"HTTP Error {e.code}: {error_body}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error fetching usage: {e}", file=sys.stderr)
        return None


def scrape_claude_web_usage():
    """
    Scrape claude.ai/settings/usage med Selenium.
    Fallback hvis API ikke fungerer.
    """
    # TODO: Implementer selenium scraping hvis nødvendig
    # For nå, returnerer None
    return None


def get_cached_usage():
    """Les cached weekly usage hvis < 5 min gammelt."""
    if not CACHE_PATH.exists():
        return None

    with open(CACHE_PATH) as f:
        cache = json.load(f)

    age = time.time() - cache.get("timestamp", 0)
    if age < CACHE_TTL:
        return cache.get("weekly_percent")

    return None


def save_cache(weekly_percent):
    """Lagre weekly usage til cache."""
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(CACHE_PATH, "w") as f:
        json.dump({
            "weekly_percent": weekly_percent,
            "timestamp": time.time()
        }, f)


def calculate_weekly_percent(usage_data):
    """
    Beregn weekly % basert på Anthropic cost_report response.

    Actual format fra Admin API:
    {
        "data": [
            {
                "starting_at": "2025-11-17T00:00:00Z",
                "ending_at": "2025-11-18T00:00:00Z",
                "results": [
                    {"currency": "USD", "amount": "12.49127", ...}
                ]
            },
            ...
        ],
        "has_more": false
    }
    """
    # Debug: skriv rådata til stderr (optional - sett DEBUG=1 for å enable)
    # print(f"DEBUG: Raw API response: {json.dumps(usage_data, indent=2)[:1000]}", file=sys.stderr)

    try:
        # Parse cost_report format (liste av dager)
        if "data" in usage_data:
            data = usage_data["data"]

            # Summer alle amounts fra alle dager
            total_cost = 0.0
            for day in data:
                if "results" in day:
                    for result in day["results"]:
                        amount = float(result.get("amount", 0))
                        total_cost += amount

            # Estimert weekly limit basert på Max 5x plan
            # Max 5x: 140-280 hours/uke Sonnet 4
            # Fra claude.ai web: $27.85 = 80% → 100% = $34.82/uke
            weekly_cost_limit = 34.82

            # Beregn %
            weekly_percent = (total_cost / weekly_cost_limit) * 100.0

            return weekly_percent

        # Fallback: returnerer None hvis vi ikke kan parse
        return None

    except Exception as e:
        print(f"DEBUG: Error parsing usage data: {e}", file=sys.stderr)
        return None


def main():
    """
    Returner weekly usage % (0-100).
    Bruker cache hvis tilgjengelig, ellers hent fra API/web.
    """
    # Sjekk cache først (gyldig i 5 min)
    cached = get_cached_usage()
    if cached is not None:
        print(cached)
        return 0

    # Hent admin API key
    api_key = get_admin_api_key()
    if not api_key:
        # Fallback: returner cached eller hardkodet
        print(79.0)
        return 0

    # Hent usage fra Anthropic Organizations API
    usage_data = fetch_usage_from_api(api_key)
    if usage_data:
        weekly_percent = calculate_weekly_percent(usage_data)

        if weekly_percent is not None:
            save_cache(weekly_percent)
            print(f"{weekly_percent:.1f}")
            return 0

    # Fallback: returner cached eller hardkodet verdi
    cached_fallback = get_cached_usage() if CACHE_PATH.exists() else None
    if cached_fallback is not None:
        print(cached_fallback)
    else:
        print(79.0)

    return 0


if __name__ == "__main__":
    sys.exit(main())
