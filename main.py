import xml.etree.ElementTree as ET
from datetime import datetime as dt
from datetime import timedelta as td
import matplotlib.pyplot as plt
import sys
import splits_work as sw
from datetime import timedelta as td
from skopt.space import Real
import splits_analysis as sa
import os
from typing import cast, List, Tuple
from copy import deepcopy

format_code = "%H:%M:%S.%f"


start_date = dt(2,1,1)
end_date = dt.now()


players = os.listdir("./splits/")

all_players = deepcopy(players)

types = ["Boomerless", "Classic", "Lite", "APNT"]

all_types = ["Boomerless", "Classic", "Lite", "Pixlless", "APNT"]

runs : list[sw.Run] = []

runs = sw.get_runs_filtered(start_date, end_date, players, types)






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

        runs = sw.get_runs_filtered(start_date, end_date, players, types)

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

        runs = sw.get_runs_filtered(start_date, end_date, players, types)

    if inp[0] == "types":
        if inp[1] == "add":
            types += inp[2:]

        elif inp[1] == "remove":
            for p in inp[2:]:
                try:
                    types.remove(p)
                except:
                    print(f"{p} not found.")
        
        elif inp[1] == "clear":
            types.clear()
        
        elif inp[1] == "all":
            types = all_types

        runs = sw.get_runs_filtered(start_date, end_date, players, types)

    if inp[0] == "gold":
        pb = sw.get_pb(sw.limit_to_range(inp[1], runs))

        if pb == None:
            print("no pb found")
            continue
    
        print(sw.get_run_descriptor(pb))

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
                if r.is_trustworthy_segment(i) and r.segment_times[i] < found_min.segment_times[i]:
                    found_min = r
            best_segments_runs.append(found_min)

        for r in range(len(best_segments_runs)):
            restricted = sw.limit_to_range(sw.split_names[r],[best_segments_runs[r]])[0]
            descriptor = sw.get_run_descriptor(restricted)

            print(sw.pad_to_length(sw.split_names[r], 5), descriptor)
        print("Sum: ", str(sw.sum_td([best_segments_runs[i].segment_times[i] for i in range(11)]))[:-4])



                

    if inp[0] == "rank":

        if inp[1] == "times" or inp[1] == "golds" or inp[1] == "averages":
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
    
                    player = run.player

                    if player in seen_players:
                        to_remove.append(run)
                    else:
                        seen_players.append(player)
                    
                    
                for t in to_remove:
                    relevant_runs_sorted.remove(t)
            
            if len(inp) == 3:
                size = 20
            else:
                size = int(inp[3])


            for i in range(min(len(relevant_runs_sorted), size)):

                run = relevant_runs_sorted[i]
                print(sw.pad_to_length(f"{i+1}.", 4),sw.get_run_descriptor(run))
        
                

            


          

    




    


        
        
        




    


    




    


    















