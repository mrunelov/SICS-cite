import graph_tool.all as gt   
import pickle
from datetime import datetime,timedelta

g = gt.load_graph("AAN.graphml")
dates = g.vertex_properties["date"]
dateformat = "%Y"

#with open("fellow_indexes.pickle", "rb") as f:
    #fellow_indexes = pickle.load(f)

earliest = datetime(2015,1,1)
cutoff = datetime(2000,1,1)
second_earliest = earliest
num_after = 0
for i in range(18158):
    v = g.vertex(i)
    date = datetime.strptime(dates[v],dateformat) 
    if date < earliest:
        earliest = date
    if date >= cutoff:
        num_after += 1

print "Earliest article: " + str(earliest)
print "Num after 2000: " + str(num_after)
