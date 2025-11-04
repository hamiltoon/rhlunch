"""Web scraper for ISS restaurant menus."""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, date
from typing import Dict, List, Optional
import logging
import base64
import json
from .base_scraper import BaseMenuScraper
from .dish_classifier import DishClassifier

logger = logging.getLogger(__name__)


class ISSMenuScraper(BaseMenuScraper):
    """Scraper for ISS restaurant lunch menus."""
    
    def __init__(self, restaurant_url: str, restaurant_id: str = "Restaurang Gourmedia", restaurant_name: str = "Gourmedia"):
        super().__init__(restaurant_name)
        self.restaurant_url = restaurant_url
        self.restaurant_id = restaurant_id
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,sv;q=0.8',
        })
        self.api_base_url = 'https://www.iss-menyer.se/_api/cloud-data/v2/items/query'
        self.app_id = '16d45e35-d3d8-4d5e-b24d-2a680b7e5089'
        self._session_established = False
        self._meta_site_id = '5e5cfbed-93b8-4425-8938-b96c735bd6c1'  # Meta Site ID for iss-menyer.se
        self._auth_token = None
    
    def _establish_session(self):
        """Visit the main page to establish a browser session."""
        if self._session_established:
            return
        
        # First visit the home page to establish session
        logger.debug("Establishing session by visiting home page")
        try:
            home_response = self.session.get('https://www.iss-menyer.se/', timeout=10)
            home_response.raise_for_status()
            logger.debug(f"Home page visited. Status: {home_response.status_code}")
            logger.debug(f"Cookies after home: {self.session.cookies}")
        except Exception as e:
            logger.warning(f"Failed to visit home page: {e}")
        
        # Then visit the restaurant page
        logger.debug(f"Visiting restaurant page: {self.restaurant_url}")
        try:
            response = self.session.get(self.restaurant_url, timeout=10)
            response.raise_for_status()
            logger.debug(f"Session established. Status: {response.status_code}")
            
            # Extract authorization token from HTML using BeautifulSoup
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            viewer_script = soup.find('script', {'id': 'wix-viewer-model'})
            if viewer_script:
                json_content = viewer_script.string
                # Parse the JSON to find the authorization token
                try:
                    import json
                    viewer_data = json.loads(json_content)
                    # The token is in the headers of the dynamic pages configuration
                    for prefix_data in viewer_data.get('siteFeaturesConfigs', {}).get('dynamicPages', {}).get('prefixToRouterFetchData', {}).values():
                        if 'headers' in prefix_data.get('optionsData', {}):
                            headers = prefix_data['optionsData']['headers']
                            if 'Authorization' in headers:
                                self._auth_token = headers['Authorization']
                                logger.debug(f"Found auth token")
                                break
                except Exception as e:
                    logger.warning(f"Could not parse viewer-model JSON: {e}")
            else:
                logger.warning("Could not find wix-viewer-model script tag")
            
            self._session_established = True
        except Exception as e:
            logger.warning(f"Failed to establish session: {e}")
            # Don't raise, we'll try the API anyway
    
    def _get_week_number(self, target_date: date) -> int:
        """Get ISO week number for a given date."""
        return target_date.isocalendar()[1]
    
    def _build_api_query(self, week_number: int) -> str:
        """Build the API query parameter."""
        query_data = {
            "dataCollectionId": "Meny",
            "query": {
                "filter": {
                    "restrauntId": self.restaurant_id,  # Note: misspelled in API
                    "weekNumber": week_number
                },
                "paging": {
                    "offset": 0,
                    "limit": 1
                },
                "fields": []
            },
            "referencedItemOptions": [],
            "returnTotalCount": True,
            "environment": "LIVE",
            "appId": self.app_id
        }
        
        # Encode to base64
        json_str = json.dumps(query_data, separators=(',', ':'))
        encoded = base64.urlsafe_b64encode(json_str.encode('utf-8')).decode('utf-8')
        
        return encoded
    
    def _fetch_menu_from_api(self, week_number: int) -> dict:
        """Fetch menu data from the ISS API."""
        # First establish a session by visiting the main page
        self._establish_session()
        
        # Update headers for API call
        api_headers = {
            'Accept': 'application/json, text/plain, */*',
            'Referer': self.restaurant_url,
            'Origin': 'https://www.iss-menyer.se'
        }
        
        # Add Meta Site ID if we have it
        if self._meta_site_id:
            api_headers['X-Wix-Meta-Site-Id'] = self._meta_site_id
        
        # Add authorization token if we have it
        if self._auth_token:
            api_headers['Authorization'] = self._auth_token
        
        self.session.headers.update(api_headers)
        
        query_param = self._build_api_query(week_number)
        url = f"{self.api_base_url}?.r={query_param}"
        
        logger.debug(f"Fetching menu from API for week {week_number}")
        logger.debug(f"API URL: {url}")
        
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code != 200:
                logger.debug(f"API error response: {response.text}")
            response.raise_for_status()
            data = response.json()
            logger.debug(f"API response received successfully")
            return data
        except Exception as e:
            raise Exception(f"Failed to fetch menu from API: {e}")
    
    def _parse_api_response(self, api_data: dict) -> Dict[str, Dict[str, List[str]]]:
        """Parse the API response into our menu format."""
        weekly_menu = {}
        
        logger.debug(f"Parsing API response")
        
        # The API response contains dataItems array
        items = api_data.get('dataItems', [])
        logger.debug(f"Found {len(items)} items in API response")
        
        if not items:
            raise Exception("No menu items found in API response")
        
        # Get the first item (should be the weekly menu)
        menu_item = items[0]
        menu_data = menu_item.get('data', {})
        
        # Extract menuSwedish array
        menu_swedish = menu_data.get('menuSwedish', [])
        logger.debug(f"Found {len(menu_swedish)} days in menuSwedish")
        
        if not menu_swedish:
            raise Exception("No menuSwedish data found in API response")
        
        # Map Swedish day names to the menu array indices
        day_names = ['måndag', 'tisdag', 'onsdag', 'torsdag', 'fredag', 'lördag', 'söndag']
        
        for idx, day_menu_obj in enumerate(menu_swedish):
            if idx >= len(day_names):
                break
            
            day_name = day_names[idx]
            menu_text = day_menu_obj.get('menu', '').strip()
            
            if not menu_text:
                logger.debug(f"No menu for {day_name}")
                continue
            
            # Parse the menu text
            menu_items = self._parse_day_menu_from_text(menu_text)
            weekly_menu[day_name] = menu_items
            logger.debug(f"Parsed {day_name}: {len(menu_items['vegetarian'])} veg, {len(menu_items['meat'])} meat")
        
        if not weekly_menu:
            raise Exception("Could not parse any menu data from API response")
        
        logger.debug(f"Successfully parsed menu for days: {list(weekly_menu.keys())}")
        return weekly_menu
    
    def _parse_day_menu_from_text(self, menu_text: str) -> Dict[str, List[str]]:
        """Parse menu text for a single day."""
        if not menu_text:
            return {'vegetarian': [], 'fish': [], 'meat': []}

        # Split by newlines and tabs to get all parts
        dishes = []
        lines = menu_text.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Split by tabs
            parts = line.split('\t')

            for part in parts:
                part = part.strip()
                if part:
                    dishes.append(part)

        # Use classifier to categorize dishes
        categorized = DishClassifier.classify_dishes(dishes)

        # Return all three categories
        return categorized
    
    def get_menu_for_day(self, target_date: Optional[date] = None) -> Dict[str, List[str]]:
        """
        Get the menu for a specific day.
        
        Args:
            target_date: The date to get menu for. If None, uses today.
            
        Returns:
            Dictionary with 'vegetarian' and 'meat' menu items for the day.
        """
        if target_date is None:
            target_date = date.today()
        
        logger.debug(f"Fetching menu for date: {target_date} ({target_date.strftime('%A, %B %d, %Y')})")
        
        # Get the week number for the target date
        week_number = self._get_week_number(target_date)
        logger.debug(f"Week number: {week_number}")
        
        try:
            # Fetch menu from API
            api_data = self._fetch_menu_from_api(week_number)
            weekly_menu = self._parse_api_response(api_data)
        except Exception as e:
            raise Exception(f"Failed to fetch menu: {e}")
        
        # Get the day of week (0=Monday, 6=Sunday)
        day_of_week = target_date.weekday()
        day_names = ['måndag', 'tisdag', 'onsdag', 'torsdag', 'fredag', 'lördag', 'söndag']
        
        if day_of_week >= len(day_names):
            logger.warning(f"Invalid day of week: {day_of_week}")
            return {'vegetarian': [], 'meat': []}
        
        day_name = day_names[day_of_week]
        logger.debug(f"Looking for menu for day: {day_name} (day of week: {day_of_week})")
        logger.debug(f"Available days in menu: {list(weekly_menu.keys())}")
        
        if day_name not in weekly_menu:
            raise Exception(f"No menu found for {day_name}. Available days: {', '.join(weekly_menu.keys())}")
        
        menu = weekly_menu[day_name]
        logger.debug(f"Found {len(menu.get('vegetarian', []))} vegetarian items and {len(menu.get('meat', []))} meat items")
        
        if menu.get('vegetarian'):
            logger.debug(f"Vegetarian items: {menu['vegetarian']}")
        if menu.get('meat'):
            logger.debug(f"Meat items: {menu['meat']}")
        
        # Check if menu is empty
        if not menu.get('vegetarian') and not menu.get('meat'):
            logger.warning(f"Found menu entry for {day_name} but it contains no items")
        
        return menu
    
    def get_weekly_menu(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Get the menu for the whole week.
        
        Returns:
            Dictionary with days as keys and menu items for each day.
        """
        # Get the current week number
        today = date.today()
        week_number = self._get_week_number(today)
        logger.debug(f"Fetching weekly menu for week {week_number}")
        
        try:
            # Fetch menu from API
            api_data = self._fetch_menu_from_api(week_number)
            weekly_menu = self._parse_api_response(api_data)
        except Exception as e:
            raise Exception(f"Failed to fetch menu: {e}")
        
        return weekly_menu
