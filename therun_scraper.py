import requests
from time import sleep
import urllib.request
import os
import splits_work as sw
from pathlib import Path
import db_work as db
import sqlite3
import datetime as dt
#urllib.request.urlretrieve("https://d2c9jb6sm40v74.cloudfront.net/Moonrise45555/Super+Paper+Mario+Category+Extensions-Pit%25+Lite.lss", "some-splits.lss")

con = sqlite3.connect("runs.db")
cur = con.cursor()
db.regenerate_database()

try:
    os.remove("./work_splits.lss")
except:
    pass


#aliases = {"PTL1667" : "kora20_", "KoraFloof" : "kora20_", "vVanity485" : "Vanity485", "DiamondcrafterA" : "LunaEclipse_4"}
blacklisted_players = ["savetheseasponges", "SwayNC", "PTL1667", "vVanity485", "DiamondcrafterA", "JCRRiles", "samlilwall06", "KoraFloof", "kora20__"] #blacklisted for splitting abnormally or for being an alias of another player


type_from_cat_name = {"flipside pit of 100 trials" : sw.PitType.INVALID, 
                  "pit%" : sw.PitType.CLASSIC , 
                  "pit% lite" : sw.PitType.CLASSIC, 
                  "pit% (classic)" : sw.PitType.CLASSIC, 
                  "pit lite" : sw.PitType.CLASSIC, 
                  "flipside pit boomerless" : sw.PitType.BOOMERLESS, 
                  "pixeless pit% yeah" : sw.PitType.PIXLLESS, 
                  "flipside pit only" : sw.PitType.CLASSIC, 
                  "flipside pit of 100 trials (boomerless)" : sw.PitType.BOOMERLESS,
                  "pit% lite (split up)" : sw.PitType.CLASSIC,
                  "pit% lite (split up, boomerless)" : sw.PitType.BOOMERLESS,
                  "boomerless pit% lite" : sw.PitType.BOOMERLESS,
                  "pixlless lite" : sw.PitType.PIXLLESS,
                  "routeless pixlless pit" : sw.PitType.PIXLLESS}   

detail_from_cat_name = {"flipside pit of 100 trials" : sw.SplitDetail.MERGED, 
                  "pit%" : sw.SplitDetail.MERGED , 
                  "pit% lite" : sw.SplitDetail.MERGED, 
                  "pit% (classic)" : sw.SplitDetail.MERGED, 
                  "pit lite" : sw.SplitDetail.MERGED, 
                  "flipside pit boomerless" : sw.SplitDetail.MERGED, 
                  "pixeless pit% yeah" : sw.SplitDetail.MERGED, 
                  "flipside pit only" : sw.SplitDetail.MERGED, 
                  "flipside pit of 100 trials (boomerless)" : sw.SplitDetail.MERGED,
                  "pit% lite (split up)" : sw.SplitDetail.SPLIT,
                  "pit% lite (split up, boomerless)" : sw.SplitDetail.SPLIT,
                  "boomerless pit% lite" : sw.SplitDetail.MERGED,
                  "pixlless lite" : sw.SplitDetail.MERGED,
                  "routeless pixlless pit" : sw.SplitDetail.MERGED}

length_from_cat_name = {"flipside pit of 100 trials" : sw.CategoryLength.FULL, 
                  "pit%" : sw.CategoryLength.FULL , 
                  "pit% lite" : sw.CategoryLength.LITE, 
                  "pit% (classic)" : sw.CategoryLength.FULL, 
                  "pit lite" : sw.CategoryLength.LITE, 
                  "flipside pit boomerless" : sw.CategoryLength.FULL, 
                  "pixeless pit% yeah" : sw.CategoryLength.FULL, 
                  "flipside pit only" : sw.CategoryLength.FULL, 
                  "flipside pit of 100 trials (boomerless)" : sw.CategoryLength.FULL,
                  "pit% lite (split up)" : sw.CategoryLength.LITE,
                  "pit% lite (split up, boomerless)" : sw.CategoryLength.LITE,
                  "boomerless pit% lite" : sw.CategoryLength.LITE,
                  "pixlless lite" : sw.CategoryLength.LITE}
                  

cat_names = ["flipside pit of 100 trials", 
                  "pit%",
                  "pit% lite", 
                  "pit% (classic)", 
                  "pit lite", 
                  "flipside pit boomerless", 
                  "pixeless pit% yeah", 
                  "flipside pit only", 
                  "flipside pit of 100 trials (boomerless)",
                  "pit% lite (split up)",
                  "pit% lite (split up, boomerless)",
                  "boomerless pit% lite",
                  "pixlless lite"]



time_offset = dt.timedelta(days=1)








games_urls = ["https://api.therun.gg/games/Super%20Paper%20Mario%20Category%20Extensions","https://api.therun.gg/games/SPM%20Category%20Extensions?q=SPM%2520category%2520extensions", 'https://api.therun.gg/games/Super%20Paper%20Mario']
delay = 0
while True:
    try:
        games_pages = [requests.get(u) for u in games_urls]
        break
    except:
        sleep(delay)
        delay += 1



lbs = [g.json()["result"]["stats"]["categoryLeaderboards"] for g in games_pages]

found_players = []
found_split_names : list[tuple[sw.RunContext, str, dt.datetime]] = []


def ctx_from_cat_name(player, str):
    return sw.RunContext(player, type_from_cat_name[str], length_from_cat_name[str], detail_from_cat_name[str])

def file_name_from_ctx(ctx : sw.RunContext):
    return str(ctx.pit_type.lower()) + "_" + str(ctx.cat_length.lower()) + "_" + str(ctx.split_detail.lower()) + ".lss"

for l in lbs:
    for c in l:
        if c["categoryNameDisplay"].lower() in cat_names:
            for r in c["attemptCountLeaderboard"]:
                if not r["username"] in found_players and not r["username"] in blacklisted_players:
                    found_players.append(r["username"])

root = []
for p_name in found_players:
    print("searching through", p_name)
    while(True):
        try:
            root = requests.get("https://api.therun.gg/users/" + p_name).json()["result"]
            break
        except:
            sleep(delay)
            delay += 1
    for cat in root:
        category_name : str = cat["displayRun"].split('#')[1].lower()
        if category_name in cat_names:

            try:
                if cat["variables"]["Flipside/Flopside"] == "DS Lite":
                    continue
            except:
                pass

            try:
                if cat["variables"]["Normal/NG+"] != "Normal":
                    continue
            except:
                pass
            
            print("found " + category_name)
            ctx = ctx_from_cat_name(p_name,category_name)

            last_session = cat["sessions"][-1]

            last_session_time = dt.datetime.fromisoformat(last_session["endedAt"])

            if ctx.pit_type == sw.PitType.INVALID:
                try:
                    ctx.pit_type = sw.PitType(cat["variables"]["Category"])
                except:
                    ctx.pit_type = sw.PitType.CLASSIC

            crnt_latest = db.get_latest_run_in_context(cur, ctx)





            if crnt_latest == None or crnt_latest.time_ended.replace(tzinfo=None) < (last_session_time - time_offset).replace(tzinfo=None):
                found_split_names.append((ctx, cat["splitsFile"], last_session_time))


#generate folders for each player
for p in found_players:
    Path(sw.splits_path + p + "/").mkdir(parents=True,exist_ok=True)

for f in found_split_names:
    #download the file
    sleep(1)
    print("downloading " + f[1])
    while(True):
        try:
            urllib.request.urlretrieve("https://d2c9jb6sm40v74.cloudfront.net/" + f[1], "work_splits.lss")
            break
        except:
            sleep(delay)
            delay += 2
    ctx = f[0]

    #get current latest run
    #latest_run_in_new_splits = sw.get_latest_run_in_splits("./work_splits.lss")
    runs = sw.get_runs("./work_splits.lss", ctx)


    if ctx.pit_type == sw.PitType.INVALID:
        ctx = sw.guess_context_from_runs(ctx.player, runs)

    print("crnt ctx:", ctx.player, file_name_from_ctx(ctx))

    print("last therun session:", f[2])

    new_latest = sw.get_latest_run_in_splits("./work_splits.lss").time_ended
    crnt_latest = db.get_latest_run_in_context(cur, ctx)

    if crnt_latest != None:
        print("crnt_latest:", crnt_latest.time_ended)
    else:
        print("no crnt latest!")
    print("new_latest:", new_latest)

    print("new_latest_modified: ", (new_latest - time_offset))
    if crnt_latest == None or crnt_latest.time_ended.replace(tzinfo=None) < (new_latest - time_offset).replace(tzinfo=None):
        dest_path = sw.splits_path + ctx.player + "/" + file_name_from_ctx(ctx)

        if os.path.exists(dest_path):
            os.remove(dest_path)

        print("added " + dest_path + "!!!")
        os.rename("./work_splits.lss", dest_path)
    else:
        print("did not add")
    print("\n")

db.regenerate_database()
    



#TODO:
# update the db live so that multiples of splits dont overwrite eachother
















    
















