"""Classifier for categorizing restaurant dishes."""

import re
from typing import Dict, List, Tuple


class DishClassifier:
    """Classifier for categorizing dishes into vegetarian, meat, and fish."""

    # Category markers that appear in menus
    CATEGORY_MARKERS = {
        'vegetarian': [
            'vegetariskt:', 'vegetariskt', 'vego:', 'vego', 'vegansk:', 'vegansk',
            'vegan:', 'vegan', 'vegetarisk:', 'vegetarisk', 'grönt:', 'grönt',
            'växtbaserat:', 'växtbaserat', 'veganskt alternativ:', 'veganskt alternativ'
        ],
        'fish': [
            'fisk:', 'fisk', 'fiskrätt:', 'fiskrätt', 'dagens fisk:', 'dagens fisk',
            'skaldjur:', 'skaldjur'
        ],
        'meat': [
            'kött:', 'kött', 'kötträtt:', 'kötträtt', 'dagens kött:', 'dagens kött',
            'fågel:', 'fågel'
        ]
    }

    # Ingredient keywords for classification
    FISH_KEYWORDS = [
        'fisk', 'lax', 'torsk', 'sej', 'räkor', 'scampi', 'hummer', 'skaldjur',
        'tonfisk', 'sill', 'strömming', 'gös', 'abborre', 'sardiner', 'makrill',
        'hälleflundra', 'rödspätta', 'piggvar', 'havskräfta', 'kummel', 'fish'
    ]

    MEAT_KEYWORDS = [
        'kött', 'kyckling', 'fläsk', 'biff', 'oxfilé', 'kalv', 'lamm', 'älg',
        'ren', 'ankbröst', 'fågel', 'entrecote', 'ryggbiff', 'sidfläsk',
        'bacon', 'chorizo', 'korv', 'köttbullar', 'hamburgare', 'schnitzel',
        'frikadeller', 'pulled pork', 'revbensspjäll', 'korvstroganoff',
        'wallenbergare', 'pytt i panna', 'raggmunk med fläsk', 'coq au vin',
        'porchetta', 'färsbiff', 'kycklinglår', 'nötkött', 'fläskkarré'
    ]

    VEGETARIAN_KEYWORDS = [
        'vego', 'vegan', 'vegetarisk', 'halloumi', 'falafel', 'tempeh',
        'tofu', 'vegansk', 'vegetariskt', 'bönor', 'linser', 'quinoa',
        'seitan', 'svampgryta', 'svampsås', 'svampsoppa', 'rotselleri', 'selleri',
        'kikärtor', 'grönsaker', 'vegoburgare', 'vegoköttbullar', 'chili med bönor',
        'böff ala lindström', 'gnocchi', 'zucchini', 'aubergine', 'moussaka på vegofärs',
        'långbakad rotselleri', 'skogssvamp', 'tempura svamp', 'tortellini', 'ricotta',
        'spenat'
    ]

    # Special Swedish dishes that should be classified as meat
    MEAT_DISHES = [
        'ärtsoppa',  # Usually served with pork
        'pannkaka'   # Context-dependent but traditionally with pork soup
    ]

    # Labels/headers to skip (not actual dishes)
    SKIP_LABELS = [
        'extra', 'övrig', 'övrigt', 'dessert', 'tillbehör'
    ]

    @classmethod
    def classify_dish(cls, dish: str, previous_category: str = None) -> str:
        """
        Classify a single dish into vegetarian, meat, or fish.

        Args:
            dish: The dish text to classify
            previous_category: If the dish follows a category marker, use this

        Returns:
            Category string: 'vegetarian', 'meat', or 'fish'
        """
        dish_lower = dish.lower().strip()

        # Check if this is a category marker itself
        # Only match if it's EXACTLY the marker or marker with trailing colon
        for category, markers in cls.CATEGORY_MARKERS.items():
            for marker in markers:
                # Exact match or marker followed by colon
                if dish_lower == marker or dish_lower == marker + ':':
                    return f'marker:{category}'
                # Also match if marker with colon at start (e.g., "Fisk: dagens rätt")
                if dish_lower.startswith(marker + ':'):
                    return f'marker:{category}'

        # Check for explicit vegan/vegetarian markers first (highest priority)
        # This catches dishes like "Ärtsoppa/Vegan" even if they contain meat keywords
        # Also includes strong vegetable indicators to override "biff" in vegetable patties
        explicit_veg_markers = ['vegan', 'vegansk', 'vegetarisk', 'vegetariskt', 'vego',
                                'morot', 'morötter']
        if any(marker in dish_lower for marker in explicit_veg_markers):
            return 'vegetarian'

        # Check for special meat dishes that should override category markers
        # (e.g., "Ärtsoppa" after "Vegetariskt:" marker should still be meat)
        if any(dish_name in dish_lower for dish_name in cls.MEAT_DISHES):
            return 'meat'

        # Check for meat keywords to avoid false positives
        # (e.g., "fläsk" contains "fisk" as substring, but should be classified as meat)
        if any(keyword in dish_lower for keyword in cls.MEAT_KEYWORDS):
            return 'meat'

        # Check for fish keywords
        if any(keyword in dish_lower for keyword in cls.FISH_KEYWORDS):
            return 'fish'

        # Check for vegetarian keywords
        if any(keyword in dish_lower for keyword in cls.VEGETARIAN_KEYWORDS):
            return 'vegetarian'

        # If previous line was a category marker, use that as fallback
        # This comes AFTER keyword checks so that explicit dishes override markers
        if previous_category:
            return previous_category

        # Default to meat if it looks like a dish (has serveras, med, etc.)
        if any(word in dish_lower for word in ['serveras', ' med ', 'till', 'samt', 'och']):
            return 'meat'

        # If we can't determine, return None
        return None

    @classmethod
    def classify_dishes(cls, dishes: List[str]) -> Dict[str, List[str]]:
        """
        Classify a list of dishes into categories.

        Args:
            dishes: List of dish strings to classify

        Returns:
            Dictionary with 'vegetarian', 'meat', and 'fish' categories
        """
        categorized = {
            'vegetarian': [],
            'meat': [],
            'fish': []
        }

        current_marker_category = None

        for dish in dishes:
            if not dish or len(dish.strip()) < 3:
                continue

            # Skip labels/headers
            dish_lower = dish.lower().strip()
            if any(label in dish_lower for label in cls.SKIP_LABELS):
                # Only skip if it's a very short text (likely just the label)
                if len(dish_lower) < 15:
                    continue

            category = cls.classify_dish(dish, current_marker_category)

            # Check if this is a category marker
            if category and category.startswith('marker:'):
                current_marker_category = category.split(':')[1]
                continue  # Don't add the marker itself

            # Reset marker category if we encounter a dish without a clear category
            # (meaning we've moved past the marked section)
            if category and current_marker_category:
                if category != current_marker_category:
                    # Only reset if it's clearly a different category
                    if any(keyword in dish.lower() for keyword in
                           cls.FISH_KEYWORDS + cls.MEAT_KEYWORDS + cls.VEGETARIAN_KEYWORDS):
                        current_marker_category = None

            if category and category in categorized:
                categorized[category].append(dish)
            elif category is None:
                # Default uncategorized items to meat
                categorized['meat'].append(dish)

        return categorized

    @classmethod
    def merge_categories_for_display(cls, categorized: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """
        Merge categories for backward compatibility (fish + meat = meat).

        Args:
            categorized: Dict with vegetarian, meat, fish

        Returns:
            Dict with vegetarian and meat (fish merged into meat)
        """
        return {
            'vegetarian': categorized.get('vegetarian', []),
            'meat': categorized.get('meat', []) + categorized.get('fish', [])
        }
