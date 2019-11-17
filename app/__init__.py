from config import config
from flask import Flask
import redis
from elasticsearch import Elasticsearch

r=None
es=None

def create_app(config_name):
    config_name="default"
    app=Flask(__name__)
    config_class=config.get(config_name)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    global r
    global es
    r=redis.StrictRedis(host=config_class.REDIS_HOST,port=config_class.REDIS_PORT,db=config_class.REDIS_DB)
    es=Elasticsearch(config_class.ES_URI,timeout=60)

    from .v1 import v1
    from .v2 import v2
    app.register_blueprint(v1,url_prefix="/v1")
    app.register_blueprint(v2, url_prefix="/v2")
    return app
