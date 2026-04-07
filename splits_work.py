from datetime import timedelta as td
from datetime import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
import random
import xml.etree.ElementTree as ET
import sys
import os
import dataclasses
from enum import StrEnum
from typing import cast, List, Tuple
splits_path = "./splits/"
split_names = ["0-10", "10-20", "20-30", "30-40", "40-50", "50-60", "60-70", "70-80", "80-90", "90-99", "100"]

lengths_from_filesnames = []


class PitType(StrEnum):
    CLASSIC = "Classic"
    BOOMERLESS = "Boomerless"
    PIXLLESS = "Pixlless"
    INVALID = "INVALID"

class CategoryLength(StrEnum):
    FULL = "Full"
    LITE = "Lite"
    APNT = "APNT"

class SplitDetail(StrEnum):
    SPLIT = "Split"
    MERGED = "Merged"

def sum_td(list):
    """Sums the times in the list, ignores None"""
    total = td(0)
    for i in list:
        if i != None:
            total += i
    return total

type_from_name = {"boomerless" : PitType.BOOMERLESS, "classic" : PitType.CLASSIC, "pixlless" : PitType.PIXLLESS}
length_from_name = {"lite" : CategoryLength.LITE, "full" : CategoryLength.FULL, "apnt" : CategoryLength.APNT}
split_detail_from_name = {"split" : SplitDetail.SPLIT, "merged" : SplitDetail.MERGED}



@dataclasses.dataclass
class RunContext:
    player : str
    pit_type : PitType
    cat_length : CategoryLength
    split_detail : SplitDetail

def get_context_from_splits_name(name, player : str) -> RunContext:

    assert("_" in name)

    name = name.split("_")

    return RunContext(player, type_from_name[name[0]], length_from_name[name[1]], split_detail_from_name[name[2]])


    


class Run:
    db_id : int
    player : str
    segment_times : list[td|None]
    

    
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
    
    def is_trustworthy_range(self, start, end):
        return self.is_trustworthy_segment(start) and self.segment_times[end - 1] != None

    
    def get_final_time(self):
        """gets the sum of all segments in the run, returns none if the run did not finish."""
        if self.segment_times[-1] == None:
            return None
        
        total = td(0,0,0)
        for i in self.segment_times:
            if i != None:
                total += i

        return total
    
    def get_player(self) -> str:
        return self.run_context.player
    
    def get_pit_type(self) -> PitType:
        return self.run_context.pit_type
    
    def get_category_length(self) -> CategoryLength:
        return self.run_context.cat_length
    
    def get_segments_sum(self, start,end) -> td:
        return sum_td([i for i in self.segment_times[start:end] if i != None])
    
    def get_segment_time(self, seg) -> td:
        return self.segment_times[seg]
    
    def get_split_detail(self) -> SplitDetail:
        return self.run_context.split_detail
    

    


    

        

    livesplit_id : int
    time_started : dt
    time_ended : dt

    def __init__(self, splitt : list[td | None], id : int, started : dt, ended : dt, run_ctx : RunContext, db_id : int):
        self.segment_times = splitt
        self.livesplit_id = id
        self.time_started = started
        self.time_ended = ended
        self.run_context = run_ctx
        self.db_id = db_id



        
def copy_run_with_new_segments(r, segments : list[td|None]):
    return Run(segments, r.livesplit_id, r.time_started, r.time_ended, RunContext(r.get_player(), r.get_pit_type(), r.get_category_length(), r.get_split_detail()), r.db_id)


def get_lite_runs(classic_runs : list[Run]):
    cut_runs = []
    for r in classic_runs:
        if r.get_category_length() == CategoryLength.APNT:
            new_segments = r.segment_times[11:22]
        else:
            new_segments = r.segment_times[-11:]

        cut_runs.append(copy_run_with_new_segments(r, new_segments))
    return cut_runs
    
def get_latest_run_in_splits(path):
    rcx = RunContext("INVALID RCX", PitType.PIXLLESS, CategoryLength.LITE, SplitDetail.SPLIT)
    runs = get_runs(path, rcx)
    runs = sort_by_date(runs)

    return runs[0]

def guess_context_from_runs(player, runs):
    num_splits = len(runs[0].segment_times)

    type = PitType.CLASSIC
    if num_splits > 90:
        return RunContext(player, type, CategoryLength.LITE, SplitDetail.SPLIT)
    
    if num_splits == 13 or num_splits == 14:
        type = PitType.PIXLLESS
    
    if num_splits == 15 or num_splits == 16:
        type = PitType.BOOMERLESS

    return RunContext(player, type, CategoryLength.FULL, SplitDetail.MERGED)
    
    









def get_livesplit_ids(root):
    """used for the run construction process"""
    ids = []
    attempt_history = root[7]
    for atmpt in attempt_history:
        try:
            ids.append(int(atmpt.attrib["id"]))
        except:
            print("error?")
    return ids

def get_segment_time(segment, id):
    """used for the run construction process"""
    format_code = "%H:%M:%S.%f"
    #searches for the id of the chosen run within the segment
    s_history= segment[4]
    

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
          


def get_runs(path, ctx):
    """gets all the runs in a certain splt file"""
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
        runs.append(Run(segment_times, id, started, ended, ctx, -1))
    return runs



def assign_ids(runs : list[Run]):
    for i in range(len(runs)):
        runs[i].db_id = i
        
            




            














def skipped(seg_ind, segments, run_id):
    """used for the run construction process"""
    for i in segments[seg_ind][4]:
        if i.attrib["id"] == run_id:
            
            return len(i) == 0 
    print("run id not found")
    return True

def valid_segment(seg_ind, segments, time):
    """used for the run construction process"""
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
    """used for the run construction process"""
    id_list = [int(i.attrib["id"]) for i in attempt_history]
    index = binary_search(run_id, id_list)
    if index == -2:
        return dt(1, 1, 1)
    date_str = attempt_history[index].attrib["started"]
    
    return dt.strptime(date_str, "%m/%d/%Y %H:%M:%S")

def get_run_ended(run_id, attempt_history):
    """used for the run construction process"""
    id_list = [int(i.attrib["id"]) for i in attempt_history]
    index = binary_search(run_id, id_list)
    if index == -2:
        return dt(1, 1, 1)
    date_str = attempt_history[index].attrib["ended"]
    
    return dt.strptime(date_str, "%m/%d/%Y %H:%M:%S")



def get_times_from_segment(seg_ind, root, start_date = dt(2,1,1), end_date = dt.now()) -> list[td]:
    """used for the run construction process"""
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
    """returns the run with the best final time"""
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










def get_average_run(runs : list[Run]) -> list[td|None]:
    """returns a list with the average of each segment"""
    segments = [td(0,0,0) for i in range(len(runs[0].segment_times))]
    for i in range(len(segments)):
        s_times = [j.segment_times[i] for j in runs if j.segment_times[i] != None and j.is_trustworthy_segment(i)]
        segments[i] = average(s_times) # type: ignore
    segments = [None if s == td(0,0,0) else s for s in segments]

    return segments



def construct_runs_from_player(player : str):
    """used for the run construction process"""
    files = os.listdir(splits_path + f"{player}/")
    runs = []

    for f in files:
        path = splits_path +  f"{player}/{f}"
        file_descriptor = f[:-4]

        ctx = get_context_from_splits_name(file_descriptor, player)

        raw_file_runs = get_runs(path, ctx)

        if ctx.split_detail == SplitDetail.SPLIT:
            runs += merge_tens_splits(raw_file_runs)
        else:
            runs += get_lite_runs(raw_file_runs)
        
    return runs
        



            


    

def merge_tens_splits(split_up_runs : list[Run]):
    """used for the run construction process"""
    new_runs = []

    for r in split_up_runs:
        new_splits = []

        buffer = td(0)

        for i in range(0,10):
            set_start = 10 * i
            set_end = i * 10 + 10

            if i == 9:
                set_end -= 1

            if r.is_trustworthy_range(set_start, set_end):
                new_splits.append(buffer + sum_td(r.segment_times[set_start:set_end]))
                buffer = td(0)
            else:
                buffer += sum_td(r.segment_times[set_start:set_end])
                new_splits.append(None)

        if r.segment_times[-1] != None:
            new_splits.append(r.segment_times[-1])
        else:
            new_splits.append(None)

        new_runs.append(copy_run_with_new_segments(r, new_splits))




        

    return new_runs


        

    


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




    



def plot_segment(runs):
    """deprecated(?)"""
    times = [r.get_final_time() for r in sort_by_date(runs) if r.get_final_time() != None]
    tx = [sort_by_date(runs)[i].time_started.toordinal() for i in range(len(times))]
    ty = [t.total_seconds()/60 for t in times]
    plt.scatter(tx, ty)
    if True:
        b, a = np.polyfit(tx, ty, deg=1)

    
        xseq = np.linspace(min(tx), len(tx), num=100)
        r_val = improval_chance(ty)
    
        plt.plot(xseq, a + b * xseq, color="k", lw=2.5)
        plt.figtext(0, 0.9, "slope: " + ("%.4f" % b) + " r_val:" + ("%.4f" % r_val) + " average:" + ("%.4f" % average(ty)))
        

    plt.show()

def sort_by_date(runs : list[Run]):
    """sorts the runs by the time started"""
    date_func = lambda r : r.time_started
    runs.sort(key=date_func, reverse=True)
    return runs
    

def get_seg_name(seg_ind, segments):
    """used for the run construction process"""
    w_segment = segments[seg_ind]
    return w_segment[0].text



def filter_date(runs, start_date, end_date):
    """returns the subset of runs that was done in the given time range"""
    return [r for r in runs if r.time_started >= start_date and r.time_started <= end_date]
    
def split_sessions(Runs : list[Run]):
    """deprecated(?)"""
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


def get_range_from_str(range):
    """internal, returns a tuple associated with the passed string range, e.g. 0-99 returns (0,10)"""
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
        #form 0-10
        rooms = range.split("-")
        start_segment = int(rooms[0][0])
        end_segment = int(rooms[1][0])

        if len(rooms[0]) == 1 and rooms[0][0] == "1":
            start_segment = 0

        if rooms[1] == "99":
            end_segment = 10


    elif range == "full":
        pass
    elif range == "100":

        start_segment = 10
        end_segment = 11

    return (start_segment, end_segment)

    

def limit_to_range(range : str, runs : list[Run]) -> list[Run]:
    """returns the same runs with their segments limited to the given range"""
    #interpret range..
    start_segment, end_segment = get_range_from_str(range)

    cut_runs = []
    for r in runs:

        if r.is_trustworthy_range(start_segment, end_segment):

            new_segments = r.segment_times[start_segment:end_segment]
            cut_runs.append(copy_run_with_new_segments(r, new_segments))
    return cut_runs
    

def filter_runs(runs, start_date, end_date, types, lengths, players):
    runs = filter_date(runs, start_date, end_date)
    new_runs = []

    for r in runs:
        if r.get_pit_type() in types and r.get_player() in players and r.get_category_length() in lengths:
            new_runs.append(r)
     
    

    return new_runs

def get_playtime(runs):
    time = td(0)
    for r in runs:     
        time += sum_td(r.segment_times)

    return time


def get_all_players():
    return os.listdir(splits_path)
    




def construct_all_runs():
    runs = []

    players = get_all_players()


    for player in players:
        player_runs = construct_runs_from_player(player)
        for r in player_runs:
            runs.append(r)

    assign_ids(runs)


    return runs



def pad_to_length(string, length):
    return string + (" " * (length - len(string)))

def get_run_descriptor(run : Run):

    time : str = str(run.get_final_time())
    time = time[:-4]

    player = pad_to_length(run.get_player(), 15)

    type = pad_to_length(run.get_pit_type(), 12)


    return f"{time}  {player}  {run.time_started}  {type} {run.get_category_length()}   id {run.db_id}"

def print_run_details(run : Run):
    print(get_run_descriptor(run))

    print(" ", end="")
    for s in range(len(split_names)):
        print(split_names[s], pad_to_length(str(run.get_segment_time(s))[:-4], 10), pad_to_length(str(run.get_split_time(s))[:-4], 10)) 


def get_segment_ranges_as_runs(runs, range):

    relevant_runs = limit_to_range(range, runs)
    
    runs_with_final_times = [(r,r.get_final_time()) for r in relevant_runs if r.get_final_time() != None] 
    #stupid annoying    
    runs_with_final_times = cast(List[Tuple[Run, td]], runs_with_final_times)
    runs_with_final_times.sort(key=lambda x: x[1])
    relevant_runs_sorted = [r[0] for r in runs_with_final_times]

    return relevant_runs_sorted

def get_wr_progression(runs : List[Run]) -> List[Run]:
    prog_entries = []
    crnt_wr = td.max
    crnt_date = dt(year=1,month=1,day=1)

    runs = list(reversed(sort_by_date(runs)))

    for r in runs:
        time = r.get_final_time()

        if time != None and time < crnt_wr and crnt_date < r.time_started: # type: ignore
            prog_entries.append(r)
            crnt_wr = r.get_final_time()
            crnt_date = r.time_started
    
    return list(reversed(prog_entries))



    
