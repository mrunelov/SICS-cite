import graph_tool.all as gt   
import pickle
from datetime import datetime,timedelta

g = gt.load_graph("/home/mrunelov/KTH/exjobb/SICS-cite/APS/data/APS.graphml")
dates = g.vertex_properties["date"]
dateformat = "%Y-%m-%d"

#with open("fellow_indexes.pickle", "rb") as f:
    #fellow_indexes = pickle.load(f)

earliest = datetime(2015,1,1)
cutoff = datetime(1980,1,1)
second_earliest = earliest
fa_dates = []
i = 0
num_after = 0
#for idx in fellow_indexes:
for i in range(527129):
    v = g.vertex(i)
    date = datetime.strptime(dates[v],dateformat) 
    if date >= cutoff:
        num_after += 1

print "Num after cutoff: " + str(num_after)
#for x in s[:50]:
    #print x
