#!/usr/bin/python
#-*- coding: utf-8 -*-
import sys
from bs4 import BeautifulSoup
import random
import re
import numpy as np
import sys
import urllib
import pandas as pd
import xlwt
import os
from urllib.parse import quote
import time
import random
data_path = './processed_data/0.csv'

def user_proxy(proxy_addr, url):
    import urllib.request
    proxy = urllib.request.ProxyHandler({'http': proxy_addr})
    opener = urllib.request.build_opener(proxy, urllib.request.HTTPHandler)
    opener.addheaders = [('User-Agent',
                          'Mozilla/5.0 (Linux; Android 4.1.1; Nexus 7 Build/JRO03D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Safari/535.19')]
    urllib.request.install_opener(opener)
    data = urllib.request.urlopen(url)
    return data

proxy_addr = ["192.155.185.171:80", '192.155.185.171:80', '192.155.185.131:80']

def random_addr(url):
    addr_index = random.randint(0, 2)
    addr = proxy_addr[addr_index]
    response = user_proxy(addr, url)
    return response


def get_tag(search):
    url = u'https://www.douban.com/search?cat=1002&q=' # 搜索电影
    # url = 'https://www.douban.com/search?q=' # 搜索全部
    url = quote(url + search, safe='/:?=&')
    try:
        response = random_addr(url) # 随机代理
        # response = urllib.request.urlopen(url)
        # 第一层
        html = response.read()
        html = html.decode('utf-8')
        pattern1 = '<a href=\".*url=.*target="_blank"'
        f = re.compile(pattern1)
        link = f.findall(html)[0].split('\"')[1]
        # 第二层
        response = random_addr(link)  # 随机代理
        #html = urllib.request.urlopen(link)
        html = response.read()
        html = html.decode('utf-8')
        # 类型pattern
        pattern = '<span property="v:genre">.*</span>'
        f = re.compile(pattern)
        types = f.findall(html)
        types = re.sub('[<>a-zA-Z:=\ "]', '', types[0])
        types = types.strip('/')
        types = types.replace('//', ' ')
    # 简介pattern
    # pattern = "<span property=\"v:summary\" class=\"\">.*?</span>"
    # f = re.compile(pattern)
    # html = html.replace('\n', '')
    # summary = f.findall(html)
    # summary = re.sub('[<>=: a-zA-Z0-9"（.*?）\u3000]', '', summary[0])
        print(search + '的类型为:' + types)

    # print(search + '的简介:' + summary)
        return types
    except Exception as e:
        if 'HTTP' in str(e):
            sys.exit(0)
        print(e)
        print('豆瓣中找不到'+search + '的信息')
        return False


def is_program(line):  # 过滤掉明显爬不到的节目名称

    if len(line) > 17:
        return False
    donot = ['CCTV', 'CQTV', '卫视', '金鹰卡通', '卡酷动画', '测试']
    for x in donot:
        if x in line:
            return False
    return True

def main():
    np.seed = 0
    # r1 = '[0-9’!"#$%&\'()（）*+,-./:;<=>?@，。?★、…【】《》？“”‘’！[\\]^_`{|}~]+'
    data = pd.read_csv(data_path, sep='|')
    data['chanel_name'] = data['chanel_name'].apply(lambda x: str(x).strip())
    docs = pd.unique(data['chanel_name'])
    # data = pd.read_csv('./text_info/un_crawled.csv', sep='|')
    # docs = data['name']
    crawled = pd.read_csv('./text_info/text_info.csv', sep='|')
    crawled_list = list(crawled['name'].values)
    uncrawled = list(set(docs) - set(crawled_list))
    print('%s条数据' %len(uncrawled))
    if not os.path.exists('./text_info'):
        os.mkdir('./text_info')
    with open('./text_info/text_info.csv', 'a', encoding='utf-8', buffering=1) as f:
        with open('./text_info/un_crawled.csv', 'a', encoding='utf-8', buffering=1) as f1:
            #f.write('name|text_type\n')
            #f1.write('name\n')
            for line in uncrawled:
                t = np.abs(np.random.normal()+1)
                if not is_program(line):
                    continue
                time.sleep(t)
                info = get_tag(line)
                if info!=False:
                    print('写入')
                    f.write('|'.join([line, info]) + '\n')
                else:
                    f1.write(line +'\n')

if __name__=='__main__':
    main()