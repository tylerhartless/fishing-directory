"""
Fix leading/trailing spaces in community fishing lakes names
"""

import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import RAW_DATA_DIR

json_path = os.path.join(RAW_DATA_DIR, 'community_fishing_lakes.json')

with open(json_path, 'r') as f:
    data = json.load(f)

fixed = 0
for feature in data['features']:
    original_name = feature['properties']['name']
    cleaned_name = original_name.strip()

    if original_name != cleaned_name:
        print(f"Fixing: '{original_name}' -> '{cleaned_name}'")
        feature['properties']['name'] = cleaned_name
        fixed += 1

print(f"\nFixed {fixed} names with leading/trailing spaces")

# Save back
with open(json_path, 'w') as f:
    json.dump(data, f, indent=2)

print(f"Saved to: {json_path}")
