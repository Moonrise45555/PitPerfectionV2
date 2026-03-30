```
A tool for analysing Statistics about Pit%. The code is extremely poorly optimised and organised at the moment, i think a rework into a website would be best.

Usage:
-> to scrape split data from therun, run therun_scraper.py. The Runs are both stored as Splits under splits/player/ and in the database runs.db. If you already have a database, put it into the root as runs.db.
-> to clear the list of blacklisted runs, run db_work.py.
-> to actually evaluate the data, run main.py.

ranges are of the form:
0s
10s
10-20
0-99
91-99
90s
100
Full (means 0-100)

Available Commands:

regen
  regenerates the database with the split files stored in the splits folder.

blacklist {run id}
  adds the given run id to the Blacklist table, run regen after to remove it from the database.

progression {range}
  prints the progression of best times in that range.

seltime {date} {date}
  dates are of the form 2025-12-31. restricts any future commands to only take runs from within that timerange.
  example: seltime 2023-01-01 2026-10-21

run {run id}
  prints details about a given run.

comsob
  prints the best Time for every segment.

rank times/golds/count {range} {amnt}
  prints a certain ranking.
  times ranks every time ever gotten on that range, amnt is the length of the leaderboard printed
  golds ranks the best time every player has gotten on that range, that means no player appears twice, amnt is the length of the leaderboard printed
  count ranks the amount of times every player shows up in the top {amnt} spots of the times leaderboard in the given range. very WIP.
  example: rank times 0s, rank times 0-30 100, rank golds 0s, rank count 0-20 50

player add/remove/clear/all
  removes, adds, clears, or fills the list of players which are evaluated. This is case-sensitive.
  example: player add Moonrise45555, player remove FRN6_Phantom, player clear

type add/remove/clear/all
  removes, adds, clears, or fills the list of pit types which are evaluted.
  example: type add boomerless, type remove pixlless, type remove classic, type all

length add/remove/clear/all
  removes, adds, clears, or fills the list of length categories which are evaluted.
  example: length add lite, length remove full, length clear, length all

WIP Commands, technically work but unstable, somewhat untrustworthy, ugly, probably should be evacuated to a more modular system

playtime players
  prints the in-pit playtime of all players, does not count the playtime completely correctly

pbs-time
  prints a ranking of the longest times spent in the pit without pbing, not completely accurate
```






