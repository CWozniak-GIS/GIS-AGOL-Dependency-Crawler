"""
update_agol_dump.py

Connects to the Bedford County ArcGIS Online organization and exports all item metadata
to a line-delimited JSON file. Each record includes item properties (ID, title, type,
owner, URL, description, tags) and associated data content.

Intended to be used in conjunction with `find_agol_dependencies.py`, which parses the
generated JSONL file to analyze item dependencies across the organization.

Author: Chris Wozniak (GIS Senior Specialist)
"""

import json
import time
import os
from arcgis.gis import GIS
import urllib3 # https://urllib3.readthedocs.io/en/latest/advanced-usage.html#tls-warnings

# --- CONFIG ---
OUTPUT_PATH = os.path.join([PATH_TO_AGOL_DEPENDENCY_JSON_DIR],r'agol_item_jsons.jsonl') #Define Output Location!!!
DELAY_SECONDS = 0.1 # To avoid any potential API limits
urllib3.disable_warnings() # Avoids printing thousands of warnings about an unverified HTTPS request to host 'www.arcgis.com'

# --- Connect to GIS ---
def connect_to_portal():
    gis = GIS("pro") #Uses open ArcGIS Pro session for authentication — feel free to replace with your own method
    print(f"Connected to: {gis.properties.portalHostname} as {gis.users.me.username}")
    return gis


# --- Dump all item JSONs ---
def dump_all_items_to_file(gis, output_path, delay=0.1):
    all_items = gis.content.search(query='', max_items=10000)
    print(f"Found {len(all_items)} items. Writing to: {output_path}")

    with open(output_path, 'w', encoding='utf-8') as f:
        for i, item_stub in enumerate(all_items, start=1):
            try:
                item = gis.content.get(item_stub.id)
                item_data = {
                    "id": item.id,
                    "title": item.title,
                    "type": item.type,
                    "owner": item.owner,
                    "url": item.url,
                    "description": item.description,
                    "tags": item.tags,
                    "data": item.get_data() or {}
                }
                f.write(json.dumps(item_data, ensure_ascii=False) + '\n')
                print(f"{i}. {item.title} ({item.id})")
            except Exception as e:
                print(f"{i}. *Skipped item* {item_stub.id}: {e}")
            time.sleep(delay)

# --- MAIN ---
if __name__ == "__main__":
    gis = connect_to_portal()

    dump_all_items_to_file(gis, OUTPUT_PATH, delay=DELAY_SECONDS)
