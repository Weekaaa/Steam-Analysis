# Steam-Analysis

Current File Tree
```
├── data
│   ├── apps_dict-chpkt.p   # ignored by git
│   └── sample.txt          # ignored by git
├── logs
│   └── steam_api.log
├── README.md
├── requirements.txt
└── src
    └── steam_api_requests.py
```

This program is meant to:
1. Pull Game IDs for all games from the [SteamAPI](https://partner.steamgames.com/doc/webapi/ISteamApps)
2. Use IDs collected to pull data on games using [SteamAppDetails API](https://github.com/Revadike/InternalSteamWebAPI/wiki/Get-App-Details)
    - Log Changes
    - Save Progress in [Pickel Files](https://docs.python.org/3/library/pickle.html)

