import pandas as pd
from scipy import sparse
from datetime import datetime, timedelta
from sklearn.cluster import KMeans
import numpy as np
from Cluster import Cluster, Preprocess
import pickle
import re


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
                rank.setdefault(u, 0)
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
    user_program = data_.groupby('uid')[['chanel_name']].agg(lambda x: list(set(x))).reset_index()
    ucf = UCF(clusters, train, 20, len(item_set), user_program, text_info, 5)
    us = list(train.keys())[0:1000]
    for u in us:
        recommend_with_rank = ucf.recommend(u, 5)
        print(recommend_with_rank)




if __name__=='__main__':
    main()
