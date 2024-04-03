import requests
import json
import numpy as np
import pandas as pd
import flatdict as fd
import itertools


# load tree for POST request
with open('C:\\Users\\NiceRice\\git\\scraper_ochama\\scraper_ochama\\ochama_structure.txt') as f:
    all_in: list = json.load(f)       # convert
    all_in: dict = all_in[:]          # convert

#### organise structure
# flatten
all: pd.DataFrame = pd.json_normalize(all_in)
# get parents overview
parents_overview: pd.DataFrame = all.loc[all['parentId'] == 0]
# child overview
child_overview = all[all['parentId'].isin(parents_overview['id'])]
# sub_child_sorting_overview
sub_child_sorting_overview = all[all['parentId'].isin(child_overview['id'])]





#%%
for i in parents_id.loc[:, "id"]:   #parents loop
    for j in all[all['parentId'] == i]:       #child loop
        trash.append(all[all['id'] == j])
        print(i)
#matches = all[all['parentId'] == 4722]

#%%
import pandas as pd

# Sample data for df1
data1 = {
    'ID': [1, 2, 3, 4, 5],
    'Value': ['A', 'B', 'C', 'D', 'E']
}
df1 = pd.DataFrame(data1)

# Sample data for df2
data2 = {
    'ID': [2, 4]
}
df2 = pd.DataFrame(data2)

# Selecting rows from df1 where IDs match those in df2
matched_df = df1[df1['ID'].isin(df2['ID'])]

print(matched_df)


#%%
for i in parents_id.loc[:, "id"]:   #parents loop
    for j in all.loc[:, "id"]:       #child loop
        trash.append(i)



#%% working section
# generate parent id list
df_parent_id: list = []
for i in post_data:
    id_parent = i["parentId"]
    df_parent_id.append(id_parent)






#pandas df
df_pandas = pd.DataFrame()



# organize list
all_in: list = []
for cont, i in enumerate(post_data):
    name = i["name"]
    id_parent = i["parentId"]
    id_child = i["id"]



print(len(df_parent_id))

