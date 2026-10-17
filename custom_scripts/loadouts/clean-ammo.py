# Remove selected items from this server's Assault_Rifles.json market file.

import json
import os

# Get the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the full path to the JSON file
json_file_path = os.path.join(os.path.dirname(os.path.dirname(current_dir)), 'config', 'ExpansionMod', 'Market', 'Assault_Rifles.json')

# Read the JSON file
with open(json_file_path, 'r') as file:
    data = json.load(file)

# Filter out items that start with "Rev" or "Jebs"
data['Items'] = [item for item in data['Items'] if not (item['ClassName'].startswith('Rev') or item['ClassName'].startswith('Jebs'))]

# Write the updated JSON back to the file
with open(json_file_path, 'w') as file:
    json.dump(data, file, indent=4)

print("Entries starting with 'Rev' or 'Jebs' have been removed.")
