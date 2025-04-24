# description
this is the documentation for the main.py file.

# Init Funciton
This function initializes the program by
- Creating a logger.
    This is an interface used to write different types of logs such as *info* and *error*.
- Get the path of the directory used to store data.


# Restore_progress Function
This function gets the previously collected data so we can continue where we started (So we don't get data for the same game twice).

It works by retrieving the dictionary of game_data from the last run.
Then it gets all the game ID's and subtracts from it the IDs of games we previously retrieved, and the IDs of games we excluded (bc of an error or the game doesn't exist).

Returns a deque of the remaining appIDs needed to be fetched, the current app_dictionary (with app data) and the list of IDs of apps we excluded.

# main Function
for every ID in the deque with appIDs we need to fetch
- it makes a get request to fetch the App data
- handles the different status codes
- if there are too many requests, it times out
- if the app doesn't exists or errors, it add's it's ID in the excluded_list
- every 2500 entries it saves the progress.

