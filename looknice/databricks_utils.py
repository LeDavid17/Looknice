"""Functions taking a SQL script as argument"""

def get_sql_code(path: str) -> str:
    "Returns the sql script of the Databticks schema file"
    with open(path, "r") as file:
        return file.read().replace("\n", "")

def replace_hive_types(t: str) -> str:
    """Convert Hive data type to Looker dimension type"""
    if (t == "integer") | ("decimal" in t) | (t == "bigint") | (t == "double"):
        return "number"
    if (t == "timestamp") | (t == "date"):
        return "time"
    if (t == "boolean"):
        return "yesno"
    return t

def convert_sql_columns(
    name: str,
    type: str,
    comment: str
) -> None:
    """Convert SQL schema defintion to LookML dimension code"""

    is_timestamp = (type == "timestamp") | (type == "date")
    dimension = "dimension_group" if is_timestamp else "dimension"
    timeframes = "[time, date, week, month, quarter, year]" if type == "timestamp" else "[date]"

    s1 = f"\n\t{dimension}: {name} {{\n\t\tdescription: {comment}\n\t\ttype: {replace_hive_types(type)}\n"
    s2 = f"\t\ttimeframes: {timeframes}\n" if is_timestamp else""
    s3 = f"\t\tsql: {{$TABLE}}.{name};;\n\t}}"
    return s1+s2+s3