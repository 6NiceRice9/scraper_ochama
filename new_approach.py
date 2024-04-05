import json
from typing import Tuple, Any

import pandas as pd  # for working with dataframes
import requests  # for sending POST requests
import numpy as np
import time
import random
from openpyxl import load_workbook


def split_in_groups(raw_json: pd.DataFrame):
    """Data sorting (find groups without children/parents)
    :param raw_json: DataFrame of raw imported data"""
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


def search_results(searching_term: str, parents: pd.DataFrame, children: pd.DataFrame, groups: pd.DataFrame) -> tuple[
    str, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """searching by: parent -> children -> groups
    :param searching_term: name of the main category
    :param parents: DataFrame with all parents
    :param children: DataFrame with all children
    :param groups: DataFrame with all groups"""
    searching_term = searching_term
    looking_for_id_parent = parents[parents["name"] == searching_term].reset_index()  # parent row
    looking_for_children = children[
        children["parentId"].isin(looking_for_id_parent["id"])].reset_index()  # matching children to parent id
    looking_for_groups = groups[
        groups["parentId"].isin(looking_for_children["id"])].reset_index()  # match groups to children and parent
    return searching_term, looking_for_id_parent, looking_for_children, looking_for_groups


def header_request(id_group: int, page=1, pageSize=1000, sortType="sort_dredisprice_asc"):
    """
    :param id_group: group id that has to be scraped
    :param page: number of pages (less pages, when >> pageSize)
    :param pageSize: >>> value, to avoid scraping over several pages
    :param sortType:
        "Price" = sort_dredisprice_asc (=lowest on top) / sort_dredisprice_desc (=highest on top)
        "Feature" = rank
        "Bestsellers" = sort_totalsales15_desc
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
    return request


# %%
def all_products_incl_promo(header_received) -> pd.DataFrame:
    """Nesting out the Promococed from the "promoList" column"""
    header_received_list = header_received.json()["content"]

    all_products = pd.DataFrame()
    # Iterate over each item in the content list
    for i in header_received_list:
        row_in_main_table = pd.json_normalize(i)
        row_in_promoList = pd.json_normalize(i['promoList'])
        merged = pd.concat([row_in_main_table, row_in_promoList], axis=1)
        all_products: pd.DataFrame = all_products._append(merged)

    return all_products


tree_path: str = 'ochama_structure.txt'
with open(tree_path, 'r') as f:
    raw_json: pd.DataFrame = pd.json_normalize(json.loads(f.read()))
raw_json.drop(columns=["children", "backgroundImg", "sort", "imageUrl"], inplace=True)  # remove unneeded columns

#  %%%% separated groups
parents, children, groups, group_without_parent = split_in_groups(raw_json)

# %%
_, _, groups, _ = search_results("Fresh", parents, children, groups)

all_requests = pd.DataFrame()
for i in range(30, len(looking_for_groups["id"])):
    group_id = int(looking_for_groups["id"].values[i])
    all_requests = pd.concat([all_requests, header_request(group_id)], ignore_index=True)
    ##delay
    delay = random.uniform(2, 5)
    print(f"Waiting {delay:.2f} seconds...")
    time.sleep(5)

# %%

file_path = "C:/Users/NiceRice/git/scraper_ochama/scraper_ochama/ochama_products.xlsx"
sheet_name = looking_for
all_requests.to_csv(f"{looking_for}.txt", index=False)

# %%
group_id = 5099
