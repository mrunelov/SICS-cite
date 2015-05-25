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

g = gt.load_graph("co-citation-AAN.graphml")
print "Loaded a graph with " + str(g.num_vertices()) + " nodes and " + str(g.num_edges()) + " edges."

for i in range(1,11):
    num = str(i)
    first = get_first(num)
    second = get_second(num)
    g1,g2 = get_gt_graphs(g,first,second)
    
    print "Calculating betweenness for first" + str(i) + "..."
    vp1,_ = gt.betweenness(g1)
    print "Done calculating betweenness!"
    pickle_result(vp1,name="between_first" + str(i))
    
    print "Calculating betweenness for second" + str(i) + "..."
    vp2,_ = gt.betweenness(g2)
    print "Done calculating betweenness!"
    pickle_result(vp2,name="between_second" + str(i))

#with open("vpa-between.pickle","rb") as f:
    #vpa = np.asarray(pickle.load(f))

#ids = g.vertex_properties["_graphml_vertex_id"]
# write betweenness along with corresponding id to a csv file
#g_cg = gt.load_graph("APS.graphml") # load the original citation graph
#with open("betweenness.csv","w+") as csv:
    #csv.write("id,gt_index,betweenness\n")
    #i = 0
    ##for i,v_i in enumerate(top_vp):
    #for n in g_cg.vertices(): # loop original order from citation graph
        #v = g.vertex(v_i)
        #line = ids[n].strip().replace(",","") +\
                #"," + str(i) + "," + str(vp[n]) + "\n"
        #i += 1
        #csv.write(line)
#print "Wrote betweenness.csv"

#with open("top_vp.pickle","wb") as f:
    #pickle.dump(top_vp,f)

#with open("top_vp.pickle","rb") as f:
    #top_vp = pickle.load(f)


