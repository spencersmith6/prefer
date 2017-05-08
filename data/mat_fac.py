# from theano.sandbox import cuda
# cuda.use('gpu2')
#

import utils.utils; reload(utils)
from utils.utils import *

from __future__ import division, print_function
import pandas as pd
import os
from db_admin.sql_helper import getConn, getCur
import numpy as np

from keras.layers import Embedding, Flatten
from keras.engine import Input
from keras.regularizers import l2
from time import time



def embedding_input(name, n_in, n_out, reg):
    inp = Input(shape=(1,), dtype='int64', name=name)
    return inp, Embedding(n_in, n_out, input_length=1, W_regularizer=l2(reg))(inp)

def create_bias(inp, n_in):
    x = Embedding(n_in, 1, input_length=1)(inp)
    return Flatten()(x)

conn = getConn('db_admin/creds.json')
cur = getCur(conn)



st = time()
query = 'SELECT reviewerid, reviews.asin AS asin, overall, title FROM reviews LEFT JOIN item_meta ON reviews.asin = item_meta.asin LIMIT 100000;'
dataDF = pd.read_sql(query, conn)
print(time()-st)




title_dict = dataDF.set_index('asin')['title'].to_dict()
ratingsDF = dataDF[['reviewerid', 'asin', 'overall']]

reviewer = ratingsDF.reviewerid.unique()
products = ratingsDF.asin.unique()

userID2inx = {uid:idx for idx, uid in enumerate(reviewer)}
productID2inx = {uid:idx for idx, uid in enumerate(products)}

ratingsDF.reviewerid = ratingsDF.reviewerid.apply(lambda x: userID2inx[x])
ratingsDF.asin = ratingsDF.asin.apply(lambda x: productID2inx[x])

nReviewers = ratingsDF.reviewerid.nunique()
nProducts = ratingsDF.asin.nunique()

n_factors = 50
np.random.seed = 42

choose = np.random.rand(len(ratingsDF)) < 0.8
train = ratingsDF[choose]
validate = ratingsDF[~choose]

reviewer_in, r = embedding_input('reviewer_in', nReviewers, n_factors, 1e-4)
product_in, p = embedding_input('product_in', nProducts, n_factors, 1e-4)

reviewer_bias = create_bias(reviewer_in, nReviewers)
product_bias = create_bias(product_in, nProducts)
print ('done')



x = merge([r, p], mode='dot')
x = Flatten()(x)
x = merge([x, reviewer_bias], mode='sum')
x = merge([x, product_bias], mode='sum')
model = Model([reviewer_in, product_in], x)
model.compile(Adam(0.001), loss='mse')

print('done')

model.fit([train.reviewerid, train.asin], train.overall, batch_size=64, nb_epoch=1,
          validation_data=([validate.reviewerid, validate.asin], validate.overall))
model.optimizer.lr=0.01
model.fit([train.reviewerid, train.asin], train.overall, batch_size=64, nb_epoch=6,
          validation_data=([validate.reviewerid, validate.asin], validate.overall))

model.optimizer.lr=0.001
model.fit([train.reviewerid, train.asin], train.overall, batch_size=64, nb_epoch=10,
          validation_data=([validate.reviewerid, validate.asin], validate.overall))
model.fit([train.reviewerid, train.asin], train.overall, batch_size=64, nb_epoch=5,
          validation_data=([validate.reviewerid, validate.asin], validate.overall))


model.predict([np.array([3]), np.array([6])])

# ## Analyze results

# To make the analysis of the factors more interesting, we'll restrict it to the top 2000 most popular movies.
g=ratingsDF.groupby('asin')['overall'].count()
topProducts=g.sort_values(ascending=False)[:2000]
topProducts = np.array(topProducts.index)

get_product_bias = Model(product_in, product_bias)
product_bias = get_product_bias.predict(topProducts)
product_ratings = [(b[0], title_dict[products[i]]) for i,b in zip(topProducts,product_bias)]


sorted(product_ratings, key=itemgetter(0))[:15]
sorted(product_ratings, key=itemgetter(0), reverse=True)[:15]

get_movie_emb = Model(product_in, p)
product_emb = np.squeeze(get_movie_emb.predict([topProducts]))
product_emb.shape


from sklearn.decomposition import PCA
pca = PCA(n_components=3)
movie_pca = pca.fit(product_emb.T).components_

fac0 = movie_pca[0]
product_comp = [(f, title_dict[products[i]]) for f,i in zip(fac0, topProducts)]
sorted(product_comp, key=itemgetter(0), reverse=True)[:10]
sorted(product_comp, key=itemgetter(0))[:10]

fac1 = movie_pca[1]
product_comp = [(f, title_dict[products[i]]) for f,i in zip(fac1, topProducts)]
sorted(product_comp, key=itemgetter(0), reverse=True)[:10]
sorted(product_comp, key=itemgetter(0))[:10]

start=50; end=100
X = fac0[start:end]
Y = fac1[start:end]
plt.figure(figsize=(15,15))
plt.scatter(X, Y)
for i, x, y in zip(topProducts[start:end], X, Y):
    plt.text(x,y,title_dict[products[i]], color=np.random.rand(3)*0.7, fontsize=14)
plt.show()