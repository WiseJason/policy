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
    data=collention.find({},{"title":1,"summary":1,"_id":0})
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
        "_index":"polycies",
     "_type":"doc",
     "_id":idx,
        "_source":{
            # 需要提取的字段
            "title":item.get('title'),
            "summary":item.get('summary')
        }
    }
    actions.append(i)
start = time.time()

time.sleep(10)
helpers.bulk(es, actions)

end = time.time() - start
print(end)



# import os
# import time
# import random
#
# elasticsearch = r'D:\elastic\elasticsearch-7.4.0\bin\elasticsearch.bat'
# kibana = r'D:\elastic\kibana-7.4.0-windows-x86_64\bin\kibana.bat'
# def progress_bar(item):
#     for i in range(11, 0, -1):
#         if item == 'kibana':
#             time.sleep(random.random() + 0.8)
#         else:
#             time.sleep(random.random() + 0.4)
#         res = '\r%s正在加载：%s %s%%\n' % (item, ('████' * (12 - i)), (11 - i) * 10) if i == 1 else '\r%s正在加载：%s %s%%' % (
#         item,
#         (
#             '████' * (
#             12 - i)),
#         (11 - i) * 10)
#         print('\033[31m%s\033[0m' % res, end='')
#
#
# def run():
#     for item in [(elasticsearch, 'elasticsearch'), (kibana, 'kibana')]:
#         os.system('start %s' % item[0])
#         progress_bar(item[1])
#         time.sleep(10)
#
#
#
# run()



# @app.route("/search",methods=["get","post"])
# def search():
#     search = request.form.get("search")
#     if search:
#         body = {
#             "query": {
#                 "bool": {
#                     "should": [
#                         {
#                             "match": {
#                                 "title": search
#                             }
#                         }, {
#                             "match": {
#                                 "summary": search
#                             }}]
#                 }
#             },
#         }
#
#         res = es.search(index="polycies", body=body,filter_path=["hits"])
#         count=res.get("hits").get("total").get("value")
#         if count==0:
#             return render_template("no_search.html")
#         else:
#             body = {
#                 "query": {
#                     "bool": {
#                         "should": [
#                             {
#                                 "match": {
#                                     "title": search
#                                 }
#                             }, {
#                                 "match": {
#                                     "summary": search
#                                 }}]
#                     }
#                 },
#                 "highlight": {
#                     "pre_tags": '<b style="color:red">',
#                     "post_tags": "</b>",
#                     "fields": {
#                         "title": {},
#                         "summary": {}
#                     }
#                 }
#             }
#             res = es.search(index="polycies", body=body,filter_path=["hits.hits"])
#             items=res.get("hits").get("hits")
#         return render_template("seach.html",items=items)
#     else:
#         return render_template("index.html")



# @app.route("/search/")
# def search():
#     search = request.args.get("search")
#     if search:
#         body = {
#             "query": {
#                 "bool": {
#                     "should": [
#                         {
#                             "match": {
#                                 "title": search
#                             }
#                         }, {
#                             "match": {
#                                 "summary": search
#                             }}]
#                 }
#             },
#         }
#
#         res = es.search(index="polycies", body=body, filter_path=["hits"])
#         count = res.get("hits").get("total").get("value")
#         g.count=count
#         if count == 0:
#             return render_template("no_search.html")
#         else:
#             body = {
#                 "query": {
#                     "bool": {
#                         "should": [
#                             {
#                                 "match": {
#                                     "title": search
#                                 }
#                             }, {
#                                 "match": {
#                                     "summary": search
#                                 }}]
#                     }
#                 },
#                 "highlight": {
#                     "pre_tags": '<b style="color:red">',
#                     "post_tags": "</b>",
#                     "fields": {
#                         "title": {},
#                         "summary": {}
#                     }
#                 }
#             }
#             res = es.search(index="polycies", body=body, filter_path=["hits.hits"])
#             items = res.get("hits").get("hits")
#             g.search=search
#         return render_template("seach.html", items=items)
#     else:
#         return render_template("index.html")


# @app.route("/search/<int:page>")
# def turn_page():
#     page_num = request.args.get("page")
#     if page_num>g.count/10:
#         body = {
#             "query": {
#                 "bool": {
#                     "should": [
#                         {
#                 "fields": {
#                     "title": {},
#                             "match": {
#                                 "title": g.search
#                             }
#                         }, {
#                             "match": {
#                                 "summary": g.search
#                             }}]
#                 }
#             },
#             "size":10,
#             "from":(page_num-1)*10,
#             "highlight": {
#                 "pre_tags": '<b style="color:red">',
#                 "post_tags": "</b>",
#                     "summary": {}
#                 }
#             }
#         }
#         res = es.search(index="polycies", body=body, filter_path=["hits.hits"])
#         items = res.get("hits").get("hits")
#         start=(page_num-1)*10
#         end=start+10
#         total=g.count
#         pagination=Pagination(bs_version=3,page=page_num,total=total)
#         context={
#             "items":items,
#             "pagination":pagination
#         }
#         return render_template("turn.html",**context)


# if page_num > g.count / 10:
#     body = {
#         "query": {
#             "bool": {
#                 "should": [
#                     {
#                         "match": {
#                             "title": g.search
#                         }
#                     }, {
#                         "match": {
#                             "summary": g.search
#                         }}]
#             }
#         },
#         "size": 10,
#         "from": (page_num - 1) * 10,
#         "highlight": {
#             "pre_tags": '<b style="color:red">',
#             "post_tags": "</b>",
#             "fields": {
#                 "title": {},
#                 "summary": {}
#             }
#         }
#     }
#     res = es.search(index="polycies", body=body, filter_path=["hits.hits"])
#     items = res.get("hits").get("hits")
#     start = (page_num - 1) * 10
#     end = start + 10
#     total = g.count
#     pagination = Pagination(bs_version=3, page=page_num, total=total)
#     context = {
#         "items": items,
#         "pagination": pagination
#     }
#     return render_template("turn.html", **context)