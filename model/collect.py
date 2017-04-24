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

def get_next_item(user_id):
    # TODO: Give next item id in list
    conn = getConn('db_admin/creds.json')
    cur = getCur(conn)
    query = "SELECT num_reviews from user_meta WHERE user_id = '{}'""".format(user_id)
    cur.execute(query)
    next_to_rate = int(cur.fetchone()[0]) + 1

    conn = getConn('db_admin/creds.json')
    cur = getCur(conn)
    query = "SELECT * from etsy_items WHERE id = '{}' LIMIT 1;".format(next_to_rate)
    cur.execute(query)
    item = cur.fetchone()
    #TODO This is cheating, this means it sets the item as reviewed regardless of if the user actually swipes on it or not. Fix it.
    query = "UPDATE user_meta SET num_reviews = num_reviews + 1 WHERE user_meta.user_id = '{}';".format(user_id)
    cur.execute(query)
    conn.commit()
    item_dict = create_etsy_item_dict(item)
    cur.close()

    return item_dict