import pandas as pd
from scipy import sparse
from datetime import datetime, timedelta
from sklearn.cluster import KMeans
import numpy as np
from config import *
from Cluster import Cluster, Preprocess
import pickle
import os
import re


def Precision(recommend_list, real_list):
    '''
    :param recomend_list: 包含N个用户的推荐列表
    :param real_list: N个用户的真实行为列表
    :return: precision
    '''
    hit = 0
    num_rec = 0
    for rec, real in zip(recommend_list, real_list):
        hit += len(set(rec) & set(real))
        num_rec += len(rec)
    return hit / num_rec

def Recall(recommend_list, real_list):
    '''
    :param recomend_list: 包含N个用户的推荐列表
    :param real_list: N个用户的真实行为列表
    :return: recall
    '''
    hit = 0
    num_all = 0
    for rec, real in zip(recommend_list, real_list):
        hit += len(set(rec) & set(real))
        num_all += len(real)
    return hit / num_all


class UCF:
    def __init__(self, clusters, train, K, len_item, user_program, text_info, N):
        '''
        :param clusters: 用户的聚类结果
        :param train: 训练集包含用户对节目标签的感兴趣程度 train[u][i] 表示用户u对节目i的感兴趣程度
        :param K: 近邻size
        :param len_item: 总共有的标签
        :param user_program: 用户观看的节目列表user_program[u]是用户u观看过的节目列表
        :param text_info: 节目的标签
        :param N: 推荐列表的大小
        '''
        self.clusters = clusters
        self.train = train
        self.K = K
        self.len_item = len_item
        self.user_program = user_program
        self.text_info = text_info
        self.N = N


    def KNN(self, u):
        '''
        :param user: 带计算的用户
        :return: 返回与user最相似的K个用户和他们与user的相似度
        '''
        label = self.clusters[self.clusters['uid'] == u]['label'].values[0]
        users = self.clusters[self.clusters['label'] == label]['uid']
        rank = dict()
        for item in self.train[u]:
            for user in users:
                fenmu1 = 0
                fenmu2 = 0
                rank.setdefault(user, 0)
                if item in self.train[user]:
                    rank[user] += self.train[user][item] * self.train[u][item]
                    fenmu1 += self.train[user][item] ** 2
                    fenmu2 += self.train[u][item] ** 2
                rank[user] / (np.sqrt(fenmu1) * np.sqrt(fenmu2))  # 余弦相似度要reverse
        return sorted(rank.items(), key=lambda x: x[1], reverse=True)[0:self.K]


    def user_interest_program(self, user, program):
        inte = 0
        li = list(self.text_info.chanel_name)
        if program in li:
            for item in self.text_info[self.text_info.chanel_name == program]['text_type'].values[0]:
                if item in self.train[user]:
                    inte += self.train[user][item]
            inte /= len(self.text_info[self.text_info.chanel_name == program]['text_type'].values[0])
        elif program in self.train[user]:
            inte += self.train[user][program]
        else:
            inte = 0
        return inte


    def recommend(self, user, N):
        self.N = N
        Kneigh = self.KNN(user)
        rank = dict()
        for neighbor in Kneigh:
            uid = neighbor[0]
            if uid == user:
                continue
            sim = neighbor[1]
            for program in self.user_program[self.user_program.uid == uid]['chanel_name'].values[0]:
                rank[program] = self.user_interest_program(user, program) * sim  # 用余弦相似度用乘以 /(dist + 0.01)
        return sorted(rank.items(), key=lambda x: x[1], reverse=True)[0:N]

def main():
    train, data_, text_info = Preprocess()
    clusters, item_set = Cluster(train, 18)
    Ns = [5, 10, 20]
    Ks = [10, 20]
    user_program = data_.groupby('uid')[['chanel_name']].agg(lambda x: list(set(x))).reset_index()
    all_program = set()
    for x in user_program['chanel_name']:
        all_program |= set(x)
    ucf = UCF(clusters, train, 20, len(item_set), user_program, text_info, 5)
    us = list(train.keys())
    df = {'N':[],
    'K':[],
    'precision':[],
    'recall':[],
          'coverage':[]}
    if not os.path.exists(xls_path):
        os.mkdir(xls_path)
    writer = pd.ExcelWriter(recommend_xls_result)
    for N in Ns:
        for K in Ks:
            ucf.K = K
            recommend_list = []
            real_list = []
            recommend_set = set()
            for u in us:
                recommend_with_rank = ucf.recommend(u, N)
                real = user_program[user_program.uid == u]['chanel_name'].values[0]
                if len(real) > 0 and len(recommend_with_rank) > 0:
                    print('recommend:', ','.join([x[0] for x in recommend_with_rank]))
                    print('groundtruth:', ','.join(real))
                recommend_list.append([x[0] for x in recommend_with_rank])
                recommend_set |= set(recommend_list[-1])
                real_list.append(real)
            # all_program = list(user_program.chanel_name)
            precision = Precision(recommend_list, real_list)
            recall = Recall(recommend_list, real_list)
            coverage = len(recommend_set) / len(all_program)
            df['N'].append(N)
            df['K'].append(K)
            df['precision'].append(precision)
            df['recall'].append(recall)
            df['coverage'].append(coverage)
            print('N=%s, K=%s precision: %s' %(N, K, precision))
            print('N=%s, K=%s recall: %s' %(N, K, recall))
            print('N=%s, K=%s coverage: %s' %(N, K, coverage))
    df = pd.DataFrame(df)
    df.to_excel(writer, sheet_name='sheet1', index=False)
    writer.save()




if __name__=='__main__':
    main()
