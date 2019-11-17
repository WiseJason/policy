import jieba
from pymongo import MongoClient
from redis import StrictRedis
import jieba.posseg as pseg
#
# r=StrictRedis(host="localhost",port=6379,decode_responses=True)
# client=MongoClient(host="localhost",port=27017)
# db=client["发改委"]
# collection=db["国策1-详情页"]
# datas=collection.find({},{"title":1,"summary":1,"content":1,"_id":0})
# for data in datas:
#     print(data["summary"])
#     break

import jieba
import jieba.posseg
import jieba.analyse
# jieba.enable_parallel(4)
# seg_list = jieba.cut("为贯彻落实国务院《关于做好自由贸易试验区第五批改革试点经验复制推广工作的通知》（国函〔2019〕38号）精神，切实做好复制推广工作，结合我省实际，制定本方案。", cut_all=False)
# print(",".join(seg_list))
