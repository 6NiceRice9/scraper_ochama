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
    parents_and_children = raw_json[
        raw_json['id'].isin(raw_json['parentId'])]  # select: parents and _children == exclude groups
    parents = raw_json[
        raw_json['id'].isin(parents_and_children['parentId'])]  # select: parents == exclude chiren and groups
    excluded_groups = raw_json[~raw_json['parentId'].isin(
        raw_json['id'])]  # select: id_parent which are not in id_ == parents and matches without parents
    groups_without_parents = excluded_groups[
        ~excluded_groups['id'].isin(parents['id'])]  # select: id_parent wouthout parents
    children = parents_and_children[parents_and_children['parentId'].isin(parents['id'])]  # select:
    group = raw_json[~raw_json["id"].isin(parents_and_children["id"])]
    group = group[~group["id"].isin(groups_without_parents["id"])]
    return parents, children, group, groups_without_parents


def search_results(searching_term: str, parents: pd.DataFrame, children: pd.DataFrame, groups: pd.DataFrame) -> tuple[
    str, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """searching by: parent -> children -> groups
    :param searching_term: name of the main category
    :param parents: DataFrame with all parents
    :param children: DataFrame with all children
    :param groups: DataFrame with all groups"""
    _searching_term = searching_term
    looking_for_id_parent = parents[parents["name"] == searching_term].reset_index()  # parent row
    looking_for_children = children[
        children["parentId"].isin(looking_for_id_parent["id"])].reset_index()  # matching children to parent id
    looking_for_groups = groups[
        groups["parentId"].isin(looking_for_children["id"])].reset_index()  # match groups to children and parent
    return searching_term, looking_for_id_parent, looking_for_children, looking_for_groups


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

def all_products_incl_promo_optimized(header_received) -> pd.DataFrame:
    """Nesting out the Promocoded from the 'promoList' column with optimized approach."""
    header_received_list = header_received.json()["content"]

    all_rows = pd.DataFrame()  # A list to collect DataFrame rows
    # Iterate over each item in the content list
    for item in header_received_list:
        _row_in_main_table = pd.json_normalize(item).reset_index(drop=True)
        #original: _row_in_promoList = pd.json_normalize(item.get('promoList', [])).reset_index(drop=True)  # Use .get for safer access
        #original: merged = pd.concat([_row_in_main_table, _row_in_promoList], axis=1)
        #original: all_rows = all_rows._append(merged, ignore_index=False)
        all_rows = all_rows._append(_row_in_main_table, ignore_index=False)
#NEED ATTENTION, BECAUSE NO PROMOLIST INCLUDED    #print(all_rows)
   # _all_products = pd.concat(all_rows, ignore_index=True)
    return all_rows


tree_path: str = 'ochama_structure.txt'
with open(tree_path, 'r') as f:
    raw_json: pd.DataFrame = pd.json_normalize(json.loads(f.read()))
raw_json.drop(columns=["children", "backgroundImg", "sort", "imageUrl"], inplace=True)  # remove unneeded columns

#  %%%% separated groups
parents, _children, _groups, _groups_without_parents = split_in_groups(raw_json)

#  %% looping here through all categories
search_category = ["World Food", "Food", "Fresh", "Frozen", "Beverage", "Electronics", "Home Appliances", "Home Living", "Household", "Health", "Beauty", "Global", "Pre-order"]
all_group_ids_matching_search_criteria = pd.DataFrame()
template_search_result_groupsgroups = pd.DataFrame()

max_outer_loop_steps = 0
max_inner_loop_steps = 0
current_outer_loop = 0
total_n_steps = 0
current_inner_loop = 0
reduced_category = 0

for f in range(1, len(search_category)-reduced_category):  # search_category: "-11" to avoid "Global"
    search_term = search_category[f]
    a, b, c, template_search_result_groupsgroups = search_results(search_term, parents, _children, _groups)
    all_group_ids_matching_search_criteria = pd.concat([all_group_ids_matching_search_criteria, template_search_result_groupsgroups], ignore_index=True)
####### all_group_ids_matching_search_criteria = all_group_ids_matching_search_criteria.extend(template_search_result_groupsgroups)
####### request website for results & save after each iteration after one category iteration to txt file
    website_response_all_info = pd.DataFrame()
    max_outer_loop_steps = len(search_category) - reduced_category   # left over steps
    max_inner_loop_steps = len(template_search_result_groupsgroups["id"])  # for the counter im terminal
    current_outer_loop += 1
    for i in range(0, len(template_search_result_groupsgroups["id"])):
        group_id = int(template_search_result_groupsgroups["id"].values[i])
        website_response_raw = header_request(group_id, page=1, pageSize=1000, sortType="sort_dredisprice_asc") # request website for results
        website_response_df = pd.DataFrame(website_response_raw.json()["content"])
        website_response_product_incl_promo = all_products_incl_promo_optimized(website_response_raw)  # all products incl. promo
        website_response_all_info = pd.concat([website_response_all_info, website_response_product_incl_promo], ignore_index=True) # merging all responses
        ##delay
        delay = random.uniform(1, 2)
        current_inner_loop += 1
        total_n_steps += 1
        print(f"Waiting {delay:.2f} seconds... categorys: {max_outer_loop_steps - 1}/{current_outer_loop} steps:{max_inner_loop_steps}/{current_inner_loop}, total steps: {total_n_steps}")
        time.sleep(2)
####### after looping over first category, saving file to txt
    current_inner_loop = 0  #reset inner loop timer
    file_path = "C:/Users/NiceRice/git/scraper_ochama/scraper_ochama/ochama_products"
    sheet_name = search_term
    website_response_all_info.to_csv(f"{sheet_name}.txt", index=False)
    print(f"Saved: {sheet_name}.txt\n"
          f"with the shape: {website_response_all_info.shape}")

