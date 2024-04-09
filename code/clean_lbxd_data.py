import pandas as pd

df_orig = pd.read_csv('../data/letterboxd-reviews.csv',encoding='ISO-8859-1')

#Remove (year) from movie title to avoid duplicates
df_orig['Movie name'] = df_orig['Movie name'].str.replace(r"\(.*\)","") 
df_orig['Movie name'] = df_orig['Movie name'].str.strip()

edges_orig_df = df_orig[['Reviewer name', 'Movie name', 'Rating','Review','Comment count','Like count','Review date']]
vertices_df_orig = df_orig[['Movie name', 'Reviewer name']]

# Extract unique vertex names by stacking movie names on top of reviewer names and giving them unique indices
vertices_df_unclean = pd.concat([vertices_df_orig, vertices_df_orig.T.stack().reset_index(name='new')['new']], axis=1)
vertex_name_list = list(vertices_df_unclean["new"])
vertex_movie_null_idx = list(vertices_df_unclean["Movie name"].isnull().values)
vertex_type_list = ['reviewer' if v else 'movie' for v in vertex_movie_null_idx]
vertex_df = pd.DataFrame(list(zip(vertex_name_list,vertex_type_list)), columns = ['vertex_name','type'])
vertex_df = vertex_df.drop_duplicates()
vertex_df['vertex_id'] = pd.factorize(vertex_df['vertex_name'])[0]
vertex_df = vertex_df[['vertex_id','vertex_name','type']]

# Add vertex id to edge list
edges_reviewer_id_list = [vertex_df.vertex_id[vertex_df['vertex_name'] == r].values[0] for r in edges_orig_df['Reviewer name']]
edges_movie_id_list = [vertex_df.vertex_id[vertex_df['vertex_name'] == m].values[0] for m in edges_orig_df['Movie name']]

edges_id_df = pd.DataFrame(list(zip(edges_reviewer_id_list,edges_movie_id_list)), columns = ['reviewer_id','movie_id'])

edges_df = pd.concat([edges_id_df, edges_orig_df], axis=1).reindex(edges_id_df.index)

# Save off edges and vertices
edges_df.to_csv('../data/lbxd_edges.csv',index=False)
vertex_df.to_csv('../data/lbxd_vertices.csv',index=False)

