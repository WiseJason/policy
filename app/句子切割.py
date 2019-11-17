import jieba.posseg as pseg
import jieba.analyse
def add_data(text):
    words = pseg.cut(text)
    for word, flag in words:
        print(word,flag)

text="猪价政策对上证指数的影响2012年"
add_data(text)
keywords1=jieba.analyse.extract_tags(text)
print(keywords1)