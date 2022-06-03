import importlib.resources
import click
import sqlfluff
from looknice.utils import get_code, get_parameters, convert_to_sql, convert_to_lookml
from looknice.utils import SQLFLUFF_CONFIG

error_string = "no derived table code found"

@click.command()
def my_test():
    click.echo("Hello, world!")

@click.command()
@click.argument("path", type = str)
def lint(path: str):
    code = get_code(path)
    if code:
        res = sqlfluff.lint(
            code,
            dialect = "ansi",
            config_path = SQLFLUFF_CONFIG
        )
        click.echo(res)
    else:
        click.echo(error_string)

@click.command()
@click.argument("path", type = str)
def print_parameters(path: str):
    code = get_code(path)
    if code:
        parameters = get_parameters(code)
        click.echo(parameters)
    else:
        click.echo(error_string)

@click.command()
@click.argument("path", type = str)
def fix(path: str):
    code = get_code(path)
    if code:
        parameters = get_parameters(code)
        sql_code = convert_to_sql(
            lookml = code,
            params = parameters
        )
        fixed_sql_code = sqlfluff.fix(
            sql_code,
            dialect = "ansi",
            config_path = SQLFLUFF_CONFIG
        )
        res = convert_to_lookml(
            sql = fixed_sql_code,
            params = parameters
        )
        click.echo(res)
    else:
        click.echo(error_string)


@click.command()
def path():
    with importlib.resources.path("looknice", "config") as p:
        click.echo(p / "my_text_file.txt")