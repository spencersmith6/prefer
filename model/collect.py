from scipy.stats import bernoulli
from db_admin.sql_helper import getConn, getCur
from utils.db_utils import *
import exploit
import explore
import numpy as np
import pandas as pd


def create_etsy_item_dict(item_cols):
    """Create item object from data return from query"""
    item = {'id': item_cols[0],
            'title': item_cols[1],
            'link': item_cols[2],
            'im_url': item_cols[3],
            'price': item_cols[4],
            'category': item_cols[5]}
    return item

def get_item_sub_500(user_id, next_to_rate):

    conn = getConn('db_admin/creds.json')
    cur = getCur(conn)
    query = "SELECT * from etsy_items WHERE id = '{}' LIMIT 1;".format(next_to_rate)
    cur.execute(query)
    item = cur.fetchone()

    # TODO This is cheating, this means it sets the item as reviewed regardless of if the user actually swipes on it or not. Fix it.

    p = .5
    skip = 1 + bernoulli.rvs(p, size=1)[0]
    query = "UPDATE user_meta SET num_reviews = num_reviews + {} WHERE user_meta.user_id = '{}';".format(skip, user_id)
    cur.execute(query)
    conn.commit()
    cur.close()
    return item


def get_item_over_500(user_id):
    conn = getConn('db_admin/creds.json')
    cur = getCur(conn)
    query = """ SELECT etsy_items.asin, etsy_items.title, etsy_items.link, etsy_items.imurl, etsy_items.price, etsy_items.category, A.overall as overall
                FROM etsy_items LEFT JOIN(
                    SELECT asin, reviewerid, overall
                    FROM etsy_reviews where reviewerid = '{}') AS A
                ON etsy_items.asin = A.asin
                WHERE A.overall is null ORDER BY id LIMIT 1;""".format(user_id)
    cur.execute(query)
    item = cur.fetchone()

    # TODO This is cheating, this means it sets the item as reviewed regardless of if the user actually swipes on it or not. Fix it.

    skip = 1
    query = "UPDATE user_meta SET num_reviews = num_reviews + {} WHERE user_meta.user_id = '{}';".format(skip, user_id)
    cur.execute(query)
    conn.commit()
    cur.close()
    return item


def get_next_item(user_id):
    # TODO: Give next item id in list
    conn = getConn('db_admin/creds.json')
    cur = getCur(conn)
    query = "SELECT num_reviews from user_meta WHERE user_id = '{}'".format(user_id)
    cur.execute(query)
    next_to_rate = int(cur.fetchone()[0]) + 1
    print 'next to rate: %i' %next_to_rate


    if next_to_rate < 500:
        item = get_item_sub_500(user_id, next_to_rate)
    else:
        item = get_item_over_500(user_id)

    item_dict = create_etsy_item_dict(item)
    
    return item_dict
