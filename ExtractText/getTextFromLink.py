#!/usr/bin/env python
# -*- coding:utf-8 -*-
from newspaper import Article
import requests  #爬取网页的库
from bs4 import BeautifulSoup #用于解析网页的库
import time
import random
from FindChildLinks import AnalysisLinks
from FindChildLinks import getSecondLink
from FindChildLinks import getThreeLink

from ParentLevel import JudgeCurrentLevel
from ExtractText import getTextFromLink

# 判断标题是否存在"招聘"，如果有，提取正文
def checkifContainUrl(url,status):
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
        response = requests.request("GET", url, headers=headers)  # 获取网页数据
    except:
        print("服务器拒绝连接........")
        print("让我休息5秒钟啊！！！")
        print("ZZzzzz...")
        time.sleep(5)
        print("做了个美美的梦，睡的很好, 那我们继续吧...")
        return


    response.encoding = response.apparent_encoding  # 当获取的网页有乱码时加
    soup2 = BeautifulSoup(response.text, 'html.parser')
    bf = soup2.find('div', class_='view TRS_UEDITOR trs_paper_default trs_web')
    a = Article(url, language='zh')
    if(a):
        a.download()
        if(a.download_exception_msg):
            print("出现网页下载异常：",a.download_exception_msg)
            return
        a.parse()

        if(status == '1'):
            guolvResult = getThreeLink.guolv(a.title,url,status)
            if(guolvResult == ''):
                return
        if (status == '2'):
            print('级别' + status + '   不是公告::' + a.title + '         链接： ' + url)
        zhaopinresult = "招聘" in a.title
        if zhaopinresult:
            print('级别' + status + '是招聘公告::' + a.title + '         链接： ' + url)
