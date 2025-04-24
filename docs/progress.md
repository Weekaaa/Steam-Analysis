# Description
this is the documentation for the **progress.py** file.

# Functions
## saveProgress
This funciton saves the state of the app_dict dictionary (containing the data of all games) and excluded_AppID_list (list containing IDs of games that couldn't be fetched e.g. game doesn't exist).

## savePickle
Opens and writes into a '.p' file.

## loadPickle
Opens and loads a '.p' file.

## checkLastProgress Function
This function restores the state of the app_dict and excluded_AppID_list from previous run.
- Loops through files in the data folder
- filters out '.p' file
- restores app_dict and excluded_AppID_list from respective '.p' files
