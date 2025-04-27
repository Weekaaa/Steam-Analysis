import requests
import traceback
import time

from progress import saveProgress

# class GlobalVars: 
#     # Singleton that holds data about the program
#     data_folder : Path
#     logger : Logger
#     apps_dict: dict
#     excluded_appid_list: list
#     apps_remaining_deque : deque
#     steamspy_dict: dict

# This is used to 
def spyApiRequest(global_vars):
    logger = global_vars.logger

    if global_vars.steamspy_dict != {}:
        page = max(list(map(int, set(global_vars.steamspy_dict.keys())))) + 1
    else:
        page = 1

    while True:
        req = requests.get(f"https://steamspy.com/api.php?request=all&page={page}")

        match req.status_code:
            case 500:
                logger.info("Page not found, i.e. finished all available pages.")
                return

            case 429:
                logger.error(f'Too many requests for StamSpy API page: {page} . Sleep for 10 sec')
                time.sleep(10)
                continue
                

        try:
            data = req.json()

        except Exception:
            # Print info about the last 5 call stack traces
            traceback.print_exc(limit=5)
            return

        global_vars.steamspy_dict[page] = data
        logger.info(f"Successfully get content of Page: {page}, from StamSpy API")

        if page % 5 == 0:
            saveProgress(global_vars)
        page += 1

        time.sleep(2) # Max poll rate is 1 per second
