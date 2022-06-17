# import importlib.resources
import click
import sqlfluff
import looknice.looker_utils as looker
import looknice.databricks_utils as databricks
import looknice.api
from looknice.looker_utils import SQLFLUFF_CONFIG
import re

error_string = "no derived table code found"

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
    code = looker.get_code(path)
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
    code = looker.get_code(path)
    if code:
        parameters = looker.get_parameters(code)
        click.echo(parameters)
    else:
        click.echo(error_string)

@cli.command()
@click.argument(
    "path",
    type = str,
)
def fix(path: str):
    """Format the derived table SQL code"""
    code = looker.get_code(path)
    if code:
        parameters = looker.get_parameters(code)
        sql_code = looker.convert_lookml(
            lookml = code,
            params = parameters
        )
        fixed_sql_code = sqlfluff.fix(
            sql_code,
            dialect = "ansi",
            config_path = SQLFLUFF_CONFIG
        )
        res = looker.convert_sql(
            sql = fixed_sql_code,
            params = parameters
        )
        click.echo(res)
    else:
        click.echo(error_string)


# @cli.command()
# def config_path():
#     """Returns the location of the config files"""
#     with importlib.resources.path("looknice", "config") as p:
#         click.echo(p)

@cli.command()
@click.argument(
    "path",
    type = str
)
def get_missing_descriptions(path: str):
    """Returns a list of Looker dimensions with a missing description"""
    dimensions = looker.get_dimensions(path)
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
    left_dims = looker.get_dimensions(left_path)
    right_dims = looker.get_dimensions(right_path)

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

# @cli.command()
# @click.argument(
#     "path",
#     type = str
# ) 
# def get_comments(path: str) -> str:
#     """Returns a dictionary of comments based on the databrick schema file. Takes a databricks schema file as argument"""
#     script = databricks.get_sql_code(path)
#     schema = re.findall(r"\((.*?)\)", script)[0].split(",")
    
#     for s in schema:
#         name = s.split()[0]
#         comment = re.findall(r"\"(.*?)\"", s)[0]
#         click.echo(f"\n{name}: {comment}")

@cli.command()
@click.argument(
    "path",
    type = str
) 
def write_lkml(path: str) -> None:
    """Writes the lookml code from the Databricks' SQL script"""
    script = databricks.get_sql_code(path)
    columns = re.findall(r"\((.*?)\)", script)[0].split(",")
    schema, table = re.findall("CREATE TABLE IF NOT EXISTS (.*?)\(", script)[0].split(".")

    click.echo(f"\n\nview: {table}{{\n\tdescription: <TODO: description>\n\tsql_table_name: {schema}.{table} ;;")
    miss_descriptions = []
    for c in columns:
        name = c.split()[0]
        type = c.split()[1]
        try:
            comment = re.findall(r"\"(.*?)\"", c)[0]
        except IndexError:
            comment = "<TODO: comment>"
            miss_descriptions.append(name)

        click.echo(
            databricks.convert_sql_columns(
                name = name,
                type = type,
                comment = comment
            )
        )

    if miss_descriptions:
        click.echo(f"\n\n***ALERT***\nThe following dimensions are missing a description:\n{miss_descriptions}")

@cli.command()
@click.argument(
    "path",
    type = str
)
def write_sql(path: str) -> None:
    """Writes the Databricks SQL script from the LookML view file"""
    s = "\n\nCREATE OR REPLACE VIEW <TODO: schema>.vw_<TODO: viewname> (\n"
    s = s + looker.convert_lookml_dims(path)[:-2] + "\n)\n" #[:-2] to remove last comma
    s = s + looknice.api.fix(path)[:-1] +";\n\nALTER VIEW <TODO: schema>.vw_<TODO: viewname> OWNER TO `super-users`"
    click.echo(s)
    
    miss_descriptions = looknice.api.get_missing_descriptions(path)
    if miss_descriptions:
        click.echo(f"\n\n***ALERT***\nThe following dimensions are missing a description:\n{miss_descriptions}")