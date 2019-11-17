import jieba
from pymongo import MongoClient
from redis import StrictRedis
import jieba.posseg as pseg

r=StrictRedis(host="localhost",port=6379,decode_responses=True)
client=MongoClient(host="localhost",port=27017)
db=client["发改委"]
collection=db["国策1-详情页"]
datas=collection.find({},{"content":1,"_id":0})

def add_data(text):
    words = pseg.cut(text)
    for word, flag in words:
        if flag in ["n","ns","nsf","nt","nz","nl","ng","v","vd","vn"]:
            r.sadd("n",word)

print(datas)
print(datas.count())

for data in datas:
    print(data)
    import time
    a=time.time()
    add_data(data["content"])
    print(time.time()-a)
#     # break