import os.path
import requests
import json
import gzip
import psycopg2
import argparse
import sql_helper


def downloadData(datapath, filenames):
    # File names for metadata and 5core data
    # For each file
    for filename in filenames:
        # If the file does not exist, download it.
        if not os.path.isfile(datapath+filename):
            url = 'http://snap.stanford.edu/data/amazon/productGraph/{}'.format(filename)
            r = requests.get(url)
            with open(datapath+filename, 'wb') as f:
                f.write(r.content)
    return None


# This function was taken from http://jmcauley.ucsd.edu/data/amazon/links.html
def parse(path):
    g = gzip.open(path, 'r')
    for l in g:
        yield json.dumps(eval(l))


# This function was taken from http://jmcauley.ucsd.edu/data/amazon/links.html
def write_strict_json(datapath, infile):
    # Build outfile name
    outfile = "{}.strict.json".format(infile.split('.')[0])
    # If outfile does not already exist
    if not os.path.isfile(datapath + outfile):
        # Write strict json to outfile
        with open(datapath+outfile, 'w') as f:
            for l in parse(datapath+infile):
                f.write(l + '\n')
            f.close()
    return None


def getPsqlCur(creds):
    try:
        # Connect to the database
        conn = psycopg2.connect("dbname='{}' user='{}' host='{}' password='{}'".format(
            creds['dbname'], creds['user'], creds['host'], creds['password']))
    except:
        print "I am unable to connect to the database"
        return None
    # Return the connection and the cursor
    cur = conn.cursor()
    return conn, cur


def main(args):
    filenames = ['metadata.json.gz', 'kcore_5.json.gz']

    print "Getting Credentials"
    datapath = args.datapath
    with open(datapath + 'creds.json') as f:
        creds = json.loads(f.read())

    print "Downloading Data"
    downloaded = downloadData(datapath, filenames)

    print "Writing Strict JSON"
    strictly_written = [write_strict_json(datapath, i) for i in filenames]

    print "Connecting to Database"
    conn, cur = getPsqlCur(creds)

    print "Checking for Existing Tables"
    tables_exist = sql_helper.checkTables(cur)

    if sum(tables_exist) != 2:

        print 'Tables Do Not Exist\nBuilding Tables'
        builtTable = sql_helper.buildTables(cur, conn)

        if not tables_exist[0]:
            print "Building Metadata Insert Query"
            meta_insert_query = sql_helper.buildMetaSQLQuery(datapath)
            print "Inserting Metadata"
            meta_inserted = sql_helper.writeToDB(cur, conn, meta_insert_query)

        if not tables_exist[1]:
            print "Building Review Insert Query"
            review_insert_query = sql_helper.buildMetaSQLQuery(datapath)
            print "Inserting Reviews"
            review_inserted = sql_helper.writeToDB(cur, conn, review_insert_query)

    else:
        print """Both Tables Already Exist
                    Please reevaluate your life or manually drop both tables and rerun this script."""

    print 'Closing Connection'
    conn.close()
    cur.close()
    print 'Finished'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-datapath", help="Path to Data Directory")
    args = parser.parse_args()
    main(args)