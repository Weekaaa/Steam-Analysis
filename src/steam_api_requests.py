import traceback
import requests





# Use Steam's ISteamApps API to collect:
# - Game Name
# - GameID
# for each game
def requestSteamAppsIDs(logger):
    req = requests.get("https://api.steampowered.com/ISteamApps/GetAppList/v2/")

    # 200 is the OK code for Http requests
    if (req.status_code != 200):
        logger.error("Failed to get all games on steam.")
        return
    
    try:
        data = req.json()
    except Exception:
        # Print info about the last 5 stack traces
        traceback.print_exc(limit=5)
        return {}
    

    # IDs from JSON, refer to API doc for the structure of the response
    apps_data = data['applist']['apps']


    # List to hold all App IDs
    apps_ids = []

    for app in apps_data:
        appid = app['appid']
        name = app['name']
        
        # skip apps that have empty name
        if not name:
            continue

        apps_ids.append(appid)

    return apps_ids



