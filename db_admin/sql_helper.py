import psycopg2
import os.path
import json
import re

def getPsqlConn(creds):
    try:
        # Connect to the database
        conn = psycopg2.connect("dbname='{}' user='{}' host='{}' password='{}'".format(
            creds['dbname'], creds['user'], creds['host'], creds['password']))
    except:
        print "I am unable to connect to the database"
        return None
    # Return the connection
    return conn


def getNamedCur(conn):
    return conn.cursor("my_cursor_name")


def getCur(conn):
    return conn.cursor()


def writeToDB(cur, conn, query):
    cur.execute(query)
    conn.commit()
    cur.close()
    return None


def checkTables(conn):
    meta_query = "SELECT COUNT(*) FROM information_schema.tables WHERE table_name LIKE 'item_meta';"
    review_query = "SELECT COUNT(*) FROM information_schema.tables WHERE table_name LIKE 'reviews';"
    results = []
    for query in [meta_query, review_query]:
        try:
            cur = getNamedCur(conn)
            cur.execute(query)
            if cur.fetchall()[0][0] == 1:
                results.append(True)
            else:
                results.append(False)
            cur.close()
        except:
            results.append(False)
    return results


def buildMetaTable(conn):
    query = """CREATE TABLE IF NOT EXISTS item_meta (
asin  VARCHAR,
title VARCHAR,
description VARCHAR,
price VARCHAR,
brand VARCHAR,
imurl VARCHAR
);"""
    writeToDB(getCur(conn), conn, query)
    return None


def buildReviewTable(conn):
    query = """CREATE TABLE IF NOT EXISTS reviews (
reviewerid VARCHAR,
asin VARCHAR,
overall VARCHAR
);"""
    writeToDB(getCur(conn), conn, query)
    return None


def buildTables(conn):
    buildMetaTable(conn)
    buildReviewTable(conn)
    return None


def buildMetaSQLQuery(strict_json):
    meta_insert_query_part_one = """with meta_json (doc) as (
       values
('["""

    meta_insert_query_part_two = """]'
::json)) insert into item_meta (asin, title, description, price, brand, imurl) select p.* from meta_json l cross join lateral json_populate_recordset(null::item_meta, doc) as p;"""

    # Need to remove all apostrophes to play nice with psql
    # Also need to take to lower the "imUrl" key to play nice with psql syntax
    # Taken from http://stackoverflow.com/questions/6116978/python-replace-multiple-strings
    rep = {"'": "", "imUrl": "imurl"}  # Define desired replacements here
    # Use these three lines to do the replacement
    rep = dict((re.escape(k), v) for k, v in rep.iteritems())
    pattern = re.compile("|".join(rep.keys()))
    clean_strict_json = pattern.sub(lambda x: rep[re.escape(x.group(0))], ','.join(strict_json))

    meta_insert_query = meta_insert_query_part_one + clean_strict_json + meta_insert_query_part_two

    return meta_insert_query


def buildReviewSQLQuery(strict_json):
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
    cross join lateral json_populate_recordset(null::reviews, doc) as p;"""

    # Need to take to lower the "reviewerID" key to play nice with psql syntax
    rep = {"'": "", "imUrl": "imurl"}  # Define desired replacements here
    # Use these three lines to do the replacement
    rep = dict((re.escape(k), v) for k, v in rep.iteritems())
    pattern = re.compile("|".join(rep.keys()))
    clean_strict_json = pattern.sub(lambda x: rep[re.escape(x.group(0))], ','.join(strict_json))

    review_insert_query = review_insert_query_part_one + clean_strict_json + review_insert_query_part_two
    return review_insert_query


def buildMetaQueries(datapath, meta_filename):
    fullpath = datapath+'meta_inserts'
    if os.path.isdir(fullpath):
        return None
    else:
        os.makedirs(fullpath)
        insert_lim = 100000
        cnt = 0
        with open(datapath+meta_filename) as f:
            strict_json = f.readlines()
        while (cnt+insert_lim) < (len(strict_json)-1):
            # query = buildMetaSQLQuery([i.strip() for i in strict_json[cnt:cnt+insert_lim]])
            query = buildMetaSQLQuery(strict_json[cnt:cnt+insert_lim])
            with open(datapath+'meta_inserts/meta_insert_{}'.format(cnt), 'w') as f:
                f.write(query)
            cnt += insert_lim

        query = buildMetaSQLQuery(strict_json[cnt:])
        with open(datapath + 'meta_inserts/meta_insert_{}'.format(cnt), 'w') as f:
            f.write(query)
        return None


def buildReviewQueries(datapath, review_filename):
    fullpath = datapath + 'review_inserts'
    if os.path.isdir(fullpath):
        return None
    else:
        insert_lim = 100000
        cnt = 0
        with open(datapath+review_filename) as f:
            strict_json = f.readlines()
        while (cnt+insert_lim) < (len(strict_json)-1):
            query = buildReviewSQLQuery(strict_json[cnt:cnt+insert_lim])
            with open(datapath+'review_inserts/review_insert_{}'.format(cnt), 'w') as f:
                f.write(query)
            cnt += insert_lim

        query = buildReviewSQLQuery(strict_json[cnt:])
        with open(datapath + 'review_inserts/review_insert_{}'.format(cnt), 'w') as f:
            f.write(query)
        return None