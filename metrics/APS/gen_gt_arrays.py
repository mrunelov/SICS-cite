"""
Generate Px and burst pickles that contain numpy arrays
with the same ordering as the graph-tool Graph used.
"""

import pickle
import sys
import graph_tool.all as gt
from split import split_graph

def create_Px_list(g,Px_location,name="Px_list"):
    print "Px_location = " + Px_location
    with open(Px_location,"rb") as Px_pickle:
        Px, ids = zip(*pickle.load(Px_pickle))

    Px_map = {}
    for i,nid in enumerate(ids):
        Px_map[nid] = Px[i]


    #g = gt.load_graph("APS.graphml")
    graph_ids = g.vertex_properties["_graphml_vertex_id"]

    Px_list = []
    num_not_found = 0
    for n in g.vertices():
        found = False
        nid = graph_ids[n]
        if nid in Px_map:
            found = True
            Px_list.append(Px_map[nid])
        if not found:
            Px_list.append(0)
            num_not_found += 1

    print "Number of nodes not found in Px: " + str(num_not_found)

    with open(name + ".pickle","wb") as f:
        pickle.dump(Px_list,f)

#Px_location = "/home/mrunelov/KTH/exjobb/SICS-cite/algorithms/pickles/APS-backbone-Px.pickle"
#Px_location1 = "/home/mrunelov/KTH/exjobb/SICS-cite/algorithms/pickles/APS-backbone-Px.pickle"
#Px_location2 = "/home/mrunelov/KTH/exjobb/SICS-cite/algorithms/pickles/APS-backbone-Px.pickle"

g = gt.load_graph("/home/mrunelov/KTH/exjobb/SICS-cite/graph-tool/APS/APS.graphml")
#g1,g2 = split_graph(g)
#create_Px_list(g,Px_location1,"Px_list_first")
#create_Px_list(g,Px_location2,"Px_list_second")

Px_location_base = "/home/mrunelov/KTH/exjobb/SICS-cite/algorithms/pickles/APS-backbone-Px-"

weighted_location = Px_location_base + "weighted.pickle"
create_Px_list(g,weighted_location,"Px_list_weighted")

for i in range(1,11):
    for x in ["first","second"]:
        filename = Px_location_base + x + str(i) + ".pickle"
        name = "pickles/Px_list_" + x + str(i)
        create_Px_list(g,filename,name)

