"""Command line interface for the lunch menu scraper."""

import click
from datetime import date, datetime
import logging
from .iss_scraper import ISSMenuScraper
from .kvartersmenyn_scraper import KvartersmenynsMenuScraper

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)

# Restaurant configurations
RESTAURANTS = {
    'gourmedia': {
        'name': 'Gourmedia',
        'type': 'iss',
        'url': 'https://www.iss-menyer.se/restaurants/restaurang-gourmedia',
        'id': 'Restaurang Gourmedia'
    },
    'filmhuset': {
        'name': 'Filmhuset',
        'type': 'kvartersmenyn',
        'url': 'https://filmhuset.kvartersmenyn.se/'
    },
    'karavan': {
        'name': 'Karavan',
        'type': 'kvartersmenyn',
        'url': 'https://karavan.kvartersmenyn.se/'
    }
}


@click.command()
@click.option('--restaurant', '-r', 'restaurant_key',
              default=None,
              type=click.Choice(list(RESTAURANTS.keys()), case_sensitive=False),
              help='Specific restaurant to show. By default shows all restaurants.')
@click.option('--vegetarian-only', '-v', is_flag=True,
              help='Show only vegetarian options.')
@click.option('--meat-only', '-m', is_flag=True,
              help='Show only meat options.')
@click.option('--week', '-w', is_flag=True,
              help='Show the whole week menu.')
@click.option('--debug', '-d', is_flag=True,
              help='Enable debug logging to show which date is being fetched.')
def main(restaurant_key, vegetarian_only, meat_only, week, debug):
    """
    Get lunch menu from multiple restaurants.

    Examples:
        lunch                    # Get today's menu from all restaurants
        lunch -r gourmedia      # Show only Gourmedia
        lunch -v                # Show only vegetarian options
        lunch -m                # Show only meat options
        lunch -w                # Show whole week menu
        lunch -d                # Enable debug logging
    """
    # Enable debug logging if requested
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger = logging.getLogger(__name__)
        logger.debug("Debug logging enabled")

    # Determine which restaurants to fetch
    if restaurant_key:
        restaurants_to_fetch = {restaurant_key: RESTAURANTS[restaurant_key]}
    else:
        restaurants_to_fetch = RESTAURANTS

    # Fetch menus from all selected restaurants
    all_menus = {}
    for key, config in restaurants_to_fetch.items():
        try:
            # Create appropriate scraper based on type
            if config['type'] == 'iss':
                scraper = ISSMenuScraper(config['url'], config['id'], config['name'])
            elif config['type'] == 'kvartersmenyn':
                scraper = KvartersmenynsMenuScraper(config['url'], config['name'])
            else:
                click.echo(f"⚠️  Unknown scraper type for {config['name']}", err=True)
                continue

            # Fetch menu
            if week:
                menu = scraper.get_weekly_menu()
            else:
                menu = scraper.get_menu_for_day()

            all_menus[config['name']] = menu

        except Exception as e:
            click.echo(f"\n❌ Error fetching menu from {config['name']}:", err=True)
            click.echo(f"   {e}", err=True)
            if debug:
                import traceback
                traceback.print_exc()

    # Display results
    if not all_menus:
        click.echo("\n❌ Failed to fetch any menus", err=True)
        click.echo("\nTry running with --debug (-d) flag for more details.", err=True)
        raise click.Abort()

    if week:
        display_all_weekly_menus(all_menus, vegetarian_only, meat_only)
    else:
        display_all_daily_menus(all_menus, vegetarian_only, meat_only)


def display_all_daily_menus(all_menus, vegetarian_only, meat_only):
    """Display daily menus from multiple restaurants."""
    today = date.today()
    day_names = {
        0: 'Monday',
        1: 'Tuesday',
        2: 'Wednesday',
        3: 'Thursday',
        4: 'Friday',
        5: 'Saturday',
        6: 'Sunday'
    }
    day_name = day_names[today.weekday()]

    # Header
    click.echo()
    click.echo(click.style("  🍽️  LUNCH MENU", fg='bright_white', bold=True) +
               click.style(f"  •  {day_name}, {today.strftime('%B %d, %Y')}", fg='white', dim=True))
    click.echo()

    for i, (restaurant_name, menu) in enumerate(all_menus.items()):
        # Restaurant header with emoji and bold name
        click.echo(click.style(f"  📍  {restaurant_name.upper()}", fg='bright_cyan', bold=True))
        click.echo(click.style("      " + "─" * 74, fg='cyan', dim=True))

        has_items = False

        # Show vegetarian options
        if not meat_only and menu.get('vegetarian'):
            has_items = True
            click.echo()
            click.echo(click.style("🥬  Vegetarian".center(80), fg='green', bold=True))
            click.echo()
            for item in menu['vegetarian']:
                click.echo(f"      {item}")

        # Show fish options
        if not vegetarian_only and menu.get('fish'):
            has_items = True
            click.echo()
            click.echo(click.style("🐟  Fish".center(80), fg='blue', bold=True))
            click.echo()
            for item in menu['fish']:
                click.echo(f"      {item}")

        # Show meat options
        if not vegetarian_only and menu.get('meat'):
            has_items = True
            click.echo()
            click.echo(click.style("🥩  Meat".center(80), fg='red', bold=True))
            click.echo()
            for item in menu['meat']:
                click.echo(f"      {item}")

        # Handle case where no menu items found
        if not has_items:
            click.echo(click.style("      ❌ No menu items found for today", fg='yellow'))

        # Add spacing between restaurants (except for the last one)
        if i < len(all_menus) - 1:
            click.echo()

    click.echo()


def display_all_weekly_menus(all_menus, vegetarian_only, meat_only):
    """Display weekly menus from multiple restaurants."""
    # Header
    click.echo()
    click.echo(click.style("  🍽️  WEEKLY LUNCH MENU", fg='bright_white', bold=True))
    click.echo()

    day_names = {
        'måndag': 'Monday',
        'tisdag': 'Tuesday',
        'onsdag': 'Wednesday',
        'torsdag': 'Thursday',
        'fredag': 'Friday',
        'lördag': 'Saturday',
        'söndag': 'Sunday'
    }

    for rest_idx, (restaurant_name, weekly_menu) in enumerate(all_menus.items()):
        # Restaurant header
        click.echo(click.style(f"  📍  {restaurant_name.upper()}", fg='bright_cyan', bold=True))
        click.echo(click.style("      " + "─" * 74, fg='cyan', dim=True))

        for day_key, day_name in day_names.items():
            if day_key in weekly_menu:
                menu = weekly_menu[day_key]

                # Skip if no menu items and it's a weekend
                if not menu.get('vegetarian') and not menu.get('fish') and not menu.get('meat'):
                    if day_key in ['lördag', 'söndag']:
                        continue  # Skip empty weekends

                # Day header
                click.echo()
                click.echo(click.style(f"      📅  {day_name}", fg='bright_yellow', bold=True))

                has_items = False

                # Show vegetarian options
                if not meat_only and menu.get('vegetarian'):
                    has_items = True
                    click.echo()
                    click.echo(click.style("🥬  Vegetarian".center(80), fg='green', bold=True))
                    click.echo()
                    for item in menu['vegetarian']:
                        click.echo(f"          {item}")

                # Show fish options
                if not vegetarian_only and menu.get('fish'):
                    has_items = True
                    click.echo()
                    click.echo(click.style("🐟  Fish".center(80), fg='blue', bold=True))
                    click.echo()
                    for item in menu['fish']:
                        click.echo(f"          {item}")

                # Show meat options
                if not vegetarian_only and menu.get('meat'):
                    has_items = True
                    click.echo()
                    click.echo(click.style("🥩  Meat".center(80), fg='red', bold=True))
                    click.echo()
                    for item in menu['meat']:
                        click.echo(f"          {item}")

                # Show message if no items found
                if not has_items:
                    click.echo(click.style("          ❌ No menu available", fg='yellow'))

        # Add spacing between restaurants (except for the last one)
        if rest_idx < len(all_menus) - 1:
            click.echo()

    click.echo()


if __name__ == '__main__':
    main()
