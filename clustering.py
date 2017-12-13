#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Juanjo Sierra
"""

import time
import seaborn as sns
import pandas as pd
import os

from sklearn.cluster import KMeans, DBSCAN, Birch, SpectralClustering, AgglomerativeClustering
from sklearn import metrics
from sklearn import preprocessing

from math import floor

# Function that preprocesses the given dataset, and then applies five clustering
# algorithms calculating their execution time, Calinski-Harabaz and Silhouette
# scores and saves their scatter matrix in a 'plots' directory in png format,
# using the given dataset name combined with the algorithm name as file name.
# If the dataset's size is under 100 samples, it also saves a heatmap and dendrogram
# for each algorithm.
def ClusteringAlgorithms(dataset, dataset_name):

    # Normalization of the dataset
    normalized_dataset = preprocessing.normalize(dataset, norm='l2')

    # K-Means
    k_means = KMeans(init='k-means++', n_clusters=4, n_init=5)

    # DBSCAN
    dbscan = DBSCAN(eps=0.1)

    # Birch
    birch = Birch(threshold=0.1, n_clusters=4)

    # Spectral Clustering
    spectral = SpectralClustering(n_clusters=4)

    # Ward
    hierarchical_clusters = 100
    half_dataset_size = floor(dataset.shape[0]/2)
    if hierarchical_clusters > half_dataset_size:
        hierarchical_clusters = half_dataset_size

    ward = AgglomerativeClustering(n_clusters=hierarchical_clusters, linkage='ward')

    clustering_algorithms = [
        ("K-Means", k_means),
        ("DBSCAN", dbscan),
        ("Birch", birch),
        ("Spectral Clustering", spectral),
        ("Ward", ward)
    ]

    print("-----------------------{}-----------------------".format(dataset_name))

    for name, algorithm in clustering_algorithms:
        #print("{:20s}".format(name), end='')
        print("{} && ".format(name), end='')
        t1 = time.time()
        cluster_predict = algorithm.fit_predict(normalized_dataset)
        t2 = time.time() - t1
        k = len(set(cluster_predict))
        print("{} && ".format(k), end='')
        print("{:.3f} && ".format(t2), end='')
        #print("| k: {:3.0f}, ".format(k),end='')
        #print("{:0.3f} seconds, ".format(t2),end='')
        if (k>1) and (name is not "Ward"):
            metric_CH = metrics.calinski_harabaz_score(normalized_dataset, cluster_predict)
            metric_SC = metrics.silhouette_score(normalized_dataset, cluster_predict, metric='euclidean', sample_size=floor(0.1*len(normalized_dataset)), random_state=123456)
        else:
            metric_CH = 0
            metric_SC = 0
        #print("CH Index: {:9.3f}, ".format(metric_CH),end='')
        #print("SC: {:.5f}".format(metric_SC))
        print("{:.3f} && ".format(metric_CH), end='')
        print("{:.5f}".format(metric_SC))

        # Assignment gets turned into DataFrame
        column_name = name + " clusters"
        clusters = pd.DataFrame(cluster_predict,index=dataset.index,columns=[column_name])

        # Clusters column gets added to dataset
        modified_dataset = pd.concat([dataset, clusters], axis=1)

        # Define directory path
        script_dir = os.path.dirname(__file__)

        if (dataset.shape[0] > 100):
            # And now scatter matrix is generated with the appended dataset
            sns.set()
            variables = list(modified_dataset)
            variables.remove(column_name)
            sns_plot = sns.pairplot(modified_dataset, vars=variables, hue=column_name, palette='Paired', plot_kws={"s": 25}, diag_kind="hist")
            sns_plot.fig.subplots_adjust(wspace=.03, hspace=.03);

            # Directory is created if does not exist
            plot_dir = os.path.join(script_dir, 'plots/')
            plot_name = name+"-"+dataset_name+"-ScatterMatrix.png"

            if not os.path.isdir(plot_dir):
                os.makedirs(plot_dir)

            # File plot is saved in 'plots' directory
            sns_plot.savefig(plot_dir + plot_name)

        else:
            # Heatmap
            sns.set()
            heatmap = sns.heatmap(modified_dataset)
            heatmap_fig = heatmap.get_figure()

            heatmap_dir = os.path.join(script_dir, 'heatmaps/')
            heatmap_name = name+"-"+dataset_name+"-Heatmap.png"

            if not os.path.isdir(heatmap_dir):
                os.makedirs(heatmap_dir)

            heatmap_fig.savefig(heatmap_dir + heatmap_name)
