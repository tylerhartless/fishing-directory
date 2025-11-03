"""
Convert TPWD Community Fishing Lakes JavaScript file to clean JSON

The cfl.js file contains a JavaScript variable declaration.
This script extracts the GeoJSON data and saves it as clean JSON.
"""
import json
import re

# Read the JavaScript file
with open('../../raw-data/cfl.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract the GeoJSON data from the variable declaration
# Pattern: var cfls = {...};
match = re.search(r'var cfls = ({.*});?', content, re.DOTALL)

if match:
    json_str = match.group(1)

    # Remove trailing commas before parsing (JavaScript allows them, JSON doesn't)
    # Remove commas before closing braces and brackets
    json_str = re.sub(r',\s*}', '}', json_str)
    json_str = re.sub(r',\s*]', ']', json_str)

    # Parse the JSON
    data = json.loads(json_str)

    print(f"Found {len(data['features'])} community fishing lakes")

    # Save as clean JSON
    with open('../../raw-data/community_fishing_lakes.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

    print("[OK] Saved to community_fishing_lakes.json")

    # Print sample
    print("\nSample entry:")
    print(json.dumps(data['features'][0], indent=2))
else:
    print("❌ Could not extract GeoJSON data from cfl.js")
