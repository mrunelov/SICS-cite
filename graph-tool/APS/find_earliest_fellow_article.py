import graph_tool.all as gt   
import pickle
from datetime import datetime,timedelta

g = gt.load_graph("/home/mrunelov/KTH/exjobb/SICS-cite/APS/data/APS.graphml")
dates = g.vertex_properties["date"]
dateformat = "%Y-%m-%d"

with open("fellow_indexes.pickle", "rb") as f:
    fellow_indexes = pickle.load(f)

earliest = datetime(2015,1,1)
cutoff = datetime(1960,1,1)
second_earliest = earliest
fa_dates = []
i = 0
for idx in fellow_indexes:
    v = g.vertex(idx)
    date = datetime.strptime(dates[v],dateformat) 
    if date < cutoff:
        i += 1
    fa_dates.append(date)

s = sorted(fa_dates)

print "Num before cutoff: " + str(i) + " / " + str(len(fellow_indexes))

#for x in s[:50]:
    #print x
