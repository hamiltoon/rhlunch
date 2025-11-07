"""Tests for KvartersmenynsMenuScraper."""

from datetime import date
from unittest.mock import patch, MagicMock
import pytest
import responses
from bs4 import BeautifulSoup
from lunchscraper.kvartersmenyn_scraper import KvartersmenynsMenuScraper


class TestKvartersmenynsMenuScraper:
    """Tests for KvartersmenynsMenuScraper class."""

    @pytest.fixture
    def scraper(self):
        """Create a scraper instance for testing."""
        return KvartersmenynsMenuScraper(
            restaurant_url="https://kvartersmenyn.se/filmhuset",
            restaurant_name="Filmhuset"
        )

    @pytest.fixture
    def sample_html(self):
        """Sample HTML from Kvartersmenyn page."""
        return """
        <html>
        <body>
        <div class="meny">
            <h2>Måndag</h2>
            A Kycklingfilé med currysås
            serveras med ris
            <h2>Tisdag</h2>
            B Lax med citron och dill
            C Falafel med hummus
            <h2>Onsdag</h2>
            D Biff med bearnaisesås
            <h2>Torsdag</h2>
            E Halloumi med rostade grönsaker
            <h2>Fredag</h2>
            A Fiskgratäng med ost
            B Vegoburgare med pommes
            <h3>Veckans salladsbowl</h3>
            <p>Klimato information</p>
        </div>
        </body>
        </html>
        """

    @pytest.fixture
    def sample_html_with_allergen_codes(self):
        """Sample HTML with allergen codes."""
        return """
        <html>
        <body>
        <div class="meny">
            <h2>Måndag</h2>
            A Kycklingfilé med currysås _gluten_ _laktos_
            <h2>Tisdag</h2>
            B Halloumi med sallad _laktos_
        </div>
        </body>
        </html>
        """

    @pytest.fixture
    def sample_html_with_category_markers(self):
        """Sample HTML with category markers."""
        return """
        <html>
        <body>
        <div class="meny">
            <h2>Måndag</h2>
            Kött:
            Biff med lök
            Vegetariskt:
            Falafel med hummus
            <h2>Tisdag</h2>
            Fisk:
            Lax med dillsås
        </div>
        </body>
        </html>
        """

    def test_init(self, scraper):
        """Test scraper initialization."""
        assert scraper.restaurant_name == "Filmhuset"
        assert scraper.restaurant_url == "https://kvartersmenyn.se/filmhuset"
        assert scraper.session is not None

    @responses.activate
    def test_fetch_page_success(self, scraper, sample_html):
        """Test successful page fetch."""
        responses.add(
            responses.GET,
            'https://kvartersmenyn.se/filmhuset',
            body=sample_html,
            status=200
        )

        soup = scraper._fetch_page()
        assert isinstance(soup, BeautifulSoup)
        assert soup.find('div', class_='meny') is not None

    @responses.activate
    def test_fetch_page_failure(self, scraper):
        """Test page fetch failure."""
        responses.add(
            responses.GET,
            'https://kvartersmenyn.se/filmhuset',
            status=500
        )

        with pytest.raises(Exception, match="Failed to fetch menu page"):
            scraper._fetch_page()

    def test_parse_dishes_with_climate_ratings(self, scraper):
        """Test parsing dishes with climate ratings."""
        dishes = [
            "A Kycklingfilé med currysås",
            "B Lax med dillsås",
            "C Falafel med hummus"
        ]

        result = scraper._parse_dishes(dishes)

        assert 'Kycklingfilé med currysås' in result['meat']
        assert 'Lax med dillsås' in result['fish']
        assert 'Falafel med hummus' in result['vegetarian']

    def test_parse_dishes_with_allergen_codes(self, scraper):
        """Test parsing dishes with allergen codes."""
        dishes = [
            "A Kycklingfilé med currysås _gluten_ _laktos_",
            "B Halloumi med sallad _laktos_"
        ]

        result = scraper._parse_dishes(dishes)

        # Allergen codes should be removed
        assert 'Kycklingfilé med currysås' in result['meat']
        assert 'Halloumi med sallad' in result['vegetarian']

        # Check that allergen codes are not in the result
        for category_dishes in result.values():
            for dish in category_dishes:
                assert '_gluten_' not in dish
                assert '_laktos_' not in dish

    def test_parse_dishes_multiline(self, scraper):
        """Test parsing dishes that span multiple lines."""
        dishes = [
            "A Kycklingfilé med currysås",
            "serveras med ris"
        ]

        result = scraper._parse_dishes(dishes)

        # Should combine into one dish
        combined = ' '.join(result['meat'])
        assert 'Kycklingfilé med currysås' in combined
        assert 'serveras med ris' in combined

    def test_parse_dishes_empty_list(self, scraper):
        """Test parsing empty dish list."""
        result = scraper._parse_dishes([])
        assert result == {'vegetarian': [], 'fish': [], 'meat': []}

    def test_parse_dishes_with_standalone_metadata(self, scraper):
        """Test that standalone metadata lines (with climate rating prefix) are filtered."""
        dishes = [
            "A Kycklingfilé med currysås",
            "B Klimato rating info",  # Has B prefix so treated as new dish, then filtered
        ]

        result = scraper._parse_dishes(dishes)

        # First dish should be parsed, second filtered as metadata
        assert 'Kycklingfilé med currysås' in result['meat']
        # Klimato line should be filtered out
        assert len(result['meat']) == 1

    def test_parse_weekly_menu(self, scraper, sample_html):
        """Test parsing weekly menu from HTML."""
        soup = BeautifulSoup(sample_html, 'html.parser')
        weekly_menu = scraper._parse_weekly_menu(soup)

        assert 'måndag' in weekly_menu
        assert 'tisdag' in weekly_menu
        assert 'onsdag' in weekly_menu
        assert 'torsdag' in weekly_menu
        assert 'fredag' in weekly_menu

        # Check specific dishes (combined from multiline)
        assert any('Kycklingfilé med currysås' in dish for dish in weekly_menu['måndag']['meat'])
        assert 'Lax med citron och dill' in weekly_menu['tisdag']['fish']
        assert 'Falafel med hummus' in weekly_menu['tisdag']['vegetarian']

    def test_parse_weekly_menu_with_category_markers(self, scraper, sample_html_with_category_markers):
        """Test parsing menu with category markers."""
        soup = BeautifulSoup(sample_html_with_category_markers, 'html.parser')
        weekly_menu = scraper._parse_weekly_menu(soup)

        assert 'måndag' in weekly_menu
        assert 'Biff med lök' in weekly_menu['måndag']['meat']
        assert 'Falafel med hummus' in weekly_menu['måndag']['vegetarian']
        assert 'Lax med dillsås' in weekly_menu['tisdag']['fish']

    def test_parse_weekly_menu_no_menu_div(self, scraper):
        """Test parsing when menu div is not found."""
        html = "<html><body><div>No menu here</div></body></html>"
        soup = BeautifulSoup(html, 'html.parser')

        weekly_menu = scraper._parse_weekly_menu(soup)

        assert weekly_menu == {}

    def test_parse_weekly_menu_stops_at_veckans_header(self, scraper):
        """Test that parsing stops at 'Veckans' header."""
        html = """
        <html>
        <body>
        <div class="meny">
            <h2>Måndag</h2>
            A Kyckling med ris
            <h2>Veckans salladsbowl</h2>
            <p>This should not be parsed</p>
        </div>
        </body>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        weekly_menu = scraper._parse_weekly_menu(soup)

        # Should have Monday but stop at "Veckans"
        assert 'måndag' in weekly_menu
        assert len(weekly_menu) == 1

    def test_parse_weekly_menu_removes_i_tags(self, scraper):
        """Test that invisible <i> tags are removed."""
        html = """
        <html>
        <body>
        <div class="meny">
            <h2>Måndag</h2>
            A Kyckling med ris <i>(invisible allergen code)</i>
        </div>
        </body>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        weekly_menu = scraper._parse_weekly_menu(soup)

        # <i> tag content should not appear
        for day_menu in weekly_menu.values():
            for category_dishes in day_menu.values():
                for dish in category_dishes:
                    assert '(invisible allergen code)' not in dish

    @responses.activate
    def test_get_menu_for_day(self, scraper, sample_html):
        """Test getting menu for a specific day."""
        responses.add(
            responses.GET,
            'https://kvartersmenyn.se/filmhuset',
            body=sample_html,
            status=200
        )

        # Test Monday (weekday 0)
        test_date = date(2025, 1, 6)  # This is a Monday
        menu = scraper.get_menu_for_day(test_date)

        assert 'vegetarian' in menu
        assert 'meat' in menu
        # Dish may be combined from multiple lines
        assert any('Kycklingfilé med currysås' in dish for dish in menu['meat'])

    @responses.activate
    def test_get_menu_for_day_tuesday(self, scraper, sample_html):
        """Test getting menu for Tuesday."""
        responses.add(
            responses.GET,
            'https://kvartersmenyn.se/filmhuset',
            body=sample_html,
            status=200
        )

        # Test Tuesday (weekday 1)
        test_date = date(2025, 1, 7)  # This is a Tuesday
        menu = scraper.get_menu_for_day(test_date)

        assert 'Lax med citron och dill' in menu['fish']
        assert 'Falafel med hummus' in menu['vegetarian']

    @responses.activate
    def test_get_menu_for_day_not_found(self, scraper):
        """Test getting menu when day is not available."""
        html = """
        <html>
        <body>
        <div class="meny">
            <h2>Måndag</h2>
            A Kyckling med ris
        </div>
        </body>
        </html>
        """

        responses.add(
            responses.GET,
            'https://kvartersmenyn.se/filmhuset',
            body=html,
            status=200
        )

        # Test Tuesday (not in menu)
        test_date = date(2025, 1, 7)  # Tuesday

        with pytest.raises(Exception, match="No menu found for tisdag"):
            scraper.get_menu_for_day(test_date)

    @responses.activate
    def test_get_weekly_menu(self, scraper, sample_html):
        """Test getting the full weekly menu."""
        responses.add(
            responses.GET,
            'https://kvartersmenyn.se/filmhuset',
            body=sample_html,
            status=200
        )

        weekly_menu = scraper.get_weekly_menu()

        assert 'måndag' in weekly_menu
        assert 'tisdag' in weekly_menu
        assert 'onsdag' in weekly_menu
        assert 'torsdag' in weekly_menu
        assert 'fredag' in weekly_menu

        # Verify some content (dishes may be combined from multiple lines)
        assert any('Kycklingfilé med currysås' in dish for dish in weekly_menu['måndag']['meat'])
        assert 'Lax med citron och dill' in weekly_menu['tisdag']['fish']
        assert 'Halloumi med rostade grönsaker' in weekly_menu['torsdag']['vegetarian']

    @responses.activate
    def test_get_weekly_menu_failure(self, scraper):
        """Test weekly menu fetch failure."""
        responses.add(
            responses.GET,
            'https://kvartersmenyn.se/filmhuset',
            status=500
        )

        with pytest.raises(Exception, match="Failed to fetch menu"):
            scraper.get_weekly_menu()
