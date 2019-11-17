import os
from elasticsearch import Elasticsearch

BASE_DIR=os.path.abspath(os.path.dirname(__file__))

class Config():
    SECRET_KEY=os.urandom(24)
    ES_URI = 'localhost:9200'
    REDIS_HOST="localhost"
    REDIS_PORT=6379
    REDIS_DB=0
    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG=True
    # SQLALCHEMY_DATABASE_URI="postgresql:{username}:{password}@{host}:{port}/{database}"



config={
    "development":DevelopmentConfig,
    "default":DevelopmentConfig
}


