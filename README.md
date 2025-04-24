# Steam-Analysis

Current File Tree
```
.
├── data
├── docs
│   ├── get-app-details_response_json_format.json
│   ├── log.md
│   └── main.md
├── logs
│   └── steam_api.log
├── README.md
├── requirements.txt
└── src
    ├── checkpoints.py
    ├── log.py
    ├── main.py
    ├── __pycache__
    └── steam_api_requests.py
```

This program is meant to:
1. Pull Game IDs for all games from the [SteamAPI](https://partner.steamgames.com/doc/webapi/ISteamApps)
2. Use IDs collected to pull data on games using [SteamAppDetails API](https://github.com/Revadike/InternalSteamWebAPI/wiki/Get-App-Details)
    - Log Changes
    - Save Progress in [Pickel Files](https://docs.python.org/3/library/pickle.html)

# Documentation
Functions and files are thuroughly documented and can be found in the [docs directory](https://github.com/Weekaaa/Steam-Analysis/tree/main/docs).

# External Sources
## Inspiration
- [I Scraped the Entire Steam Catalog, Here’s the Data - Newbie Indie Game Dev](https://www.youtube.com/watch?v=qiNv3qv-YbU&ab_channel=NewbieIndieGameDev)

## Helpful Resources
- [Scraping information of all games from Steam with Python](https://medium.com/codex/scraping-information-of-all-games-from-steam-with-python-6e44eb01a299)

