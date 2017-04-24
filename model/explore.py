from db_admin.sql_helper import getConn, getCur
from utils.db_utils import *

def get_new_item_id(user_reviews):
    # TODO: explore in a more intelligent way, instead of getting random item
    conn = getConn('db_admin/creds.json')
    cur = getCur(conn)
    query = "SELECT * from item_meta ORDER BY random() LIMIT 1;"
    cur.execute(query)
    item_cols = cur.fetchone()
    item = create_item_dict(item_cols)
    cur.close()
    return item
