import unittest
import httplib
import pandas as pd

import uuid
from db_admin.sql_helper import getConn, getCur
from utils.db_utils import get_item_by_id, write_new_user_to_db, write_new_rating_to_db, check_if_user_in_db
import model.explore_or_exploit
import model.explore
import model.exploit


SERVER = 'ec2-52-26-197-182.us-west-2.compute.amazonaws.com:5000'


def get_prefer():
    out = dict()
    h = httplib.HTTPConnection(SERVER)
    h.request('GET', 'http://{}/prefer'.format(SERVER))
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
    print "******** Prefer Homepage **********"
    print " "
    print get_prefer()
    print " "
    print "******** Random Item ID **********"
    print model.explore.get_new_item_id(None)
    print " "
    print "******** User Preferences for User 'nplevitt' **********"
    print " "
    prefs = get_user_prefs('nplevitt')
    print prefs
    print " "
    print "******** Recommended Item for User 'nplevitt' **********"
    print " "
    print model.exploit.get_new_item_id(prefs)