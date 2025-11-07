#!/usr/bin/env python3
"""Script to fetch real HTML data for testing.

This script fetches live HTML snapshots from restaurant websites and saves them
with the current date. This allows for maintaining multiple snapshots over time
for regression testing.

Usage:
    python tests/fixtures/fetch_test_data.py [--date YYYY-MM-DD]

If no date is provided, uses today's date.
"""

import requests
import json
from pathlib import Path
from datetime import date
import sys

# Get the fixtures directory
fixtures_dir = Path(__file__).parent

# Determine date for fixtures
if len(sys.argv) > 2 and sys.argv[1] == '--date':
    # Parse date from command line
    date_parts = sys.argv[2].split('-')
    fetch_date = date(int(date_parts[0]), int(date_parts[1]), int(date_parts[2]))
else:
    # Use today's date
    fetch_date = date.today()

date_str = fetch_date.strftime("%Y_%m_%d")
date_dir = fixtures_dir / date_str

print(f"Fetching test data for date: {fetch_date.strftime('%Y-%m-%d')} ({date_str})")
print(f"Saving to: {date_dir}\n")

# Create date directory if it doesn't exist
date_dir.mkdir(exist_ok=True)

# Configure session with proper headers
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9,sv;q=0.8',
})

print("Fetching test data from restaurant websites...\n")

# Fetch ISS Menyer home page
try:
    print("1. Fetching ISS Menyer home page...")
    response = session.get('https://www.iss-menyer.se/', timeout=10)
    response.raise_for_status()
    filename = 'iss_home.html'
    with open(date_dir / filename, 'w', encoding='utf-8') as f:
        f.write(response.text)
    print(f"   Saved {filename} ({len(response.text)} bytes)")
except Exception as e:
    print(f"   ERROR: {e}")

# Fetch ISS Menyer Gourmedia page
try:
    print("2. Fetching ISS Menyer Gourmedia restaurant page...")
    response = session.get('https://www.iss-menyer.se/restaurants/restaurang-gourmedia', timeout=10)
    response.raise_for_status()
    filename = 'iss_gourmedia.html'
    with open(date_dir / filename, 'w', encoding='utf-8') as f:
        f.write(response.text)
    print(f"   Saved {filename} ({len(response.text)} bytes)")
except Exception as e:
    print(f"   ERROR: {e}")

# Fetch Kvartersmenyn Filmhuset page
try:
    print("3. Fetching Kvartersmenyn Filmhuset page...")
    response = session.get('https://filmhuset.kvartersmenyn.se/', timeout=10)
    response.raise_for_status()
    filename = 'kvartersmenyn_filmhuset.html'
    with open(date_dir / filename, 'w', encoding='utf-8') as f:
        f.write(response.text)
    print(f"   Saved {filename} ({len(response.text)} bytes)")
except Exception as e:
    print(f"   ERROR: {e}")

# Fetch Kvartersmenyn Karavan page
try:
    print("4. Fetching Kvartersmenyn Karavan page...")
    response = session.get('https://karavan.kvartersmenyn.se/', timeout=10)
    response.raise_for_status()
    filename = 'kvartersmenyn_karavan.html'
    with open(date_dir / filename, 'w', encoding='utf-8') as f:
        f.write(response.text)
    print(f"   Saved {filename} ({len(response.text)} bytes)")
except Exception as e:
    print(f"   ERROR: {e}")

# Note: API responses should be created manually for specific test weeks
# since we can't easily fetch this without proper authentication
print("\n5. Note: ISS API response fixtures should be created manually")
print(f"   To add API data for this date, create: {date_dir}/iss_api_response.json")
print(f"   See README.md for the expected format")

print(f"\n✓ Done! Test fixtures have been saved to: {date_dir}")
