import psycopg2
import os.path
import json
import re

def writeToDB(cur, conn, query):
    cur.execute(query)
    conn.commit()
    return None


def checkTables(cur):
    meta_query = "SELECT COUNT(*) FROM information_schema.tables WHERE table_name LIKE 'item_meta';"
    review_query = "SELECT COUNT(*) FROM information_schema.tables WHERE table_name LIKE 'reviews';"
    results = []
    for query in [meta_query, review_query]:
        try:
            cur.execute(query)
            results.append(True)
        except:
            results.append(False)
    return results


def buildMetaTable(cur, conn):
    query = """CREATE TABLE IF NOT EXISTS item_meta (
asin  VARCHAR,
title VARCHAR,
description VARCHAR,
price VARCHAR,
brand VARCHAR,
imurl VARCHAR
);"""
    writeToDB(cur, conn, query)
    return None


def buildReviewTable(cur, conn):
    query = """CREATE TABLE IF NOT EXISTS reviews (
reviewerid VARCHAR,
asin VARCHAR,
overall VARCHAR
);"""
    writeToDB(cur, conn, query)
    return None


def buildTables(cur, conn):
    buildMetaTable(cur, conn)
    buildReviewTable(cur, conn)
    return None


def buildMetaSQLQuery(datapath):
    # I'm sorry this is so ugly. I don't know what a better way to do this is...
    filename = 'meta_insert.txt'
    # If the Meta insert query is not already built, build it
    if not os.path.isfile(datapath + filename):
        with open(datapath+'metadata.strict.json') as f:
            strict_json = f.readlines()

        meta_insert_query_part_one = """with meta_json (doc) as (
           values
        ('["""

        meta_insert_query_part_two = """]'
        ::json)
        )
        insert
        into
        item_meta(asin, title, description, price, brand, imurl)
        select
        p. *
        from meta_json l
            cross join lateral json_populate_recordset(null::item_meta, doc) as p;"""

        # Need to remove all apostrophes to play nice with psql
        # Also need to take to lower the "imUrl" key to play nice with psql syntax
        # Taken from http://stackoverflow.com/questions/6116978/python-replace-multiple-strings
        rep = {"'": "", "imUrl": "imurl"}  # Define desired replacements here
        # Use these three lines to do the replacement
        rep = dict((re.escape(k), v) for k, v in rep.iteritems())
        pattern = re.compile("|".join(rep.keys()))
        clean_strict_json = pattern.sub(lambda x: rep[re.escape(x.group(0))], ','.join(strict_json))

        meta_insert_query = meta_insert_query_part_one + clean_strict_json + meta_insert_query_part_two
        # Store the full query as a textfile for backup
        with open(datapath+filename, 'w') as f:
            f.write(meta_insert_query)
    else:
        with open(datapath + filename, ) as f:
            meta_insert_query = f.read()

    return meta_insert_query


def buildReviewSQLQuery(datapath):
    # I'm sorry this is so ugly. I don't know what a better way to do this is...
    filename = 'kcore_5_insert.txt'
    # If the Meta insert query is not already built, build it
    if not os.path.isfile(datapath + filename):
        with open(datapath+'kcore_5.strict.json') as f:
            strict_json = f.readlines()

        review_insert_query_part_one = """with review_json (doc) as (
           values
        ('["""

        review_insert_query_part_two = """]'
        ::json)
        )
        insert
        into
        reviews(reviewerid, asin, overall)
        select
        p. *
        from review_json l
            cross join lateral json_populate_recordset(null::item_meta, doc) as p;"""

        # Need to take to lower the "reviewerID" key to play nice with psql syntax
        clean_strict_json = ','.join(strict_json).replace("reviewerID", "reviewerid")

        review_insert_query = review_insert_query_part_one + clean_strict_json + review_insert_query_part_two
        # Store the full query as a textfile for backup
        with open(datapath+filename, 'w') as f:
            f.write(review_insert_query)
    else:
        with open(datapath + filename, ) as f:
            review_insert_query = f.read()

    return review_insert_query

