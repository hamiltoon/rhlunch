"""Base scraper interface for restaurant menu scrapers."""

from abc import ABC, abstractmethod
from datetime import date
from typing import Dict, List, Optional


class BaseMenuScraper(ABC):
    """Abstract base class for restaurant menu scrapers."""

    def __init__(self, restaurant_name: str):
        self.restaurant_name = restaurant_name

    @abstractmethod
    def get_menu_for_day(self, target_date: Optional[date] = None) -> Dict[str, List[str]]:
        """
        Get the menu for a specific day.

        Args:
            target_date: The date to get menu for. If None, uses today.

        Returns:
            Dictionary with 'vegetarian', 'fish', and 'meat' menu items for the day.
        """
        pass

    @abstractmethod
    def get_weekly_menu(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Get the menu for the whole week.

        Returns:
            Dictionary with days as keys (Swedish day names in lowercase)
            and menu items for each day. Each day contains 'vegetarian', 'fish', and 'meat' lists.
        """
        pass
