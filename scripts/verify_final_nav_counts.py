#!/usr/bin/env python3
"""Verify final navigation counts"""

import json
from pathlib import Path

nav_file = Path("frontend/public/gui_nav.latest.json")
data = json.loads(nav_file.read_text())

platforms = set()
categories = set()
features = 0

for edition, platforms_dict in data.items():
    if isinstance(platforms_dict, dict):
        for platform_name, categories_dict in platforms_dict.items():
            platforms.add(platform_name)
            if isinstance(categories_dict, dict):
                for category_name, features_list in categories_dict.items():
                    categories.add(f"{platform_name}/{category_name}")
                    if isinstance(features_list, list):
                        features += len([f for f in features_list if isinstance(f, dict) and 'path' in f])

print("Final Navigation Counts:")
print(f"  Editions: {len(data)}")
print(f"  Platforms: {len(platforms)}")
print(f"  Categories: {len(categories)}")
print(f"  Features: {features}")


