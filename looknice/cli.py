import importlib.resources
import click
import sqlfluff
import looknice.utils
from looknice.utils import SQLFLUFF_CONFIG
import re

error_string = "no derived table code found"

@click.command()
def my_test():
    click.echo("Hello, world!")

### derived table
@click.group()
def cli():
    pass

@cli.command()
@click.argument(
    "path",
    type = str,
)
def lint(path: str):
    """Lint the derived table code. Take a path to a view.lkml file"""
    code = looknice.utils.get_code(path)
    if code:
        res = sqlfluff.lint(
            code,
            dialect = "ansi",
            config_path = SQLFLUFF_CONFIG
        )
        click.echo(res)
    else:
        click.echo(error_string)

@cli.command()
@click.argument(
    "path",
    type = str,
)
def parameters(path: str):
    """LookML special parameters contained in the derived table code. Take a path to a view.lkml file."""
    code = looknice.utils.get_code(path)
    if code:
        parameters = looknice.utils.get_parameters(code)
        click.echo(parameters)
    else:
        click.echo(error_string)

@cli.command()
@click.argument(
    "path",
    type = str,
)
def fix(path: str):
    """Fix derived table code. Take a path to a view.lkml file."""
    code = looknice.utils.get_code(path)
    if code:
        parameters = looknice.utils.get_parameters(code)
        sql_code = looknice.utils.convert_to_sql(
            lookml = code,
            params = parameters
        )
        fixed_sql_code = sqlfluff.fix(
            sql_code,
            dialect = "ansi",
            config_path = SQLFLUFF_CONFIG
        )
        res = looknice.utils.convert_to_lookml(
            sql = fixed_sql_code,
            params = parameters
        )
        click.echo(res)
    else:
        click.echo(error_string)


@cli.command()
def config_path():
    """Returns the location of the config files"""
    with importlib.resources.path("looknice", "config") as p:
        click.echo(p)

#dimensions
@cli.command()
@click.argument(
    "path",
    type = str
)
def miss_description(path: str):
    """Returns a list of dimensions with missing description"""
    dimensions = looknice.utils.get_dimensions(path)
    res = [d["name"] for d in dimensions if ~("description" in d.keys())]
    if res:
        click.echo("\nThe following dimensions are missing a description:")
        click.echo(res)
    else:
        click.echo("No missing description")

#joins
@cli.command()
@click.argument(
    "left_path",
    type = str
)
@click.argument(
    "right_path",
    type = str
)
def join_views(
    left_path: str,
    right_path: str,
):
    """Returns the list of primary keys and duplicate dimensions and measures"""
    left_dims = looknice.utils.get_dimensions(left_path)
    right_dims = looknice.utils.get_dimensions(right_path)

    dup_names = []
    left_pk = None
    right_pk = None
    for r in right_dims:
        for l in left_dims:

            if r["name"]==l["name"]:
                dup_names.append(r["name"])

            if "primary_key" in l.keys():
                if l["primary_key"] == "yes":
                   left_pk = l

            if "primary_key" in r.keys():
                if r["primary_key"] == "yes":
                    right_pk = r
    
    click.echo("\nPrimary keys are:")
    if left_pk:
        click.echo(f'{left_pk["name"]}(left)')

    if right_pk:        
        click.echo(f'{right_pk["name"]}(right)')

    click.echo("\nFailure to use the primary keys in a join will result in a many-to-many join.")


    if dup_names:
        click.echo(f"\nThe following dimensions were found in both view: {dup_names}")
        click.echo("Please make sure they are not identical before including both.\n")

@cli.command()
@click.argument(
    "path",
    type = str
) 
def get_comments(path: str) -> str:
    """Returns a dictionary of comments based on the databrick schema file. Takes a databricks schema file as argument"""
    script = looknice.utils.get_schema(path)
    schema = re.findall(r"\((.*?)\)", script)[0].split(",")
    
    for s in schema:
        name = s.split()[0]
        comment = re.findall(r"\"(.*?)\"", s)[0]
        click.echo(f"\n{name}: {comment}")

@cli.command()
@click.argument(
    "path",
    type = str
) 
def write_lkml_schema(path: str) -> None:
    """Returns a dictionary of comments based on the databrick schema file"""

    script = looknice.utils.get_schema(path)
    schema = re.findall(r"\((.*?)\)", script)[0].split(",")
    for s in schema:
        name = s.split()[0]
        type = s.split()[1]
        comment = re.findall(r"\"(.*?)\"", s)[0]
        looknice.utils.print_dimension(
            name = name,
            type = type,
            comment = comment
        )