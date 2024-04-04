import json
import pandas as pd


# # Organize structure
# # Identify the parent and child relationships.
# parents_overview = tree_data[tree_data['parentId'] == 0]
# child_overview = tree_data[tree_data['parentId'].isin(parents_overview['id'])]
# group_overview = tree_data[tree_data['parentId'].isin(child_overview['id'])]

# Categorize all items by their level.
def group_by_level(tree_data: pd.DataFrame, level: int) -> dict:
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


# %% getting the valeus by id
def all_values_by_id(nested_dict: dict, id: int, header: str):
    """
    Function to get the values of a column by ID.
    :param nested_dict: three level nested template structure from ochama homepage
    :param id: group_id from the deepest level
    :param header: column header
    :return header value at given id
    """
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
# separate 3 levels
level1 = nested_all[1]
level2 = nested_all[2]
level3 = nested_all[3]
# create connceted groups
groups_connected: dict = all_group_ids(nested_all)


# %% make dictionary

print(all_values_by_id(nested_all, 4777, "name"))
print(all_values_by_id(nested_all, 4777, "imageUrl"))
