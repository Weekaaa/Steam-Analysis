import json
import os
import csv

# handling file paths
apps_path = os.path.join('data', 'output_json', 'apps_dict-progress.json')
spy_path = os.path.join('data', 'output_json', 'SteamSpy-progress.json')
output_path = os.path.join('data', 'merged_progress.csv')


with open(apps_path, 'r', encoding='utf-8') as f:
    apps_data = json.load(f)

with open(spy_path, 'r', encoding='utf-8') as f:
    spy_data = json.load(f)


# Flattened the SteamSpy data (vibe coded this)
flat_spy = {}
for page_key, page_content in spy_data.items():
    if isinstance(page_content, dict):
        flat_spy.update(page_content)


# headers for the CSV file
fieldnames = [
    'name',
    'steam_appid',
    'is_free',
    'developers',
    'publishers',
    'price',
    'platforms',
    'achievements_total',
    'release_date',
    'tags',
    'positive_reviews',
    'negative_reviews',
    'owners'
]


with open(output_path, 'w', encoding='utf-8', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    # iterate through the apps data not the SteamSpy data...
    # ...because the SteamSpy data is a subset of the apps data
    for app_key, app_info in apps_data.items():
        name = app_info.get('name', '')
        steam_appid = app_info.get('steam_appid')

        is_free = app_info.get('is_free', False)

        developers = ','.join(app_info.get('developers', []))
        publishers = ','.join(app_info.get('publishers', []))

        # check if the game is free because free games...
        # ...have no price overview key in the JSON data
        price = '' if is_free else app_info.get('price_overview', {}).get('final_formatted', '') 

        platforms_info = app_info.get('platforms', {})
        available_platforms = [plat for plat, available in platforms_info.items() if available]
        platforms = ','.join(available_platforms)

        achievements_total = app_info.get('achievements', {}).get('total', 0)

        release_date = app_info.get('release_date', {}).get('date', '')

        tags = ','.join(app_info.get('tags', []))

        spy_entry = flat_spy.get(str(steam_appid), {})
        positive_reviews = spy_entry.get('positive', 0)
        negative_reviews = spy_entry.get('negative', 0)
        owners = spy_entry.get('owners', '')

        writer.writerow({
            'name': name,
            'steam_appid': steam_appid,
            'is_free': is_free,
            'developers': developers,
            'publishers': publishers,
            'price': price,
            'platforms': platforms,
            'achievements_total': achievements_total,
            'release_date': release_date,
            'tags': tags,
            'positive_reviews': positive_reviews,
            'negative_reviews': negative_reviews,
            'owners': owners
        })
