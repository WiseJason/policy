from pymongo import MongoClient
from elasticsearch import Elasticsearch,helpers
import datetime
import pandas as pd
import time

#es 语句
"""
PUT polycies2
{
  "mappings": {
    "doc": {
      "properties": {
        "title":{
          "type": "text",
          "analyzer": "ik-index",
          "search_analyzer": "ik-smart"
        },"summary":{
          "type": "text",
          "analyzer": "ik-index",
          "search_analyzer": "ik-smart"
        }
      }
    }
  }
  ,
  "settings": {
    "analysis": {
      "filter": {
        "local_synonym" : {
            "type" : "synonym",
            "synonyms_path" : "analysis/synonyms.txt"  
        }
      },
      "analyzer": {
        
             "jt_cn": {

      "type": "custom",

      "use_smart": "true",

      "tokenizer": "ik_smart",

      "filter": ["local_synonym"]
     },
        "ik-index": { 
          "type": "custom",
          "tokenizer": "ik_max_word",
          "filter": [
              "local_synonym"   
           ]
        },
        "ik-smart": {
          "type": "custom",
          "tokenizer": "ik_smart",
          "filter": [
              "local_synonym"
           ]
        }
      }
    }
  }
}
"""


"""
;overflow:hidden; text-overflow:ellipsis;
"""

# 一次同步的数据量，批量同步
syncCountPer = 10000

# Es 数据库地址
es_url = 'http://127.0.0.1:9200/'
es=Elasticsearch(es_url)
# mongodb 数据库地址
mongo_url="localhost"
port=27017
# mongod 需要同步的数据库名
DB = '发改委'
# mongod 需要同步的表名
COLLECTION = '20171120'

count = 0

client = MongoClient(mongo_url,port)
db_mongo = client[DB]

def get_data_from_mongo(db_mongo,collection_name):
    collention=db_mongo[collection_name]
    # print(collention.find_one())
    data=collention.find({},{"title":1,"summary":1,"source":1,"styleName":1,"levelName":1,"publishTime":1,"content":1,"id":1,"_id":0})
    # data=pd.DataFrame(list(collention.find({"title":1,"summary":1,"source":1,"styleName":1,"levelName":1,"publishTime":1,"text":1})))
    # data=data[["title","summary","source","styleName","levelName","publishTime","text"]]
    return data


data=get_data_from_mongo(db_mongo,"国策1-详情页")

def delid(x):
    del (x['_id'])
    return x

# data=map(lambda x:delid(x),data)
actions=[]
for idx,item in enumerate(data):
    print(idx)
    i={
        "_index":"polycies2",
     "_type":"doc",
     "_id":idx,
        "_source":{
            # 需要提取的字段
            "id":item.get("id"),
            "title":item.get('title'),
            "summary":item.get('summary'),
            "source": item.get('source'),
            "styleName": item.get('styleName'),
            "levelName": item.get('levelName'),
            "publishTime": item.get('publishTime'),
            "content": item.get('content')
        }
    }
    actions.append(i)
start = time.time()

time.sleep(10)
helpers.bulk(es, actions)

end = time.time() - start
print(end)

