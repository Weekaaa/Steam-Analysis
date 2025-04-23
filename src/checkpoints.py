import os
import pickle
from pathlib import Path


def saveCheckpoint(apps_dict, data_folder, logger):

    save_path = data_folder.joinpath(
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



def checkLatestCheckpoints(data_folder):
    # app_dict
    all_pkl_files = []

    # get all pickle files in the data folder
    
    for root, _, files in os.walk(data_folder):
        for file in files:
            full_path = Path(root, file)

            # add only files that end with .p to the list
            if full_path.suffix == '.p':
                all_pkl_files.append(full_path)
        break
    print(
        "\n\n\n",
        all_pkl_files,
        "\n\n\n",
            )

    # create a list to store all the checkpoint files
    # then sort them
    # the latest checkpoint file for each of the object is the last element in each of the lists
    apps_dict_ckpt_files = [f for f in all_pkl_files if 'apps_dict' in f.name and "ckpt" in f.name]

    apps_dict_ckpt_files.sort()

    latest_checkpoint_file = apps_dict_ckpt_files[-1] if apps_dict_ckpt_files else None

    return latest_checkpoint_file
