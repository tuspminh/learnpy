You can build a command-line tool using the Python click library with a main group command (story) and four subcommands: add, remove, search, and export.

import click

@click.group()def story():
    """Manage your story library."""
    pass

@story.command()
@click.argument("title")def add(title):
    """Add a new story."""
    click.echo(f"Adding story: {title}")

@story.command()
@click.argument("story_id", type=int)def remove(story_id):
    """Remove a story by ID."""
    click.echo(f"Removing story ID: {story_id}")

@story.command()
@click.argument("keyword")def search(keyword):
    """Search for a story."""
    click.echo(f"Searching for: {keyword}")

@story.command()
@click.argument("db")
@click.option("--format", required=True, help="File format (e.g., epub).")
@click.option("--output", required=True, help="Output directory.")def export(db, format, output):
    """Export the story library."""
    click.echo(f"Exporting {db} to {output} in {format} format.")
if __name__ == "__main__":
    story()

## How to Run It

* Add a story: python script.py story add "Harry Potter"
* Remove a story: python script.py story remove 15
* Search a story: python script.py story search "Magic"
* Export library: python script.py story export library.db --format epub --output exports/

Would you like me to add database integration (SQLite) or error handling to these commands?
