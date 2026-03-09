from datetime import timedelta as td
from datetime import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
import random
import xml.etree.ElementTree as ET
import sys
import os


def sum_td(list):
    total = list[0] - list[0]
    for i in list:
        total += i
    return total


class Run:
    player : str
    segment_times : list[td]
    type : str

    
    def get_split_time(self, split : int):
        total = td(0,0,0)
        for i in self.segment_times[:(split + 1)]:
            if i != None:
                total += i
        return total
    
    def is_trustworthy_segment(self, index):
        if self.segment_times[index] == None:
            return False
        if index != 0:
            if self.segment_times[index - 1] == None:
                return False
        return True
    
    def get_final_time(self):

        
        if self.segment_times[-1] == None:
            return None
        
        total = td(0,0,0)
        for i in self.segment_times:
            if i != None:
                total += i


        
        
        return total

    

        

    livesplit_id : int
    time_started : dt
    time_ended : dt

    def __init__(self, splitt, id, started, ended, player, type):
        self.segment_times = splitt
        self.livesplit_id = id
        self.time_started = started
        self. time_ended = ended
        self.player = player
        self.type = type
        

invalid_run : Run = Run(None, None, None, None, None, None)


def get_lite_runs(classic_runs : list[Run]):
    cut_runs = []
    for r in classic_runs:
        new_segments = r.segment_times[-11:]
        cut_runs.append(Run(new_segments, r.livesplit_id, r.time_started, r.time_ended, r.player, r.type))
    return cut_runs
    










def get_livesplit_ids(root):
    ids = []
    attempt_history = root[7]
    for atmpt in attempt_history:
        try:
            ids.append(int(atmpt.attrib["id"]))
        except:
            print("error?")
    return ids

def get_segment_time(segment, id):
    format_code = "%H:%M:%S.%f"
    #searches for the id of the chosen run within the segment
    s_history= segment[4]
    if id == 135:
        pass
    ids = [int(h.attrib["id"]) for h in s_history]
    run_index = binary_search(id, ids)
    if run_index == -2:
        #nothing found, skipped split possibly?
        return None
    else:
        #
        Time_entry = s_history[run_index]
        if len(Time_entry) == 0:
            return None
        if "." in Time_entry[0].text:
            time_datetime = (dt.strptime(str(Time_entry[0].text)[0:-1],format_code))
        else:
            time_datetime = (dt.strptime(str(Time_entry[0].text)[0:-1],"%H:%M:%S"))
        time_deltatime = td(hours=time_datetime.hour, minutes=time_datetime.minute, seconds=time_datetime.second, microseconds=time_datetime.microsecond)
        return time_deltatime
          


def get_runs(path, player, run_type):
    tree = ET.parse(path)
    root = tree.getroot()

    #get all livesplit ids of all runsF
    segments = root[8]
    
    attempt_history = root[7]
    livesplit_ids = get_livesplit_ids(root)
    runs = []
    for id in livesplit_ids:
        segment_times = []
        for s in segments:

            segment_times.append(get_segment_time(s, id))

        started = get_run_date(id, attempt_history)
        ended = get_run_ended(id, attempt_history)
        runs.append(Run(segment_times, id, started, ended, player, run_type))
    return runs


        
            




            














def skipped(seg_ind, segments, run_id):
    
    for i in segments[seg_ind][4]:
        if i.attrib["id"] == run_id:
            
            return len(i) == 0 
    print("run id not found")
    return True

def valid_segment(seg_ind, segments, time):
    #takes in Time object, not a timedelta!
    run_id = time.attrib["id"]
    if skipped(seg_ind, segments, run_id):
        return False          
    
    if seg_ind != 0:
        if skipped(seg_ind - 1, segments, run_id ):
            return False
    return True

def binary_search(num, list):
    if(len(list) == 0):
        return -2
    if len(list) == 1 and list[0] != num:
        return -2
    middle = len(list) // 2
    if list[middle] == num:
        return middle
    if list[middle] > num:
        b = binary_search(num, list[0:middle])
        if b == -2:
            return -2
        else:
            return b
    if list[middle] < num:
        b = binary_search(num, list[middle:])
        if b == -2:
            return -2
        else:
            return middle + b
        
            
def get_run_date(run_id, attempt_history):

    id_list = [int(i.attrib["id"]) for i in attempt_history]
    index = binary_search(run_id, id_list)
    if index == -2:
        return dt(1, 1, 1)
    date_str = attempt_history[index].attrib["started"]
    
    return dt.strptime(date_str, "%m/%d/%Y %H:%M:%S")

def get_run_ended(run_id, attempt_history):

    id_list = [int(i.attrib["id"]) for i in attempt_history]
    index = binary_search(run_id, id_list)
    if index == -2:
        return dt(1, 1, 1)
    date_str = attempt_history[index].attrib["ended"]
    
    return dt.strptime(date_str, "%m/%d/%Y %H:%M:%S")



def get_times_from_segment(seg_ind, root, start_date = dt(2,1,1), end_date = dt.now()) -> list[td]:
    segments = root[8]
    format_code = "%H:%M:%S.%f"
    w_segment = segments[seg_ind]
    w_segmentHistory = w_segment[4]
    times = []
    
    for time in w_segmentHistory:
        if not valid_segment(seg_ind, segments, time):
            continue
        run_id = int(time.attrib["id"])




        if "." in time[0].text:
            time_datetime = (dt.strptime(str(time[0].text)[0:-1],format_code))
        else:
            time_datetime = (dt.strptime(str(time[0].text)[0:-1],"%H:%M:%S"))


        time_deltatime = td(hours=time_datetime.hour, minutes=time_datetime.minute, seconds=time_datetime.second, microseconds=time_datetime.microsecond)

        if (get_run_date(run_id, root[7]) <= end_date and get_run_date(run_id, root[7]) >= start_date):
            times.append(time_deltatime)
        

    return times

def get_pb(runs : list[Run]):

    pb = None
    min_final_time = td(99999)
    for r in runs:
        f = r.get_final_time()
        if f == None:
            continue
        if f < min_final_time:
            min_final_time = f
            pb = r
           
    return pb 
from math import inf

def expected_pb_time(runs : list[Run], pb, reset_thresholds=None, simulations=10000):
    if reset_thresholds == None:
        reset_thresholds = [td(999) for i in runs[0].segment_times]

    
    pb_final_time = pb.get_final_time()
    


   
    valid_segment_times = [[] for r in runs[0].segment_times]
    for r in runs:
        for s in range(len(r.segment_times)):
            if r.is_trustworthy_segment(s):
                valid_segment_times[s].append(r.segment_times[s])
    
    

    
    
    time_elapsed = td(0,0,0)
    passed = 1
    
    for _ in range(simulations):

        working_run = td(0,0,0)
        for i in range(len(valid_segment_times)):
            seg_time = valid_segment_times[i][random.randint(0, len(valid_segment_times[i]) - 1)]
            working_run += seg_time
            time_elapsed += seg_time
            if i != len(valid_segment_times) - 1:
                if working_run > reset_thresholds[i]:
                    working_run = td.max
                    break


        if working_run < pb_final_time:
            passed += 1

        
    return time_elapsed / passed if passed != 0 else td.max









def get_average_run(runs : list[Run]):
    segments = [td(0,0,0) for i in range(len(runs[0].segment_times))]
    for i in range(len(segments)):
        s_times = [j.segment_times[i] for j in runs if j.segment_times[i] != None and j.is_trustworthy_segment(i)]
        segments[i] = average(s_times) # type: ignore
    segments = [None if s == td(0,0,0) else s for s in segments]

    return Run(segments, -1, dt.now(), dt.now(), "Mixed", "Mixed")


def get_runs_by_player(player : str):
    files = os.listdir(f"./splits/{player}/")
    runs = []

    for f in files:
        if f == "classic.lss":
            runs += get_lite_runs(get_runs(f"./splits/{player}/{f}", player, "Classic"))
        if f == "lite.lss":
            runs += get_runs(f"./splits/{player}/{f}", player, "Lite")
        if f == "boomerless.lss":
            runs += get_lite_runs(get_runs(f"./splits/{player}/{f}", player, "Boomerless"))
    
    return runs


    

            

        

    


def average(lis):
    if len(lis) == 0:
        return None
    sum = lis[0] - lis[0]
    for i in lis:
        sum += i
    return sum / len(lis)

def std_deviation(lis):
    if len(lis) == 0:
        return 0.0
    avg = average(lis)
    sum_sqrd = 0.0
    for i in lis:
        sum_sqrd += ((i - avg) ** 2)
    return (sum_sqrd / (len(lis) - 1)) ** 0.5

def get_segments(root):
    return root[8]










def covariance(ty, tx):
    sum = 0.0
    average_tx = average(tx)
    average_ty = average(ty)
    for i in tx:
        sum += (tx[i] - average_tx) * (ty[i] - average_ty)
    return sum / (len(ty) - 1)

def correlation_coefficient(ty, tx):
    return covariance(ty, tx) / (std_deviation(tx) * std_deviation(ty))

def improval_chance(ty):
    tx = [i for i in range(len(ty))]

    return correlation_coefficient(ty, tx)




    



def plot_segment(seg_ind, root, start_date = dt(2,1,1), end_date = dt.now(), lin_reg = False):
    times = get_times_from_segment(seg_ind, root, start_date = start_date, end_date = end_date)
    tx = [i for i in range(len(times))]
    ty = [t.total_seconds() for t in times]
    plt.scatter(tx, ty)
    if lin_reg:
        b, a = np.polyfit(tx, ty, deg=1)

    
        xseq = np.linspace(0, len(tx), num=100)
        r_val = improval_chance(ty)
    
        plt.plot(xseq, a + b * xseq, color="k", lw=2.5)
        plt.figtext(0, 0.9, "slope: " + ("%.4f" % b) + " r_val:" + ("%.4f" % r_val) + " average:" + ("%.4f" % average(ty)))
        

    plt.show()

def sort_by_date(runs : list[Run]):
    date_func = lambda r : r.time_started
    runs.sort(key=date_func)
    return runs
    

def get_seg_name(seg_ind, segments):
    w_segment = segments[seg_ind]
    return w_segment[0].text



def filter_date(runs, start_date, end_date):
    return [r for r in runs if r.time_started >= start_date and r.time_started <= end_date]
    
def split_sessions(Runs : list[Run]):
    #returns lists of lists of runs which represents sessions
    Runs = sort_by_date(Runs)
    session_threshold = td(minutes=30)
    session_ind = 0
    run_work_ind = 1
    sessions : list[list[Run]] = [[]]
    newest_time = Runs[0].time_ended
    while newest_time != Runs[-1].time_ended:
        #check if runs are sufficiently close together
        if Runs[run_work_ind].time_started - newest_time < session_threshold:
            #add run to session
            sessions[session_ind].append(Runs[run_work_ind])
        else:
            session_ind += 1
            sessions.append([])
            sessions[session_ind].append(Runs[run_work_ind])
        newest_time = Runs[run_work_ind].time_ended
        run_work_ind += 1


    return sessions


def limit_to_range(range : str, runs : list[Run]) -> list[Run]:
    #interpret range..
    start_segment = 0
    end_segment = 11


    if range[-1] == "s":
        if len(range) == 3:
            #form 20s, 30s, etc
            start_segment = int(range[0])
            end_segment = start_segment + 1
        if len(range) == 2:
            #form 0s
            start_segment = 0
            end_segment = 1

    elif "-" in range:
        rooms = range.split("-")
        start_segment = int(rooms[0][0])
        end_segment = int(rooms[1][0])

        if len(rooms[0]) == 1 and rooms[0][0] == "1":
            start_segment = 0

        if rooms[1] == "99":
            end_segment = 10


    elif range == "full":
        pass
    else:
        raise Exception()


    cut_runs = []
    for r in runs:

        if r.is_trustworthy_segment(start_segment) and r.is_trustworthy_segment(start_segment) and r.is_trustworthy_segment(end_segment - 1):

            new_segments = r.segment_times[start_segment:end_segment]
            cut_runs.append(Run(new_segments, r.livesplit_id, r.time_started, r.time_ended, r.player, r.type))
    return cut_runs
    


    




def get_runs_filtered(start_date, end_date, players):

    runs = []

    for player in players:
        player_runs = get_runs_by_player(player)
        for r in player_runs:
            runs.append(r)


    runs = filter_date(runs, start_date, end_date)

    return runs

def pad_to_length(string, length):
    return string + (" " * (length - len(string)))

def get_run_descriptor(run):

    time : str = str(run.get_final_time())
    time = time[:-4]

    player = pad_to_length(run.player, 15)

    type = pad_to_length(run.type, 15)


    return f"{time}  {player}  {run.time_started}  {type}"


