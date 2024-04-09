import numpy as np
import igraph as ig
from itertools import chain

def calc_leadership_insularity(g, clusters):
    
    N = len(g.vs)
    N_c = len(clusters)

    sizes = clusters.sizes()

    # find leader of each cluster.
    # "The community leaders were those nodes with the highest betweenness centrality when a community
    # was viewed as a graph, separate from the network as a whole."
    subgraphs = clusters.subgraphs()
    cluster_to_leader = {}
    for i, s_g in enumerate(subgraphs):
        orig_g_indices = np.array([v['orig_vertex_id'] for v in s_g.vs])
        s_g_betweenness = np.array(s_g.betweenness())
        leaders = np.argwhere(s_g_betweenness == np.amax(s_g_betweenness)).flatten().tolist()
        if len(leaders) == 1:
            cluster_to_leader[i] = orig_g_indices[leaders].tolist()[0]
        else:
            degree_of_leaders = np.array(s_g.vs[leaders].degree())
            tie_breakers = np.argwhere(degree_of_leaders == np.amax(np.array(s_g.vs[leaders].degree())))
            tie_breakers = list(chain.from_iterable(tie_breakers.tolist()))
            cluster_to_leader[i] = orig_g_indices[np.random.choice(tie_breakers,1)].tolist()[0]

    # Leadership insularity is undefined for disjoint communities so we will remove those communities
    # from the calculation
    cluster_subgraph = clusters.cluster_graph()
    disconnected_clusters = [v.index for v in cluster_subgraph.vs if v.degree() == 0]
    vertices_in_disconnected_clusters = [[v for v in clusters[d_c]] for d_c in disconnected_clusters]
    vertices_in_disconnected_clusters = list(chain.from_iterable(vertices_in_disconnected_clusters))

    # find average distance between any two members of communities
    mean_distance_between_communities = np.zeros((len(clusters),len(clusters)))
    distance_between_leaders = np.zeros((len(clusters),len(clusters)))

    shortest_paths = np.array(g.shortest_paths())
    for i, c1 in enumerate(clusters):
        if i not in disconnected_clusters:
            c1_leader_idx = cluster_to_leader[i]
            for j, c2 in enumerate(clusters):
                if j > i and j not in disconnected_clusters:
                    c2_leader_idx = cluster_to_leader[j]
                    mean_distance_between_communities[i,j] = np.average(shortest_paths[np.ix_(c1,c2)])
                    distance_between_leaders[i,j] = shortest_paths[c1_leader_idx,c2_leader_idx]
        else:
            mean_distance_between_communities[i,:] = np.Inf
            distance_between_leaders[i,:] = np.Inf
                    
    # Put it all together
    N_c_mod = N_c - len(disconnected_clusters)
    N_mod = N - len(vertices_in_disconnected_clusters)
    
    cum_sum = 0
    for i in range(0,N_c,1):
        for j in range(i+1,N_c,1):
            if i not in disconnected_clusters and j not in disconnected_clusters:
                cum_sum = cum_sum + distance_between_leaders[i,j] \
                    / mean_distance_between_communities[i,j] \
                    * (len(clusters[i]) + len(clusters[j]))

    return ((1/(2 * N_c_mod * N_mod)) * cum_sum)
    
