import pandas as pd
from sklearn.cluster import KMeans
from datetime import datetime, timedelta
import os
from config import *
import re
from scipy import sparse


def TimeFilter(start, end, min_gap=300, max_gap=72000):
    '''
    :param start: 开始观看时间字符串
    :param end: 结束观看时间字符串
    :param min_gap: 最小的观看时间
    :param max_gap: 最大的观看时间
    :return: bool变量，观看时间在min_gap到max_gap之间返回True，否则返回False
    '''
    pattern = '%Y%m%d%H%M%S'
    start_time = datetime.strptime(start, pattern)
    end_time = datetime.strptime(end, pattern)
    gap = (end_time - start_time).seconds
    if gap >= min_gap and gap <=max_gap:
        return (True, gap)
    else:
        return (False, gap)


def DataClean():
    '''
    数据清洗，去除观看时间过长的数据并整理格式为 uid|chanel_name|watch_time|start_watch|end_watch
    去除节目名称中的停用词
    '''
    columns = ['uid', 'chanel_name', 'watch_time', 'start_watch', 'end_watch']
    with open(raw_data_path, 'r') as f:
        if not os.path.exists(processed_path):
            os.mkdir(processed_path)
        if not os.path.exists(cleaned_path):
            fw = open(cleaned_path, 'w', encoding='utf-8')
            fw.write('|'.join(columns) + '\n')
            for line in f:
                line = line.strip()
                line_list = line.split('|')
                start = line_list[3]
                end = line_list[4]
                tmp = TimeFilter(start, end)
                if tmp[0]:
                    r1 = '[0-9’!"#$%&\'()（）*+,-./:;<=>?@，。?★、…【】《》？“”‘’！[\\]^_`{|}~]+'
                    chanel_name = re.sub(r1, '', line_list[2].strip())
                    fw.write('|'.join([line_list[0], chanel_name, str(tmp[1]), start, end]) + '\n')
    print('clean complete')


def Crawl():
    '''
    爬取豆瓣数据
    '''
    pass


def Preprocess():
    '''
    数据预处理，将数据处理成可以聚类的向量格式
    :return:train， 原始数据，节目的标签
    '''
    data = pd.read_csv(processed_path + '/0.csv', sep='|')
    # for i in range(1, 7):
    #     tmp = pd.read_csv(processed_path + '/%s.csv' %i, sep='|')
    #     data = pd.concat([data, tmp])
    text_info = pd.read_csv(text_info_path, sep='|')
    text_info.rename(columns={'name': 'chanel_name'}, inplace=True)
    text_info.text_type = text_info.text_type.apply(lambda x: str(x).split(' '))
    text_info.chanel_name.apply(lambda x: str(x).strip())
    data = pd.merge(data, text_info[['chanel_name', 'text_type']], on='chanel_name', how='left')
    # mask = data.text_type.apply(lambda x: str(x) == 'nan')
    # fill = data.chanel_name[mask].apply(lambda x:[x])
    # data.text_type[mask] = fill
    mask = data.text_type.apply(lambda x: str(x) != 'nan')
    data = data[mask]
    pattern = '%Y%m%d%H%M%S'
    start = data.start_watch.apply(lambda x: datetime.strptime(str(x), pattern))
    end = data.end_watch.apply(lambda x: datetime.strptime(str(x), pattern))
    data['watch_time'] = [(x1 - x2).seconds for x1, x2 in zip(end, start)]
    text_type_set = set()
    for each in data.text_type:
        text_type_set |= set(each)
    text_count = dict()
    for each in text_type_set:
        text_count[each] = 0
    for text_list in data.text_type:
        for text in text_list:
            text_count[text] += 1

    for text_list in data.text_type:
        for text in text_list:
            text_count[text] += 1
    # 滤除低频
    data.text_type = data.text_type.apply(lambda x: [z for z in x if text_count[z] > 50])
    user_watchtime = data.groupby('uid')['watch_time'].agg(sum)
    user_watchtime = user_watchtime.reset_index()
    user_watch = dict(user_watchtime.values)
    data_ = data
    data = data_[['uid', 'text_type', 'watch_time']]
    train = dict()
    for each in data.values:
        train.setdefault(each[0], dict())
        for item in each[1]:
            train[each[0]].setdefault(item, 0)
            train[each[0]][item] += each[2]
    for u, items in train.items():
        for item in items:
            train[u][item] /= user_watch[u]
    return train, data_, text_info



def Cluster(train, K):
    '''
    :param train: 训练集
    :param K: 聚类数目
    :return:聚类结果和节目类型集合
    '''
    print('create sparse matrix')
    item_set = set()
    for u in train:
        item_set |= train[u].keys()
    item_set = list(item_set)
    item_dict = dict()
    for i, item in enumerate(item_set):
        item_dict[item] = i
    row = []
    col = []
    dat = []
    uid = list(train.keys())
    for i, u in enumerate(train.keys()):
        for j, item in train[u].items():
            row.append(i)
            col.append(item_dict[j])
            dat.append(item)
    train_sparse = sparse.coo_matrix((dat, (row, col)), shape=(len(train), len(item_set)))  # 稀疏矩阵
    print('begin')
    KM = KMeans(n_clusters=K)
    KM.fit(train_sparse)
    labels = KM.labels_
    clusters = pd.DataFrame({'uid': uid, 'label': labels})
    return clusters, item_set



def main():
    print('processing data')
    train, data_, text_info = Preprocess()
    clusters, item_set = Cluster(train, 18)
    if not os.path.exists(result_path):
        os.mkdir(result_path)
    pd.to_pickle(clusters, cluster_result_path)
    print('complete')



if __name__=='__main__':
    main()