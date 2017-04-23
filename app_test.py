import unittest
import httplib
import pandas as pd
import urllib

import uuid
from db_admin.sql_helper import getConn, getCur
from utils.db_utils import get_item_by_id, write_new_user_to_db, write_new_rating_to_db, check_if_user_in_db
import model.explore_or_exploit
import model.explore
import model.exploit


SERVER = 'ec2-52-26-197-182.us-west-2.compute.amazonaws.com:5000'


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
    conn = getConn('db_admin/creds.json')
    user_reviews = pd.read_sql(query, conn)
    return user_reviews


if __name__ == '__main__':
    print "************************************************"
    print "Test of Prefer at ", SERVER
    print "created by Nick Levitt, Kelsey MacMillan and Spencer Smith"
    print "************************************************"
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
    print "******** User Preferences for User 'kjmacmil' **********"
    print " "
    prefs = get_user_prefs('kjmacmil')
    print prefs
    print " "
