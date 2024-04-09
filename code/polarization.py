import numpy as np
import igraph as ig

def calc_polarization(g, clusters):

    membership = np.array(clusters.membership)
    crossing = clusters.crossing()
    # Create B matrix which is [n_clusters x n_clusters] where index (i,j) contains a set
    # vertices where all members of the set satisfy two conditions:
    # 1. A node v in cluster_i has at least one edge connecting to cluster_j
    # 2. A node v in cluster_i has at least one edge connecting to cluster_i which is not 
    #    connected to cluster_j
    B = np.array([set() for _ in range(np.square(len(clusters)))]).reshape(len(clusters), len(clusters))

    crossing_es = []
    for i,v in enumerate(crossing):
        if v:
            crossing_es.append(g.es[i])

    edge_to_cluster_dict = {}
    for e in crossing_es:
        edge_to_cluster_dict[e] = (membership[e.source],membership[e.target])
    cluster_to_set = {}
    for (i,c) in enumerate(clusters):
        cluster_to_set[i] = set(c)

    for k,(i,j) in edge_to_cluster_dict.items():

        # Evaluate the vertices on either end of edge k
        vertex_1 = k.source
        vertex_2 = k.target
        neighbors_vertex_1 = g.neighbors(vertex_1)
        neighbors_vertex_2 = g.neighbors(vertex_2)

        # does vertex_1 belong to cluster i or j?
        cluster_of_vertex_1 = membership[vertex_1]
        cluster_of_vertex_2 = membership[vertex_2]

        # In (i,j) ordering
        for candidate_vertex in neighbors_vertex_1:
            if candidate_vertex in clusters[cluster_of_vertex_1]:
                candidate_vertex_neighbors = set(g.neighbors(candidate_vertex))
                # True iff vertex_1 has a neighbor in cluster_i that is not adjacent to cluster_j
                condition_2 = len(cluster_to_set[cluster_of_vertex_2].intersection(candidate_vertex_neighbors)) == 0
                if condition_2:
                    B[cluster_of_vertex_1,cluster_of_vertex_2].add(vertex_1)
                    break
        
        # In (j,i) order
        for candidate_vertex in neighbors_vertex_2:
            if candidate_vertex in clusters[cluster_of_vertex_2]:
                candidate_vertex_neighbors = set(g.neighbors(candidate_vertex))
                # True iff vertex_1 has a neighbor in cluster_i that is not adjacent to cluster_j
                condition_2 = len(cluster_to_set[cluster_of_vertex_1].intersection(candidate_vertex_neighbors)) == 0
                if condition_2:
                    B[cluster_of_vertex_2,cluster_of_vertex_1].add(vertex_2)
                    break

    # Create I array which are nodes from cluster_i which do not belong to B_i_j and 
    # are named *internal* nodes
    # This array has shape (n_clusters,)
    I = np.array([set() for _ in range(np.square(len(clusters)))]).reshape(len(clusters), len(clusters))
    for i,c1_v in enumerate(list(cluster_to_set.values())):
        for j in range(len(clusters)):
            I[i,j] = c1_v.difference(B[i,j])

    # Find d_i(v) and d_b(v) for each node on the boundary, that is, each entry in B
    # d_i(v) is the number of edges that connect that boundary vertex back to internal vertices
    # d_b(v) is the number of edges that connect that boundary vertex to the other cluster
    D = np.array([np.nan for _ in range(np.square(len(clusters)))]).reshape(len(clusters), len(clusters))
    for i in range(len(clusters)):
        for j in range(len(clusters)):
            s = B[i,j]
            if len(s) > 0:
                cum_sum = 0
                for v in s:
                    neighbors_idx = set(g.neighbors(v))
                    d_b = len(neighbors_idx.intersection(cluster_to_set[j]))
                    d_i = len(neighbors_idx.intersection(I[i,j]))
                    cum_sum = cum_sum + ((d_i/(d_i + d_b)) - 0.5)
                D[i,j] = cum_sum / len(s)

    return D
