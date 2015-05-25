import sys
import graph_tool.all as gt
import matplotlib
import pickle
import numpy as np
from sets import Set
from split import split_graph,get_first,get_second,get_gt_graphs

"""
Calculates betweenness centrality for a co-citation network and prints info and plots the top results
"""

#num_top = 1000

g = gt.load_graph("/home/mrunelov/KTH/exjobb/SICS-cite/algorithms/co-citation-APS.graphml")
#cc1,cc2 = split_graph(g)

print "Loaded a graph with " + str(g.num_vertices()) + " nodes and " + str(g.num_edges()) + " edges."

#g2 = gt.load_graph("APS.graphml")
# Only loaded to get correct vertex loop order. If we create the co-citation graph using co_citation.py this is not needed
# since the original order is preserved then.
#g = gt.GraphView(g, vfilt=lambda v:g2.vertex(v).in_degree() > 20)
#g.purge_vertices()
#print "Pruned g, now with " + str(g.num_vertices()) + " nodes and " + str(g.num_edges()) + " edges."

#vp, ep = gt.betweenness(g)
#pickle_result(vp)

with open("vpa-between.pickle","rb") as f:
    vpa = np.asarray(pickle.load(f))

ids = g.vertex_properties["_graphml_vertex_id"]
# write betweenness along with corresponding id to a csv file
#g_cg = gt.load_graph("APS.graphml") # load the original citation graph
with open("betweenness.csv","w+") as csv:
    csv.write("id,gt_index,betweenness\n")
    i = 0
    #for i,v_i in enumerate(top_vp):
    for n in g_cg.vertices(): # loop original order from citation graph
        v = g.vertex(v_i)
        line = ids[n].strip().replace(",","") +\
                "," + str(i) + "," + str(vp[n]) + "\n"
        i += 1
        csv.write(line)
print "Wrote betweenness.csv"

#with open("top_vp.pickle","wb") as f:
    #pickle.dump(top_vp,f)

#with open("top_vp.pickle","rb") as f:
    #top_vp = pickle.load(f)


def pickle_result(vp, name="vpa-betweenness"):
    betweens = []
    for b in vp.a:
        betweens.append(b)
    #closeness = []
    #for c in vp.a:
        #closeness.append(c)
    with open("metrics/" + name + ".pickle","wb") as f:
        pickle.dump(betweens,f)
        #pickle.dump(closeness,f)
    print "vpa pickled!"
