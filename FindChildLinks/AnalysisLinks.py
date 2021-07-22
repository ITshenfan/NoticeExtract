# -*- coding:utf-8 -*-
from fake_useragent import UserAgent
# from newspaper import Article
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
import FindChildLinks
from FindChildLinks import AnalysisLinks
from FindChildLinks import getSecondLink
from FindChildLinks import getThreeLink

from ParentLevel import JudgeCurrentLevel
from ExtractText import getTextFromLink



# 判断二级链接是否具有域名，没有的话需要拼接,返回二级的http链接
def GetChildLinkHasNetloc(firstlink,childlink):
    linkTest = parse.urlparse(childlink)
    if (linkTest.netloc != ""):
        return childlink
    else:
        my_url = parse.urlparse(firstlink)
        if (childlink[:1] == '.'):
            resultLink = my_url.scheme + '://' + my_url.netloc + my_url.path + childlink
            return resultLink
        else:
            resultLink = my_url.scheme + '://' + my_url.netloc
            resultLink = resultLink + childlink
            if(my_url.netloc in resultLink):
                return resultLink



# 判断是几级链接
def getcurrentLevel(url,status):

    linkTest = parse.urlparse(url)
    if(status == 2):
        print('阶级为'+status + ' ' + url)
        return status
    if('http://'+ linkTest.netloc == url):
        print('阶级为'+'0')
        return 0
    if('http://'+ linkTest.netloc + '/' == url):
        print('阶级为'+'0'+ ' ' + url)
        return 0
    else:
        print('阶级为'+'1'+ ' ' + url)
        return 1

# 判断链接是否有效
pattern = re.compile(
    r'^(([a-zA-Z]{1})|([a-zA-Z]{1}[a-zA-Z]{1})|'
    r'([a-zA-Z]{1}[0-9]{1})|([0-9]{1}[a-zA-Z]{1})|'
    r'([a-zA-Z0-9][-_.a-zA-Z0-9]{0,61}[a-zA-Z0-9]))\.'
    r'([a-zA-Z]{2,13}|[a-zA-Z0-9-]{2,30}.[a-zA-Z]{2,3})$'
)
# unuseWord = ['logout','login','void','javascript','beian']
# idx = any(word if word in title else False for word in lista)

def is_valid_domain(value):
    return True if pattern.match(value) else False


# 二级链接是否是有效的招聘公告
def LinkValid(url):
    if ("article" in url):
        return "456"
    if ("logout" in url):
        return "123"
    if ("login" in url):
        return "123"
    if ("void" in url):
        return "123"
    if ("user" in url):
        return "123"
    if ("javascript" in url):
        return "123"
    if ("beian" in url):
        return "123"
    else:
        return "456"




