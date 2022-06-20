This Python script generates a new query for every query passed.
Two types of queries can be generated: queries that return empty result sets or queries where the URI predicate in the first triple pattern in the graph pattern is substituted with a variable, and another variable in either the subject or object position in any triple pattern is chosen and substituted with a solution for that variable in all occurrences of that variable in the graph pattern.
For queries that return empty result sets, a list of the 100 most frequently used predicates in Wikidata are collected, as well as the 100 least used predicates. every predicate in an input query, except for the last predicate, are substituted with a popular predicate, and the last predicate is substituted with an unpopular one.

# How To

To run and generate both types of queries, build and run the Docker container, where `<QUERIES>` is the path to the folder of queries.
These queries are listed in .txt files, with one query per line.

```
docker build -t query_gen .
docker run --rm -v ${PWD}:/home/gen -v ${PWD}/../benchmark:/home/database -v <QUERIES>:/home/queries -d query_gen
```

The new queries will be added to a new folders in the current directory `queries/mod` and `queries/empty`.

`generator.py` generates a new query file from a passed .txt query file and outputs the result to stdout.
`make.sh` is simply a wrapper that takes a path to a folder of .txt files as argument. It outputs the results in a new folders `./queries/mod` and `./queries/empty`.
These .txt files are the query files, with one query per line.

## Example

To generate new queries for the query files in an example folder `some/example/dir`, run the following commands.
The new query files will be generated in the folder `queries`.

```
docker build -t query_gen .
docker run --rm -v ${PWD}:/home/gen -v {PWD}/../benchmark:/home/database -v some/example/dir:/home/queries -d query_gen
```

As an example, assume we have a file `ex_queries.txt` in the directory `some/example/dir` that contains the following two queries

```
SELECT (COUNT(*) AS ?c) WHERE { ?x1 wd:P1151> ?x2 . ?x2 wd:P155 ?x3 . ?x3 wd:P1204 ?x4 . ?x4 wd:P156 ?x1 }
SELECT * WHERE { ?x1 wd:P3373 ?x2 . ?x2 wd:P1080 ?x3 . ?x3 wd:P138 ?x4 . ?x1 wd:P1441 ?x4 }
```

We run the following commands

```
docker build -t query_gen .
docker run --rm -v ${PWD}:/home/gen -v {PWD}/../benchmark:/home/database -v some/example/dir:/home/queries -d query_gen
```

Now, a folder `queries` is created and it contains two folders `mod` and `empty` with a file `ex_queries.txt` each containing the two new queries

In `queries/mod`

```
SELECT (COUNT(*) AS ?c) WHERE { wd:Q315 ?p ?x2 . ?x2 wd:P155 ?x3 . ?x3 wd:P1204 ?x4 . ?x4 wd:P156 wd:Q315 }
SELECT * WHERE { ?x1 ?p wd:Q23 . wd:Q23 wd:P1080 ?x3 . ?x3 wd:P138 ?x4 . ?x1 wd:P1441 ?x4 }
```

In `queries/empty`

```
SELECT (COUNT(*) AS ?c) WHERE { ?x1 wd:P304> ?x2 . ?x2 wd:P356 ?x3 . ?x3 wd:P50 ?x4 . ?x4 wd:P4734 ?x1 }
SELECT * WHERE { ?x1 wd:P17 ?x2 . ?x2 wd:P3083 ?x3 . ?x3 wd:P921 ?x4 . ?x1 wd:P5231 ?x4 }
```
