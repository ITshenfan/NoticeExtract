import nltk
import xlrd
import requests  #爬取网页的库
import re
import bs4
from urllib import parse
from bs4 import BeautifulSoup #用于解析网页的库
import time
import pymysql
import FindChildLinks


# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
from FindChildLinks import AnalysisLinks
from FindChildLinks import getSecondLink
from FindChildLinks import getThreeLink

from ParentLevel import JudgeCurrentLevel
from ExtractText import getTextFromLink


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

    print('=' * 40)
    # 选择数据源
    url = 'http://jyt.gxzf.gov.cn/'
    print('我是雄赳赳气昂昂的数据源:' + url)
    level = AnalysisLinks.getcurrentLevel(url,'x')
    print(level)
    if(level == 0):
        getSecondLink.getSecondUtl(url,'0')
    if(level == 1):
        getThreeLink.getThreeUtl(url,'1')
    # else:循环的时候作为条件
    print('=' * 40)
