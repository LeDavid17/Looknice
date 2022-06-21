"""Functions taking a SQL script as argument"""
import re

def get_sql_code(path: str) -> str:
    "Returns the sql script of the Databticks schema file"

    with open(path, "r") as file:
        return file.read()

def clean_sql_code(s: str) -> str:
    # clean the initial script
    special_chars = (
        {"find": r"\n", "replace": ""}, #remove break line to use regular expressions
        {"find": r"decimal\(.*?\)", "replace": "decimal"} #remove option for decimal to split with comma
    )
    for d in special_chars:
        s = re.sub(d["find"], d["replace"], s)
    
    # deal with structures
    structs = dict(
        zip(
            re.findall(r"(\w+)\sSTRUCT", s), #find structure names     
            re.findall(r"STRUCT\<(.*?)\>", s) #find columns in structure
        )
    )
    for k, v in structs.items():
        cols = v.split(",")
        new_cols = []
        for c in cols:
            new_cols.append(k + "." + c.strip())
        # s = re.sub(k+r" STRUCT\<(.*?)\>,?", ','.join(new_cols) + ",", s)
        s = re.sub(k+r" STRUCT\<(.*?)\>", ','.join(new_cols), s)
    # return s[:-1] if s[-1]=="," else s #remove trailing comma
    return s

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

    # dates and timestamp
    is_timestamp = (type == "timestamp") | (type == "date")
    dimension = "dimension_group" if is_timestamp else "dimension"
    timeframes = "[time, date, week, month, quarter, year]" if type == "timestamp" else "[date]"

    #struct object
    group_label = None
    if "." in name:
        group_label = name.split(".")[0]
        name = name.split(".")[1]

    s1 = f"\n\t{dimension}: {name} {{\n\t\tdescription: {comment}\n"
    s2 = f"\t\tgroup_label: {group_label}\n" if group_label else ""
    s3 = f"\t\ttype: {replace_hive_types(type)}\n"
    s4 = f"\t\ttimeframes: {timeframes}\n" if is_timestamp else""
    s5 = f"\t\tsql: {{$TABLE}}.{name};;\n\t}}"
    
    return s1+s2+s3+s4+s5