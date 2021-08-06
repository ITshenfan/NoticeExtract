# -*- coding:utf-8 -*-
import optparse
import urllib

import newspaper.article
from fake_useragent import UserAgent
# from newspaper import Article
from urllib import parse
from fake_useragent import UserAgent
import bs4
import jieba
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
from cocoNLP.extractor import extractor


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


# 判断项目类型，教招为1，其他为0
teacherRecruitment = ['教师', '辅导员']


# 判断公告类型，省统考、市统考、市单招、区县单招
universityRecruitment = ['大学', '学院', '专科']


# 使用类创建结构体
class urlNode(object):
    class Struct(object):
        def __init__(self, url,title,status,preurl,province_city_county):
            self.url = url
            self.title = title
            self.status = status
            self.preurl = preurl
            # 存储数据源的名称，后续抽取出省市县
            self.province_city_county = province_city_county
            # # 教招类型，教招为1，其他为0
            # self.noticeType = noticeType
            # # 公告类型，省统考、市统考、市单招、区县单招
            # self.noticecategory = noticecategory
            # # 编制类型，编制为1，其他为0
            # self.organizationType = organizationType


    def make_struct(self, url,title,status,preurl,province_city_county):
        return self.Struct(url,title,status,preurl,province_city_county)
urlNode = urlNode()

# 判断教招类型，教招为1，其他为0
def noticeType(title) -> str:
    isteacher = any(word if word in title else False for word in teacherRecruitment)
    if (isteacher):
        return '教招'
    else:
        if('编制' in title):
            return '编制'
        else:
            return '其他'


# 判断公告类型，省统考、市统考、市单招、区县单招
def noticecategory(title)-> str:
    # 判断公告类型
    # 省统考:1
    # 市统考:2
    # 市单招:3
    # 区县单招:4
    if('区' in title):
        return '区县单招'
    if('县' in title):
        return '区县单招'
    if ('市' in title):
        return '市单招'
    isuniversity = any(word if word in title else False for word in universityRecruitment)
    if (isuniversity):
            return '市统考'
    if('省' in title):
        return '省统考'
    isteacher = any(word if word in title else False for word in teacherRecruitment)
    if (isteacher):
        return '市单招'
    else:
        return '未知类型'

# 判断编制类型，编制为1，其他为0
def organizationType(title)-> str:
    if ('编制' in title):
        return '编制'
    else:
        return '合同制'

# 链接是否返回404
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
    sourcename = None
    if (soup.head.title.string != None):
        sourcename = soup.head.title.string
        print('确定源的名称：  ' + sourcename)
    for x in soup.find_all('a',href = True):
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
                    addnode(url,title,1,testurl,sourcename)

# 创建结点，判断当前的逻辑，加入到对应的集合
def addnode(url,title,status,preurl,province_city_county):
    if ('招聘' in title):
        node1 = urlNode.make_struct(url, title, status, preurl,province_city_county)
        firstresult.add(node1)
        notice = noticeType(node1.title)
        category = noticecategory(node1.title)
        organization = organizationType(node1.title)
        print('√' + title + "        : " + str(notice) + "    " + str(category) + "      " + str(organization) + "  " )
    if (status == 1):
        isincludeUse = any(word if word in title else False for word in possibleUse)
        if (isincludeUse):
            print('我有可能具备有效的子链接哦,in>>>>secondresult    ' + title + '    ' + url + '     ')
            node2 = urlNode.make_struct(url, title, status, preurl,province_city_county)
            secondresult.add(node2)
    if (status == 2):
        if ('更多' in title):
            node4 = urlNode.make_struct(url, title, status, preurl,province_city_county)
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
                        sourcename = None
                        if (soup.head.title.string != None):
                            sourcename = soup.head.title.string

                        addnode(url, title, key.status + 1, key.url,sourcename)


fileStatus = ['doc','docx','pdf','xls','xls','ppt','pptx','txt']
fileSource = None
# 判断当前链接下是否有附件
def get_file(url) ->str:
    soup = analysisurl(url)
    if (soup == ''):
        print('soup为空' + url)
        return None
    for x in soup.find_all('a', href=True):
        url = GetLinkHasNetloc(url, x['href'])
        if(url != None):
            title = None
            print('嘻嘻哈哈哈哈哈:' + url)
            if (get_proxy(url) != None):
                if (x.title is not None):
                    title = x.title
                if (x.string is not None):
                    title = str(x.string).replace('\n', '').replace('\t', '').replace(' ', '')
                if (title is not None):
                    isfileStatus = any(word if word in title else False for word in fileStatus)
                    if(isfileStatus):
                        global fileSource
                        if(fileSource == None):
                            fileSource = url
                        else:
                            fileSource = fileSource + '&' + url
    if(fileSource == None):
        return None
    else:
        print('我真的好强壮啊' + fileSource)
        return fileSource

# 选择数据源
def select_datasource():
    read_path = "DataSourceFile/sp_govs.xlsx"

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

cursor = db.cursor()
cursor.execute("DROP TABLE IF EXISTS TreeTest")

# sql = """CREATE TABLE SUCCESS11 (ID INT PRIMARY KEY AUTO_INCREMENT,
#                                   公告级别id INT(11),
#                                   公告标签 TEXT,
#                                   省份 VARCHAR(255),
#                                   地市 VARCHAR(255),
#                                   区县 VARCHAR(255),
#                                   项目类型 VARCHAR(255),
#                                   公告类型 VARCHAR(255),
#                                   编制情况 VARCHAR(255),
#                                   公告名称 TEXT,
#                                   公告链接 VARCHAR(255),
#                                   公告原网链接 VARCHAR(255),
#                                   公告父链接 VARCHAR(255),
#                                   招录人数 INT(11),
#                                   招录岗位数 INT(11),
#                                   公告发布时间 VARCHAR(255),
#                                   公告正文 TEXT,
#                                   附件链接 VARCHAR(255)
#                                   )"""
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
        if (get_proxy(key.url) != None):

            count = count + 1
            a = Article(key.url, language='zh')
            # print("标题%d：" % count + "      级别：%d" % key.status + "    " + key.title + "       链接 ：" + key.url + "        父链接 ：" + key.preurl + key.province_city_county + noticeType(
            #         key.title) + "    " + noticecategory(key.title) + "      " + organizationType(key.title) + "  " + a.publish_date + "    tag:" + a.tags)
            try:
                a.download()
                a.parse()
            except newspaper.article.ArticleException:
                continue

            ex = extractor()
            locations = ex.extract_locations(a.text)
            # print(locations)
            # print(noticeType(a.title))

            # print(count)
            # print(key.province_city_county)
            # print(noticeType(key.title))
            # print(key.title)
            # print(key.url)
            print(get_file(key.url))
            db.ping(reconnect=True)
            sqlw = """INSERT INTO SUCCESS11 (公告级别id,公告标签, 省份,地市,区县,项目类型,公告类型,编制情况,公告名称,公告链接,公告原网链接,公告父链接,招录人数,招录岗位数,公告发布时间,公告正文,附件链接) VALUES (%d,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%d,%d,%s,%s,%s)"""
            data = (key.status,"'None'","'%s'"%key.province_city_county,"'%s'"%key.province_city_county,"'%s'"%key.province_city_county,"'%s'"%noticeType(key.title),"'%s'"%noticecategory(key.title),"'%s'"%organizationType(key.title),"'%s'"%key.title,"'%s'"%key.url,"'%s'"%key.preurl,"'%s'"%key.preurl,count,count,"'%s'"%a.publish_date,"'%s'"%a.text,"'%s'"%get_file(key.url))
            global fileSource
            fileSource = None
            try:
                cursor.execute(sqlw % data)
                db.commit()
                print('插入数据成功')
            except:
                db.rollback()
                print("插入数据失败")

# 链接的爬取和处理
def visitlink(testurl):
    print(testurl)
    getresult(testurl)
    useful_title(secondresult)
    useful_title(moreresult)
    # useful_title(firstresult)


def main():
    # 选择数据源
    sh,nrows = select_datasource()
    x = 1
    # for i in range(nrows):
    #     testurl = sh.cell_value(i, 5)
    #     print("访问第%d个链接:" %x)
    #     x = x + 1
    #     # 处理链接
    #     visitlink(testurl)
    #     # 保存数据
    #     savedata()
    #     # 清除当前链接相关的数据集合
    #     firstresult.clear()
    #     secondresult.clear()
    #     moreresult.clear()
    db.close()
    print('=' * 40)
    url = 'http://www.panzhihua.gov.cn/zwgk/rsxx/rskl/1893885.shtml'
    print(get_file(url))


if __name__ == '__main__':
    main()