from redis import StrictRedis
from pymongo import MongoClient
from elasticsearch import Elasticsearch,helpers
import datetime
import pandas as pd
import time


# 一次同步的数据量，批量同步
syncCountPer = 10000

# Es 数据库地址
es_url = 'http://127.0.0.1:9200/'
es=Elasticsearch(es_url)


import pandas as pd
r=StrictRedis(host="localhost",port=6379,decode_responses=True)
n=r.smembers("n")
with open("vb.txt","a",encoding="utf8") as f:
    for i in n:
        f.write(i+"\r\n")
