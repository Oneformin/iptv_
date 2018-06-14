import pandas as pd
from config import *
import gc
from Cluster import Preprocess
import os
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
mpl.rcParams['font.sans-serif'] = [u'SimHei']
mpl.rcParams['axes.unicode_minus'] = False


def merge_result():
    train, _1, _2 = Preprocess()
    del _1
    del _2
    gc.collect()
    cluster = pd.read_pickle(cluster_result_path)
    uids = [x[0] for x in cluster.items()]
    profiles = [x[1] for x in cluster.items()]
    cluster_profile = pd.merge(cluster, pd.DataFrame({'uid':uids, 'profile': profiles}), on='uid')
    if not os.path.exists(cluster_xls_path):
        os.mkdir(cluster_xls_path)
    label_average = dict()
    writer = pd.ExcelWriter(cluster_xls_path + '/cluster_result.xlsx')
    for i, label in enumerate(sorted(pd.unique(cluster_profile['label']))):
        label_i_data = cluster_profile[cluster_profile['label']==label]
        label_average.setdefault(i, dict())
        for profile in label_i_data['profile']:
            label_average[i].setdefault(profile, 0)
            label_average[i]['profile'] += label_i_data['profile'][profile] / label_i_data.shape[0]
        label_i_data.to_excel(writer, sheet_name='label%s' %i)
        writer.save()
    return label_average

def plot(label_average):
    counts = label_average
    for i, count in enumerate(counts.items()):
        interset_distrib = sorted(count.items(), key=lambda x: x[1], reverse=True)[0:10]
        fig = plt.figure(i)
        x = np.arange(len(interset_distrib))
        plt.title(u'第%s类的平均感兴趣程度分布Top10' % i)
        plt.bar(x, [x[1] for x in interset_distrib])
        plt.xticks(x + 0.4, [x[0] for x in interset_distrib], size='large', rotation=20)
        for a, b in zip(x, [x[1] for x in interset_distrib]):
            plt.text(a + 0.05, b + 0.00001, '%.3f' % b, ha='left', va='bottom', fontsize=13)
        plt.ylabel(u'平均感兴趣程度', fontsize=15)
        plt.ylim([0, 1])
        # user_number = int(f.readline().split(' ')[1]) + 1
        # plt.text(a - 0.1, 1 + 0.01, u'用户数：%s' % user_number, fontsize=14)
        print(interset_distrib)
        fig.savefig(u'./result/第%s类的平均感兴趣程度分布Top10' % i)
    plt.show()





if __name__=='__main__':
    label_average = merge_result()
    plot(label_average)


