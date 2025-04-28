# Steam-Analysis

Current File Tree
```
.
├── convert_pickle_to_json.py
├── data
├── docs
│   ├── get-app-details_response_json_format.json
│   ├── log.md
│   ├── main.md
│   ├── progress.md
│   └── steam_api_requests.md
├── logs
├── README.md
├── requirements.txt
└── src
    ├── log.py
    ├── main.py
    ├── progress.py
    ├── scrape.py
    ├── spy_api.py
    └── steam_api_requests.py
```

This program is meant to:
1. Pull Game IDs for all games from the [SteamAPI](https://partner.steamgames.com/doc/webapi/ISteamApps)
2. Use IDs collected to pull data on games using [SteamAppDetails API](https://github.com/Revadike/InternalSteamWebAPI/wiki/Get-App-Details)
    - Log Changes
    - Save Progress in [Pickel Files](https://docs.python.org/3/library/pickle.html)

# Documentation
Functions and files are thuroughly documented and can be found in the [docs directory](https://github.com/Weekaaa/Steam-Analysis/tree/main/docs).

## API Docs
- [SteamAPI](https://partner.steamgames.com/doc/webapi/ISteamApps)
- [SteamAppDetails API](https://github.com/Revadike/InternalSteamWebAPI/wiki/Get-App-Details)
- [SteamSpy Api](https://steamspy.com/api.php)

# Author's Note
This project doesn't follow all [clean code practices](https://gist.github.com/wojteklu/73c6914cc446146b8b533c0988cf8d29) since the point is to not have any unecessary abstraction, the goal is to create understandable code that an outsider can look at and understand. If something is repeated twice in the code, that's fine.

# External Sources
## Inspiration
- [I Scraped the Entire Steam Catalog, Here’s the Data - Newbie Indie Game Dev](https://www.youtube.com/watch?v=qiNv3qv-YbU&ab_channel=NewbieIndieGameDev)

## Helpful Resources
- [Scraping information of all games from Steam with Python](https://medium.com/codex/scraping-information-of-all-games-from-steam-with-python-6e44eb01a299)

