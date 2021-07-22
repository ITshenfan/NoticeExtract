# -*- coding:utf-8 -*-
from fake_useragent import UserAgent
import nltk
import xlrd
import requests  # 爬取网页的库
import re
from urllib import parse
from bs4 import BeautifulSoup  # 用于解析网页的库
import time
import pymysql
from scrapy import signals
from twisted.enterprise import adbapi
from pymysql import cursors
import random
import  FindChildLinks
import ExtractText
from FindChildLinks import AnalysisLinks
from FindChildLinks import getSecondLink
from FindChildLinks import getThreeLink

from ParentLevel import JudgeCurrentLevel
from ExtractText import getTextFromLink


def guolv(title,url,status):
    listpossibleUse = ['公示公告','公告栏','通知公告','人事','考录','招聘']
    idxe = any(word if word in title else False for word in listpossibleUse)
    if(idxe):
        print('我有可能具备有效的子链接哦:    ' + title + '    ' + url)
        getThreeLink.getThreeUtl(url,'1')
        return "true"
    lista = ['新闻','工伤','职工','无障碍','政务','环境','领导','信箱','咨询','投诉','访谈','天气','互动','招商','引资','规划','计划','资金','交通','运输','救援','代理','机构','站点','地图','登录','注册','任职','职务','服务','医疗','审批','不良','记分','人文','排气','污染','走向','财政','资金','目标','责任','脱贫','攻坚','就业','创业','项目','开展','互联','互动','交流','技术局','义务教育','霾','抽查','农业','免职','任职','智能','初心','使命','停电','实施','无障碍','走进','印发','体育','彩票','安全','管理','联系我们','消防','救援','土地','征收','征地','补偿招标','图片','民生','资讯','财政','不动产','继承','共产党','讲话','物流','产业','房屋所有权','应急管理','任免','建设','权责','科技','合格单位','计划','培训','补贴','手机','APP','App','app','学习','干部','群众','庆祝','新媒体','防汛','抗旱','总理','共产党','低保','金','业务','先进事迹','退役军人','数据统计','个人','法人','中共','问卷调查','食品安全','信箱','开通','办理','科学技术','林业局','自然资源','结果反馈']
    idx = any(word if word in title else False for word in lista)

    if(idx):
        judge = AnalysisLinks.getcurrentLevel(url,'999')
        print('级别 ：%d'%judge + '        过滤掉的标题::' + title + '        '+ url)
        return ""
    else:
        return "true"



# 得到a标签下的三级链接
def getThreeUtl(firsturl,status):
    print("方法名 ：getThreeUtl   " + firsturl)
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
    except:
        print("服务器拒绝连接........")
        print("让我休息5秒钟啊！！！")
        print("ZZzzzz...")
        time.sleep(5)
        print("做了个美美的梦，睡的很好, 那我们继续吧...")
        return


    response = requests.request("GET", firsturl, headers=headers)  # 获取网页数据
    response.encoding = response.apparent_encoding  # 当获取的网页有乱码时加
    soup = BeautifulSoup(response.text, 'html.parser')
    bf = soup.find('div', class_='view TRS_UEDITOR trs_paper_default trs_web')
    # 提取二级链接的地址
    linklst2 = []
    for x in soup.find_all('a'):
        link = x.get('href')
        if link:
            linklst2.append(link)
            if(AnalysisLinks.GetChildLinkHasNetloc(firsturl, link)):
                naninani = AnalysisLinks.GetChildLinkHasNetloc(firsturl, link)
                if(AnalysisLinks.is_valid_domain(naninani) != "123"):# 如果二级链接有效，再判断是否有标题和正文
                    getTextFromLink.checkifContainUrl(naninani,'2')
