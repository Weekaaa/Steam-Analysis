import traceback
import os
import time
import json
from pathlib import Path
from collections import deque

import log
from checkpoints import checkLatestCheckpoints, saveCheckpoint, loadPickle
from steam_api_requests import requestSteamAppsIDs


def init():
    project_root_path = Path(__file__).parent.parent # Root Directory of the Project

    

    data_folder = project_root_path / "data"
    log_folder = project_root_path / "logs"


    # Create logger
    logger = log.setup_logging(log_folder)

    if not data_folder.exists():
        data_folder.mkdir(parents=True)
        logger.info(f"Created {data_folder}")


    logger.info("Started Steam scraper process", os.getpid())
    return data_folder, logger


def restore_progress(data_folder, logger):
    apps_dict = {} 
    excluded_appid_list = []


    all_app_ids = requestSteamAppsIDs(logger) # returns a list of IDs of All Games
    last_checkpoint_path, last_excluded_apps_list_path = checkLatestCheckpoints(data_folder)

    if last_checkpoint_path:
        apps_dict = loadPickle(last_checkpoint_path)
        logger.info('Successfully load apps_dict checkpoint:', last_checkpoint_path)
        logger.info(f'Number of apps in apps_dict: {len(apps_dict)}')

    if last_excluded_apps_list_path:
        excluded_appid_list = loadPickle(last_excluded_apps_list_path)
        logger.info('Successfully load apps_dict checkpoint:', last_checkpoint_path)
        logger.info(f'Number of apps in apps_dict: {len(apps_dict)}')
    

    # remove app_ids that already scrapped or excluded or error
    all_app_ids = set(all_app_ids) \
            - set(map(int, set(apps_dict.keys()))) \
            - set(map(int, excluded_appid_list)) \

    # first get remaining apps
    apps_remaining_deque = deque(set(all_app_ids))

    return apps_dict, excluded_appid_list, apps_remaining_deque





def main():

    # ========== INITIALIZATION ==========
    data_folder, logger = init()

    apps_dict, excluced_appid_list, apps_remaining_deque = restore_progress(data_folder, logger)

    logger.info(f'Number of remaining apps: {len(apps_remaining_deque)}')

    # Temporary File To Get a sample of the Data and it's structure
    # fd  = open(data_folder / 'data.json', 'w+') 

    fd = open(data_folder / 'data.json', 'w', encoding='utf-8')
    fd.write('[')

    # ====================================
    

    i = 0
    while len(apps_remaining_deque) > 0:
        appid = apps_remaining_deque.popleft()

        # test whether the game exists or not
        # by making request to get the details of the app
        try:
            appdetails_req = requests.get(f"https://store.steampowered.com/api/appdetails?appids={appid}")

            # Game Exists
            if appdetails_req.status_code == 200:
                appdetails = appdetails_req.json()
                appdetails = appdetails[str(appid)]

            # Too Many Requests, pause for a while
            elif appdetails_req.status_code == 429:
                logger.error(f'Too many requests. Put App ID {appid} back to deque. Sleep for 10 sec')
                apps_remaining_deque.appendleft(appid)
                time.sleep(10)
                continue


            # Access blocked, wait a while
            elif appdetails_req.status_code == 403:
                logger.error(f'Forbidden to access. Put App ID {appid} back to deque. Sleep for 5 min.')
                apps_remaining_deque.appendleft(appid)
                time.sleep(5 * 60)
                continue

            else:
                continue
                
        except Exception:
            logger.info(f"Error in decoding app details request. App id: {appid}")

            # Print last 5 stack traces (look it up...)
            traceback.print_exc(limit=5)
            appdetails = {'success':False}
        # not success -> the game does not exist anymore
        # add the app id to excluded app id list
        if appdetails['success'] == False:
            excluced_appid_list.append(appid)
            logger.info(f'No successful response. Add App ID: {appid} to excluded apps list')
            continue

        appdetails_data = appdetails['data']
        

        appdetails_data['appid'] = appid     


        apps_dict[appid] = appdetails_data

        json.dump(appdetails_data, fd, ensure_ascii=False)
        fd.write(',')

        logger.info(f"Successfully get content of App ID: {appid}")

        i += 1
        # for each 2500, save a checkpoint
        # if i >= 2500:
        if i >= 25: # 25 for testing

            saveCheckpoint(apps_dict, excluced_appid_list, data_folder, logger)
            i = 0

    # save checkpoints at the end
    saveCheckpoint(apps_dict, excluced_appid_list, data_folder, logger)

    logger.info(f"Total number of valid apps: {len(apps_dict)}")
    logger.info('Successful run. Program Terminates.')

if __name__ == '__main__':
    main()
