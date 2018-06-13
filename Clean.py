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


def DataClean(input_path, out_path):
    '''
    数据清洗，去除观看时间过长的数据并整理格式为 uid|chanel_name|watch_time|start_watch|end_watch
    去除节目名称中的停用词
    '''
    columns = ['uid', 'chanel_name', 'watch_time', 'start_watch', 'end_watch']
    with open(input_path, 'r') as f:
        if not os.path.exists(processed_path):
            os.mkdir(processed_path)
        if not os.path.exists(out_path):
            fw = open(out_path, 'w', encoding='utf-8')
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


if __name__=='__main__':
    path = week_data_path
    data_list = os.listdir(path)
    output_path = processed_path
    for i, input_path in enumerate(data_list):
        DataClean(path + '/' + input_path, output_path + '/%s.csv' %i)

