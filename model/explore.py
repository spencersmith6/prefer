from db_admin.sql_helper import getConn, getCur


def get_new_item_id(user_reviews):
    # TODO: explore in a more intelligent way, instead of getting random item
    conn = getConn('db_admin/creds.json')
    cur = getCur(conn)
    query = "SELECT asin from etsy_items ORDER BY random() LIMIT 1;"
    cur.execute(query)
    item_id = cur.fetchone()[0]
    cur.close()
    return item_id