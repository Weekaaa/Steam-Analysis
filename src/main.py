from logging import Logger
from pathlib import Path
from collections import deque
import threading

import log
from progress import checkLatestProgress, saveProgress, loadPickle
from steam_api_requests import requestSteamAppsIDs, handleSteamApiResponse
from spy_api import spyApiRequest



# Yarab fok el di2a
class GlobalVars: 
    # Singleton that holds data about the program
    data_folder : Path
    logger : Logger
    apps_dict: dict
    excluded_appid_list: list
    apps_remaining_deque : deque
    steamspy_dict: dict



def init():
    project_root_path = Path(__file__).parent.parent # Root Directory of the Project
    

    data_folder = project_root_path / "data"
    log_folder = project_root_path / "logs"


    # Create logger
    logger = log.setup_logging(log_folder)

    if not data_folder.exists():
        data_folder.mkdir(parents=True)
        logger.info(f"Created {data_folder}")


    logger.info("Started Steam scraper")

    global_vars = GlobalVars()
    global_vars.data_folder = data_folder
    global_vars.logger = logger

    return global_vars


# Restores the state of the last run and sets the appropriate values in the global_vars class object
def restore_progress(global_vars: GlobalVars):
    apps_dict = {} 
    excluded_appid_list = []
    steamspy_dict = {}

    logger = global_vars.logger

    all_app_ids = requestSteamAppsIDs(logger) # returns a list of IDs of All Games
    last_checkpoint_path, last_excluded_apps_list_path, steam_spy_save_path = checkLatestProgress(global_vars.data_folder)

    if last_checkpoint_path:
        apps_dict = loadPickle(last_checkpoint_path)
        logger.info(f'Successfully load apps_dict checkpoint:{str(last_checkpoint_path)}')
        logger.info(f'Number of apps in apps_dict: {len(apps_dict)}')

    if last_excluded_apps_list_path:
        excluded_appid_list = loadPickle(last_excluded_apps_list_path)
        logger.info(f'Successfully load excluded_appid_list checkpoint:{str(last_checkpoint_path)}')
        logger.info(f'Number of apps in excluded_appid_list: {len(excluded_appid_list)}')
    
    if steam_spy_save_path:
        steamspy_dict = loadPickle(steam_spy_save_path)
        logger.info(f'Successfully load SteamSpy checkpoint: {str(last_checkpoint_path)}')
        logger.info(f'Number of Pages in SteamSpy dict {len(steamspy_dict)}')

    # remove app_ids that already scrapped or excluded or error
    all_app_ids = set(all_app_ids) \
            - set(map(int, set(apps_dict.keys()))) \
            - set(map(int, excluded_appid_list)) \

    # first get remaining apps
    apps_remaining_deque = deque(set(all_app_ids))


    global_vars.apps_dict               =   apps_dict
    global_vars.excluded_appid_list     =   excluded_appid_list
    global_vars.apps_remaining_deque    =   apps_remaining_deque
    global_vars.steamspy_dict           =   steamspy_dict 





def main():

    # ========== INITIALIZATION ==========
    global_vars = init()

    logger = global_vars.logger

    restore_progress(global_vars)

    logger.info(f'Number of remaining apps: {len(global_vars.apps_remaining_deque)}')

    # ====================================

    # This beautiful function sends a get request, handles each error and updates the apps_dict and apps_remaining_deque
    # It runs in the main thread

    t1 = threading.Thread(target=spyApiRequest, args=(global_vars,))
    t1.start()
    
    handleSteamApiResponse(global_vars)

    t1.join()
    
    # ====================

    # save progress at the end
    saveProgress(global_vars)

    logger.info(f"Total number of valid apps: {len(global_vars.apps_dict)}")
    logger.info('Successful run. Program Terminates.')

if __name__ == '__main__':
    main()
