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

print(enumerate(df_parent_id))
# organize list
all_in: list = []
for cont, i in enumerate(data):
    name = i["name"]
    id_parent = i["parentId"]
    id_child = i["id"]
    print(cont, i)
    #print(df_parent_id)
   # all_in[df_parent_id] = [id_parent, id_child, name]
    #df_parent_id += 1
print(len(df_parent_id))

