# -*- coding:utf-8 -*-
import optparse
import urllib

from fake_useragent import UserAgent
# from newspaper import Article
from urllib import parse
# -*- coding:utf-8 -*-
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
from FindChildLinks import AnalysisLinks
from FindChildLinks import getSecondLink
from FindChildLinks import getThreeLink

from ParentLevel import JudgeCurrentLevel
from ExtractText import getTextFromLink



def get_proxy(url):
    try:
        if(url == ''):
            return None
        response = requests.get(url)
        if response.status_code == 200:
            # print(response.text)
            return response.text
        return None
    except ConnectionError:
        return None

# 判断二级链接是否具有域名，没有的话需要拼接,返回二级的http链接
def GetLinkHasNetloc(firstlink,childlink):
    linkTest = parse.urlparse(childlink)
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

# 包含需要正文的链接集合
firstresult = set()

# 包含可能出现有效子链接的集合
secondresult = set()

# 更多内容
moreresult = set()

# 判断链接是否有效的list
invalidLink = ['logout','login','void','javascript','void(0)','#','(0)']


# 判断是否可能包含有效子链接的判断条件
possibleUse = ['公示公告', '公告栏', '通知公告', '考录', '招聘','招考','招录']


def analysisurl(testurl):
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
    try:
        # 构造请求头信息
        headers = {
            "User-Agent": agent,
            "Cookie": "__guid=54589117.3355346342630053000.1545469390794.6116; Hm_lvt_6bcd52f51e9b3dce32bec4a3997715ac=1545469392; _ga=GA1.2.525028080.1545469392; customerId=5c1dfddd1c648b470dce01bc; customerToken=7094f880-05c8-11e9-b37a-bbc022d7aefd; customerMail=; isLogin=yes; __utmz=54589117.1550903385.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utma=54589117.525028080.1545469392.1550986423.1551265116.3; _gid=GA1.2.1073060500.1552831283; aliyungf_tc=AQAAAD/RilUP4wcAn/Q5cZh/y5cvhjrW; connect.sid=s:dBSjH13Adl1RlFsC2zZlAxGDmFh2kF_F.Yf52AS5i06bgo8lsniQWt1F4NtgmI3rOrmjBIiLwR6Q; SERVER_ID=5aa5eb5e-f0eda04d; Hm_lvt_5667c6d502e51ebd8bd9e9be6790fb5d=1551698067,1551698230,1552831282,1552908428; monitor_count=29; Hm_lpvt_5667c6d502e51ebd8bd9e9be6790fb5d=1552909773"
        }
        response = requests.get(testurl, headers=headers)  # 获取网页数据
        response.encoding = response.apparent_encoding  # 当获取的网页有乱码时加
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup
    except:
        print("服务器拒绝连接........")
        print("让我休息5秒钟啊！！！")
        print("ZZzzzz...")
        time.sleep(5)
        print("做了个美美的梦，睡的很好, 那我们继续吧...")
        return ''

# 判断具备有效招聘信息的1级链接，含有公告专栏的1级链接
def getresult(testurl):
    soup = analysisurl(testurl)
    # bf = soup.find('div', class_='view TRS_UEDITOR trs_paper_default trs_web')
    if(soup == ''):
        return
    for x in soup.find_all('a',href = True):
        if(x.string is not None):
            title = str(x.string).replace('\n', '').replace('\t', '').replace(' ', '')
            url = GetLinkHasNetloc(testurl, x['href'])
            if(url != ''):
                isNotValidLink = any(word if word in x['href'] else False for word in invalidLink)
                if(isNotValidLink):
                    # print('×无效链接：' + url)
                    pass
                else:
                    # print('✓正常标题:' + url + '    标题:' + title)
                    if('招聘' in title):
                        node1 = urlNode.make_struct(url,title,1,testurl)
                        firstresult.add(node1)
                    isincludeUse = any(word if word in title else False for word in possibleUse)
                    if (isincludeUse):
                        print('我有可能具备有效的子链接哦:    ' + title + '    ' + url)
                        node2 = urlNode.make_struct(url,title,1,testurl)
                        secondresult.add(node2)

# 可能具备有效招聘信息的1级链接
def getresultFromSecondresult(setArray):
    for key in setArray:
        soup = analysisurl(key.url)
        if(soup == ''):
            return
        for x in soup.find_all('a', href=True):
            if (x.string is not None):
                title = str(x.string).replace('\n', '').replace('\t', '').replace(' ', '')
                url = GetLinkHasNetloc(key.url, x['href'])
                if(url != ''):
                    isNotValidLink = any(word if word in x['href'] else False for word in invalidLink)
                    if (isNotValidLink):
                        # print('×无效链接：' + url)
                        pass
                    else:
                        # print('✓正常标题:' + url + '    标题:' + title)
                        if ('招聘' in title):
                            node3 = urlNode.make_struct(url, title, 2, key.url)
                            firstresult.add(node3)
                        if('更多' in title):
                            node4 = urlNode.make_struct(url, title, 2,2 key.url)
                            moreresult.add(node4)

# 一级链接中，可能含有二级链接的链接跳转更多
def getresultFromMoreresult(setArray):
    for key in setArray:
        soup = analysisurl(key.url)
        if(soup == ''):
            return
        for x in soup.find_all('a', href=True):
            if (x.string is not None):
                title = str(x.string).replace('\n', '').replace('\t', '').replace(' ', '')
                url = GetLinkHasNetloc(key.url, x['href'])
                if(url != ''):
                    isNotValidLink = any(word if word in x['href'] else False for word in invalidLink)
                    if (isNotValidLink):
                        print('×无效链接：' + url)
                        pass
                    else:
                        print('✓正常标题:' + url + '    标题:' + title)
                        if ('招聘' in title):
                            node3 = urlNode.make_struct(url, title, 3, key.url)
                            firstresult.add(node3)

# 当前的所有链接中，可能还有有效的文本，也就是4级别，这个仅判断firstresult即可
def getresultFromMoreresult(setArray):
    for key in setArray:
        soup = analysisurl(key.url)
        if(soup == ''):
            return
        for x in soup.find_all('a', href=True):
            if (x.string is not None):
                title = str(x.string).replace('\n', '').replace('\t', '').replace(' ', '')
                url = GetLinkHasNetloc(key.url, x['href'])
                isNotValidLink = any(word if word in x['href'] else False for word in invalidLink)
                if (isNotValidLink):
                    pass
                else:
                    if ('招聘' in title):
                        node3 = urlNode.make_struct(url, title, 3, key.url)
                        firstresult.add(node3)



def getresultFromFirstresult(setArray):
    for key in setArray.copy():
        soup = analysisurl(key.url)
        if(soup == ''):
            return
        for x in soup.find_all('a', href=True):
            if (x.string is not None):
                title = str(x.string).replace('\n', '').replace('\t', '').replace(' ', '')
                url = GetLinkHasNetloc(key.url, x['href'])
                isNotValidLink = any(word if word in x['href'] else False for word in invalidLink)
                if (isNotValidLink):
                    pass
                else:
                    if ('招聘' in title):
                        node3 = urlNode.make_struct(url, title, 4, key.url)
                        firstresult.add(node3)
                        # 如果这个下面还有招聘，则说明现在的链接可以删除了


db = pymysql.connect(host='localhost',
                                     port=3306,
                                     user='root',
                                     password='root',
                                     database='shanxiyuan',
                                     charset='utf8',
                                     unix_socket = '/tmp/mysql.sock'

)  # 连接数据库
print(db)

cursor = db.cursor()
cursor.execute("DROP TABLE IF EXISTS TreeTest")

sql = """CREATE TABLE ExaminationSituation3 (
                                      ID INT PRIMARY KEY AUTO_INCREMENT,
                                      PARENTID INT(11),
                                      LINK  VARCHAR(255),
                                      TITLE TEXT,
                                      TEXT TEXT
                                      )"""

try:
    cursor = db.cursor()
    cursor.execute(sql)
except:
    db.ping()
    cursor = db.cursor()
    cursor.execute(sql)

def main():
    # 选择数据源
    read_path = "../DataSourceFile/sp_govs.xlsx"

    bk = xlrd.open_workbook(read_path)
    shxrange = range(bk.nsheets)

    try:
        sh = bk.sheet_by_name("sp_govs")
    except:
        print("no sheet in %s named sheet1" % read_path)
    print('this message is from main function')
    nrows = sh.nrows
    x = 1
    for i in range(nrows):
        testurl = sh.cell_value(i, 5)  # 依次读取每行第11列的数据，也就是 URL
        print("2、访问第%d个链接:" %x)
        x = x + 1
        print(testurl)
        getresult(testurl)
        getresultFromSecondresult(secondresult)
        getresultFromMoreresult(moreresult)
        count = 1
        getresultFromFirstresult(firstresult)
        for key in firstresult:
            print("标题%d：" % count  + "           " + key.title + "       链接 ：" + key.url + "        父链接 ：" + key.preurl)
            count = count + 1
            a = Article(key.url, language='zh')

            if(get_proxy(key.url) != None):
                a.download()
                a.parse()
                db.ping(reconnect=True)
                status = 2;
                sqlw = """INSERT INTO ExaminationSituation3 (PARENTID,LINK, TITLE, TEXT) VALUES (%d,%s,%s,%s)"""
                data = (key.status, "'%s'" % key.url, "'%s'" % key.title, "'%s'" % a.text)

                try:
                    cursor.execute(sqlw % data)
                    db.commit()
                    print('插入数据成功')
                except:
                    db.rollback()
                    print("插入数据失败")

        firstresult.clear()
        secondresult.clear()
        moreresult.clear()
    print('=' * 40)


if __name__ == '__main__':
    # sql = "DROP TABLE IF EXISTS ExaminationSituation3"
    # try:
    #     cursor.execute(sql)
    #     print('table：ExaminationSituation3-已被删除')
    # except Exception as e:
    #     print(e)
    main()
    db.close()



