import json
import pandas as pd  # for working with dataframes
import requests  # for sending POST requests
import numpy as np
import time
import random
from openpyxl import load_workbook
#%%

tree_path: str = 'ochama_structure.txt'
with open(tree_path, 'r') as f:
    raw_json: pd.DataFrame = pd.json_normalize(json.loads(f.read()))
raw_json.drop(columns=["children", "backgroundImg", "sort", "imageUrl"], inplace=True)


def split_in_groups(raw_json: pd.DataFrame):
    """Data sorting (find groups without children/parents)"""
    _parents_and_children = raw_json[
        raw_json['id'].isin(raw_json['parentId'])]  # select: parents and children == exclude groups
    parents = raw_json[
        raw_json['id'].isin(_parents_and_children['parentId'])]  # select: parents == exclude chiren and groups
    _excluded_groups = raw_json[~raw_json['parentId'].isin(
        raw_json['id'])]  # select: id_parent which are not in id_ == parents and matches without parents
    groups_without_parents = _excluded_groups[
        ~_excluded_groups['id'].isin(parents['id'])]  # select: id_parent wouthout parents
    children = _parents_and_children[_parents_and_children['parentId'].isin(parents['id'])]  # select:
    _groups = raw_json[~raw_json["id"].isin(_parents_and_children["id"])]
    groups = _groups[~_groups["id"].isin(groups_without_parents["id"])]
    return parents, children, groups, groups_without_parents


# groups
parents, children, groups, group_without_parent = split_in_groups(raw_json)

#### searching by: parent -> children -> groups
looking_for = "Fresh"
looking_for_id_parent = parents[parents["name"] == "Fresh"].reset_index()  # parent row
looking_for_children = children[
    children["parentId"].isin(looking_for_id_parent["id"])].reset_index()  # matching children to parent id
looking_for_groups = groups[groups["parentId"].isin(looking_for_children["id"])].reset_index()  # match groups to children and parent

# %%
# constructing tree

def header_request(id_group: int, page=1, pageSize=1000, sortType="sort_dredisprice_asc"):
    """
    :param id_group:
    :param page:
    :param pageSize:
    "Feature" = rank
    "Bestsellers" = sort_totalsales15_desc
    "Price" = sort_dredisprice_asc (=lowest on top) / sort_dredisprice_desc (=highest on top)
    "Promotion" = sort_discount_asc
    :return:
    """
    headers = {
        "Content-type": "application/json",
    }
    data = {"categoryId": id_group,
            "page": page,
            "pageSize": pageSize,
            "sortType": sortType
            }

    request = requests.post("https://www.ochama.com/api/v1/category/aggregate/sku", headers=headers,
                            json=data)  # the right way to send POST requests

    #separate nested promolist
    products = pd.json_normalize(request.json()["content"])
    promolist = [pd.json_normalize(item['promoList']) for item in request.json()['content']]
    return request
    #return pd.json_normalize(request.json()["content"])
    #%%

data = header_request(5099)
# Load the main data into a DataFrame
df = pd.DataFrame(data)

# Assuming each item in your main data list only contains one promoList,
# we can extract and normalize this nested structure like so:
promo_list_dfs = [pd.json_normalize(item['promoList']) for item in data.json()['content']]

# If you want to work with the first product's promoList as an example:
promo_df = promo_list_dfs[0]

print(promo_df)


#%%
all_requests = pd.DataFrame()
for i in range(30, len(looking_for_groups["id"])):
    group_id = int(looking_for_groups["id"].values[i])
    all_requests = pd.concat([all_requests, header_request(group_id)], ignore_index=True)
    ##delay
    delay = random.uniform(2, 5)
    print(f"Waiting {delay:.2f} seconds...")
    time.sleep(5)


#%%

file_path = "C:/Users/NiceRice/git/scraper_ochama/scraper_ochama/ochama_products.xlsx"
sheet_name = looking_for
all_requests.to_csv(f"{looking_for}.txt", index=False)


#%%
group_id = 5099
test_request = {group_id: header_request(group_id)}

#%% filter data
a = pd.DataFrame(test_request[group_id]["content"])
b = pd.DataFrame(test_request[group_id]["content"])[["price", "basePrice", "largeImg", "stock", 'skuName', "brandName", "fresh", "largeProduct"]]
