# LookNice
Command line interface to help migrate Databricks' schemas to LookML.
 
## Installation
```$ pip install git+https://github.com/LeDavid17/looknice.git```

## Commands
-`write-lkml` writes the lookml code from the Databricks' SQL script
```
$ looknice write-lkml <path_to_databricks_sql_file>
```

## What it does

Input:
```
CREATE TABLE IF NOT EXISTS schema_name.table_name(
    user_id string COMMENT 'Unique customer identifier',
    created_at timestamp 'Action timestamp',
    tiers STRUCT<
        tier1 string,
        tier2 string,
        tier3 string
    > COMMENT "Description of tiers columns",
    status COMMENT 'Desciption of status column',
    type string
)
USING delta
location 'path_to_the_dbfs_file';
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true');
```

Output:
```
view: table_name{
        sql_table_name: schema_name.table_name;;

        dimension: user_id {
                description: "Unique customer identifier"
                type: string
                sql: ${TABLE}.user_id;;
        }

        dimension_group: created_at {
                description: "<TODO>"
                type: time
                timeframes: [time, date, week, month, quarter, year]
                sql: ${TABLE}.created_at;;
        }

        dimension: tier1 {
                description: "<TODO>"
                group_label: tiers
                type: string
                sql: ${TABLE}.tier1;;
        }

        dimension: tier2 {
                description: "<TODO>"
                group_label: tiers
                type: string
                sql: ${TABLE}.tier2;;
        }

        dimension: tier3 {
                description: "Description of tiers columns (see README.md)"
                group_label: tiers
                type: string
                sql: ${TABLE}.tier3;;
        }

        dimension: status {
                description: "Desciption of status column"
                type: COMMENT
                sql: ${TABLE}.status;;
        }

        dimension: type {
                description: "<TODO>"
                type: string
                sql: ${TABLE}.type;;
        }
}


***ALERT***
The following dimensions are missing a description:
['created_at', 'tiers.tier1', 'tiers.tier2', 'type']
```

## Known Limitations
- With views, the tool can't infer the dimension types. Remember to change time dimensions to dimension_group.
- With [STRUCT type](https://docs.databricks.com/sql/language-manual/data-types/struct-type.html), the description, if any, is only assign to the last element of the structure.
