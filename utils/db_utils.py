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

        query = """ SELECT * FROM item_meta WHERE asin = '%s';""" %(item_id)
        cur.execute(query)

    item_cols = cur.fetchone()
    item = create_item_dict(item_cols)

    return item


def write_new_user_to_db(cur, user):
    """user is dict with fiels id, name, gender, age"""
    query = """ INSERT INTO user_meta (user_id, name, gender, age)
                VALUES ('%s', '%s', '%s', %s);
                """ %(user['id'], user['name'], user['gender'], user['age'])
    cur.execute(query)
    return None


def write_new_rating_to_db(cur, user_id, item_id, rating):
    """user is dict with fiels id, name, gender, age"""
    query = """ INSERT INTO reviews (reviewerid, asin, overall)
                VALUES ('%s', '%s', '%s');
                """ %(user_id, item_id, rating)
    cur.execute(query)
    return None

