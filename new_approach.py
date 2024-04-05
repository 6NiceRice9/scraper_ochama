import json
import pandas as pd  # for working with dataframes
import requests  # for sending POST requests
import numpy as np
import time
import random

tree_path: str = 'ochama_structure.txt'
with open(tree_path, 'r') as f:
    raw_json: pd.DataFrame = pd.json_normalize(json.loads(f.read()))
raw_json.drop(columns=["children", "backgroundImg", "sort", "imageUrl"], inplace=True)

# %%
_parents_and_children = raw_json[raw_json['id'].isin(raw_json['parentId'])]              # select: parents and children == exclude groups
parents = raw_json[raw_json['id'].isin(_parents_and_children['parentId'])]               # select: parents == exclude chiren and groups
_excluded_groups = raw_json[~raw_json['parentId'].isin(raw_json['id'])]                  # select: id_parent which are not in id_ == parents and matches without parents
groups_without_parents = _excluded_groups[~_excluded_groups['id'].isin(parents['id'])]   # select: id_parent wouthout parents
children = _parents_and_children[_parents_and_children['parentId'].isin(parents['id'])]  # select:
_groups = raw_json[~raw_json["id"].isin(_parents_and_children["id"])]
groups = _groups[~_groups["id"].isin(groups_without_parents["id"])]


