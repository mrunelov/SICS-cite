"""
Generate Px and burst pickles that contain numpy arrays
with the same ordering as the graph-tool Graph used.
"""

import pickle
import sys
import graph_tool.all as gt

Px_location = "/home/mrunelov/KTH/exjobb/SICS-cite/algorithms/pickles/APS-backbone-Px.pickle"

with open(Px_location,"rb") as Px_pickle:
    Px, ids = zip(*pickle.load(Px_pickle))

Px_map = {}
for i,nid in enumerate(ids):
    Px_map[nid] = Px[i]


g = gt.load_graph("APS.graphml")
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

with open("Px_list.pickle","wb") as f:
    pickle.dump(Px_list,f)

