import sys
import graph_tool.all as gt
import matplotlib
import pickle
import numpy as np
from sets import Set
from find_fellows import *

"""
Calculates betweenness centrality for a co-citation network and prints info and plots the top results
"""

num_top = 1000

g = gt.load_graph("co-citation.graphml")

# Only loaded to get correct vertex loop order. If we create the co-citation graph using co_citation.py this is not needed
# since the original order is preserved then.
g_cg = gt.load_graph("APS.graphml") # load the original citation graph
g.set_directed(False)
labels = g.vertex_properties["label"]
# in_degs = g.degree_property_map("in")
print "Loaded a graph with " + str(g.num_vertices()) + " nodes"
#g = gt.GraphView(g, vfilt=gt.label_largest_component(g))

print "Calculating betweenness..."
vp, ep = gt.betweenness(g) # This takes a while...
print "Done calculating betweenness!"
#vp = gt.closeness(g)

# TODO: find out if we can pickle betweenness scores with correct indexes
# and then just load that array of floats
betweens = []
for b in vp.a:
    betweens.append(b)


#closeness = []
#for c in vp.a:
    #closeness.append(c)
with open("vpa-betweenness.pickle","wb") as f:
    pickle.dump(betweens,f)
    #pickle.dump(closeness,f)
print "vpa pickled!"

#with open("vpa-between.pickle","rb") as f:
    #vpa = np.asarray(pickle.load(f))

# write betweenness along with corresponding id to a csv file
with open("betweenness.csv","w+") as csv:
    csv.write("id,gt_index,betweenness\n")
    i = 0
    #for i,v_i in enumerate(top_vp):
    for n in g_cg.vertices(): # loop original order from citation graph
        #v = g.vertex(v_i)
        line = titles[n].strip().replace(",","") +\
                "," + str(i) + "," + str(vp[n]) + "\n"
        i += 1
        csv.write(line)
print "Wrote betweenness.csv"

#with open("top_vp.pickle","wb") as f:
    #pickle.dump(top_vp,f)

#with open("top_vp.pickle","rb") as f:
    #top_vp = pickle.load(f)