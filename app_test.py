import httplib
import pandas as pd
import urllib
import psycopg2

CREDS = {"dbname": "prefer", "user": "prefer_msan", "host": "prefer.cnnbuuvumzbs.us-west-2.rds.amazonaws.com", "password": "Swiper_no_Swiping?"}
SERVER = 'ec2-52-26-197-182.us-west-2.compute.amazonaws.com:5000'


# Get DB connection using creds dict
def getConn():
    creds = CREDS
    return getPsqlConn(creds)


# This gets a default cursor for the DB
def getCur(conn):
    return conn.cursor()


def getPsqlConn(creds):
    """
    This gets a connection to the PostgreSQL database
    :param creds: Credentials for DB
    :type creds: Dictionary
    :return: pycopg2 connection to the DB
    """
    try:
        # Connect to the database
        conn = psycopg2.connect("dbname='{}' user='{}' host='{}' password='{}'".format(
            creds['dbname'], creds['user'], creds['host'], creds['password']))
    except:
        print "I am unable to connect to the database"
        return None
    # Return the connection
    return conn


def get_prefer():
    h = httplib.HTTPConnection(SERVER)
    h.request('GET', 'http://{}/prefer'.format(SERVER))
    resp = h.getresponse()
    out = resp.read()
    return out


def get_homepage():
    h = httplib.HTTPConnection(SERVER)
    h.request('GET', 'http://{}/'.format(SERVER))
    resp = h.getresponse()
    out = resp.read()
    return out


def post_login(username):
    h = httplib.HTTPConnection(SERVER)
    params = urllib.urlencode({'username': username})
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    h.request('POST', 'http://{}/post-login'.format(SERVER), params, headers)
    resp = h.getresponse()
    out = resp.read()
    return out


def get_next_prefer(preference, product_id, cookiename):
    h = httplib.HTTPConnection(SERVER)
    params = urllib.urlencode({'preference': preference, 'product_id': product_id})
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain",
               "Cookie": "userID=" + cookiename}
    h.request('POST', 'http://{}/next_prefer'.format(SERVER), params, headers)
    resp = h.getresponse()
    out = resp.read()
    return out


def get_user_prefs(id):
    query = """SELECT * FROM reviews WHERE reviewerid = '{}'""".format(id)
    conn = getConn()
    user_reviews = pd.read_sql(query, conn)
    return user_reviews


def hit_service(user_id):
    h = httplib.HTTPConnection(SERVER)
    h.request('GET', 'http://{}/get_new_item/{}'.format(SERVER, user_id))
    resp = h.getresponse()
    out = resp.read()
    return out



if __name__ == '__main__':
    print "************************************************"
    print "Test of Prefer at ", SERVER
    print "created by Nick Levitt, Kelsey MacMillan and Spencer Smith"
    print "************************************************"
    print " "
    print "******** Prefer Hit Service with Username to Return Item Recommendation **********"
    print " "
    print hit_service('kjmacmil')
    print " "
    print "******** Prefer Home Page **********"
    print " "
    print get_homepage()
    print " "
    print "******** Login with Valid Username **********"
    print " "
    print post_login('kjmacmil')
    print " "
    print "******** Login with Invalid Username **********"
    print " "
    print post_login('not_a_valid_name')
    print " "
    print "******** Prefer Landing Page **********"
    print " "
    print get_prefer()
    print " "
    print "******** Prefer Post Swipe **********"
    print " "
    print get_next_prefer('Like','B001AO2PXK',"testcookie")
    print " "
    print "******** Check that Cookie was Set **********"
    print " "
    prefs = get_user_prefs('testcookie')
    print prefs
    print " "
    print "******** User Preferences for User 'testcookie' **********"
    print " "
    prefs = get_user_prefs('testcookie')
    print prefs
    print " "
