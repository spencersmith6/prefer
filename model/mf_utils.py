import pandas as pd
from db_admin.sql_helper import getConn, getCur
import numpy as np

def get_user_reviews(user_id):
    query = """SELECT * FROM reviews WHERE reviewerid = {}""".format(user_id)
    conn = getConn('db_admin/creds.json')
    return pd.read_sql(query, conn), conn

def explore_exploit(user_id):
    user_reviews, conn = get_user_reviews(user_id)
    if len(user_reviews) < 10 | (np.random.rand() < 0.2):
        query = "SELECT asin from item_meta ORDER BY random() LIMIT 1;"
        cur = getCur(conn)
        cur.execute(query)
        item_id = cur.fetchone()[0]
        cur.close()
        return item_id
    else:
        exploit(user_reviews)