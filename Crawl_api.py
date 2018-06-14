#!/usr/bin/python
#-*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import json
import os
import urllib
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
    url = 'https://api.douban.com/v2/movie/search?q='
    url = quote(url + search, safe='/:?=&')
    try:
        response = random_addr(url)  # 随机代理
    except urllib.error.HTTPError:
        print('找不到%s的信息' % search)
        return False
    html = response.read()
    html = html.decode('utf-8')
    dicts = json.loads(html)
    try:
        ret = dicts['subjects'][0]['genres']
        print('%s的类型为%s' %(search, ' '.join(ret)))
        return ' '.join(ret)
    except IndexError:
        print('找不到%s的信息' %search)
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
    un_crawled = pd.read_csv('./text_info/un_crawled.csv', sep='|')
    crawled_list = list(crawled['name'].values)
    un_crawled_list = list(un_crawled['name'].values)
    uncrawled = list(set(docs) - set(crawled_list) - set(un_crawled_list))
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
                time.sleep(t+5)
                info = get_tag(line)
                if info!=False:
                    print('写入')
                    f.write('|'.join([line, info]) + '\n')
                else:
                    f1.write(line +'\n')

if __name__=='__main__':
    main()