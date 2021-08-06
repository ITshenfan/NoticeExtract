# -*- coding:utf-8 -*-
import optparse
import urllib

import newspaper.article
from fake_useragent import UserAgent
# from newspaper import Article
from urllib import parse
from fake_useragent import UserAgent
import bs4
from newspaper import Article
import requests  #爬取网页的库
from bs4 import BeautifulSoup #用于解析网页的库
import time
import random
import nltk
import xlrd
import requests  #爬取网页的库
import re
from urllib import parse
from bs4 import BeautifulSoup #用于解析网页的库
import time
import pymysql
from scrapy import signals
from twisted.enterprise import adbapi
from pymysql import cursors
import random


# 定义

# 包含需要正文的链接集合
firstresult = set()

# 包含可能出现有效子链接的集合
secondresult = set()

# 更多内容
moreresult = set()

# 判断链接是否有效的list
invalidLink = ['logout', 'login', 'void', 'javascript', 'void(0)', '#', '(0)']
invalidTitle = ['无障碍', '404']

# 判断是否可能包含有效子链接的判断条件
possibleUse = ['公示公告', '公告栏', '通知公告', '考录', '招聘', '招考', '招录']


# 使用类创建结构体
class urlNode(object):
    class Struct(object):
        def __init__(self, url,title,status,preurl):
            self.url = url
            self.title = title
            self.status = status
            self.preurl = preurl

    def make_struct(self, url,title,status,preurl):
        return self.Struct(url,title,status,preurl)
urlNode = urlNode()



def get_proxy(url):
    try:
        if(url == ''):
            return None
        try:
            response = requests.get(url)
        except:
            return None
        if response.status_code == 200:
            return response.text
        return None
    except ConnectionError:
        return None

# 判断二级链接是否具有域名，没有的话需要拼接,返回二级的http链接
def GetLinkHasNetloc(firstlink,childlink):
    try:
        linkTest = parse.urlparse(childlink)
    except AttributeError:
        print("urllib.parse hasn't been imported yet")
        return ''
    # 如果域名不为空，说明是全部路径
    if (linkTest.netloc != ""):
        return childlink

    # 在这里对父链接进行解析
    my_url = parse.urlparse(firstlink)

    # 如果是/开头，则拼接父链接的域名，无效则拼接域名+路径+/
    if (childlink[:1] == '/'):
        resultLink = my_url.scheme + '://' + my_url.netloc + childlink
        if(get_proxy(resultLink) != None):
            return resultLink
        else:
            resultLink = my_url.scheme + '://' + my_url.netloc + my_url.path + childlink
            if (get_proxy(resultLink) != None):
                return resultLink

    # 如果是绝对路径
    if (childlink[:1] == '.'):
        rightLink = my_url.netloc + my_url.path + childlink[1:]
        if('//' in rightLink):
            rightLink = rightLink.replace('//', '/')
        resultLink = my_url.scheme + '://' + rightLink
        if('index.html' in resultLink):
            resultLink = resultLink.replace('/index.html','')
        if('%@.html' in resultLink):
            resultLink = resultLink.replace('/%@.html', '')
        if(get_proxy(resultLink) != None):
            return resultLink
    else:
        rightLink = my_url.netloc + my_url.path + childlink[1:]
        if ('//' in rightLink):
            rightLink = rightLink.replace('//', '/')
        resultLink = my_url.scheme + '://' + rightLink
        if(my_url.netloc in resultLink):
            if(get_proxy(resultLink) != None):
                return resultLink
    return ''


def analysisurl(testurl):
    if(get_proxy(testurl) == None):
        return ''
    # 构造请求头
    urllist = [
        r"https://gitbook.cn/gitchat/columns?page=1&searchKey=&tag=",
        r"https://gitbook.cn/gitchat/columns?page=2&searchKey=&tag=",
        r"https://gitbook.cn/gitchat/columns?page=3&searchKey=&tag=",
        r"https://gitbook.cn/gitchat/columns?page=4&searchKey=&tag=",
    ]

    agent1 = "Mozilla/5.0 (Linux; U; Android 8.1.0; zh-cn; BLA-AL00 Build/HUAWEIBLA-AL00) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.132 MQQBrowser/8.9 Mobile Safari/537.36"
    agent2 = "Mozilla/5.0 (Linux; Android 8.1; EML-AL00 Build/HUAWEIEML-AL00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/53.0.2785.143 Crosswalk/24.53.595.0 XWEB/358 MMWEBSDK/23 Mobile Safari/537.36 MicroMessenger/6.7.2.1340(0x2607023A) NetType/4G Language/zh_CN"
    agent3 = "Mozilla/5.0 (Linux; U; Android 8.0.0; zh-CN; MHA-AL00 Build/HUAWEIMHA-AL00) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.108 UCBrowser/12.1.4.994 Mobile Safari/537.36"
    agent4 = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"
    agent5 = "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36"
    list1 = [agent1, agent2, agent3, agent4, agent5]

    agent = random.choice(list1)
    headers = {
        "User-Agent": agent,
        "Cookie": "__guid=54589117.3355346342630053000.1545469390794.6116; Hm_lvt_6bcd52f51e9b3dce32bec4a3997715ac=1545469392; _ga=GA1.2.525028080.1545469392; customerId=5c1dfddd1c648b470dce01bc; customerToken=7094f880-05c8-11e9-b37a-bbc022d7aefd; customerMail=; isLogin=yes; __utmz=54589117.1550903385.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utma=54589117.525028080.1545469392.1550986423.1551265116.3; _gid=GA1.2.1073060500.1552831283; aliyungf_tc=AQAAAD/RilUP4wcAn/Q5cZh/y5cvhjrW; connect.sid=s:dBSjH13Adl1RlFsC2zZlAxGDmFh2kF_F.Yf52AS5i06bgo8lsniQWt1F4NtgmI3rOrmjBIiLwR6Q; SERVER_ID=5aa5eb5e-f0eda04d; Hm_lvt_5667c6d502e51ebd8bd9e9be6790fb5d=1551698067,1551698230,1552831282,1552908428; monitor_count=29; Hm_lpvt_5667c6d502e51ebd8bd9e9be6790fb5d=1552909773",
        "Connection": "close"
    }
    for i in range(1,6):
        requestSuccessful = 1
        try:
            response = requests.get(testurl, headers=headers)  # 获取网页数据
            response.encoding = response.apparent_encoding  # 当获取的网页有乱码时加
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup
        except:
            print("服务器拒绝连接........，休息5s ，第%d次    "%i + testurl)
            time.sleep(5)
            print("做了个美美的梦，睡的很好, 那我们继续吧...")
            requestSuccessful = 0
        if (i == 5):
            return ''
        if (requestSuccessful):
            break


# 判断具备有效招聘信息的1级链接，含有公告专栏的1级链接
def getresult(testurl):
    soup = analysisurl(testurl)
    if(soup == ''):
        return
    # 后续可根据这个名字来进行级别的判断
    print('确定源的名称soup.head.title.string：  ' + soup.head.title.string)
    for x in soup.find_all('a',href = True):
        title = None
        if(x.string is not None):
            title = str(x.string).replace('\n', '').replace('\t', '').replace(' ', '')
        if(x.title is not None):
            title = x.title
        if(title is not None):
            url = GetLinkHasNetloc(testurl, x['href'])
            if(get_proxy(url) != None):
                isNotValidLink = any(word if word in x['href'] else False for word in invalidLink)
                if (isNotValidLink):
                    pass
                else:
                    addnode(url,title,1,testurl)

# 创建结点，判断当前的逻辑，加入到对应的集合
def addnode(url,title,status,preurl):
    if ('招聘' in title):
        node1 = urlNode.make_struct(url, title, status, preurl)
        # print('firstresult: ' + url + title)
        firstresult.add(node1)
    if (status == 1):
        isincludeUse = any(word if word in title else False for word in possibleUse)
        if (isincludeUse):
            print('我有可能具备有效的子链接哦:    加入到secondresult吧     ' + title + '    ' + url)
            node2 = urlNode.make_struct(url, title, status, preurl)
            secondresult.add(node2)
    if (status == 2):
        if ('更多' in title):
            node4 = urlNode.make_struct(url, title, status, preurl)
            print('moreresult:' + url + title)
            moreresult.add(node4)

# 判断有效的title
def useful_title(setArray):
    for key in setArray:
        if ('无障碍' in key.title):
            return None
        soup = analysisurl(key.url)
        if(soup == ''):
            print('soup为空' + key.url)
            return None
        for x in soup.find_all('a', href=True):
            title = None
            # a标签题目title属性
            if (x.title is not None):
                title = x.title
            if (x.string is not None):
                title = str(x.string).replace('\n', '').replace('\t', '').replace(' ', '')
            if (title is not None):
                url = GetLinkHasNetloc(key.url, x['href'])
                if (get_proxy(url) != None):
                    isNotValidLink = any(word if word in x['href'] else False for word in invalidLink)
                    if (isNotValidLink):
                        pass
                    else:
                        # print('useful_title ：' + url + '%d'%(key.status + 1))
                        addnode(url, title, key.status + 1, key.url)

# 选择数据源
def select_datasource():
    read_path = "sp_govs.xlsx"

    bk = xlrd.open_workbook(read_path)
    shxrange = range(bk.nsheets)

    try:
        sh = bk.sheet_by_name("sp_govs")
    except:
        print("no sheet in %s named sheet1" % read_path)
    print('this message is from main function')
    nrows = sh.nrows
    return sh,nrows

db = pymysql.connect(host='localhost',
                     port=3306,
                     user='root',
                     password='root',
                     database='shanxiyuan',
                     charset='utf8',
                     unix_socket='/tmp/mysql.sock'

)  # 连接数据库

# cursor = db.cursor()
# cursor.execute("DROP TABLE IF EXISTS TreeTest")
#
# sql = """CREATE TABLE SUCCESS1 (
#                                       ID INT PRIMARY KEY AUTO_INCREMENT,
#                                       PARENTID INT(11),
#                                       LINK  VARCHAR(255),
#                                       TITLE TEXT,
#                                       TEXT TEXT
#                                       )"""
# try:
#     cursor = db.cursor()
#     cursor.execute(sql)
# except:
#     db.ping()
#     cursor = db.cursor()
#     cursor.execute(sql)


def savedata():
    count = 1
    for key in firstresult:
        print(
            "标题%d：" % count + "      级别：%d" % key.status + "           " + key.title + "       链接 ：" + key.url + "        父链接 ：" + key.preurl)
        count = count + 1
        a = Article(key.url, language='zh')
        if (get_proxy(key.url) != None):
            try:
                a.download()
                a.parse()
            except newspaper.article.ArticleException:
                continue

            # db.ping(reconnect=True)
            # sqlw = """INSERT INTO SUCCESS1 (PARENTID,LINK, TITLE, TEXT) VALUES (%d,%s,%s,%s)"""
            # data = (key.status, "'%s'" % key.url, "'%s'" % key.title, "'%s'" % a.text)
            #
            # try:
            #     cursor.execute(sqlw % data)
            #     db.commit()
            #     print('插入数据成功')
            # except:
            #     db.rollback()
            #     print("插入数据失败")

# 链接的爬取和处理
def visitlink(testurl):
    print(testurl)
    getresult(testurl)
    useful_title(secondresult)
    useful_title(moreresult)
    useful_title(firstresult)


def main():
    # 选择数据源
    sh,nrows = select_datasource()
    x = 1
    for i in range(2):
        testurl = sh.cell_value(i, 5)
        print("访问第%d个链接:" %x)
        x = x + 1
        # 处理链接
        visitlink(testurl)
        # 保存数据
        savedata()
        # 清除当前链接相关的数据集合
        firstresult.clear()
        secondresult.clear()
        moreresult.clear()
    db.close()
    print('=' * 40)

if __name__ == '__main__':
    main()