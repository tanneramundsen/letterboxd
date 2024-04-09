from igraph import Graph
import igraph as ig
import pandas as pd
import numpy as np
import pickle

LOAD_GRAPH = 1
CREATE_GRAPH = 0
LOAD_CLUSTER = 1
CREATE_CLUSTER = 0


df_lbxd_edges = pd.read_csv('../data/lbxd_edges.csv')
df_lbxd_vertices = pd.read_csv('../data/lbxd_vertices.csv')

if CREATE_GRAPH:
    g_lbxd = Graph.DataFrame(df_lbxd_edges, directed=True,vertices=df_lbxd_vertices)

    ig.plot(g_lbxd,
            vertex_size=[10 if t=='reviewer' else 20 for t in g_lbxd.vs['type']],
            vertex_color=["steelblue" if t=="reviewer" else "salmon" for t in g_lbxd.vs['type']])

    # extract adajacency matrix of full matrix [(num_movies + num_reviewer) x (num_movies + num_reviewer)]
    full_x_full_mat = g_lbxd.get_adjacency()
    mat = np.array(full_x_full_mat.data)

    # extract adajacency matrix of reviewer x movie [num_reviewers x num_movies]
    vs_type = g_lbxd.vs['type']
    vs_id = g_lbxd.vs['vertex_id']
    vs_name = g_lbxd.vs['vertex_name']
    first_reviewer_index = vs_type.index('reviewer')
    reviewer_x_movie_mat = mat[first_reviewer_index:,:first_reviewer_index]

    # perform relationship algebra (reviewer_x_movie_mat @* reviewer_x_movie_mat.T) to get 
    # reviewer_x_reviewer_mat social network (undirected) of reviewers that have reviewed the same 
    # film. Dimension [num_reviewer x num_reviewer]
    reviewer_x_reviewer_mat = np.matmul(reviewer_x_movie_mat,np.transpose(reviewer_x_movie_mat))
    # Remove self-connections
    np.fill_diagonal(reviewer_x_reviewer_mat,0)

    g_lbxd_r_x_r = Graph.Adjacency(reviewer_x_reviewer_mat,mode="undirected")
    g_lbxd_r_x_r.vs['vertex_id'] = vs_id[first_reviewer_index:]
    g_lbxd_r_x_r.vs['vertex_name'] = vs_name[first_reviewer_index:]

    # Remove unconnected nodes
    to_delete_indices = [v.index for v in g_lbxd_r_x_r.vs if v.degree() == 0]
    to_delete_ids = [v['vertex_id'] for v in g_lbxd_r_x_r.vs if v.degree() == 0]
    g_lbxd_r_x_r.delete_vertices(to_delete_indices)

    ig.plot(g_lbxd_r_x_r, vertex_size=10)

    with open('../graphs/lbxd_reviewer_x_reviewer.pickle', 'wb') as handle:
        pickle.dump(g_lbxd_r_x_r, handle)

    with open('../graphs/lbxd_reviewer_x_movie.pickle', 'wb') as handle:
        pickle.dump(g_lbxd, handle)

    g = g_lbxd_r_x_r

if LOAD_GRAPH:
    # Optionally load in graphs if they have already been made above
    with open('../graphs/lbxd_reviewer_x_reviewer.pickle', 'rb') as handle:
        g = pickle.load(handle)

if CREATE_CLUSTER:
    # calculate dendrogram
    dendrogram = g.community_edge_betweenness()
    # convert it into a flat clustering
    clusters = dendrogram.as_clustering()

if LOAD_CLUSTER:
    with open('../graphs/lbxd_dendrogram.pickle', 'rb') as handle:
        g = pickle.load(handle)

# get the membership vector
membership = clusters.membership
# Color by membership
pal = ig.drawing.colors.ClusterColoringPalette(len(clusters))
g.vs['color'] = pal.get_many(membership)

ig.plot(g, vertex_size=10,layout="fruchterman_reingold")

membership = np.array(membership)
# Create a cluster to reviewer mapping mapping the cluster number to a list of
# the original vertex ids of each reviewer back in the original movie_x_reviewer_graph 
unique_clusters = np.unique(membership)
cluster_to_vertex_id = {}
vertex_ids_list = np.array(g.vs['vertex_id'])
for c in unique_clusters:
    idx = membership == c
    cluster_vertex_indices = vertex_ids_list[idx]
    cluster_to_vertex_id[c] = cluster_vertex_indices

# Create a cluster to movie mapping where the KEY is the cluster number and the 
# value is a one-dimensional numpy array of length N where N is the number of movies
# represented in this dataset.
#
# This array will have values that sum up to 1.
#
# The value in the i'th index of the array corresponds to the percentage of reviewers
# in this cluster who reviewed movie i

# explicit function to normalize array
# Code from GeeksforGeeks
def normalize(arr, t_min, t_max):
    norm_arr = []
    diff = t_max - t_min
    diff_arr = max(arr) - min(arr)   
    for i in arr:
        temp = (((i - min(arr))*diff)/diff_arr) + t_min
        norm_arr.append(temp)
    return norm_arr
 
range_to_normalize = (0,1)

cluster_to_movie_encoding = {}
cluster_to_unique_movie_count = {}
cluster_to_movie_count = {}
for c in unique_clusters:
    # Create numpy array of zeros the length of num_movies
    movie_array = np.zeros(first_reviewer_index)
    # iterate over reviewer vertex ids within this cluster
    for orig_r_id in cluster_to_vertex_id[c]:
        m_ids = df_lbxd_edges.movie_id[df_lbxd_edges.reviewer_id == orig_r_id]
        # (movie indices are zero indexed)
        movie_array[m_ids] = movie_array[m_ids] + 1
    
    cluster_to_movie_count[c] = np.sum(movie_array)
    cluster_to_unique_movie_count[c] = np.sum(movie_array != 0)
    l1_norm = np.linalg.norm(movie_array, ord=1)
    cluster_to_movie_encoding[c] = movie_array / l1_norm

with open('../data/cluster_to_unique_movie_count.pickle', 'wb') as handle:
    pickle.dump(cluster_to_unique_movie_count, handle)

with open('../data/cluster_to_movie_count.pickle', 'wb') as handle:
    pickle.dump(cluster_to_movie_count, handle)