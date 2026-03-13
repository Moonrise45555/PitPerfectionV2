import sqlite3
import splits_work as sw
from datetime import datetime as dt
from datetime import timedelta as td
import os

def add_run(cur, run : sw.Run):
    stringed_segments = [str(s.total_seconds()) if s != None else "NULL" for s in run.segment_times]

    cur.execute(f"INSERT INTO runs VALUES('{run.db_id}','{run.player}', '{run.get_pit_type()}', '{run.get_category_length()}', '{run.get_split_detail()}',{run.time_started.timestamp()}, {run.time_ended.timestamp()} , '{run.livesplit_id}', {stringed_segments[0]} \
                ,{stringed_segments[1]}, {stringed_segments[2]}, {stringed_segments[3]}, {stringed_segments[4]}, {stringed_segments[5]} \
                    , {stringed_segments[6]}, {stringed_segments[7]}, {stringed_segments[8]} , {stringed_segments[9]} , {stringed_segments[10]})")


def regenerate_database():
    

    db = sqlite3.connect("runs.db")

    cur = db.cursor()
    

    runs = sw.construct_all_runs()

    try:
        cur.execute("DROP TABLE runs")
    except:
        pass

    cur.execute("""CREATE TABLE runs(id, player, pit_type , category_type, split_detail, time_started, time_ended, livesplit_id, "0s", "10s", "20s", "30s", "40s", "50s", "60s", "70s", "80s", "90s", "100")""")

    for r in runs:
        add_run(cur, r)
    
    db.commit()
    db.close()
    
    
    
def get_run_from_row(row):
    segments = [td(seconds=float(i)) if i != None else None for i in row[8:]]
    return sw.Run(segments, int(row[7]),dt.fromtimestamp(float(row[5])), dt.fromtimestamp(float(row[6])), sw.RunContext(row[1], row[2], row[3], row[4]), row[0])

def get_all_runs(cur):
    res = cur.execute("SELECT * FROM runs")
    res = res.fetchall()

    runs = [get_run_from_row(i) for i in res]

    return runs



if __name__ == '__main__':
    regenerate_database()





