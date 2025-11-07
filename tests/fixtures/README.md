# Test Fixtures

This directory contains test fixtures for the rhlunch test suite.

**All fixtures are organized in date folders** to allow for multiple test snapshots over time, making it easy to maintain regression tests and debug issues with specific data.

## Structure

```
fixtures/
├── README.md                     # This file
├── fetch_test_data.py            # Script to fetch live HTML snapshots
│
├── 2025_11_07/                   # Current snapshots (Nov 7, 2025)
│   ├── iss_home.html
│   ├── iss_gourmedia.html
│   ├── kvartersmenyn_filmhuset.html
│   └── kvartersmenyn_karavan.html
│
└── 2025_01_06/                   # Sample API data (Jan 6, 2025)
    └── iss_api_response.json
```

**Date format**: `YYYY_MM_DD` (e.g., `2025_11_07`)

**Current default date**: `2025_11_07` (configured in `conftest.py`)

## Adding New Test Data

### Quick Start: Fetch Fresh Snapshots

To fetch HTML snapshots for today:

```bash
python tests/fixtures/fetch_test_data.py
```

This creates a new date folder (e.g., `2025_12_15/`) with:
- `iss_home.html`
- `iss_gourmedia.html`
- `kvartersmenyn_filmhuset.html`
- `kvartersmenyn_karavan.html`

To fetch snapshots for a specific date:

```bash
python tests/fixtures/fetch_test_data.py --date 2025-12-15
```

### Adding ISS API Response Data

API responses must be created manually since they require authentication.

1. **Create the date folder** (if it doesn't exist):
   ```bash
   mkdir tests/fixtures/2025_01_20
   ```

2. **Create the fixture file**:
   ```bash
   tests/fixtures/2025_01_20/iss_api_response.json
   ```

3. **Add the menu data** for that week:
   ```json
   {
     "dataItems": [
       {
         "data": {
           "menuSwedish": [
             {"menu": "Kött:\nBiff med lök\nVegetariskt:\nFalafel"},
             {"menu": "Fisk:\nLax med dill"},
             {"menu": "Vegetariskt:\nHalloumi"},
             {"menu": "Kött:\nKyckling"},
             {"menu": "Fisk:\nTorsk\nVegetariskt:\nVegoburgare"},
             {"menu": ""},
             {"menu": ""}
           ]
         }
       }
     ]
   }
   ```

## Using Fixtures in Tests

### Using Default Fixtures (Easiest)

The pytest fixtures automatically load from the default date:

```python
def test_something(iss_home_html, iss_api_response):
    # Uses default date (2025_11_07)
    assert len(iss_home_html) > 0
    assert "dataItems" in iss_api_response
```

### Using Specific Dates

For tests requiring specific dates:

```python
from datetime import date
from tests.conftest import load_fixture_file, load_json_fixture

def test_specific_date():
    # Load HTML for a specific date
    html = load_fixture_file("iss_home.html", date(2025, 12, 15))
    # Loads from: tests/fixtures/2025_12_15/iss_home.html

    # Load JSON for a specific date
    api_data = load_json_fixture("iss_api_response.json", date(2025, 1, 6))
    # Loads from: tests/fixtures/2025_01_06/iss_api_response.json
```

### Available Fixtures

**Default fixtures** (use directly in test functions):
- `iss_home_html` - ISS home page HTML
- `iss_gourmedia_html` - Gourmedia restaurant page HTML
- `iss_api_response` - ISS API response (sample data for 2025-01-06)
- `kvartersmenyn_filmhuset_html` - Filmhuset menu page HTML
- `kvartersmenyn_karavan_html` - Karavan menu page HTML

**Helper functions** (for custom dates):
- `load_fixture_file(filename, test_date)` - Load any HTML/text fixture
- `load_json_fixture(filename, test_date)` - Load and parse JSON fixture

## Fixture Guidelines

### ISS API Response Format

The ISS API returns menu data in this structure:

```json
{
  "dataItems": [
    {
      "data": {
        "menuSwedish": [
          {"menu": "Category:\nDish 1\nDish 2"},
          // ... 7 days total (Mon-Sun)
        ]
      }
    }
  ]
}
```

**Menu text format:**
- Each day's menu can contain category markers: `"Kött:"`, `"Fisk:"`, `"Vegetariskt:"`
- Dishes are separated by newlines (`\n`)
- Empty strings `""` for days without menus (typically weekends)

**Example:**
```json
{
  "menu": "Kött:\nBiff med bearnaisesås\nVegetariskt:\nFalafel med hummus"
}
```

## When to Add New Fixtures

Add new fixtures when:
- **Testing edge cases** (e.g., empty menus, special characters, unusual formatting)
- **Testing specific date scenarios** (e.g., holidays, weekends, week boundaries)
- **Debugging production issues** - Capture the exact data that caused a problem
- **Regression testing** - Preserve known-good data to prevent regressions
- **Testing parsing changes** - Keep old data to ensure backward compatibility

## Maintaining Fixtures

### Updating the Default Date

When adding new default fixtures, update the `DEFAULT_FIXTURE_DATE` in `conftest.py`:

```python
# Default date for fixtures (update this when adding new default fixtures)
DEFAULT_FIXTURE_DATE = date(2025, 11, 7)  # Update this!
```

### Cleaning Up Old Fixtures

Old fixtures can be removed if they're no longer useful, but consider keeping them for:
- Regression tests
- Historical reference
- Known edge cases

## Test Data Quality

- Use **real menu data** from actual restaurant websites when possible
- Include **Swedish characters** (å, ä, ö) to test encoding
- Test **various dish categories** (meat, fish, vegetarian)
- Include **edge cases** (empty menus, missing categories, unusual formatting)
- Capture **problem data** that caused bugs for regression testing
