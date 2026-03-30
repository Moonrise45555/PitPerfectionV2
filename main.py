import xml.etree.ElementTree as ET
from datetime import datetime as dt
from datetime import timedelta as td
import matplotlib.pyplot as plt
import sys
import splits_work as sw
from datetime import timedelta as td
from skopt.space import Real

import os
from typing import cast, List, Tuple
from copy import deepcopy
import db_work as db
import sqlite3


con = sqlite3.connect("runs.db")

cur = con.cursor()



format_code = "%H:%M:%S.%f"


start_date = dt(2,1,1)
end_date = dt.now()


players = os.listdir(sw.splits_path)

all_players = deepcopy(players)

types = [sw.PitType.CLASSIC, sw.PitType.BOOMERLESS, sw.PitType.PIXLLESS]

lengths = [sw.CategoryLength.FULL, sw.CategoryLength.LITE, sw.CategoryLength.APNT]

runs : list[sw.Run] = []

runs = sw.filter_runs(db.get_all_runs(cur), start_date, end_date, types, lengths, players)


ctx = sw.RunContext("Moonrise45555", sw.PitType.PIXLLESS, sw.CategoryLength.FULL, sw.SplitDetail.MERGED)







while True:
    inp = input("")
    
    
    inp = inp.split(" ")


    if len(inp) == 0:
        print("invalid command")
        continue

    if inp[0] == "seltime":
        start_date = dt.strptime(inp[1],"%Y-%m-%d")
        if len(inp) == 3:
            end_date = dt.strptime(inp[2],"%Y-%m-%d")
        print("time of runs set to be between ", start_date ,"and ", end_date)

        runs = sw.filter_runs(db.get_all_runs(cur), start_date, end_date, types, lengths, players)

    if inp[0] == "player":
        if inp[1] == "add":
            players += inp[2:]

        elif inp[1] == "remove":
            for p in inp[2:]:
                try:
                    players.remove(p)
                except:
                    print(f"{p} not found.")
        
        elif inp[1] == "clear":
            players.clear()
        
        elif inp[1] == "all":
            players = all_players

        runs = sw.filter_runs(db.get_all_runs(cur), start_date, end_date, types, lengths, players)

    if inp[0] == "type":
        if inp[1] == "add":
            types += [sw.PitType(inp[2])]

        elif inp[1] == "remove":
            try:
                  types.remove(sw.PitType(inp[2]))  
            except:
                print(f"{inp[2]} not found.")
        
        elif inp[1] == "clear":
            types.clear()
        
        elif inp[1] == "all":
            types = [sw.PitType.CLASSIC, sw.PitType.BOOMERLESS, sw.PitType.PIXLLESS]

        runs = sw.filter_runs(db.get_all_runs(cur), start_date, end_date, types, lengths, players)

    if inp[0] == "length":
        if inp[1] == "add":
            lengths += [sw.CategoryLength(inp[2])]

        elif inp[1] == "remove":
            try:
                  lengths.remove(sw.CategoryLength(inp[2]))  
            except:
                print(f"{inp[2]} not found.")
        
        elif inp[1] == "clear":
            lengths.clear()
        
        elif inp[1] == "all":
            lengths  = [sw.CategoryLength.FULL, sw.CategoryLength.LITE, sw.CategoryLength.APNT]

        runs = sw.filter_runs(db.get_all_runs(cur), start_date, end_date, types, lengths, players)

    if inp[0] == "comsob":
        best_segments_runs = []

        for i in range(11):

            found_min = None

            #gets a start to work off of...
            for r in runs:
                if r.is_trustworthy_segment(i):
                    found_min = r
                    break
            if found_min == None:
                print("not enough splits!")
                break

                
            for r in runs:
                if r.is_trustworthy_segment(i) and r.segment_times[i] < found_min.segment_times[i]: # type: ignore
                    found_min = r
            best_segments_runs.append(found_min)

        for r in range(len(best_segments_runs)):
            restricted = sw.limit_to_range(sw.split_names[r],[best_segments_runs[r]])[0]
            descriptor = sw.get_run_descriptor(restricted)

            print(sw.pad_to_length(sw.split_names[r], 5), descriptor)
        print("Sum: ", str(sw.sum_td([best_segments_runs[i].segment_times[i] for i in range(11)]))[:-4])

    if inp[0] == "run":
        id = int(inp[1])

        run : sw.Run = db.get_run_with_id(cur, id)
        
        sw.print_run_details(run)

    if inp[0] == "regen":
        db.regenerate_database()
        runs = db.get_all_runs(cur)

    





                

    if inp[0] == "rank":

        if inp[1] == "times" or inp[1] == "golds" or inp[1] == "count":
            ranges = inp[2]

            relevant_runs = sw.limit_to_range(ranges, runs)

            

            runs_with_final_times = [(r,r.get_final_time()) for r in relevant_runs if r.get_final_time() != None] 

            #stupid annoying    
            runs_with_final_times = cast(List[Tuple[sw.Run, td]], runs_with_final_times)

            runs_with_final_times.sort(key=lambda x: x[1])

            relevant_runs_sorted = [r[0] for r in runs_with_final_times]


            if inp[1] == "golds":
                seen_players = []
                to_remove = []
                for run in relevant_runs_sorted:
    
                    player = run.get_player()

                    if player in seen_players:
                        to_remove.append(run)
                    else:
                        seen_players.append(player)
                    
                    
                for t in to_remove:
                    relevant_runs_sorted.remove(t)

            if inp[1] == "count":

                relevant_runs_sorted = relevant_runs_sorted[:int(inp[3])]
                found_playtimes = [0.0 for i in players]

                for p in range(len(players)):
                    for r in relevant_runs_sorted:

                        if r.get_player() == players[p]:
                            found_playtimes[p] += 1.0

                
                amnt = 20

                merged = [(players[i] ,found_playtimes[i]) for i in range(len(players))]



                merged.sort(key=lambda x: x[1], reverse=True)

                for i in range(min(amnt, len(players))):

                    print(f"{i + 1}. {sw.pad_to_length(merged[i][0], 15)}   {merged[i][1]}    {round((merged[i][1] / len(relevant_runs_sorted) ) * 100, 1)}%")
                continue
            
            if len(inp) == 3:
                size = 20
            else:
                size = int(inp[3])


            for i in range(min(len(relevant_runs_sorted), size)):

                run = relevant_runs_sorted[i]
                print(sw.pad_to_length(f"{i+1}.", 4),sw.get_run_descriptor(run))















    if inp[0] == "blacklist":
        for i in inp[1:]:
            db.add_to_blacklist(cur, db.get_run_with_id(cur, int(i)))
        con.commit()

    if inp[0] == "integrity":
        start, end = sw.get_range_from_str(inp[1])
        min_length = (end - start) * td(minutes=2)
        relevant_runs = sw.limit_to_range(inp[1], runs)
        for r in relevant_runs:
            if r.get_final_time() < min_length: # type: ignore
                db.add_to_blacklist(cur, r)
                print("added " + str(r.db_id) + " by " + r.get_player() + " to blacklist")
        con.commit()
    
    if inp[0] == "progression":
        relevant_runs = sw.get_segment_ranges_as_runs(runs, inp[1])

        prog = sw.get_wr_progression(relevant_runs)

        for p in prog:
            print(sw.get_run_descriptor(p))


    if inp[0] == "playtime":
        if inp[1] == "players":
            found_playtimes = [td(0) for i in players]

            for p in range(len(players)):
                for r in runs:

                    if r.get_player() == players[p]:
                        found_playtimes[p] += sw.sum_td(r.segment_times)

            amnt = int(inp[2])

            merged = [(players[i] ,found_playtimes[i]) for i in range(len(players))]

            

            merged.sort(key=lambda x: x[1], reverse=True)

            for i in range(min(amnt, len(players))):
                
                print(f"{i + 1}. {sw.pad_to_length(merged[i][0], 15)}   {merged[i][1]}")

    if inp[0] == "pbs-time":
        found_pbs = []
        for p in players:
            p_runs = sw.filter_runs(runs, start_date, end_date, types, lengths, [p])
            pb_progression = list(reversed(sw.get_wr_progression(sw.sort_by_date(sw.limit_to_range("full", p_runs)))))


        

            for i in range(len(pb_progression) - 1):
                prior_pb_time = pb_progression[i].time_ended
                next_pb_time = pb_progression[i + 1].time_ended
                time_played = sw.get_playtime(sw.filter_date(p_runs, prior_pb_time, next_pb_time))

                found_pbs.append((pb_progression[i+1], time_played))

            found_pbs.sort(key=lambda x: x[1], reverse=True)

        for i in found_pbs:
            print( sw.pad_to_length(str(i[1]), 25),sw.get_run_descriptor(i[0]))

        



            


    




        
                

            


          

    




    


        
        
        




    


    




    


    















