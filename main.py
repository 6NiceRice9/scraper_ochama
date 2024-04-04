import json
import pandas as pd  # for working with dataframes
import requests  # for sending POST requests


# Categorize all items by their level.
def group_by_level(tree_data: pd.DataFrame, level: int) -> dict:
    """
    Function to categorize all items by their level.
    :param tree_data: raw loaded file input
    :param level: group level (1, 2 or 3)
    :return: nested dictionary
    """
    nested_all: dict = {level: group for level, group in tree_data.groupby('level')}
    return nested_all


def link_tree(group_id: int) -> tuple:
    """Function to link a group to its parent and child, returning a tuple of their IDs."""
    try:
        # Attempt to find the child and parent for the specified group.
        child_id: int = int(nested_all[3].loc[nested_all[3]['id'] == group_id, 'parentId'].values[0])
        parent_id: int = int(nested_all[2].loc[nested_all[2]['id'] == child_id, 'parentId'].values[0])
        return parent_id, child_id, group_id
    except IndexError:  # Handle cases where the group does not have a parent or child.
        return None, None, group_id


# Apply the function to all groups in level 3.
def all_group_ids(nested_all: dict) -> dict:
    group_ids: list = nested_all[3]['id'].values
    groups_connected: dict = {group_id: link_tree(group_id) for group_id in group_ids}
    return groups_connected


# % getting the valeus by id
def all_values_by_id(id: int, header: str):
    """
    Function to get the values of a column by ID.
    :param id: group_id from the deepest level
    :param header: column header
    :return header value at given id
    """
    public = nested_all
    value = None  # Initialize value as None to indicate "not found" by default
    for i in range(1, 4):
        df = nested_all.get(i)  # Safely get the DataFrame for key `i`
        if df is not None:
            # Attempt to filter the DataFrame based on the `id`
            filtered_df = df[df["id"] == id]
            if not filtered_df.empty:
                # If the filtered DataFrame is not empty, attempt to get the value
                value = filtered_df[header].iloc[0]
                break  # Exit the loop after finding the first match
    return value


################# Start of the main program #################
# Load the tree structure from a JSON file.
tree_path: str = 'ochama_structure.txt'  # Define the file path.
with open(tree_path, 'r') as f:
    tree_data: pd.DataFrame = pd.json_normalize(json.load(f))  # Directly normalize the JSON to a pandas DataFrame.

# create a dictionary of all groups
nested_all: dict = group_by_level(tree_data, 3)  # asumption total of 3 levels deep

# create connceted groups
groups_connected: dict = all_group_ids(nested_all)

# % make dictionary

# print(all_values_by_id(4808, "name"))
# print(all_values_by_id(4808, "imageUrl"))

# % preparing request
group_ids: list = nested_all[3]['id'].values
rows = []
for i in range(1, len(group_ids)):
    group_id = int(group_ids[i])
    try:
        child_id = all_values_by_id(group_id, "parentId")
    except TypeError:
        child_id = None
    try:
        parent_id = all_values_by_id(child_id, "id")
    except TypeError:
        parent_id = None

    row = {
        "id_parent": all_values_by_id(parent_id, "id"),
        "id_child": all_values_by_id(child_id, "id"),
        "id_group": all_values_by_id(group_id, "id"),
        "name_parent": all_values_by_id(parent_id, "name"),
        "name_child": all_values_by_id(child_id, "name"),
        "name_group": all_values_by_id(group_id, "name"),
        "url": all_values_by_id(group_id, "imageUrl")
    }
    rows.append(row)
# Convert the list of dictionaries to a DataFrame
overview = pd.DataFrame(rows,
                        columns=["id_parent", "id_child", "id_group", "name_parent", "name_child", "name_group", "url"])
overview.fillna(0, inplace=True)  # replaceing NaN
overview["id_parent"] = overview["id_parent"].astype(int)  # convert to int
overview["id_child"] = overview["id_child"].astype(int)  # convert to int

# %%% request overview table
print(overview["name_group"].loc[overview["id_group"] == 5121])


# %%%%% request website

def header_request(group_id, page=1, pageSize=1000,
                   sortType=("rank", "sort_totalsales15_desc", "sort_dredisprice_asc", "sort_discount_asc")):
    """
    :param group_id:
    :param page:
    :param pageSize:
    :param sortType:
    "Feature" = rank
    "Bestsellers" = sort_totalsales15_desc
    "Price" = sort_dredisprice_asc (=lowest on top) / sort_dredisprice_desc (=highest on top)
    "Promotion" = sort_discount_asc
    :return:
    """
    headers = {
        "Content-type": "application/json",
    }
    data = {"categoryId": group_id,
            "page": page,
            "pageSize": pageSize,
            "sortType": sortType
            }
    # request to the page
    request = requests.post('https://www.ochama.com/api/v1/category/aggregate/sku', headers=headers,
                            json=data)  # the right way to send POST requests
    return request.json()

#%% saving request data
# preparing request data



raw_data = header_request()