from . import v1
from flask import render_template,request,make_response,jsonify
import hashlib
import time
from flask_paginate import Pagination, get_page_parameter
from app import r,es
import  json

def decodechar(x):
    return x.decode("utf-8")

@v1.app_template_filter("ten_multiple")
def ten_multiple(arg):
    if arg>15 and arg%10==0 :
        return True
    else:
        return False
@v1.app_template_filter("turn_int")
def turn_int(a):
    print("a 的 type %s"%type(a))
    return int(a)

# ip+useragent+md5识别用户设置cookie
@v1.route('/')
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
    response = make_response(render_template("v1/index.html", **context))
    response.set_cookie("id", cookie)
    return response


@v1.route("/search", methods=["get"])
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
            return render_template("v1/no_search.html")
        else:
            if count > 10000:
                count = 10000
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
                body["size"] = 10
                body["_source"] = "publishTime"
                res = es.search(index="polycies", body=body, filter_path=["hits.hits"])
                rets = res.get("hits").get("hits")
                time_list = [
                    time.strftime("%Y-%m-%d", time.localtime(int(item.get("_source").get("publishTime") / 1000))) for
                    item in rets if item.get("_source").get("publishTime")>0]
                time_list = list(set(time_list))
                time_list.sort()
                items.insert(0,{"time_list":time_list})
            start = (page_num - 1) * 10
            end = start + 10
            total = count
            pagination = Pagination(bs_version=3, page=page_num, total=total)
            context = {
                "items": items,
                "pagination": pagination,
                "page_num":page_num
            }

            print(json.dumps(body))
            return render_template("v1/turn_page.html", **context)

    else:
        return render_template("v1/no_search.html")


@v1.route("/clean")
def clean():
    id = request.cookies.get("id")
    r.zremrangebyrank(id, 0, -1)
    return jsonify("sucess", "ok")


@v1.route("/detail/<string:id>")
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
    return render_template("v1/detail.html",**context)