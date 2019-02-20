'''
Common variables for the modlinker.
'''
from os import environ

# configuration
MAX_RESULTS = 10
MAX_LENGTH = 9900 # real max is 10000, leave a bit of wiggle room
# TODO: Dynamically get the current alpha number
CURRENT_VERSION = environ['RIMWORLD_CURRENT_ALPHA'] # default tag for the current alpha
EPSILON = 1/1000

# reddit settings
REDDIT = {
    "username": environ['REDDIT_USER'],
    "password": environ['REDDIT_PASSWORD'],
    "client_id": environ['REDDIT_CLIENT_ID'],
    "client_secret": environ['REDDIT_CLIENT_SECRET'],
    "user_agent": 'python:rimworld-modlinker:v1.2 (by /u/FluffierThanThou)',
    "subreddits": environ['REDDIT_LISTEN_TO']
}

# steam settings
STEAM = {
    "key": environ['STEAM_KEY'],
    "WORKSHOP": {
        "search_url": 'http://steamcommunity.com/workshop/browse/?{params}',
        "mod_url": 'https://steamcommunity.com/sharedfiles/filedetails/?id={id}',
        "PARAMS": {
            "appid": 294100,   
            "browsesort": "textsearch"
        }
    }
}

# footer text
FOOTER = ( "\n\n*****\n^(I'm a bot | ) [^source](https://github.com/FluffierThanThou/reddit-modlinker)"
           " ^| [^commands](https://github.com/FluffierThanThou/reddit-modlinker/blob/master/bot/COMMANDS.MD#link-to-a-mod-or-scenario-for-a-specific-alpha-of-rimworld)"
           " ^| [^stats](http://modlinker-stats.karel-kroeze.nl/)"
           " ^(| I was made by )[^/u\/FluffierThanThou](/user/FluffierThanThou)" )
