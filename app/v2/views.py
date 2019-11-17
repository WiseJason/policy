from . import v2
from flask import render_template,request,make_response,jsonify
import hashlib
import time
from flask_paginate import Pagination, get_page_parameter
from app import r,es
import  json

def decodechar(x):
    return x.decode("utf-8")

@v2.app_template_filter("ten_multiple")
def ten_multiple(arg):
    if arg>15 and arg%10==0 :
        return True
    else:
        return False
@v2.app_template_filter("turn_int")
def turn_int(a):
    return int(a)

# ip+useragent+md5识别用户设置cookie
@v2.route('/')
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
    response = make_response(render_template("v2/index.html", **context))
    response.set_cookie("id", cookie)
    return response


@v2.route("/search", methods=["get"])
def search():
    search = request.args.get("search")
    target=request.args.get("target")
    id = request.cookies.get("id")
    if search:
        r.zadd(id, {search: int(round(time.time() * 1000000))})
        body = {
                "query": {
                    "bool": {
                        "should": [
                            {
                                "match_phrase": {
                                    "title": search
                                }
                            },
                            {
                                "match_phrase": {
                                    "summary": search
                                }
                            },
                            {
                                "match_phrase": {
                                    "title": {
                                        "query": search,
                                        "analyzer": "jt_cn"
                                    }
                                }
                            },
                            {
                                "match_phrase": {
                                    "summary": {
                                        "query": search,
                                        "analyzer": "jt_cn"
                                    }
                                }
                            }
                        ]
                    }
                },
                "aggs": {
                    "timeagg": {
                        "cardinality": {
                            "field": "publishTime"
                        }
                    }
                },
                "size": 10000,
                "_source": ["publishTime","id","summary","content"]
                }
        a=time.time()
        res = es.search(index="polycies2", body=body, filter_path=["hits"])
        count=res["hits"]["total"]
        if count>0:
            items=res["hits"]["hits"]
            items=[item["_source"] for item in items if item.get("_source").get("publishTime")>0]
            for item in items:
                item["publishTime"]=time.strftime("%Y-%m-%d", time.localtime(int(item.get("publishTime") / 1000)))
            context = {
                "items": items}
            items.sort(key=lambda item:item.get("publishTime"))
            return render_template("v2/turn_page.html", **context)
        else:
            return render_template("v2/no_search.html")
    return render_template("v2/no_search.html")


@v2.route("/clean")
def clean():
    id = request.cookies.get("id")
    r.zremrangebyrank(id, 0, -1)
    return jsonify("sucess", "ok")


@v2.route("/detail/<string:id>")
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
    res = es.search(index="polycies2", body=body,filter_path=["hits.hits"],timeout="60s")
    rets = res.get("hits").get("hits")[0]
    print(rets)
    context={
        "item":rets
    }
    return render_template("v2/detail.html",**context)


@v2.route("/autocomplete", methods=["post"])
def autocomplete():
    return jsonify({"data":["123",456,789,100,1000,20,21,22,34,2,34,5,6,7,8,94,3,12,3]})