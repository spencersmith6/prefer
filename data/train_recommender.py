import pandas as pd
import numpy as np
from sklearn import preprocessing
from sklearn.decomposition import NMF
import pickle
from db_admin.sql_helper import getConn

# import reviews data
query = """SELECT * FROM etsy_reviews"""
conn = getConn('../db_admin/creds.json')
df_reviews = pd.read_sql(query, conn)
df_reviews = df_reviews.rename(index=str, columns={"reviewerid": "user", "asin":"item", "overall":"rating"})

# import all other items
query = """SELECT asin FROM etsy_items"""
df_items = pd.read_sql(query, conn)
df_items = df_items.rename(index=str, columns={"asin":"item"})

# create a "no_rating" user and assign all zeros
df_items['user'] = pd.Series(['no_rating']*len(df_items['item']), index=df_items.index)
df_items['rating'] = pd.Series([0.5]*len(df_items['item']), index=df_items.index)

# concatenate data frames
df = pd.concat([df_reviews, df_items], axis=0, ignore_index=True)

print df

# label encoding
le_item = preprocessing.LabelEncoder()
item_inds = le_item.fit_transform(df['item'])

le_user= preprocessing.LabelEncoder()
user_inds = le_user.fit_transform(df['user'])

# create user item matrix
rating = np.array(df['rating'])
user_item_matrix = np.zeros((len(set(user_inds)), len(set(item_inds))))

for u, i, r in zip(user_inds, item_inds, rating):
    user_item_matrix[u, i] = r

# train model
nmf_model = NMF(50)
nmf_model.fit(user_item_matrix)

# save models
with open('nmf.pkl', 'wb') as fid:
    pickle.dump(nmf_model, fid)

with open('item_encoder.pkl', 'wb') as fid:
    pickle.dump(le_item, fid)