from igraph import Graph
import igraph as ig
import pandas as pd

df_lbxd_edges = pd.read_csv('./data/lbxd_edges.csv')
df_lbxd_vertices = pd.read_csv('./data/lbxd_vertices.csv')
g_lbxd = Graph.DataFrame(df_lbxd_edges, directed=True,vertices=df_lbxd_vertices)

ig.plot(g_lbxd,target='lbxd_1.pdf')