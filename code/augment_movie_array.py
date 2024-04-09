import pandas as pd
import numpy as np

# clusters_df is a C x N dataframe where C is the number of clusters and N is the number of features for that cluster
clusters_df = pd.read_csv('../data/clusters_df.csv',encoding = 'ISO-8859-1')
clusters_df['avg_polarization'] = clusters_df['avg_polarization'].fillna(0)
clusters_mat = clusters_df.iloc[:,1:].to_numpy()

# movie_to_cluster_df is a T x C dataframe where T is the number of titles and C is the number of clusters
movie_to_cluster_df = pd.read_csv('../data/movie_encoding_norm_cols.csv',encoding = 'ISO-8859-1')
movie_to_cluster_matrix = np.transpose(movie_to_cluster_df.iloc[:,1:].to_numpy())

# [T x C] x [C x N] = [T x N] which is a matrix indexed by title with columns corresponding
# to a weighted average of cluster statistics for the clusters in which this title appears
movie_to_cluster_stats_mat = np.matmul(movie_to_cluster_matrix, clusters_mat)

# movies_df is a T x M dataframe where T is the number of titles and M is the number of movie features
movies_df = pd.read_csv('../data/movies_earnings.csv', encoding = 'ISO-8859-1')
movies_df['avg_cluster_size'] = movie_to_cluster_stats_mat[:,0].tolist()
movies_df['avg_cluster_unique_movie_count'] = movie_to_cluster_stats_mat[:,1].tolist()
movies_df['avg_cluster_movie_count'] = movie_to_cluster_stats_mat[:,2].tolist()
movies_df['avg_cluster_transitivity'] = movie_to_cluster_stats_mat[:,3].tolist()
movies_df['avg_cluster_polarization'] = movie_to_cluster_stats_mat[:,4].tolist()
movies_df['avg_cluster_leadership_insularity'] = movie_to_cluster_stats_mat[:,5].tolist()
movies_df['title'] = movies_df['vertex_name']
movies_df['movie_earnings'] = movies_df['movie_earnings'].str.replace(r'\$|,', '', regex=True).astype('float')

final_movies_df = movies_df[['title',
                            'movie_earnings',
                            'avg_cluster_size',
                            'avg_cluster_movie_count',
                            'avg_cluster_unique_movie_count',
                            'avg_cluster_transitivity',
                            'avg_cluster_polarization',
                            'avg_cluster_leadership_insularity']]

final_movies_df.to_csv('../data/movie_cluster_data.csv',index=False)