import click

from chuckjokes import Joke
from prettytable import PrettyTable

@click.group()
def cli():
    """Simple CLI to get and save Chuck Norris jokes from
    https://api.chucknorris.io."""
    pass

@cli.group("joke")
def joke_group():
    """Chuck Norris jokes"""
    pass

@joke_group.command("all")
def all_jokes():
    """Prints all jokes which have already been read"""
    jokes = Joke.all()
    table = PrettyTable(["Joke", "Created at"])

    for joke in jokes:
        table.add_row([joke.value, joke.created_at])

    click.echo(table)

@joke_group.command("new")
@click.option("--category", "-c", default=None, help="specific category for the new joke")
@click.option("--unique/--no-unique", default=False, help="Just show the joke if it is really unique and was never read locally until now. [DEFAULT: False]")
@click.option("--persist/--no--persist", default=True, help="specifies if the new joke should be persisted in the local db [DEFAULT: True]")
def new_joke(category, unique, persist):
    """
    Fetches a new joke from the API and persists if locally (if wanted),
    unless it was already fetched.
    """
    new_joke = Joke.random_from_api(category=category)

    if new_joke:
        if persist:
            new_joke.save()

        click.echo(new_joke.value)
    else:
        click.echo("Sorry, Chuck is out of Jokes currently. Event he needs breakes from time to time :/")

@cli.group("category")
def category_group():
    """Categories for Chuck Norris jokes"""
    pass

# @category_group.command("all")
# def all_categories():
#     """Returns a list of all available categories for jokes"""
#     click.echo(joke.categories())
