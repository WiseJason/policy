import jieba
from pymongo import MongoClient
from redis import StrictRedis
import jieba.posseg as pseg

r=StrictRedis(host="localhost",port=6379,decode_responses=True)
client=MongoClient(host="localhost",port=27017)
db=client["发改委"]
collection=db["国策2-详情页"]
datas=collection.find({},{"title":1,"summary":1,"text":1,"_id":0})


def add_data(text):
    words = pseg.cut(text)
    for word, flag in words:
        if flag=="ns" or flag=="n" or flag=="nt":
            r.sadd("ns",word)
        elif flag=="v":
            r.sadd("v",word)


for data in datas:
    add_data(data["title"])
    add_data(data["summary"])
    add_data(data["text"])
    # break