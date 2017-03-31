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
        yield eval(l)


# This function was taken from http://jmcauley.ucsd.edu/data/amazon/links.html
def write_strict_meta_json(datapath, infile):
    # Build outfile name
    outfile = "{}.strict.json".format(infile.split('.')[0])
    # If outfile does not already exist
    if not os.path.isfile(datapath + outfile):
        # Write strict json to outfile
        with open(datapath+outfile, 'w') as f:
            for l in parse(datapath+infile):
                f.write(json.dumps(l) + '\n')
            f.close()
    return None


def write_strict_review_json(datapath, infile):
    # Build outfile name
    outfile = "{}.strict.json".format(infile.split('.')[0])
    missing_count = 0
    # If outfile does not already exist
    if not os.path.isfile(datapath + outfile):
        # Write strict json to outfile
        with open(datapath+outfile, 'w') as f:
            for tmp in parse(datapath+infile):
                try:
                    filtered_json = {"reviewerid": tmp['reviewerID'], "asin": tmp["asin"], "overall": str(tmp['overall'])}
                    f.write(json.dumps(filtered_json) + '\n')
                except KeyError:
                    missing_count += 1
            f.close()
    print "Build Review Strict JSON: {} Missing Entries".format(missing_count)
    return None


def main(args):
    filenames = ['metadata.json.gz', 'kcore_5.json.gz']

    print "Getting Credentials"
    datapath = args.datapath
    with open(datapath + 'creds.json') as f:
        creds = json.loads(f.read())

    print "Downloading Data"
    downloaded = downloadData(datapath, filenames)

    print "Writing Strict JSON"
    strictly_written_meta = write_strict_meta_json(datapath, filenames[0])
    strictly_written_review = write_strict_review_json(datapath, filenames[1])

    print "Connecting to Database"
    conn = sql_helper.getPsqlConn(creds)

    print "Checking for Existing Tables"
    tables_exist = sql_helper.checkTables(conn)

    if sum(tables_exist) != 2:

        print 'Tables Do Not Exist\nBuilding Tables'
        builtTable = sql_helper.buildTables(conn)

        if not tables_exist[0]:
            print "Building Metadata Queries"
            meta_inserted = sql_helper.buildMetaQueries(conn, datapath, 'metadata.strict.json')

        if not tables_exist[1]:
            print "Building Review Insert Query"
            review_inserted = sql_helper.buildReviewQueries(conn, datapath, 'kcore_5.strict.json')

    else:
        print """Both Tables Already Exist
                    Please reevaluate your life or manually drop both tables and rerun this script."""

    print 'Closing Connection'
    conn.close()
    print 'Finished'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-datapath", help="Path to Data Directory")
    args = parser.parse_args()
    main(args)