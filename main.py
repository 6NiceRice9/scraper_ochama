import json
import pandas as pd

# Load the tree structure from a JSON file.
tree_path = 'ochama_structure.txt'  # Define the file path.
with open(tree_path, 'r') as f:
    tree_data = pd.json_normalize(json.load(f))  # Directly normalize the JSON to a pandas DataFrame.

# Organize structure
# Identify the parent and child relationships.
parents_overview = tree_data[tree_data['parentId'] == 0]
child_overview = tree_data[tree_data['parentId'].isin(parents_overview['id'])]
group_overview = tree_data[tree_data['parentId'].isin(child_overview['id'])]

# Categorize all items by their level.
nested_all = {level: group for level, group in tree_data.groupby('level')}

def link_tree(group_id):
    """Function to link a group to its parent and child, returning a tuple of their IDs."""
    try:
        # Attempt to find the child and parent for the specified group.
        child_id = int(nested_all[3].loc[nested_all[3]['id'] == group_id, 'parentId'].values[0])
        parent_id = int(nested_all[2].loc[nested_all[2]['id'] == child_id, 'parentId'].values[0])
        return parent_id, child_id, group_id
    except IndexError:  # Handle cases where the group does not have a parent or child.
        return None, None, group_id

#%%
# Apply the function to all groups in level 3.
group_ids = nested_all[3]['id'].values
groups_connected = {group_id: link_tree(group_id) for group_id in group_ids}

# Optionally, print or further process `groups_connected` as needed.
#%%