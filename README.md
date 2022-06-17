# LookNice
Command line interface to help us migrate and format and LookML and Spark SQL code

## Commands
<fix>
Takes a Looker view file as argument and format the derived table SQL code
```
looknice fix <path_to_Looker_view_file>
```

#### get-missing-descriptions
Takes a Looker view file as argument and returns a list of Looker dimensions with a missing description
```
looknice get-missing-descriptions <path_to_Looker_view_file>
```

#### write-lkml
Write the lookml code from the Databricks' SQL script
```
looknice write-lkml <path_to_databricks_sql_file>
```

#### write-sql
Write the Databricks SQL script from the LookML view file
```
looknice write-sql <path_to_Looker_view_file>
```


