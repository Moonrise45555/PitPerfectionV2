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


format_code = "%H:%M:%S.%f"


start_date = dt(2,1,1)
end_date = dt.now()


players = os.listdir("./splits/")


runs = []

runs = sw.get_runs_filtered(start_date, end_date, players)






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

        runs = sw.get_runs_filtered(start_date, end_date, players)

    if inp[0] == "player":
        if inp[1] == "add":
            players += inp[2:]

        elif inp[1] == "remove":
            for p in inp[2:]:
                try:
                    players.remove(p)
                except:
                    print(f"{p} not found.")

        runs = sw.get_runs_filtered(start_date, end_date, players)

    if inp[0] == "gold":
        pb = sw.get_pb(sw.limit_to_range(inp[1], runs))

        if pb == None:
            print("no pb found")
            continue
    
        print(sw.get_run_descriptor(pb))

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
        
                

            


          

    




    


        
        
        




    


    




    


    















