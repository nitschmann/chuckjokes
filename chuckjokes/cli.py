import chuckjokes.api.jokes as jokes_api
import click

from chuckjokes import Category, Joke
from chuckjokes.db.exceptions import ValuesAreNotUniqueException
from prettytable import PrettyTable

@click.group()
def cli():
    """Simple CLI to get and save Chuck Norris jokes from
    https://api.chucknorris.io."""
    pass

@cli.command("categories")
@click.option("--local", "-l", is_flag=True, help="just show the local available categories")
def all_categories(local):
    """Returns a list of all available categories for jokes"""
    categories = []
    if local == True:
        categories = list(map((lambda c: c.name), Category.all()))
    else:
        categories = jokes_api.categories()

    click.echo(categories)

@cli.group("jokes")
def jokes_group():
    """Chuck Norris jokes"""
    pass

@jokes_group.command("all")
@click.option("--category", "-c", default=None, help="just return jokes saved under specific category")
def all_jokes(category):
    """Prints all jokes which have already been read"""
    jokes = []

    if category is not None:
        c = Category.find_by("name", category)

        if c:
            jokes = c.jokes()
    else:
        jokes = Joke.all()

    table = PrettyTable(["Joke", "Read at"])

    for joke in jokes:
        table.add_row([joke.value, joke.created_at])

    click.echo(table)

@jokes_group.command("new")
@click.option("--category", "-c", default=None, help="specific category for the new joke")
@click.option("--unique/--no-unique", default=False, help="Just show the joke if it is really unique and was never read locally until now. [DEFAULT: False]")
@click.option("--persist/--no--persist", default=True, help="specifies if the new joke should be persisted in the local db [DEFAULT: True]")
def new_joke(category, unique, persist):
    """
    Fetches a new joke from the API and persists it locally (if wanted),
    unless it was already fetched.
    """
    new_joke = Joke.random_from_api(category=category)

    if persist == True:
        try:
            new_joke.save(check_uniqueness_conditions = unique)
            click.echo(new_joke.value)
        except ValuesAreNotUniqueException as e:
            click.echo("Sorry, Chuck is out of Jokes currently. Event he needs breakes from time to time :/")
    else:
        click.echo(new_joke.value)
