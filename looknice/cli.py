# import importlib.resources
import click
import utils as U
import re

### derived table
@click.group()
def cli():
    pass

@cli.command()
@click.argument(
    "path",
    type = str
) 
def write_lkml(path: str) -> None:
    """Writes the lookml code from the Databricks' SQL script"""
    script = U.get_sql_code(path)
    clean_script = U.clean_sql_code(script)

    if "CREATE OR REPLACE VIEW" in clean_script:
        type, statement, keyword = "view", "CREATE OR REPLACE VIEW", "AS"
    elif "CREATE TABLE IF NOT EXISTS" in clean_script:
        type, statement, keyword = "table", "CREATE TABLE IF NOT EXISTS", "USING"
    else:
        raise Exception("The program doesn't understand if it's a view or a table")

    columns = re.findall(rf"\((.*?)\)\s?{keyword}", clean_script)[0].split(",")
    schema, table = re.findall(rf"{statement} (.*?)\s?\(", clean_script)[0].split(".")

    click.echo(f'\n\nview: {table}{{\n\tsql_table_name: {schema}.{table};;')
    miss_descriptions = []
    for c in columns:
        col_name = c.split()[0]
        col_type = c.split()[1] if type=="table" else "<TODO>"
        try:
            col_comment = re.findall(r"COMMENT \'(.*?)\'", c)[0]
        except IndexError:
            col_comment = "<TODO>"
            miss_descriptions.append(col_name)

        click.echo(
            databricks.convert_sql_columns(
                name = col_name,
                type = col_type,
                comment = col_comment
            )
        )
    click.echo("}")

    if miss_descriptions:
        click.echo(f"\n\n***ALERT***\nThe following dimensions are missing a description:\n{miss_descriptions}")
