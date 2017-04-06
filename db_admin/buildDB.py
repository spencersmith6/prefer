import os.path
import requests
import json
import gzip
import psycopg2
import argparse
import sql_helper


def downloadData(datapath, filenames):
    """
    This will automatically download the data in gzip form if it does not yet exist in the datapath
    :param datapath: Full path to directory containing data
    :type datapath: String
    :param filenames: Name of files to download
    :type filenames: Array of strings
    :return: None, downloads data and returns None
    """
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
    """
    This parses a gzipped file
    :param path: Path to the file
    :type path: String
    :return: Yields the evaluations
    """
    g = gzip.open(path, 'r')
    for l in g:
        yield eval(l)


# This function was taken from http://jmcauley.ucsd.edu/data/amazon/links.html
def write_strict_meta_json(datapath, infile):
    """
    This function converts the Amazon meta  data to strict JSON.
    We need this to be able to write the json out to the PostgreSQL table later
    :param datapath: Full path to directory containing data
    :type datapath: String
    :param infile: The non-strict json file name, must exist within the datapath
    :type infile: String
    :return: None. Writes out the strict json file
    """
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
    """
    This function converts the Amazon review  data to strict JSON.
    We need this to be able to write the json out to the PostgreSQL table later
    :param datapath: Full path to directory containing data
    :type datapath: String
    :param infile: The non-strict json file name, must exist within the datapath
    :type infile: String
    :return: None. Writes out the strict json file
    """

    # Build outfile name
    outfile = "{}.strict.json".format(infile.split('.')[0])
    missing_count = 0
    # If outfile does not already exist
    if not os.path.isfile(datapath + outfile):
        # Write strict json to outfile
        with open(datapath+outfile, 'w') as f:
            for tmp in parse(datapath+infile):
                try:
                    # Filter out only the relevant key-value pairs
                    filtered_json = {"reviewerid": tmp['reviewerID'], "asin": tmp["asin"], "overall": str(tmp['overall'])}
                    f.write(json.dumps(filtered_json) + '\n')
                except KeyError:
                    missing_count += 1
            f.close()
    print "Build Review Strict JSON: {} Missing Entries".format(missing_count)
    return None


def main(args):
    """
    This runs the entire pipeline to build out the database, minus inserting the data to the PostgreSQL tables.
    :param args: Arguments passed to the scripts
    :type args: ArgParse Object
    :return: Nothing, writes out many files and prints out status updates
    """

    # You can change these to the .gz paths for any of the datasets within the Amazon review data.
    filenames = ['meta_Home_and_Kitchen.json.gz', 'reviews_Home_and_Kitchen_5.json.gz']

    # Reads in PostgreSQL credentials
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

    # If not all tables exist, try to build them.
    if sum(tables_exist) != 3:

        print 'Tables Do Not Exist\nBuilding Tables'
        builtTable = sql_helper.buildTables(conn)

        if not tables_exist[0]:
            print "Building Metadata Queries"
            meta_inserted = sql_helper.buildMetaQueries(datapath, 'meta_Home_and_Kitchen.strict.json')

        if not tables_exist[1]:
            print "Building Review Insert Query"
            review_inserted = sql_helper.buildReviewQueries(datapath, 'reviews_Home_and_Kitchen_5.strict.json')

    else:
        print """All Tables Already Exist
                    Please reevaluate your life or manually drop the tables and rerun this script."""

    print 'Closing Connection'
    conn.close()
    print 'Finished'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-datapath", help="Path to Data Directory")
    args = parser.parse_args()
    main(args)