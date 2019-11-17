from flask import Flask, render_template, jsonify, url_for, redirect, request, g, make_response, session
from elasticsearch import Elasticsearch
from flask_paginate import Pagination, get_page_parameter
from redis import Redis
from flask_session import Session
import redis
import os
import hashlib
import time
import json
from datetime import timedelta,date
from pymongo import MongoClient
import logging

handler=logging.FileHandler("search.log",encoding="utf-8")
handler.setLevel(logging.INFO)
logging_format=logging.Formatter('%(asctime)s - %(levelname)s -%(pathname)s- %(filename)s - %(funcName)s - %(lineno)s - %(message)s')


es_url = 'localhost:9200/'
es = Elasticsearch(es_url,timeout=60)
app = Flask(__name__)

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=1)

r = redis.StrictRedis(host="localhost", port=6379, db=0)


def decodechar(x):
    return x.decode("utf-8")


# ip+useragent+md5识别用户设置cookie
@app.route('/')
def index():
    ip = request.remote_addr
    useragent = request.headers.get('User-Agent')
    m = hashlib.md5()
    m.update(bytes(ip + useragent, encoding="utf-8"))
    cookie = m.hexdigest()
    search_history = r.zrange(name=cookie, start=0, end=-1, desc=True, withscores=True)
    search_history = [i[0].decode("utf8") for i in search_history]
    items = []
    for i in search_history:
        if i not in items:
            items.append(i)
    if len(items) > 10:
        items = items[0:10]
    context = {
        "items": items
    }
    response = make_response(render_template("index.html", **context))
    response.set_cookie("id", cookie)
    return response


@app.route("/search", methods=["get"])
def search():
    search = request.args.get("search")
    id = request.cookies.get("id")
    if search:
        r.zadd(id, {search: int(round(time.time() * 1000000))})
        page_num = request.args.get("page")
        if not page_num:
            page_num = 1
        page_num = int(page_num)
        body = {
            "query": {
                "bool": {
                    "should": [
                        {
                            "match": {
                                "title.spy": search
                            }
                        }, {
                            "match": {
                                "summary.spy": search
                            }},
                        {
                            "match": {
                                "title": search
                            }
                        }, {
                            "match": {
                                "summary": search
                            }},
                        {
                            "match_phrase": {
                                "title": {
                                    "query": search,
                                    "analyzer": "ik_sync_smart"
                                }
                            }
                        }, {
                            "match_phrase": {
                                "summary": {
                                    "query": search,
                                    "analyzer": "ik_sync_smart"
                                }
                            }
                        },
                        {
                            "match": {
                                "title.fpy": search
                            }
                        }, {
                            "match": {
                                "summary.fpy": search
                            }}
                    ]}
            }}
        count = es.search(index="polycies", body=body, filter_path=["hits"],timeout="60s")
        count = count.get("hits").get("total")
        if count == 0:
            return render_template("no_search.html")
        else:
            body = {
                    "query": {
                        "bool": {
                            "should": [
                                {
                                    "match": {
                                        "title.spy": search
                                    }
                                }, {
                                    "match": {
                                        "summary.spy": search
                                    }},
                                {
                                    "match_phrase": {
                                        "title": {
                                            "query": search,
                                            "analyzer": "ik_sync_smart"
                                        }
                                    }
                                }, {
                                    "match_phrase": {
                                        "summary": {
                                            "query": search,
                                            "analyzer": "ik_sync_smart"
                                        }
                                    }
                                },
                                {
                                    "match": {
                                        "title.fpy": search
                                    }
                                }, {
                                    "match": {
                                        "summary.fpy": search
                                    }}
                            ]}
                    },
                    "size": 10,
                    "from": (page_num - 1) * 10,
                    "highlight": {
                        "pre_tags": "<b style='color:red'>",
                        "post_tags": "</b>",
                        "fields": [{
                            "title.fpy": {}
                        }, {
                            "title.spy": {}
                        }, {
                            "summary.spy": {}
                        }, {
                            "summary.spy": {}
                        }, {
                            "title": {}
                        }, {
                            "summary": {}
                        }, {
                            "id": {}
                        }]}
                }
            if page_num == 1:
                body['size']=9
            res = es.search(index="polycies", body=body, filter_path=["hits.hits"])
            rets = res.get("hits").get("hits")
            items = [{k.replace(".fpy", "").replace(".spy", ""): ''.join(v) for k, v in item.get("highlight").items()}
                     for item in rets]
            for item in items:
                item['id'] = rets[items.index(item)].get("_source").get("id")
            if page_num==1:
                if count > 10000:
                    count = 10000
                body["size"] = count
                body["_source"] = "publishTime"
                res = es.search(index="polycies", body=body, filter_path=["hits.hits"])
                rets = res.get("hits").get("hits")
                time_list = [
                    time.strftime("%Y-%m-%d", time.localtime(int(item.get("_source").get("publishTime") / 1000))) for
                    item in rets if item.get("_source").get("publishTime") != -28800000]
                time_list = list(set(time_list))
                time_list.sort()
                items.insert(0,{"time_list":time_list})
            print(items)
            start = (page_num - 1) * 10
            end = start + 10
            total = count
            pagination = Pagination(bs_version=3, page=page_num, total=total)
            context = {
                "items": items,
                "pagination": pagination,
                "page_num":page_num
            }
            print(context['page_num'])
            return render_template("turn_page.html", **context)

    else:
        return render_template("no_search.html")


@app.route("/clean")
def clean():
    id = request.cookies.get("id")
    r.zremrangebyrank(id, 0, -1)
    return jsonify("sucess", "ok")


@app.route("/detail/<string:id>")
def detail(id):
    body = {"query": {
        "constant_score": {
            "filter": {
                "term": {
                    "id": id
                }
            },
            "boost": 1.2
        }
    }
        , "_source": ["content", "title"]
    }
    res = es.search(index="polycies", body=body,filter_path=["hits.hits"],timeout="60s")
    rets = res.get("hits").get("hits")[0]
    print(rets)
    context={
        "item":rets
    }
    return render_template("detail.html",**context)

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=80)
    # app.run(debug=True)
