from igraph import Graph
import igraph as ig
import pandas as pd
import numpy as np
from itertools import chain
from polarization import calc_polarization
from leadership_insularity import calc_leadership_insularity 
import pickle
import os.path

graph_pickle_file = '../graphs/lbxd_reviewer_x_reviewer.pickle'
clusters_pickle_file = '../graphs/lbxd_clusters.pickle'

with open(graph_pickle_file, 'rb') as handle:
    g = pickle.load(handle)

with open(clusters_pickle_file, 'rb') as handle:
    clusters = pickle.load(handle)

with open('../data/cluster_to_unique_movie_count.pickle', 'rb') as handle:
    cluster_to_unique_movie_count = pickle.load(handle)

with open('../data/cluster_to_movie_count.pickle', 'rb') as handle:
    cluster_to_movie_count = pickle.load(handle)

unique_clusters = np.array(range(0,len(clusters)))
membership = np.array(clusters.membership)

# Calculate local transitivity (clustering coefficient) for each vertex in each cluster
# Create cluster_to_transitivity mapping
cluster_to_transitivity = {}
subgraphs = clusters.subgraphs()
for c in unique_clusters:
    idx = membership == c
    cluster_to_transitivity[c] = subgraphs[c].transitivity_undirected(mode="zero")

leadership_insularity, pairwise_leadership_insularity = calc_leadership_insularity(g,clusters)
polarization_matrix = calc_polarization(g,clusters)

# Convert global clustering metrics into cluster-averaged lists for DataFrame building
cluster_to_transitivity_list = list(cluster_to_transitivity.values())
avg_polarization_by_cluster = np.nanmean(polarization_matrix,axis=1)
cluster_to_polarization_list = avg_polarization_by_cluster.tolist()
avg_leadership_insularity_by_cluster = np.nanmean(pairwise_leadership_insularity,axis=1)
cluster_to_leadership_insularity_list = avg_leadership_insularity_by_cluster.tolist()


# Begin to create pandas dataframe of data organized by cluster
sizes_list = clusters.sizes()
unique_movie_count_list = list(cluster_to_unique_movie_count.values())
movie_count_list = list(cluster_to_movie_count.values())

cluster_df = pd.DataFrame(list(zip(unique_clusters,
                                   sizes_list,
                                   unique_movie_count_list,
                                   movie_count_list,
                                   cluster_to_transitivity_list,
                                   cluster_to_polarization_list,
                                   cluster_to_leadership_insularity_list)),
                                   columns=['cluster_id',
                                            'size',
                                            'unique_movie_count',
                                            'movie_count_list',
                                            'transitivity',
                                            'avg_polarization',
                                            'avg_leadership_insularity'])

cluster_df.to_csv('../data/clusters_df.csv',index=False)