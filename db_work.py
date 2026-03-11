import sqlite3
import splits_work as sw
from datetime import datetime as dt
from datetime import timedelta as td
import os



def regenerate_database():
    start_date = dt(1,1,1)
    end_date = dt.now()

    db = sqlite3.connect("runs.db")

    cur = db.cursor()
    players = os.listdir("./splits/")

    types = ["Boomerless", "Classic", "Lite", "Pixlless", "APNT"]

    runs = sw.get_runs_filtered(start_date, end_date, players, types)

    try:
        cur.execute("DROP TABLE runs")
    except:
        pass

    cur.execute("""CREATE TABLE runs(player, pit_type , category_type , time_started, time_ended, livesplit_id, "0s", "10s", "20s", "30s", "40s", "50s", "60s", "70s", "80s", "90s", "100")""")
    for r in runs:
        stringed_segments = [str(s.total_seconds()) if s != None else "NULL" for s in r.segment_times]

        cur.execute(f"INSERT INTO runs VALUES('{r.player}', '{r.type}', '{r.type}', {r.time_started.timestamp()}, {r.time_ended.timestamp()} , '{r.livesplit_id}', {stringed_segments[0]} \
                    ,{stringed_segments[1]}, {stringed_segments[2]}, {stringed_segments[3]}, {stringed_segments[4]}, {stringed_segments[5]} \
                        , {stringed_segments[6]}, {stringed_segments[7]}, {stringed_segments[8]} , {stringed_segments[9]} , {stringed_segments[10]})")
    
    db.commit()
    db.close()
    
    
    
def get_run_from_row(row):
    segments = [td(seconds=float(i)) if i != None else None for i in row[5:]]
    return sw.Run(segments, int(row[5]),dt.fromtimestamp(float(row[3])), dt.fromtimestamp(float(row[4])), row[0], row[1])

def get_all_runs(cur):
    res = cur.execute("SELECT * FROM runs")
    res = res.fetchall()

    runs = [get_run_from_row(i) for i in res]

    return runs

    





