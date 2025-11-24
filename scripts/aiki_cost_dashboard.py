#!/usr/bin/env python3
"""
AIKI Cost Dashboard - Real-time oversikt over AI-kostnader
Bruker Anthropic Admin API til å vise:
- Daily cost breakdown
- Cache efficiency
- Cost per component (Claude Code, AIKI_v3, etc.)
"""

import urllib.request
import json
from datetime import datetime, timedelta
from pathlib import Path


def get_admin_key():
    """Hent admin API key."""
    api_keys_file = Path.home() / "aiki" / "Api-nøkler" / "Api keys openai anthropic.txt"

    with open(api_keys_file) as f:
        for line in f:
            if line.strip().startswith("Anthropic_admin_key1:"):
                return line.split(":", 1)[1].strip()
    return None


def fetch_daily_costs(api_key, days=7):
    """Hent cost breakdown siste N dager."""
    now = datetime.utcnow()
    start = (now - timedelta(days=days)).replace(hour=0, minute=0, second=0)

    url = f"https://api.anthropic.com/v1/organizations/cost_report?starting_at={start.strftime('%Y-%m-%dT%H:%M:%SZ')}&bucket_width=1d"

    req = urllib.request.Request(
        url,
        headers={
            "anthropic-version": "2023-06-01",
            "x-api-key": api_key,
        }
    )

    with urllib.request.urlopen(req, timeout=10) as response:
        return json.loads(response.read().decode())


def fetch_usage_report(api_key, days=7):
    """Hent detailed token usage siste N dager."""
    now = datetime.utcnow()
    start = (now - timedelta(days=days)).replace(hour=0, minute=0, second=0)

    url = f"https://api.anthropic.com/v1/organizations/usage_report/messages?starting_at={start.strftime('%Y-%m-%dT%H:%M:%SZ')}&ending_at={now.strftime('%Y-%m-%dT%H:%M:%SZ')}&bucket_width=1d"

    req = urllib.request.Request(
        url,
        headers={
            "anthropic-version": "2023-06-01",
            "x-api-key": api_key,
        }
    )

    with urllib.request.urlopen(req, timeout=10) as response:
        return json.loads(response.read().decode())


def calculate_cache_efficiency(usage_data):
    """Beregn cache efficiency %."""
    if "data" not in usage_data:
        return 0.0

    total_cache_read = 0
    total_input = 0

    for bucket in usage_data["data"]:
        for result in bucket.get("results", []):
            total_cache_read += result.get("cache_read_input_tokens", 0)
            total_input += result.get("uncached_input_tokens", 0)

            # cache_creation er et objekt med ephemeral_5m og ephemeral_1h
            cache_creation = result.get("cache_creation", {})
            total_input += cache_creation.get("ephemeral_5m_input_tokens", 0)
            total_input += cache_creation.get("ephemeral_1h_input_tokens", 0)

    if total_input == 0:
        return 0.0

    return (total_cache_read / (total_input + total_cache_read)) * 100.0


def print_dashboard(cost_data, usage_data):
    """Print oversiktlig dashboard."""
    print("\n" + "="*60)
    print("🧠 AIKI COST DASHBOARD")
    print("="*60)

    # Daily costs
    print("\n📅 Daglige kostnader (siste 7 dager):")
    if "data" in cost_data:
        total_week = 0.0
        for day in cost_data["data"]:
            date = day["starting_at"][:10]
            day_cost = sum(float(r["amount"]) for r in day.get("results", []))
            total_week += day_cost

            if day_cost > 0:
                print(f"  {date}: ${day_cost:>6.2f}")

        print(f"\n  {'TOTAL UKE':>10}: ${total_week:>6.2f}")
        print(f"  {'Gjennomsnitt':>10}: ${total_week/7:>6.2f}/dag")

    # Cache efficiency
    cache_eff = calculate_cache_efficiency(usage_data)
    print(f"\n💾 Cache Efficiency: {cache_eff:.1f}%")

    # Token usage
    if "data" in usage_data:
        total_input = 0
        total_cache_creation = 0
        total_output = 0
        total_cache_read = 0

        for bucket in usage_data["data"]:
            for result in bucket.get("results", []):
                total_input += result.get("uncached_input_tokens", 0)
                total_output += result.get("output_tokens", 0)
                total_cache_read += result.get("cache_read_input_tokens", 0)

                # cache_creation er et objekt
                cache_creation = result.get("cache_creation", {})
                total_cache_creation += cache_creation.get("ephemeral_5m_input_tokens", 0)
                total_cache_creation += cache_creation.get("ephemeral_1h_input_tokens", 0)

        print(f"\n📊 Token Usage (siste 7 dager):")
        print(f"  Uncached Input:   {total_input:>10,} tokens")
        print(f"  Cache Creation:   {total_cache_creation:>10,} tokens")
        print(f"  Output:           {total_output:>10,} tokens")
        print(f"  Cache Read:       {total_cache_read:>10,} tokens (gratis!)")
        print(f"  TOTAL:            {total_input + total_cache_creation + total_output + total_cache_read:>10,} tokens")

    print("\n" + "="*60 + "\n")


def main():
    api_key = get_admin_key()
    if not api_key:
        print("❌ Admin API key ikke funnet!")
        return 1

    print("📡 Henter data fra Anthropic Admin API...")

    cost_data = fetch_daily_costs(api_key, days=7)
    usage_data = fetch_usage_report(api_key, days=7)

    print_dashboard(cost_data, usage_data)

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
