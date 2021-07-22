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


def Analysis(url):
    linkTest = parse.urlparse(url)

    print('1.result.scheme : 网络协议')
    print(linkTest.scheme)

    print('2.result.netloc: 服务器位置（也有可能是用户信息）')
    print(linkTest.netloc)

    print('3.result.path: 网页文件在服务器中的位置')
    print(linkTest.path)

    print('4.result.params: 可选参数')
    print(linkTest.params)

    print('5.result.query: &连接键值对')
    print(linkTest.query)

    print('result.fragment:')
    print(linkTest.fragment)

url = 'http://www.shaanxi.gov.cn/xw/ztzl/zxzt/zkzl/2020n/'
Analysis(url)