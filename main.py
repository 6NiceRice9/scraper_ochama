import requests
import json
import numpy as np
import pandas as pd

with open('C:\\Users\\NiceRice\\git\\scraper_ochama\\scraper_ochama\\ochama_structure.txt') as f:
    data: list = json.load(f)

# generate parent id list
df_parent_id: list = []
for i in data:
    id_parent = i["parentId"]
    df_parent_id.append(id_parent)

# organize list
all_in: dict = {}
for i in data:
    name = i["name"]
    id_parent = i["parentId"]
    id_child = i["id"]
    all_in["id_parent"] = {"id_parent": id_parent, "id_child": id_child, "name": name}

print(len(df_parent_id))

