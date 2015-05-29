import sys
import graph_tool.all as gt
import matplotlib
import pickle
import numpy as np
from sets import Set
from split import split_graph,get_first,get_second

"""
Calculates betweenness centrality for a co-citation network and prints info and plots the top results
"""

dataset = "AAN" # "APS"

def pickle_result(vp, postfix):
    betweens = []
    for b in vp.a:
        betweens.append(b)
    name = "vpa-betweenness-" + dataset
    with open("pickles/" + name + ".pickle","wb") as f:
        pickle.dump(betweens,f)
    print "vpa pickled!"

def random_halves(g):
    for i in range(1,11):
        num = str(i)
        first = get_first(dataset,num)
        second = get_second(dataset,num)
        g1,g2 = split_graph(g,first,second)
        
        print "Calculating betweenness for first" + str(i) + "..."
        vp1,_ = gt.betweenness(g1)
        print "Done calculating betweenness!"
        pickle_result(vp1,postfix="between_first" + str(i) + "-" + dataset)
        
        print "Calculating betweenness for second" + str(i) + "..."
        vp2,_ = gt.betweenness(g2)
        print "Done calculating betweenness!"
        pickle_result(vp2,postfix="between_second" + str(i) + "-" + dataset)

if dataset == "APS":
    graph_file = "/home/mrunelov/KTH/exjobb/SICS-cite/algorithms/co-citation-APS.graphml"
elif dataset == "AAN":
    graph_file = "co-citation-AAN.graphml"

g = gt.load_graph(graph_file)
print "Loaded a graph with " + str(g.num_vertices()) + " nodes and " + str(g.num_edges()) + " edges."
# Optional pruning
#g2 = gt.load_graph("APS.graphml")
# since the original order is preserved then.
#g = gt.GraphView(g, vfilt=lambda v:g2.vertex(v).in_degree() > 20)
#g.purge_vertices()
#print "Pruned g, now with " + str(g.num_vertices()) + " nodes and " + str(g.num_edges()) + " edges."

vp, ep = gt.betweenness(g)
pickle_result(vp)

# Load existing vpa
# with open("vpa-between.pickle","rb") as f:
    # vpa = np.asarray(pickle.load(f))

ids = g.vertex_properties["_graphml_vertex_id"]
# write betweenness along with corresponding id to a csv file
#g_cg = gt.load_graph("APS.graphml") # load the original citation graph
with open("betweenness.csv","w+") as csv:
    csv.write("id,gt_index,betweenness\n")
    i = 0
    for n in g_cg.vertices(): # loop original order from citation graph
        v = g.vertex(v_i)
        line = ids[n].strip().replace(",","") +\
                "," + str(i) + "," + str(vp[n]) + "\n"
        i += 1
        csv.write(line)
print "Wrote betweenness.csv"