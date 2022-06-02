import re
import lkml
from typing import Dict
import importlib.resources as pkg_resources
from looknice import config

PARAM_REGEXPS = (
    {"find": r"{%.*?%}.*?{%.*?%}", "replace": r"\s?{%.*?%}\s?"},
    {"find": r"\${.*?\.SQL_TABLE_NAME}", "replace": r"\${|.SQL_TABLE_NAME}"}
)

with pkg_resources.path(config, ".sqlfluff") as p:
    SQLFLUFF_CONFIG = p

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


if __name__ == "__main__":
    
    s = "and {% condition created_at %} created_at {% endcondition %}"
    get_parameters(s)
