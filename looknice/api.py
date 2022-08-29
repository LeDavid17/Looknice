import looknice.looker_utils as looker
import sqlfluff
from looknice.looker_utils import SQLFLUFF_CONFIG

def fix(path: str, dialect: str = "ansi"):
    """Fix derived table code. Take a path to a view.lkml file."""
    code = looker.get_lookml_code(path)
    if code:
        parameters = looker.get_lookml_parameters(code)
        sql_code = looker.convert_lookml(
            lookml = code,
            params = parameters
        )
        fixed_sql_code = sqlfluff.fix(
            sql_code,
            dialect = dialect,
            config_path = SQLFLUFF_CONFIG
        )
        res = looker.convert_sql(
            sql = fixed_sql_code,
            params = parameters
        )
        return res
    else:
        return looker.ERROR_STRING

def get_missing_descriptions(path: str):
    """Print a list of dimensions with missing description"""
    dimensions = looker.get_dimensions(path)
    return [d["name"] for d in dimensions if ~("description" in d.keys())]