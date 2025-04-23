from collections import deque
import os
import time
import requests
from pathlib import Path
import traceback

import log
from checkpoints import checkLatestCheckpoints, saveCheckpoint, loadPickle




# Use Steam's ISteamApps API to collect:
# - Game Name
# - GameID
# for each game
def requestSteamAppsIDs():
    req = requests.get("https://api.steampowered.com/ISteamApps/GetAppList/v2/")

    # 200 is the OK code for Http requests
    if (req.status_code != 200):
        print("Failed to get all games on steam.")
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







def main():
    # To avoid creating a class with these variables and
    # passing them in all functions, just define them as global.
    global logger
    global project_root_path
    global data_folder

    # check if file exists, create it if it does not
    project_root_path = Path(__file__).parent.parent # Root Directory of the Project

    # Create logger
    logger = log.setup_logging(project_root_path)
    

    logger.info("Started Steam scraper process", os.getpid())


    data_folder = project_root_path / "data" # Log directory at the root of the project
    if not data_folder.exists():
        data_folder.mkdir(parents=True)
        logger.info(f"Created {data_folder}")

    # Temporary File To Get a sample of the Data and it's structure
    fd  = open(project_root_path/'data' / 'data.txt', 'w+') 


    apps_dict = {} 

    all_app_ids = requestSteamAppsIDs() # returns a list of IDs of All Games


    logger.info(f'Total number of apps on steam: {len(all_app_ids)}')



    logger.info(f'Checkpoint folder: {data_folder}')

    latest_apps_dict_ckpt_path = checkLatestCheckpoints(data_folder)

    if latest_apps_dict_ckpt_path:
        apps_dict = loadPickle(latest_apps_dict_ckpt_path)
        logger.info('Successfully load apps_dict checkpoint:', latest_apps_dict_ckpt_path)
        logger.info(f'Number of apps in apps_dict: {len(apps_dict)}')
    

    # remove app_ids that already scrapped or excluded or error
    all_app_ids = set(all_app_ids) \
            - set(map(int, set(apps_dict.keys()))) \
            # - set(map(int, set(apps_dict.keys()))) \
        
    # first get remaining apps
    apps_remaining_deque = deque(set(all_app_ids))

    
    print('Number of remaining apps:', len(apps_remaining_deque))

    i = 0
    while len(apps_remaining_deque) > 0:
        appid = apps_remaining_deque.popleft()

        # test whether the game exists or not
        # by making request to get the details of the app
        try:
            appdetails_req = requests.get(f"https://store.steampowered.com/api/appdetails?appids={appid}")

            if appdetails_req.status_code == 200:
                appdetails = appdetails_req.json()
                appdetails = appdetails[str(appid)]

            elif appdetails_req.status_code == 429:
                logger.error(f'Too many requests. Put App ID {appid} back to deque. Sleep for 10 sec')
                apps_remaining_deque.appendleft(appid)
                time.sleep(10)
                continue


            elif appdetails_req.status_code == 403:
                logger.error(f'Forbidden to access. Put App ID {appid} back to deque. Sleep for 5 min.')
                apps_remaining_deque.appendleft(appid)
                time.sleep(5 * 60)
                continue

            else:
                continue
                
        except Exception:
            logger.info(f"Error in decoding app details request. App id: {appid}")

            traceback.print_exc(limit=5)
            appdetails = {'success':False}
            print()

        # not success -> the game does not exist anymore
        if appdetails['success'] == False:
            logger.info(f'No successful response.{appid} excluded')
            continue

        appdetails_data = appdetails['data']
        fd.writelines(str(appdetails_data))

        appdetails_data['appid'] = appid     

        apps_dict[appid] = appdetails_data
        logger.info(f"Successfully get content of App ID: {appid}")

        i += 1
        # for each 2500, save a checkpoint
        # if i >= 2500:
        if i >= 25: # 25 for testing
            saveCheckpoint(apps_dict, data_folder, logger)
            i = 0

    # save checkpoints at the end
    saveCheckpoint(apps_dict, data_folder, logger)

    logger.info(f"Total number of valid apps: {len(apps_dict)}")
    logger.info('Successful run. Program Terminates.')

if __name__ == '__main__':
    main()
