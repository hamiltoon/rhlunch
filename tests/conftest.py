"""Pytest configuration and shared fixtures.

All fixtures are organized by date folders to allow for multiple test snapshots over time.
This helps with regression testing and debugging issues with specific data.

Structure:
    tests/fixtures/
    ├── 2025_11_07/           # Current snapshots
    │   ├── iss_home.html
    │   ├── iss_gourmedia.html
    │   ├── kvartersmenyn_filmhuset.html
    │   └── kvartersmenyn_karavan.html
    └── 2025_01_06/           # Sample API data
        └── iss_api_response.json

Default date: 2025-11-07 (current snapshots)
"""

import json
from pathlib import Path
from datetime import date
import pytest


# Get the fixtures directory path
FIXTURES_DIR = Path(__file__).parent / "fixtures"

# Default date for fixtures (update this when adding new default fixtures)
DEFAULT_FIXTURE_DATE = date(2025, 11, 7)


def get_available_fixture_dates() -> list[date]:
    """
    Discover all available fixture dates by scanning the fixtures directory.

    Returns:
        List of date objects for all available fixture directories, sorted chronologically.

    Example:
        dates = get_available_fixture_dates()
        # Returns: [date(2025, 1, 6), date(2025, 11, 7)]
    """
    dates = []
    for date_dir in FIXTURES_DIR.iterdir():
        if date_dir.is_dir() and date_dir.name.count('_') == 2:
            try:
                # Parse date from directory name format: YYYY_MM_DD
                year, month, day = date_dir.name.split('_')
                dates.append(date(int(year), int(month), int(day)))
            except (ValueError, TypeError):
                # Skip directories that don't match the expected format
                continue
    return sorted(dates)


def get_fixture_dates_with_file(filename: str) -> list[date]:
    """
    Find all fixture dates that have a specific file.

    Args:
        filename: The fixture filename to look for (e.g., "kvartersmenyn_filmhuset.html")

    Returns:
        List of date objects for fixture directories containing the file.

    Example:
        dates = get_fixture_dates_with_file("kvartersmenyn_filmhuset.html")
        # Returns only dates that have this file
    """
    dates = []
    for test_date in get_available_fixture_dates():
        date_str = test_date.strftime("%Y_%m_%d")
        date_dir = FIXTURES_DIR / date_str
        fixture_file = date_dir / filename
        if fixture_file.exists():
            dates.append(test_date)
    return dates


# ============================================================================
# Helper Functions
# ============================================================================

def load_fixture_file(filename: str, test_date: date = None) -> str:
    """
    Load a fixture file for a specific date from the date-organized folder structure.

    Args:
        filename: The fixture filename (e.g., "iss_home.html")
        test_date: The date for which to load the fixture (defaults to DEFAULT_FIXTURE_DATE)

    Returns:
        File contents as string

    Raises:
        FileNotFoundError: If the fixture file doesn't exist

    Example:
        html = load_fixture_file("iss_home.html", date(2025, 11, 7))
        # Loads from: tests/fixtures/2025_11_07/iss_home.html
    """
    if test_date is None:
        test_date = DEFAULT_FIXTURE_DATE

    date_str = test_date.strftime("%Y_%m_%d")
    date_dir = FIXTURES_DIR / date_str
    fixture_file = date_dir / filename

    if not fixture_file.exists():
        raise FileNotFoundError(
            f"Fixture not found: {fixture_file}\n"
            f"To add this test case:\n"
            f"1. Run: python tests/fixtures/fetch_test_data.py --date {test_date.strftime('%Y-%m-%d')}\n"
            f"2. Or manually create: {date_dir}/{filename}"
        )

    with open(fixture_file, "r", encoding="utf-8") as f:
        return f.read()


def load_json_fixture(filename: str, test_date: date = None) -> dict:
    """
    Load a JSON fixture file for a specific date.

    Args:
        filename: The fixture filename (e.g., "iss_api_response.json")
        test_date: The date for which to load the fixture

    Returns:
        Parsed JSON as dict

    Example:
        data = load_json_fixture("iss_api_response.json", date(2025, 1, 6))
        # Loads from: tests/fixtures/2025_01_06/iss_api_response.json
    """
    content = load_fixture_file(filename, test_date)
    return json.loads(content)


# ============================================================================
# ISS Menyer Fixtures
# ============================================================================

@pytest.fixture
def iss_home_html():
    """
    Load ISS home page HTML snapshot.

    Default date: 2025-11-07
    To use a different date: load_fixture_file("iss_home.html", your_date)
    """
    return load_fixture_file("iss_home.html")


@pytest.fixture
def iss_gourmedia_html():
    """
    Load ISS Gourmedia restaurant page HTML snapshot.

    Default date: 2025-11-07
    To use a different date: load_fixture_file("iss_gourmedia.html", your_date)
    """
    return load_fixture_file("iss_gourmedia.html")


@pytest.fixture
def iss_api_response():
    """
    Load ISS API response for week containing 2025-01-06.

    This is sample data for testing. To use real data from a different week,
    use load_json_fixture("iss_api_response.json", your_date)
    """
    return load_json_fixture("iss_api_response.json", date(2025, 1, 6))


# ============================================================================
# Kvartersmenyn Fixtures
# ============================================================================

@pytest.fixture
def kvartersmenyn_filmhuset_html():
    """
    Load Kvartersmenyn Filmhuset page HTML snapshot.

    Default date: 2025-11-07
    To use a different date: load_fixture_file("kvartersmenyn_filmhuset.html", your_date)
    """
    return load_fixture_file("kvartersmenyn_filmhuset.html")


@pytest.fixture
def kvartersmenyn_karavan_html():
    """
    Load Kvartersmenyn Karavan page HTML snapshot.

    Default date: 2025-11-07
    To use a different date: load_fixture_file("kvartersmenyn_karavan.html", your_date)
    """
    return load_fixture_file("kvartersmenyn_karavan.html")
