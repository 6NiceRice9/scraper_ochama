import requests
import json
import numpy as np
import pandas as pd
import flatdict as fd
import itertools

# %%% load tree for POST request
with open('C:\\Users\\NiceRice\\git\\scraper_ochama\\scraper_ochama\\ochama_structure.txt') as f:
    all_in: list = json.load(f)  # convert
    all_in: dict = all_in[:]  # convert

# %%% organise structure
# flatten
all: pd.DataFrame = pd.json_normalize(all_in)
# get parents overview
parents_overview: pd.DataFrame = all.loc[all['parentId'] == 0]
# child overview
child_overview = all[all['parentId'].isin(parents_overview['id'])]
# group_overview
group_overview = all[all['parentId'].isin(child_overview['id'])]

# %%% select group
nested_all = {}
for i in all["level"].unique():
    nested_all[i] = all[all["level"] == i]


# %% link all groups together
# group = 4808  ## variable


def link_tree(group: int) -> tuple:
    try:
        child: pd.core.series.Series = nested_all[3].loc[nested_all[3]['id'] == group]["parentId"]  # get child
        child: int = int(child.values[0])  # convert from pd series to int
        parent = nested_all[2].loc[nested_all[2]['id'] == child]["parentId"]
        parent: int = int(parent.values[0])  # convert from pd series to int
        grouped = (parent, child, group)
    except:
        grouped = (None, None, group)  # some groups have no children/parents
    return grouped


get_groups = nested_all[3]["id"].values[:]
# print(len(get_groups))
# %%
# print(get_groups[:])
groups_connected = {}
i = 1
# %%
for i in range(1, len(get_groups)):
    # print(i, get_groups[i])
    try:
        groups_connected[int(get_groups[i])] = link_tree(get_groups[i])
    except:
        print("error")
    # groups_connected[get_groups[i]] = link_tree(get_groups[i])
# print(groups_connected)
