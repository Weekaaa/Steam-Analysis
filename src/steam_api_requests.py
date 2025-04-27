import traceback
import requests
import time
from progress import saveProgress
# from main import GlobalVars






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
        # Print info about the last 5 call stack traces
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



def handleSteamApiResponse(global_vars):

    logger = global_vars.logger
    apps_remaining_deque = global_vars.apps_remaining_deque

    i = 0 # This will count how many loops we made
    while len(apps_remaining_deque) > 0:
        appid = apps_remaining_deque.popleft()

        # test whether the game exists or not
        # by making request to get the details of the app
        try:
            appdetails_req = requests.get(f"https://store.steampowered.com/api/appdetails?appids={appid}")


            match appdetails_req.status_code:
            # all good
                case 200: 
                    appdetails = appdetails_req.json()
                    appdetails = appdetails[str(appid)]

            # Too Many Requests, pause for a while
                case 429:
                    logger.error(f'Too many requests. Put App ID {appid} back to deque. Sleep for 10 sec')
                    apps_remaining_deque.appendleft(appid)
                    time.sleep(10)
                    continue


            # Access blocked, wait a while
                case 403:
                    logger.error(f'Forbidden to access. Put App ID {appid} back to deque. Sleep for 5 min.')
                    apps_remaining_deque.appendleft(appid)
                    time.sleep(5 * 60)
                    continue

                case _ :
                    continue
                
        # This runs if the status code is 200
        except Exception:
            logger.info(f"Error in decoding app details request. App id: {appid}")
            traceback.print_exc(limit=5) # Print last 5 call stack traces (look it up...)
            appdetails = {'success':False} # not success -> the game does not exist anymore


        # add the app id to excluded app id list
        if appdetails['success'] == False:
            global_vars.excluded_appid_list.append(appid)
            logger.info(f'No successful response. Add App ID: {appid} to excluded apps list')
            continue

        appdetails_data = appdetails['data'] # Access the data table in the Json Response
        appdetails_data['appid'] = appid # Add appid field
        global_vars.apps_dict[appid] = appdetails_data
        logger.info(f"Successfully get content of App ID: {appid}")


        i += 1
        # for each 2500, save a checkpoint
        if i >= 2500:
        # if i >= 25: # 25 for testing
            saveProgress(global_vars)
            i = 0
