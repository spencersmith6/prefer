def create_item_dict(item_cols):
    """Create item object from data return from query"""
    item = {'id': item_cols[0],
            'title': item_cols[1],
            'description': item_cols[2],
            'price': item_cols[3],
            'brand': item_cols[4],
            'im_url': item_cols[5]}
    return item


def get_item_by_id(cur, item_id=None):
    """fetch item data based on item_id string"""

    if item_id is None:

        query = """SELECT * FROM item_meta LIMIT 1;"""
        cur.execute(query)

    else:

        query = """ SELECT * FROM item_meta WHERE asin = %s;"""
        cur.execute(query, (item_id,))

    item_cols = cur.fetchone()
    item = create_item_dict(item_cols)

    return item


def write_new_user_to_db(cur, user):
    """user is dict with fiels id, name, gender, age"""
    query = """ INSERT INTO user_meta (user_id, name, gender, age)
                VALUES (%s, %s, %s, %s);
                """
    cur.execute(query, (user['id'], user['name'], user['gender'], user['age']))
    return None


def write_new_rating_to_db(cur, user_id, item_id, rating, table):
    """user is dict with fiels id, name, gender, age"""
    query = """ INSERT INTO etsy_reviews (reviewerid, asin, overall)
                VALUES (%s, %s, %s);
                """
    cur.execute(query, (user_id, item_id, rating))
    return None


def check_if_user_in_db(cur, user_id):
    """fetch item data based on item_id string"""

    query = """ SELECT * FROM user_meta WHERE user_id = %s;"""
    cur.execute(query, (user_id,))

    if cur.fetchone():
        return True
    else:
        return False

