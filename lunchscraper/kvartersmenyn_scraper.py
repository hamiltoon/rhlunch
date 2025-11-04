"""Web scraper for Kvartersmenyn restaurant menus."""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, date
from typing import Dict, List, Optional
import re
import logging
from .base_scraper import BaseMenuScraper
from .dish_classifier import DishClassifier

logger = logging.getLogger(__name__)


class KvartersmenynsMenuScraper(BaseMenuScraper):
    """Scraper for Kvartersmenyn restaurant lunch menus."""

    def __init__(self, restaurant_url: str, restaurant_name: str):
        super().__init__(restaurant_name)
        self.restaurant_url = restaurant_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,sv;q=0.8',
        })

    def _fetch_page(self) -> BeautifulSoup:
        """Fetch the restaurant page and return BeautifulSoup object."""
        logger.debug(f"Fetching menu from {self.restaurant_url}")
        try:
            response = self.session.get(self.restaurant_url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            raise Exception(f"Failed to fetch menu page: {e}")

    def _parse_weekly_menu(self, soup: BeautifulSoup) -> Dict[str, Dict[str, List[str]]]:
        """Parse the weekly menu from the page."""
        weekly_menu = {}

        # Find the menu div
        menu_div = soup.find('div', class_='meny')
        if not menu_div:
            logger.warning("Could not find menu div")
            return weekly_menu

        # Remove invisible <i> tags that contain codes
        for i_tag in menu_div.find_all('i'):
            i_tag.decompose()

        # Get the HTML content and split by <b> or <strong> tags (day headers)
        day_names = ['måndag', 'tisdag', 'onsdag', 'torsdag', 'fredag', 'lördag', 'söndag']

        # Find all <b> and <strong> tags which contain day names
        current_day = None
        current_dishes = []

        for element in menu_div.children:
            if element.name in ['b', 'strong']:
                # Save previous day if we have one
                if current_day and current_dishes:
                    menu_items = self._parse_dishes(current_dishes)
                    if menu_items['vegetarian'] or menu_items['meat']:
                        weekly_menu[current_day] = menu_items
                        logger.debug(f"Parsed {current_day}: {len(menu_items['vegetarian'])} veg, {len(menu_items['meat'])} meat")

                # Start new day
                day_text = element.get_text().strip().lower()
                if day_text in day_names:
                    current_day = day_text
                    current_dishes = []
            elif element.name == 'br':
                continue
            elif isinstance(element, str):
                text = element.strip()
                if text and current_day:
                    current_dishes.append(text)

        # Don't forget the last day
        if current_day and current_dishes:
            menu_items = self._parse_dishes(current_dishes)
            if menu_items['vegetarian'] or menu_items['meat']:
                weekly_menu[current_day] = menu_items
                logger.debug(f"Parsed {current_day}: {len(menu_items['vegetarian'])} veg, {len(menu_items['meat'])} meat")

        return weekly_menu

    def _parse_dishes(self, dishes: List[str]) -> Dict[str, List[str]]:
        """Parse a list of dish strings."""
        if not dishes:
            return {'vegetarian': [], 'meat': []}

        # Combine dishes that belong together
        combined_dishes = []
        current_dish = []

        for line in dishes:
            line = line.strip()

            # Skip very short lines
            if len(line) < 2:
                continue

            # Check if this starts a new dish (has climate rating letter at start)
            if re.match(r'^[A-E]\.?\s+', line):
                # Save previous dish
                if current_dish:
                    combined_dishes.append(' '.join(current_dish))
                # Start new dish
                current_dish = [line]
            else:
                # Continue current dish
                if current_dish:
                    current_dish.append(line)
                else:
                    # Standalone line
                    combined_dishes.append(line)

        # Don't forget the last dish
        if current_dish:
            combined_dishes.append(' '.join(current_dish))

        # Clean up combined dishes
        cleaned_dishes = []
        for dish in combined_dishes:
            # Skip metadata lines
            if any(skip in dish for skip in ['Klimato', 'CO2e-data', 'PRIS:', 'Öppet:', 'Veckans', 'VEGO HELA VECKAN']):
                continue

            # Remove allergen/dietary codes
            dish = re.sub(r'_[a-z]+_', '', dish)

            # Remove climate rating at start
            dish = re.sub(r'^[A-E]\.?\s+', '', dish)

            # Remove multiple spaces
            dish = re.sub(r'\s+', ' ', dish).strip()

            if dish and len(dish) >= 5:
                cleaned_dishes.append(dish)

        # Use classifier to categorize dishes
        categorized = DishClassifier.classify_dishes(cleaned_dishes)

        # Merge fish and meat for backward compatibility
        return DishClassifier.merge_categories_for_display(categorized)

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

        try:
            soup = self._fetch_page()
            weekly_menu = self._parse_weekly_menu(soup)
        except Exception as e:
            raise Exception(f"Failed to fetch menu: {e}")

        # Get the day of week (0=Monday, 6=Sunday)
        day_of_week = target_date.weekday()
        day_names = ['måndag', 'tisdag', 'onsdag', 'torsdag', 'fredag', 'lördag', 'söndag']

        if day_of_week >= len(day_names):
            logger.warning(f"Invalid day of week: {day_of_week}")
            return {'vegetarian': [], 'meat': []}

        day_name = day_names[day_of_week]
        logger.debug(f"Looking for menu for day: {day_name}")

        if day_name not in weekly_menu:
            raise Exception(f"No menu found for {day_name}")

        return weekly_menu[day_name]

    def get_weekly_menu(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Get the menu for the whole week.

        Returns:
            Dictionary with days as keys and menu items for each day.
        """
        logger.debug(f"Fetching weekly menu for {self.restaurant_name}")

        try:
            soup = self._fetch_page()
            weekly_menu = self._parse_weekly_menu(soup)
        except Exception as e:
            raise Exception(f"Failed to fetch menu: {e}")

        return weekly_menu
