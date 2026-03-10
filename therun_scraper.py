import requests
from time import sleep

aliases = {"PTL1667" : "kora20_", "KoraFloof" : "kora20_", "vVanity485" : "Vanity485", "DiamondcrafterA" : "LunaEclipse_4"}
blacklisted_players = ["savetheseasponges", "SwayNC_"] #blacklisted for splitting abnormally

category_names = {"flipside pit of 100 trials" : "classic", 
                  "pit%" : "classic" , 
                  "pit% lite" : "classic", 
                  "pit% (classic)" : "classic", 
                  "pit lite" : "classic", 
                  "flipside pit boomerless" : "boomerless", 
                  "pixeless pit% yeah" : "pixlless", 
                  "flipside pit only" : "classic", 
                  "flipside pit of 100 trials (boomerless)" : "boomerless",
                  "pit% lite (splitup)" : "classic",
                  "pit% lite (splitup, boomerless)" : "boomerless"}   





#["https://api.therun.gg/games/SPM%20Category%20Extensions?q=SPM%2520category%2520extensions", 'https://api.therun.gg/games/Super%20Paper%20Mario']
games_urls = ["https://api.therun.gg/games/Super%20Paper%20Mario%20Category%20Extensions"]

games_pages = [requests.get(u) for u in games_urls]


lbs = [g.json()["result"]["stats"]["categoryLeaderboards"] for g in games_pages]

found_runs = []

for l in lbs:
    for c in l:
        if c["categoryNameDisplay"].lower() in category_names.keys():
            found_runs += c["attemptCountLeaderboard"]

import urllib.request

urllib.request.urlretrieve("https://d2c9jb6sm40v74.cloudfront.net/Moonrise45555/Super+Paper+Mario+Category+Extensions-Pit%25+Lite.lss", "some-splits.lss")










