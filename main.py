import requests
import json
import numpy as np
import pandas as pd
import flatdict as fd


with open('C:\\Users\\NiceRice\\git\\scraper_ochama\\scraper_ochama\\ochama_structure.txt') as f:
    data: list = json.load(f)



# generate parent id list
df_parent_id: list = []
for i in data:
    id_parent = i["parentId"]
    df_parent_id.append(id_parent)

#pandas df
df_pandas = pd.DataFrame()
# organize list
all_in: list = []
for cont, i in enumerate(data):
    name = i["name"]
    id_parent = i["parentId"]
    id_child = i["id"]



print(len(df_parent_id))

