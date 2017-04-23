import pandas as pd
import numpy as np
from sklearn import preprocessing
from sklearn.decomposition import NMF
import pickle
from db_admin.sql_helper import getConn

# import reviews data
query = """SELECT * FROM reviews"""
conn = getConn('db_admin/creds.json')
df = pd.read_sql(query, conn)
df = df.rename(index=str, columns={"reviewerid": "user", "asin":"item", "overall":"rating"})


def transform_rating(x):
    if x < 4.0:
        return 0.0
    else:
        return 1.0

df['rating_transformed'] = df['rating'].apply(transform_rating)

# label encoding
le_item = preprocessing.LabelEncoder()
item_inds = le_item.fit_transform(df['item'])

le_user= preprocessing.LabelEncoder()
user_inds = le_user.fit_transform(df['user'])

# create user item matrix
rating = np.array(df['rating_transformed'])
user_item_matrix = np.zeros((len(set(user_inds)), len(set(item_inds))))

for u, i, r in zip(user_inds, item_inds, rating):
    user_item_matrix[u, i] = r

# train model
nmf_model = NMF(50)
nmf_model.fit(user_item_matrix)

# save models
with open('data/nmf.pkl', 'wb') as fid:
    pickle.dump(nmf_model, fid)

with open('data/item_encoder.pkl', 'wb') as fid:
    pickle.dump(le_item, fid)





