import os
import pickle
from pathlib import Path


def saveProgress(global_vars):

    data_folder = global_vars.data_folder
    logger = global_vars.logger

    # Path of the pickle file that stores the Game data as a dictionary
    save_path = data_folder.joinpath(
        'apps_dict' + f'-progress.p'
    ).resolve()

    # Path of the pickle file that will store AppIDs that couldn't be added (error or don't exist)
    save_path2 = data_folder.joinpath(
        'excluded_dict' + f'progress.p'
    ).resolve()
    
    # Path of the pickle file that stores SteamSpyAPI Data
    steam_spy_save_path = data_folder.joinpath(
        'SteamSpy' + f'-progress.p'
    ).resolve()

    savePickle(save_path, global_vars.apps_dict)
    logger.info(f'Successfully create app_dict progress: {save_path}')

    savePickle(save_path2, global_vars.excluded_appid_list)
    logger.info(f"Successfully create excluded apps progress: {save_path2}")

    savePickle(steam_spy_save_path, global_vars.steamspy_dict)
    logger.info(f"Successfully create steamspy_dict progress: {steam_spy_save_path}")

def loadPickle(path_to_load:Path):
    obj = pickle.load(open(path_to_load, "rb"))
    return obj


def savePickle(path_to_save:Path, obj):
    with open(path_to_save, 'wb') as handle:
        pickle.dump(obj, handle, protocol=pickle.HIGHEST_PROTOCOL)



def checkLatestProgress(data_folder):
    # app_dict
    all_pkl_files = []

    # get all pickle files in the data folder
    for root, _, files in os.walk(data_folder):
        for file in files:
            full_path = Path(root, file)

            # add only files that end with .p to the list
            if full_path.suffix != '.p':
                continue
            all_pkl_files.append(full_path)
            
            
            if 'apps_dict' in full_path.name: 
                apps_dict_ckpt_file = full_path

            elif 'excluded_list' in full_path.name:
                excluded_apps_list_file = full_path
            elif 'SteamSpy' in full_path.name:
                steam_spy_save_path = full_path
        break

    # Check if they exist, if not, set them to None, otherwise, return them
    if 'apps_dict_ckpt_file' not in locals():
        apps_dict_ckpt_file = None

    if 'excluded_apps_list_file' not in locals():
        excluded_apps_list_file = None

    if 'steam_spy_save_path' not in locals():
        steam_spy_save_path = None

    return apps_dict_ckpt_file, excluded_apps_list_file, steam_spy_save_path
