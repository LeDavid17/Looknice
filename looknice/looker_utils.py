"""Functions taking a LookML script as argument"""

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

def get_lookml_code(path: str) -> str:
    """Returns the derived table lookml code in a string"""

    with open(path, "r") as file:
        view = lkml.load(file)["views"][0]
        if 'derived_table' in view.keys():
            return view["derived_table"]["sql"]


def get_lookml_parameters(
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


def convert_lookml(
    lookml: str,
    params: Dict[str, str]
) -> str:
    """Returns sql code from lookml code"""

    sql = lookml
    for key, value in params.items():
        sql = sql.replace(value, key)
    return sql


def convert_sql(
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
    """Returns the Looker dimensions in a json object"""
    with open(path, "r") as file:
            return lkml.load(file)["views"][0]["dimensions"]


def replace_lookml_types(t: str) -> str:
    """Replace Looker dimension type to Hive data type"""
    if t == "number":
        return ("<TODO: integer/decimal/bigint/double>")
    if t == "time":
        return "<TODO: timestamp/date>"
    if (t == "yesno"):
        return "boolean"
    return t


def convert_lookml_dim(d: Dict):
    """Convert Looker dimensions to spark SQL statement in sql script"""
    s = "    " + d["name"]
    try:
        s = s + " " + replace_lookml_types(d["type"])
    except KeyError:
        s = s + " <TODO: type>"
    
    try:
        s = s + " COMMENT '" + replace_lookml_types(d["description"]) + "',"
    except KeyError:
        s = s + " COMMENT '<TODO: comment>',"
    
    return s

def convert_lookml_dims(path):
    dimensions = get_dimensions(path)
    s = ""
    for d in dimensions:
        s = s + convert_lookml_dim(d) + "\n"
    
    return s

if __name__ == "__main__":
    pass
    
