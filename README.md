# LookNice
Command line interface to help us migrate and format and LookML and Spark SQL code

## Installation
```$ pip install git+https://github.com/Le-David-ml/looknice.git```

## Commands
`fix` takes a Looker view file as argument and format the derived table SQL code
```
$ looknice fix <path_to_Looker_view_file>
```

`get-missing-descriptions` takes a Looker view file as argument and returns a list of Looker dimensions with a missing description
```
$ looknice get-missing-descriptions <path_to_Looker_view_file>
```

`write-lkml` writes the lookml code from the Databricks' SQL script
```
$ looknice write-lkml <path_to_databricks_sql_file>
```

`write-sql` writes the Databricks SQL script from the LookML view file
```
$ looknice write-sql <path_to_Looker_view_file>
```


