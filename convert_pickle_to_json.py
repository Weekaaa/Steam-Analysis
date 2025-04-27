import pandas as pd
from pathlib import Path
import json
import os


data_folder = Path(__file__).parent / "data"# Root Directory of the Project

for root, _, files in os.walk(data_folder):
    for file in files:
        full_path = Path(root, file)


        # add only files that end with .p to the list
        if full_path.suffix != '.p':
            continue
        
        # opens the pickle file
        with open(full_path, 'rb') as input_file:
            # loads the pickle file into a pandas DataFrame
            data = pd.read_pickle(input_file)

            # # resets the index of the DataFrame
            # data.reset_index(drop=True, inplace=True)

            json_dir_path = Path(root) / "output_json"

            if not json_dir_path.exists():
                json_dir_path.mkdir(parents=True)

            json_file_path = Path(json_dir_path, str(file).strip(".p")  + ".json")
            json_file = open(json_file_path, "w")
            json.dump(data, json_file, indent=4, sort_keys=False)

    break
