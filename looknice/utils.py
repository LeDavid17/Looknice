import re
import lkml
from typing import Dict, List
import importlib.resources
import os

PARAM_REGEXPS = (
    {"find": r"{%.*?%}.*?{%.*?%}", "replace": r"\s?{%.*?%}\s?"},
    {"find": r"\${.*?\.SQL_TABLE_NAME}", "replace": r"\${|.SQL_TABLE_NAME}"}
)

with importlib.resources.path("looknice", "config") as p:
        SQLFLUFF_CONFIG = os.path.join(p, ".sqlfluff")

def get_code(path: str) -> str:
    """Returns the derived table lookml code in a string"""

    with open(path, "r") as file:
        view = lkml.load(file)["views"][0]
        if 'derived_table' in view.keys():
            return view["derived_table"]["sql"]


def get_parameters(
    s: str,
) -> Dict[str, str]:
    """Returns a dictionary of special Lookml parameters"""

    values = list()
    keys = list()

    for d in PARAM_REGEXPS:
        for v in re.findall(d["find"], s):
            values.append(v)
            keys.append(re.sub(d["replace"],"",v))
        
    return dict(zip(keys, values))


def convert_to_sql(
    lookml: str,
    params: Dict[str, str]
) -> str:
    """Returs sql code from lookml code"""

    sql = lookml
    for key, value in params.items():
        sql = sql.replace(value, key)
    return sql


def convert_to_lookml(
    sql: str,
    params: Dict[str, str]
) -> str:
    """Returns sql code from lookml code"""

    lookml = sql
    for key, value in params.items():
        lookml = lookml.replace("FROM " + key, "FROM " + value)
        lookml = lookml.replace("WHERE " + key, "WHERE " + value)
        lookml = lookml.replace("AND " + key, "AND " + value)
    return lookml


def get_dimensions(path: str) -> List[Dict]:
    """Returns the dimension json object"""
    with open(path, "r") as file:
            return lkml.load(file)["views"][0]["dimensions"]

def get_schema(path: str) -> str:
    "Returns the sql script of the Databticks schema file"
    with open(path, "r") as file:
        return file.read().replace("\n", "")

def convert_type(t: str) -> str:
    """Convert Hive data type to Looker dimension type"""
    if (t == "integer") | ("decimal" in t) | (t == "bigint") | (t == "double"):
        return "number"
    if (t == "timestamp") | (t == "date"):
        return "time"
    if (t == "boolean"):
        return "yesno"
    return t

def print_dimension(
    name: str,
    type: str,
    comment: str
) -> None:
    """Write the LookML code for the dimension based on the arguments"""

    is_timestamp = (type == "timestamp") | (type == "date")
    dimension = "dimension_group" if is_timestamp else "dimension"
    timeframes = "[time, date, week, month, quarter, year]" if type == "timestamp" else "[date]"

    s1 = f"\n{dimension}: {name} {{\n    description: {comment}\n    type: {convert_type(type)}\n"
    s2 = f"    timeframes: {timeframes}\n" if is_timestamp else""
    s3 = f"    sql: {{$TABLE}}.{name};;\n}}"
    print(s1+s2+s3)

if __name__ == "__main__":
    pass
    
