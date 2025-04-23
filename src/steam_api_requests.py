from collections import deque
import os
import sys

import time
# from datetime import datetime

import requests

# import json

import pickle
from pathlib import Path

import traceback
import logging
from pathlib import Path


# Boilerplate function to Configure logging
def setup_logging(log_dir="logs"):
        # Logger Usage
        # logger = setup_logging()
        # logger.error("This is an error message")
        # logger.warning("This is a warning")
        # logger.info("This is informational")

    log_dir = project_root_path / "logs" # Log directory at the root of the project
    Path(log_dir).mkdir(exist_ok=True)
    
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)  # Capture all levels
    
    # Formatting
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%d-%m-%Y %H:%M:%S'
    )
    
    # Console (stderr) handler
    console_handler = logging.StreamHandler(sys.stderr)
    # console_handler.setLevel(logging.WARNING)  # We won't need warnings
    console_handler.setFormatter(formatter)
    
    # File handler
    file_handler = logging.FileHandler(f"{log_dir}/steam_api.log")
    file_handler.setLevel(logging.DEBUG)  # All levels to file
    file_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger


# Use Steam's ISteamApps API to collect:
# - Game Name
# - GameID
# for each game
def requestSteamAppsIDs():
    req = requests.get("https://api.steampowered.com/ISteamApps/GetAppList/v2/")

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





def saveCheckpoint(apps_dict):

    # check if file exists, create it if it does not
    if not checkpoint_folder.exists():
        checkpoint_folder.mkdir(parents=True)


    save_path = checkpoint_folder.joinpath(
        'apps_dict' + f'-ckpt-fin.p'
    ).resolve()

    savePickle(save_path, apps_dict)
    logger.info(f'Successfully create app_dict checkpoint: {save_path}')


    print()


def loadPickle(path_to_load:Path) -> dict:
    obj = pickle.load(open(path_to_load, "rb"))
    
    return obj

def savePickle(path_to_save:Path, obj):
    with open(path_to_save, 'wb') as handle:
        pickle.dump(obj, handle, protocol=pickle.HIGHEST_PROTOCOL)

def checkLatestCheckpoints():
    # app_dict
    all_pkl = []

    checkpoint_folder = project_root_path / "data" # Log directory at the root of the project
    # get all pickle files in the checkpoint folder    
    for root, _, files in os.walk(checkpoint_folder):
        all_pkl = list(map(lambda f: Path(root, f), files))
        all_pkl = [p for p in all_pkl if p.suffix == '.p']
        break
            
    # create a list to store all the checkpoint files
    # then sort them
    # the latest checkpoint file for each of the object is the last element in each of the lists
    apps_dict_ckpt_files = [f for f in all_pkl if 'apps_dict' in f.name and "ckpt" in f.name]

    apps_dict_ckpt_files.sort()

    latest_apps_dict_ckpt_path = apps_dict_ckpt_files[-1] if apps_dict_ckpt_files else None

    return latest_apps_dict_ckpt_path


def main():
    global logger
    global project_root_path
    global checkpoint_folder
    project_root_path = Path(__file__).parent.parent
    checkpoint_folder = project_root_path / "data" # Log directory at the root of the project
    logger = setup_logging()
    logger.info("Started Steam scraper process", os.getpid())

    fd  = open(project_root_path/'data' / 'data.txt', 'w+')


    apps_dict = {}

    all_app_ids = requestSteamAppsIDs()

    logger.info(f'Total number of apps on steam: {len(all_app_ids)}')


    logger.info(f'Checkpoint folder: {checkpoint_folder}')

    latest_apps_dict_ckpt_path = checkLatestCheckpoints()

    if latest_apps_dict_ckpt_path:
        apps_dict = loadPickle(latest_apps_dict_ckpt_path)
        logger.info('Successfully load apps_dict checkpoint:', latest_apps_dict_ckpt_path)
        logger.info(f'Number of apps in apps_dict: {len(apps_dict)}')
    

    # remove app_ids that already scrapped or excluded or error
    all_app_ids = set(all_app_ids) \
            - set(map(int, set(apps_dict.keys()))) \
        
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
                
        except:
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
        if i >= 2500:
        # if i >= 25: # 25 for texting
            saveCheckpoint(apps_dict)
            i = 0

    # save checkpoints at the end
    saveCheckpoint(apps_dict)

    logger.info(f"Total number of valid apps: {len(apps_dict)}")

    logger.info('Successful run. Program Terminates.')

if __name__ == '__main__':
    main()
