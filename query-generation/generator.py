from SPARQLWrapper import SPARQLWrapper, JSON
import sys
from os.path import exists, isfile
import time
import argparse
import random

# Entry point for query generation of queries with small intermediate results sets
# It uses a base query file and modifies its predicates.
def gen_empty_queries(base_query_file, endpoint):
    sparql = SPARQLWrapper(endpoint)
    sparql.setTimeout(10000)
    sparql.setReturnFormat(JSON)
    queries = get_queries(base_query_file)
    new_queries = list()
    top_preds = top_predicates(sparql)

    for query in queries:
        new_queries.append(sub_predicate(query, top_preds))

    return new_queries

# Computes the top 100 most used Wikidata predicates that are not rdf:type and rdf:label
def top_predicates(sparql):
    top = list()
    forbidden = ["http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
                 "http://www.w3.org/2000/01/rdf-schema#label",
                 "http://www.w3.org/2004/02/skos/core#altLabel",
                 "http://www.w3.org/ns/prov#wasDerivedFrom",
                 "http://schema.org/description",
                 "http://wikiba.se/ontology#rank",
                 "http://schema.org/version",
                 "http://schema.org/isPartOf",
                 "http://schema.org/name",
                 "http://schema.org/inLanguage",
                 "http://schema.org/abouthttp://schema.org/about",
                 "http://wikiba.se/ontology#quantityNormalized",
                 "http://wikiba.se/ontology#statements",
                 "http://wikiba.se/ontology#identifiers",
                 "http://wikiba.se/ontology#sitelinks"]

    query = "SELECT ?p (COUNT(?p) AS ?top_preds) WHERE { ?s ?p ?o } GROUP BY ?p ORDER BY DESC(?top_preds) LIMIT 200"
    results = exec_query(sparql, query)
    counter = 0

    for result in results:
        if (result["p"]["value"] not in forbidden):
            top.append(result["p"]["value"])
            counter += 1

        if (counter == 100):
            break

    return top

# Returns list of indices of each URI in query
def uri_indices(query):
    indices = list()
    idx = 0

    while (idx < len(query)):
        if (query[idx] == '<'):
            start = idx

            while (idx < len(query)):
                if (query[idx] == '>'):
                    indices.append((start, idx))
                    break

                idx += 1

        idx += 1

    return indices

# Chooses a random predicate in the BGP to substitute with a random popular one.
def sub_predicate(query, sub_list):
    pred_indices = uri_indices(query)
    random_indices = pred_indices[random.randrange(0, len(pred_indices) - 1)]
    old_predicate = query[random_indices[0]:random_indices[1] + 1]
    new_predicate = sub_list[random.randrange(0, len(sub_list) - 1)]

    return query.replace(old_predicate, "<" + new_predicate + ">")

# Entry point for modified Leapfrog query generation
def gen_mod_queries(base_query_file, endpoint):
    sparql = SPARQLWrapper(endpoint)
    sparql.setTimeout(1200)
    sparql.setReturnFormat(JSON)
    queries = get_queries(base_query_file)
    new_queries = list()

    for query in queries:
        proj_query = count2proj(query)
        bindings = exec_query(sparql, proj_query)

        if (len(bindings) < 1):
            continue

        predicate_var_query = one_predicate2var(proj_query)
        predicate_var_query = predicate_var_query.replace("*", "(COUNT(*) AS ?count)")
        predicate_var_query = substitute_var(bindings[0], list(bindings[0].keys())[0], predicate_var_query)
        new_queries.append(predicate_var_query)
        time.sleep(1)

    return new_queries

# Returns list of queries in given file
def get_queries(file):
    queries = []

    with open(file, "r") as queries_file:
        for line in queries_file:
            queries.append(line.strip())

    return queries

# Changes COUNT aggregation for project for all variables in SELECT clause
def count2proj(query):
    if (not "COUNT" in query):
        return query

    return query.replace("(COUNT(*) AS ?count)", "*")

# Finds first predicate URI and substitutes it with a variable
# It assumes only predicates are URIs, subject and objects must be variables
def one_predicate2var(query):
    uri = query[query.find("<"):query.find(">") + 1]
    return query.replace(uri, "?p")

# Executes a query and returns the variable bindings
def exec_query(sparql, query):
    sparql.setReturnFormat(JSON)
    sparql.setQuery(query)
    return sparql.query().convert()["results"]["bindings"]

# Substitutes every occurence of variable in given binding with its value in the binding
def substitute_var(binding, var, query):
    return query.replace("?" + var, "<" + binding[var]["value"] + ">")

# Gets binding of a given variable
def get_var_bindings(bindings, var):
    var_bindings = list()

    for binding in bindings:
        var_bindings.append(binding[var])

    return var_bindings

# This script only works when only predicates are IRIs. Subjects and objects MUST be variables.
if __name__ == "__main__":
    parser = argparse.ArgumentParser("Query generation tool")
    parser.add_argument("file", metavar = 'File', type = str, nargs = 1, help = ".txt query file (one query per line)")
    parser.add_argument("type", metavar = 'Type', type = str, nargs = 1, help = "Type of file generation ([mod | empty])")

    args = parser.parse_args()
    query_file = args.file[0]
    type = args.type[0]
    endpoint = "http://localhost:3030/jena/sparql"

    if (type != "mod" and type != "empty"):
        print("Type must either be \'mod\' or \'empty\'")

    elif (not isfile(query_file)):
        print("\'" + query_file + "\' is not a file\n")

    elif (exists(query_file)):
        if (type == "mod"):
            queries = gen_mod_queries(query_file, endpoint)

        else:
            queries = gen_empty_queries(query_file, endpoint)

        for query in queries:
            print(query)

    else:
        print("File \'" + query_file + "\' does not exist\nContinuing\n")
