'''
@author syrobin
@date 2018年3月20日18:20:04
'''

import warnings
warnings.filterwarnings('ignore')
import jieba  # 分词包
import numpy  # numpy计算包
import codecs  # codecs提供的open方法来指定打开的文件的语言编码，它会在读取的时候自动转换为内部unicode
import re  # 正则
import pandas as pd
import matplotlib.pyplot as plt
from urllib import request
from bs4 import BeautifulSoup as bs
#%matplotlib inline

import matplotlib
matplotlib.rcParams['figure.figsize'] = (10.0, 5.0)
from wordcloud import WordCloud  # 词云包


#公共请求头
herders={
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.61 Safari/537.36',
    'Referer':'https://movie.douban.com/',
    'Connection':'keep-alive'}

# 分析网页函数
def getNowPlayingMovie_list():
    url='https://movie.douban.com/cinema/nowplaying/wuhan/'
    req= request.Request(url,headers=herders)
    #print(req)
    resp = request.urlopen(req)  # 获取豆瓣电影的网页的内容
    html_data = resp.read().decode('utf-8')
    soup = bs(html_data, 'html.parser')
    nowplaying_movie = soup.find_all('div', id='nowplaying')
    nowplaying_movie_list = nowplaying_movie[0].find_all('li', class_='list-item')

    #print(nowplaying_movie_list)

    nowplaying_list = [] 
    for item in nowplaying_movie_list:
        nowplaying_dict = {}  # 用来存放电影的id和name
        nowplaying_dict['id'] = item['data-subject']
        # 通过遍历找到电影的id号码
        for tag_img_item in item.find_all('img'):
            nowplaying_dict['name'] = tag_img_item['alt']
            nowplaying_list.append(nowplaying_dict)
    return nowplaying_list

# 爬取评论函数
def getCommentsByld(movield, pageNum):
    eachCommentList = []
    if pageNum > 0:
        start = (pageNum - 1) * 20
    else:
        return False
    requrl = 'https://movie.douban.com/subject/' + movield + '/comments' + '?' + 'start=' + str(start) + '&limit=20'
    #print(requrl)
    req= request.Request(requrl,headers=herders)
    #print(req)
    resp = request.urlopen(req)
    html_data = resp.read().decode('utf-8')
    soup = bs(html_data, 'html.parser')
    comment_div_list = soup.find_all('div', class_='comment')
    #print(comment_div_list)
    for item in comment_div_list:
        if item.find_all('span',class_='short')[0].string is not None:
            eachCommentList.append(item.find_all('span',class_='short')[0].string)
    #print(eachCommentList)
    return eachCommentList


def main():
    # 循环获取热映电影的前10页评论
    commentList = []
    NowPlayingMovie_list = getNowPlayingMovie_list()
    #print(NowPlayingMovie_list)
    for i in range(10):
        num = i + 1
    for NPM in NowPlayingMovie_list:
        commentList_temp = getCommentsByld(NPM['id'], num)
        commentList.append(commentList_temp)

    #print(commentList)
    # 将列表中的数据转换为字符串
    comments = ''
    for k in range(len(commentList)):
        comments = comments + (str(commentList[k])).strip()
    #print(comments)


    # 使用正则表达式去除标点符号
    pattern = re.compile(r'[\u4e00-\u9fa5]+')
    filterdata = re.findall(pattern, comments)
    cleaned_comments = ''.join(filterdata)
    print(cleaned_comments)


    # 使用结巴分词进行中文分词
    segment = jieba.lcut(cleaned_comments)
    words_df = pd.DataFrame({'segment': segment})

    # 去掉停用词
    stopwords = pd.read_csv("stopwords.txt", index_col=False, quoting=3, sep="\t", names=['stopword'], encoding='utf-8')
    # quoting=3全不引用
    words_df = words_df[~words_df.segment.isin(stopwords.stopword)]
    # print(words_df.head())


    #统计词频
    words_stat = words_df.groupby(by=['segment'])['segment'].agg([("计数","count")])
    words_stat = words_stat.reset_index().sort_values(by=["计数"], ascending=False)

    # 用词云进行显示
    wordcloud = WordCloud(font_path="simhei.ttf", background_color="white", max_font_size=100)
    word_frequence = {x[0]: x[1] for x in words_stat.head(1000).values}


    # word_frequence_list = []
    # for key in word_frequence:
    #     temp = (key, word_frequence[key])
    #     word_frequence_list.append(temp)


    wordcloud = wordcloud.fit_words(word_frequence)
    plt.imshow(wordcloud)
    plt.show()

# 主函数
main()
