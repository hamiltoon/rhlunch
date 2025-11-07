"""Tests for ISSMenuScraper."""

import json
import base64
from datetime import date
from unittest.mock import patch, MagicMock
import pytest
import responses
from lunchscraper.iss_scraper import ISSMenuScraper


class TestISSMenuScraper:
    """Tests for ISSMenuScraper class."""

    @pytest.fixture
    def scraper(self):
        """Create a scraper instance for testing."""
        return ISSMenuScraper(
            restaurant_url="https://www.iss-menyer.se/restaurang-gourmedia",
            restaurant_id="Restaurang Gourmedia",
            restaurant_name="Gourmedia"
        )


    def test_init(self, scraper):
        """Test scraper initialization."""
        assert scraper.restaurant_name == "Gourmedia"
        assert scraper.restaurant_url == "https://www.iss-menyer.se/restaurang-gourmedia"
        assert scraper.restaurant_id == "Restaurang Gourmedia"
        assert scraper.session is not None
        assert scraper._session_established is False

    def test_get_week_number(self, scraper):
        """Test week number calculation."""
        # Week 1 of 2025
        test_date = date(2025, 1, 6)
        assert scraper._get_week_number(test_date) == 2

        # Week 52 of 2024
        test_date = date(2024, 12, 30)
        assert scraper._get_week_number(test_date) == 1

    def test_build_api_query(self, scraper):
        """Test API query building."""
        query = scraper._build_api_query(week_number=45)

        # Decode the base64 query
        decoded = base64.urlsafe_b64decode(query).decode('utf-8')
        query_data = json.loads(decoded)

        assert query_data['dataCollectionId'] == 'Meny'
        assert query_data['query']['filter']['weekNumber'] == 45
        assert query_data['query']['filter']['restrauntId'] == 'Restaurang Gourmedia'
        assert query_data['appId'] == '16d45e35-d3d8-4d5e-b24d-2a680b7e5089'

    def test_parse_day_menu_from_text(self, scraper):
        """Test parsing menu text for a single day."""
        menu_text = "Kött:\nBiff med bearnaisesås\nVegetariskt:\nFalafel med hummus"
        result = scraper._parse_day_menu_from_text(menu_text)

        assert 'vegetarian' in result
        assert 'meat' in result
        assert 'fish' in result
        assert 'Falafel med hummus' in result['vegetarian']
        assert 'Biff med bearnaisesås' in result['meat']

    def test_parse_day_menu_from_text_with_tabs(self, scraper):
        """Test parsing menu text with tab separators."""
        menu_text = "Kött:\tBiff med lök\tserveras med potatis"
        result = scraper._parse_day_menu_from_text(menu_text)

        assert len(result['meat']) == 2
        assert 'Biff med lök' in result['meat']
        assert 'serveras med potatis' in result['meat']

    def test_parse_day_menu_from_text_empty(self, scraper):
        """Test parsing empty menu text."""
        result = scraper._parse_day_menu_from_text("")

        assert result == {'vegetarian': [], 'fish': [], 'meat': []}

    def test_parse_api_response(self, scraper, iss_api_response):
        """Test parsing the API response."""
        weekly_menu = scraper._parse_api_response(iss_api_response)

        assert 'måndag' in weekly_menu
        assert 'tisdag' in weekly_menu
        assert 'onsdag' in weekly_menu
        assert 'torsdag' in weekly_menu
        assert 'fredag' in weekly_menu

        # Check Monday's menu
        monday_menu = weekly_menu['måndag']
        assert 'Kycklingfilé med currysås och ris' in monday_menu['meat']
        assert 'Falafel med hummus och sallad' in monday_menu['vegetarian']

        # Check Tuesday's menu
        tuesday_menu = weekly_menu['tisdag']
        assert 'Lax med dillsås och potatis' in tuesday_menu['fish']
        assert 'Biff med bearnaisesås' in tuesday_menu['meat']

    def test_parse_api_response_empty_items(self, scraper):
        """Test parsing API response with no items."""
        api_data = {"dataItems": []}

        with pytest.raises(Exception, match="No menu items found"):
            scraper._parse_api_response(api_data)

    def test_parse_api_response_no_menu_swedish(self, scraper):
        """Test parsing API response without menuSwedish."""
        api_data = {
            "dataItems": [
                {"data": {}}
            ]
        }

        with pytest.raises(Exception, match="No menuSwedish data found"):
            scraper._parse_api_response(api_data)

    @responses.activate
    def test_establish_session(self, scraper, iss_home_html, iss_gourmedia_html):
        """Test session establishment."""
        # Mock home page request
        responses.add(
            responses.GET,
            'https://www.iss-menyer.se/',
            body=iss_home_html,
            status=200
        )

        # Mock restaurant page request
        responses.add(
            responses.GET,
            'https://www.iss-menyer.se/restaurang-gourmedia',
            body=iss_gourmedia_html,
            status=200
        )

        scraper._establish_session()

        assert scraper._session_established is True
        # Real page should contain auth token
        assert scraper._auth_token is not None or scraper._auth_token == ""

    @responses.activate
    def test_establish_session_failure(self, scraper):
        """Test session establishment with network failure."""
        # Mock failed home page request
        responses.add(
            responses.GET,
            'https://www.iss-menyer.se/',
            status=500
        )

        # Should not raise, just log warning
        scraper._establish_session()

        assert scraper._session_established is False

    @responses.activate
    def test_fetch_menu_from_api(self, scraper, iss_api_response, iss_home_html, iss_gourmedia_html):
        """Test fetching menu from API."""
        # Mock session establishment
        responses.add(
            responses.GET,
            'https://www.iss-menyer.se/',
            body=iss_home_html,
            status=200
        )
        responses.add(
            responses.GET,
            'https://www.iss-menyer.se/restaurang-gourmedia',
            body=iss_gourmedia_html,
            status=200
        )

        # Mock API request
        responses.add(
            responses.GET,
            'https://www.iss-menyer.se/_api/cloud-data/v2/items/query',
            json=iss_api_response,
            status=200
        )

        result = scraper._fetch_menu_from_api(week_number=45)

        assert result == iss_api_response

    @responses.activate
    def test_fetch_menu_from_api_failure(self, scraper, iss_home_html, iss_gourmedia_html):
        """Test API fetch failure."""
        # Mock session establishment
        responses.add(
            responses.GET,
            'https://www.iss-menyer.se/',
            body=iss_home_html,
            status=200
        )
        responses.add(
            responses.GET,
            'https://www.iss-menyer.se/restaurang-gourmedia',
            body=iss_gourmedia_html,
            status=200
        )

        # Mock API request failure
        responses.add(
            responses.GET,
            'https://www.iss-menyer.se/_api/cloud-data/v2/items/query',
            status=500
        )

        with pytest.raises(Exception, match="Failed to fetch menu from API"):
            scraper._fetch_menu_from_api(week_number=45)

    @responses.activate
    def test_get_menu_for_day(self, scraper, iss_api_response, iss_home_html, iss_gourmedia_html):
        """Test getting menu for a specific day."""
        # Mock session and API
        responses.add(
            responses.GET,
            'https://www.iss-menyer.se/',
            body=iss_home_html,
            status=200
        )
        responses.add(
            responses.GET,
            'https://www.iss-menyer.se/restaurang-gourmedia',
            body=iss_gourmedia_html,
            status=200
        )
        responses.add(
            responses.GET,
            'https://www.iss-menyer.se/_api/cloud-data/v2/items/query',
            json=iss_api_response,
            status=200
        )

        # Test Monday (weekday 0)
        test_date = date(2025, 1, 6)  # This is a Monday
        menu = scraper.get_menu_for_day(test_date)

        assert 'vegetarian' in menu
        assert 'meat' in menu
        assert 'Falafel med hummus och sallad' in menu['vegetarian']
        assert 'Kycklingfilé med currysås och ris' in menu['meat']

    @responses.activate
    def test_get_weekly_menu(self, scraper, iss_api_response, iss_home_html, iss_gourmedia_html):
        """Test getting the full weekly menu."""
        # Mock session and API
        responses.add(
            responses.GET,
            'https://www.iss-menyer.se/',
            body=iss_home_html,
            status=200
        )
        responses.add(
            responses.GET,
            'https://www.iss-menyer.se/restaurang-gourmedia',
            body=iss_gourmedia_html,
            status=200
        )
        responses.add(
            responses.GET,
            'https://www.iss-menyer.se/_api/cloud-data/v2/items/query',
            json=iss_api_response,
            status=200
        )

        weekly_menu = scraper.get_weekly_menu()

        assert 'måndag' in weekly_menu
        assert 'tisdag' in weekly_menu
        assert 'onsdag' in weekly_menu
        assert 'torsdag' in weekly_menu
        assert 'fredag' in weekly_menu

        # Verify some content
        assert 'Falafel med hummus och sallad' in weekly_menu['måndag']['vegetarian']
        assert 'Lax med dillsås och potatis' in weekly_menu['tisdag']['fish']

    @responses.activate
    def test_get_menu_for_day_not_found(self, scraper, iss_home_html, iss_gourmedia_html):
        """Test getting menu when day is not in the response."""
        # Mock with empty menuSwedish
        empty_response = {
            "dataItems": [
                {
                    "data": {
                        "menuSwedish": [
                            {"menu": ""},
                            {"menu": ""},
                            {"menu": ""},
                            {"menu": ""},
                            {"menu": ""},
                            {"menu": ""},
                            {"menu": ""}
                        ]
                    }
                }
            ]
        }

        responses.add(
            responses.GET,
            'https://www.iss-menyer.se/',
            body=iss_home_html,
            status=200
        )
        responses.add(
            responses.GET,
            'https://www.iss-menyer.se/restaurang-gourmedia',
            body=iss_gourmedia_html,
            status=200
        )
        responses.add(
            responses.GET,
            'https://www.iss-menyer.se/_api/cloud-data/v2/items/query',
            json=empty_response,
            status=200
        )

        test_date = date(2025, 1, 6)  # Monday

        with pytest.raises(Exception, match="Could not parse any menu data"):
            scraper.get_menu_for_day(test_date)
