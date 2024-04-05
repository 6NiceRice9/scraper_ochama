import json
from typing import Tuple, Any

import pandas as pd  # for working with dataframes
import requests  # for sending POST requests
import numpy as np
import time
import random
from openpyxl import load_workbook


def split_in_groups(raw_json: pd.DataFrame):
    """Data sorting based on "id" (find groups without children/parents)
    :param raw_json: DataFrame of raw imported data"""
    _parents_and_children = raw_json[
        raw_json['id'].isin(raw_json['parentId'])]  # select: parents and _children == exclude groups
    _parents = raw_json[
        raw_json['id'].isin(_parents_and_children['parentId'])]  # select: _parents == exclude chiren and groups
    _excluded_groups = raw_json[~raw_json['parentId'].isin(
        raw_json['id'])]  # select: id_parent which are not in id_ == _parents and matches without _parents
    _groups_without_parents = _excluded_groups[
        ~_excluded_groups['id'].isin(_parents['id'])]  # select: id_parent wouthout _parents
    _children = _parents_and_children[_parents_and_children['parentId'].isin(_parents['id'])]  # select:
    _groups = raw_json[~raw_json["id"].isin(_parents_and_children["id"])]
    _groups = _groups[~_groups["id"].isin(_groups_without_parents["id"])]
    return _parents, _children, _groups, _groups_without_parents


def search_results(searching_term: str, parents: pd.DataFrame, children: pd.DataFrame, groups: pd.DataFrame) -> tuple[
    str, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """searching by: parent -> children -> groups
    :param searching_term: name of the main category
    :param parents: DataFrame with all parents
    :param children: DataFrame with all children
    :param groups: DataFrame with all groups"""
    _searching_term = searching_term
    _looking_for_id_parent = parents[parents["name"] == searching_term].reset_index()  # parent row
    _looking_for_children = children[
        children["parentId"].isin(_looking_for_id_parent["id"])].reset_index()  # matching children to parent id
    _looking_for_groups = groups[
        groups["parentId"].isin(_looking_for_children["id"])].reset_index()  # match groups to children and parent
    return searching_term, _looking_for_id_parent, _looking_for_children, _looking_for_groups


def header_request(id_group: int, page=1, pageSize=1000, sortType="sort_dredisprice_asc") -> Any:
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

def all_products_incl_promo(header_received) -> pd.DataFrame:
    """Nesting out the Promococed from the "promoList" column"""
    _header_received_list = header_received.json()["content"]

    _all_products = pd.DataFrame()
    # Iterate over each item in the content list
    for i in _header_received_list:
        _row_in_main_table = pd.json_normalize(i)
        _row_in_promoList = pd.json_normalize(i['promoList'])
        _merged = pd.concat([_row_in_main_table, _row_in_promoList], axis=1)
        _all_products: pd.DataFrame = _all_products._append(_merged)

    return _all_products


tree_path: str = 'ochama_structure.txt'
with open(tree_path, 'r') as f:
    raw_json: pd.DataFrame = pd.json_normalize(json.loads(f.read()))
raw_json.drop(columns=["children", "backgroundImg", "sort", "imageUrl"], inplace=True)  # remove unneeded columns

#  %%%% separated groups
_parents, _children, _groups, _groups_without_parents = split_in_groups(raw_json)

# %%
search_term = "Fresh"
_, _, _, template_search_result_groupsgroups = search_results(search_term, _parents, _children, _groups)
#%%
#all_requests = pd.DataFrame()
for i in range(30, len(template_search_result_groupsgroups["id"])):
    group_id = int(template_search_result_groupsgroups["id"].values[i])
    website_response_raw = header_request(group_id, page=1, pageSize=1000, sortType="sort_dredisprice_asc") # request website for results
    website_response_df = pd.DataFrame(website_response_raw.json()["content"])
    website_response_product_incl_promo = all_products_incl_promo(website_response_raw)  # all products incl. promo
    website_response_all_info = pd.concat([website_response_df, website_response_product_incl_promo], ignore_index=True) # merging all responses
    ##delay
    delay = random.uniform(2, 5)
    print(f"Waiting {delay:.2f} seconds...")
    time.sleep(5)

# %%

file_path = "C:/Users/NiceRice/git/scraper_ochama/scraper_ochama/ochama_products.xlsx"
sheet_name = search_term
website_response_all_info.to_csv(f"{sheet_name}.txt", index=False)

# %%
group_id = 5099
