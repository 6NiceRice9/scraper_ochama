import json
import pandas as pd  # for working with dataframes
import requests  # for sending POST requests
import time
import random

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


def link_tree(id_group: int) -> tuple:
    """Function to link a group to its parent and child, returning a tuple of their IDs."""
    try:
        # Attempt to find the child and parent for the specified group.
        id_child: int = int(nested_all[3].loc[nested_all[3]['id'] == id_group, 'parentId'].values[0])
        id_parent: int = int(nested_all[2].loc[nested_all[2]['id'] == id_child, 'parentId'].values[0])
        return id_parent, id_child, id_group
    except IndexError:  # Handle cases where the group does not have a parent or child.
        return None, None, id_group


# Apply the function to all groups in level 3.
# def all_group_ids(nested_all: dict) -> dict:
#     ids_group_all: list = nested_all[3]['id'].values
#     groups_connected: dict = {id_group: link_tree(id_group) for id_group in ids_group_all}
#     return groups_connected


# % getting the valeus by id_any
def all_values_by_id(id_any: int, header: str):
    """
    Function to get the values of a column by ID.
    :param id_any: id_group from the deepest level
    :param header: column header
    :return header value at given id
    """
    public = nested_all
    value = None  # Initialize value as None to indicate "not found" by default
    for i in range(1, 4):
        df = nested_all.get(i)  # Safely get the DataFrame for key `i`
        if df is not None:
            # Attempt to filter the DataFrame based on the `id`
            filtered_df = df[df["id"] == id_any]
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
# groups_connected: dict = all_group_ids(nested_all)

# % make dictionary

# print(all_values_by_id(4808, "name"))
# print(all_values_by_id(4808, "imageUrl"))

# % preparing request
ids_group_all: list = nested_all[3]['id'].values[:]
rows_template = []
for i in range(1, len(ids_group_all)):
    id_group = int(ids_group_all[i])
    try:
        id_child = all_values_by_id(id_group, "parentId")
    except TypeError:
        id_child = None
    try:
        id_parent = all_values_by_id(id_child, "parentId")
    except TypeError:
        id_parent = None

    row_template = {
        "id_parent": all_values_by_id(id_parent, "id"),
        "id_child": all_values_by_id(id_child, "id"),
        "id_group": all_values_by_id(id_group, "id"),
        "name_parent": all_values_by_id(id_parent, "name"),
        "name_child": all_values_by_id(id_child, "name"),
        "name_group": all_values_by_id(id_group, "name"),
        "url": all_values_by_id(id_group, "imageUrl")
    }
    rows_template.append(row_template)
# Convert the list of dictionaries to a DataFrame
overview_template = pd.DataFrame(rows_template,
                                 columns=["id_parent", "id_child", "id_group", "name_parent", "name_child",
                                          "name_group", "url"])
overview_template.fillna(0, inplace=True)  # replaceing NaN
overview_template["id_parent"] = overview_template["id_parent"].astype(int)  # convert to int
overview_template["id_child"] = overview_template["id_child"].astype(int)  # convert to int


#  %%%% request overview_template table
# print(overview_template["name_group"].loc[overview_template["id_group"] == 5121])

# filter for value
# search_value = "Fresh"
# filtered_df = overview_template[overwiew['name_child'] == search_value]
#  %%%%% request website
def header_request(id_group, page=1, pageSize=1000, sortType="sort_dredisprice_asc"):
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

    request = requests.post('https://www.ochama.com/api/v1/category/aggregate/sku', headers=headers,
                            json=data)  # the right way to send POST requests
    return request.json()


#  %%% saving request data
# preparing request data
#  %%% ID_GROUP HAS TO BE ADJUSTED
# received_raw_data = header_request(5637, 1, 100, "rank")

# %% loop over all "id_groups"
test = []
def map_category_generater():
    mapping = {"Fresh": 4710, "World Food": 4712, "Electronics": 4718, "Food": 4722, "Household": 4763,
               "Health, Beauty": 4777, "Home Appliances": 4883, "Frozen": 4917, "Beverage": 4929, "Global": 5367,
               "Pre-Prder": 5458, "Home Living": 5493 }
    for key, value in mapping.items():
        yield (key, value)

###%%%%%%%%%%%%%%%%%%%%%%%% acess map_categorys by map_categorys[0][:] and use it in map_category function  AND use then use map cathegory in the for loop
map_categorys = list(map_category_generater())
#%%
map_category = {
    overview_template[(overview_template["id_parent"] == 4710) & (overview_template["name_parent"] == "Fresh")][
        "id_group"].values}
large_table = []
for i in range(len(overview_template[overview_template["id_parent"] == 4710])):
    try:
        received_raw_data = header_request(ids_group_all[i], 1, 100)  # add ids_group_all[i]
        large_table = [i, pd.DataFrame(received_raw_data['content'])]
    except:
        large_table.append([i, None])
    finally:
        delay = random.uniform(2, 5)
        print(f"Waiting {delay:.2f} seconds...")
        time.sleep(8)

# processed_data: pd.DataFrame = pd.DataFrame(received_raw_data['content'])
