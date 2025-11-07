"""Tests for DishClassifier."""

import pytest
from lunchscraper.dish_classifier import DishClassifier


class TestClassifyDish:
    """Tests for classify_dish method."""

    def test_classify_vegetarian_dishes(self):
        """Test classification of vegetarian dishes."""
        vegetarian_dishes = [
            "Falafel med hummus och sallad",
            "Halloumi med grillad paprika",
            "Tofu med grönsaker",
            "Tempeh med ris",
            "Vegansk lasagne",
            "Vegoburgare med pommes",
            "Vegansk chili med bönor",
            "Kikärtsgryta med quinoa",
        ]
        for dish in vegetarian_dishes:
            assert DishClassifier.classify_dish(dish) == 'vegetarian', f"Failed for: {dish}"

    def test_classify_meat_dishes(self):
        """Test classification of meat dishes."""
        meat_dishes = [
            "Kyckling med ris",
            "Biff med potatis",
            "Fläskkarré med äppelkompott",
            "Köttbullar med gräddsås",
            "Oxfilé med bearnaisesås",
            "Bacon och ägg",
            "Schnitzel med potatissallad",
            "Pulled pork med coleslaw",
            "Wallenbergare med ärtor",
            "Kalvschnitzel med citronsås",
        ]
        for dish in meat_dishes:
            assert DishClassifier.classify_dish(dish) == 'meat', f"Failed for: {dish}"

    def test_classify_fish_dishes(self):
        """Test classification of fish dishes."""
        fish_dishes = [
            "Lax med dillsås",
            "Torsk med smörås",
            "Räkor med aioli",
            "Skaldjurspasta",
            "Tonfisksallad",
            "Kokt sej med ägg",
            "Fiskgratäng med ost",
        ]
        for dish in fish_dishes:
            assert DishClassifier.classify_dish(dish) == 'fish', f"Failed for: {dish}"

    def test_classify_ambiguous_fish_dishes(self):
        """Test that dishes with 'med' keyword but no clear fish keyword default to meat."""
        # "Räksmörgås" contains "med" which triggers the default-to-meat logic
        # even though "räk" is similar to "räkor"
        assert DishClassifier.classify_dish("Räksmörgås med majonnäs") == 'meat'

    def test_classify_special_swedish_meat_dishes(self):
        """Test classification of special Swedish dishes."""
        # Ärtsoppa and pannkaka should be classified as meat
        assert DishClassifier.classify_dish("Ärtsoppa med fläsk") == 'meat'
        assert DishClassifier.classify_dish("Pannkaka med sylt") == 'meat'

    def test_fläsk_vs_fisk_priority(self):
        """Test that fläsk (meat) has priority over fisk (fish) substring match."""
        # Fläsk contains "fisk" as substring, but should be meat
        assert DishClassifier.classify_dish("Fläskfilé med gräddsås") == 'meat'
        assert DishClassifier.classify_dish("Grillad fläsk") == 'meat'

    def test_classify_category_markers(self):
        """Test detection of category markers."""
        # Vegetarian markers
        assert DishClassifier.classify_dish("Vegetariskt:") == 'marker:vegetarian'
        assert DishClassifier.classify_dish("Vego:") == 'marker:vegetarian'
        assert DishClassifier.classify_dish("Veganskt alternativ:") == 'marker:vegetarian'

        # Fish markers
        assert DishClassifier.classify_dish("Fisk:") == 'marker:fish'
        assert DishClassifier.classify_dish("Dagens fisk:") == 'marker:fish'

        # Meat markers
        assert DishClassifier.classify_dish("Kött:") == 'marker:meat'
        assert DishClassifier.classify_dish("Dagens kött:") == 'marker:meat'

    def test_classify_marker_with_dish_on_same_line(self):
        """Test markers that appear at the start of a line with dish text."""
        assert DishClassifier.classify_dish("Fisk: Lax med dillsås") == 'marker:fish'
        assert DishClassifier.classify_dish("Kött: Biff med lök") == 'marker:meat'
        assert DishClassifier.classify_dish("Vegetariskt: Halloumi") == 'marker:vegetarian'

    def test_classify_with_previous_category(self):
        """Test that previous_category parameter overrides keyword matching."""
        # If previous line was a fish marker, classify as fish even if it has no fish keywords
        assert DishClassifier.classify_dish("Stekt med potatis", previous_category='fish') == 'fish'
        assert DishClassifier.classify_dish("Dagens rätt", previous_category='vegetarian') == 'vegetarian'
        assert DishClassifier.classify_dish("Grillad med grönsaker", previous_category='meat') == 'meat'

    def test_classify_empty_and_short_strings(self):
        """Test handling of edge cases."""
        # Very short strings should return None
        assert DishClassifier.classify_dish("") is None
        assert DishClassifier.classify_dish("  ") is None
        assert DishClassifier.classify_dish("ab") is None

    def test_classify_ambiguous_dishes_with_serveras(self):
        """Test default behavior for ambiguous dishes."""
        # Dishes with "serveras", "med", etc. default to meat
        assert DishClassifier.classify_dish("Dagens rätt serveras med potatis") == 'meat'
        assert DishClassifier.classify_dish("Rätt till dagens") == 'meat'

    def test_classify_mixed_keywords(self):
        """Test dishes with multiple keywords."""
        # When both fish and meat keywords appear, meat should win (checked first)
        assert DishClassifier.classify_dish("Fläskfilé med fiskräk") == 'meat'

        # When both vegetarian and meat keywords appear, meat wins (checked first)
        # "köttbullar" is in MEAT_KEYWORDS, so it matches before checking vegetarian
        assert DishClassifier.classify_dish("Vego köttbullar") == 'meat'

        # Pure vegetarian dishes without meat keywords work fine
        assert DishClassifier.classify_dish("Vego burgare") == 'vegetarian'

    def test_case_insensitivity(self):
        """Test that classification is case-insensitive."""
        assert DishClassifier.classify_dish("KYCKLING MED RIS") == 'meat'
        assert DishClassifier.classify_dish("LaX mEd DiLlSåS") == 'fish'
        assert DishClassifier.classify_dish("HaLLoUmI sAlLaD") == 'vegetarian'

    def test_whitespace_handling(self):
        """Test that extra whitespace is handled correctly."""
        assert DishClassifier.classify_dish("  Kyckling med ris  ") == 'meat'
        assert DishClassifier.classify_dish("\tFalafel med hummus\n") == 'vegetarian'


class TestClassifyDishes:
    """Tests for classify_dishes method."""

    def test_classify_dishes_with_vegetarian_marker(self):
        """Test classification when vegetarian marker is present."""
        dishes = [
            "Vegetariskt:",
            "Falafel med hummus",
            "Halloumi med sallad",
        ]
        result = DishClassifier.classify_dishes(dishes)

        assert len(result['vegetarian']) == 2
        assert "Falafel med hummus" in result['vegetarian']
        assert "Halloumi med sallad" in result['vegetarian']

    def test_classify_dishes_with_fish_marker(self):
        """Test classification when fish marker is present."""
        dishes = [
            "Fisk:",
            "Kokt torsk med dillsås",
            "Stekt lax med potatis",
        ]
        result = DishClassifier.classify_dishes(dishes)

        assert len(result['fish']) == 2
        assert "Kokt torsk med dillsås" in result['fish']
        assert "Stekt lax med potatis" in result['fish']

    def test_classify_dishes_with_meat_marker(self):
        """Test classification when meat marker is present."""
        dishes = [
            "Kött:",
            "Biff med bearnaisesås",
            "Kycklinggryta med ris",
        ]
        result = DishClassifier.classify_dishes(dishes)

        assert len(result['meat']) == 2
        assert "Biff med bearnaisesås" in result['meat']
        assert "Kycklinggryta med ris" in result['meat']

    def test_classify_dishes_with_multiple_markers(self):
        """Test classification with multiple category markers."""
        dishes = [
            "Vegetariskt:",
            "Falafel med hummus",
            "Fisk:",
            "Lax med dillsås",
            "Kött:",
            "Biff med lök",
        ]
        result = DishClassifier.classify_dishes(dishes)

        assert len(result['vegetarian']) == 1
        assert len(result['fish']) == 1
        assert len(result['meat']) == 1
        assert "Falafel med hummus" in result['vegetarian']
        assert "Lax med dillsås" in result['fish']
        assert "Biff med lök" in result['meat']

    def test_classify_dishes_without_markers(self):
        """Test classification based on keywords alone."""
        dishes = [
            "Kyckling med ris",
            "Lax med dillsås",
            "Falafel med hummus",
        ]
        result = DishClassifier.classify_dishes(dishes)

        assert "Kyckling med ris" in result['meat']
        assert "Lax med dillsås" in result['fish']
        assert "Falafel med hummus" in result['vegetarian']

    def test_classify_dishes_skips_empty_and_short_items(self):
        """Test that empty and very short items are skipped."""
        dishes = [
            "",
            "  ",
            "ab",
            "Kyckling med ris",
        ]
        result = DishClassifier.classify_dishes(dishes)

        # Only the valid dish should be classified
        assert len(result['meat']) == 1
        assert "Kyckling med ris" in result['meat']

    def test_classify_dishes_default_to_meat(self):
        """Test that unclassified dishes default to meat."""
        dishes = [
            "Dagens rätt serveras med potatis",
            "Specialitet från köket",
        ]
        result = DishClassifier.classify_dishes(dishes)

        # These should default to meat
        assert len(result['meat']) == 2

    def test_classify_dishes_marker_continues_until_new_marker(self):
        """Test that category marker continues until a new marker or clear different category."""
        dishes = [
            "Vegetariskt:",
            "Falafel med hummus",
            "Halloumi med sallad",  # Still vegetarian
        ]
        result = DishClassifier.classify_dishes(dishes)

        assert "Falafel med hummus" in result['vegetarian']
        assert "Halloumi med sallad" in result['vegetarian']

    def test_classify_dishes_marker_reset_with_new_marker(self):
        """Test that new markers properly reset the category."""
        dishes = [
            "Vegetariskt:",
            "Falafel med hummus",
            "Kött:",
            "Kyckling med ris",
        ]
        result = DishClassifier.classify_dishes(dishes)

        assert "Falafel med hummus" in result['vegetarian']
        assert "Kyckling med ris" in result['meat']

    def test_classify_dishes_empty_list(self):
        """Test classification with empty list."""
        result = DishClassifier.classify_dishes([])

        assert result == {'vegetarian': [], 'meat': [], 'fish': []}

    def test_classify_dishes_real_world_example(self):
        """Test with a realistic menu."""
        dishes = [
            "Vegetariskt:",
            "Halloumi med rostade grönsaker",
            "Fisk:",
            "Lax med citron och dill",
            "Kött:",
            "Kycklingfilé med currysås",
            "Serveras med ris och sallad",
        ]
        result = DishClassifier.classify_dishes(dishes)

        assert len(result['vegetarian']) == 1
        assert len(result['fish']) == 1
        assert len(result['meat']) == 2  # Chicken and "Serveras med ris och sallad"


class TestMergeCategoriesForDisplay:
    """Tests for merge_categories_for_display method."""

    def test_merge_fish_into_meat(self):
        """Test that fish dishes are merged into meat category."""
        categorized = {
            'vegetarian': ['Falafel med hummus'],
            'meat': ['Kyckling med ris', 'Biff med lök'],
            'fish': ['Lax med dillsås', 'Torsk med ägg']
        }

        result = DishClassifier.merge_categories_for_display(categorized)

        assert len(result['vegetarian']) == 1
        assert len(result['meat']) == 4  # 2 meat + 2 fish
        assert 'Falafel med hummus' in result['vegetarian']
        assert 'Kyckling med ris' in result['meat']
        assert 'Lax med dillsås' in result['meat']
        assert 'Torsk med ägg' in result['meat']

    def test_merge_empty_fish_category(self):
        """Test merge when fish category is empty."""
        categorized = {
            'vegetarian': ['Falafel'],
            'meat': ['Kyckling'],
            'fish': []
        }

        result = DishClassifier.merge_categories_for_display(categorized)

        assert len(result['vegetarian']) == 1
        assert len(result['meat']) == 1

    def test_merge_missing_categories(self):
        """Test merge when some categories are missing."""
        categorized = {
            'vegetarian': ['Falafel'],
        }

        result = DishClassifier.merge_categories_for_display(categorized)

        assert result['vegetarian'] == ['Falafel']
        assert result['meat'] == []

    def test_merge_only_fish(self):
        """Test merge when only fish dishes exist."""
        categorized = {
            'vegetarian': [],
            'meat': [],
            'fish': ['Lax', 'Torsk']
        }

        result = DishClassifier.merge_categories_for_display(categorized)

        assert result['vegetarian'] == []
        assert len(result['meat']) == 2
        assert 'Lax' in result['meat']
