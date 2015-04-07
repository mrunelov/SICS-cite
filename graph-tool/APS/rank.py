import graph_tool.all as gt
import pickle
import numpy as np

num_top = 100

g = gt.load_graph("APS.graphml")
g.list_properties()
labels = g.vertex_properties["label"]
ids = g.vertex_properties["_graphml_vertex_id"]

indegs = g.degree_property_map("in")
top_indegs = indegs.a.argsort()[::-1]

print "Top " + str(num_top) + " indegrees:"
for i in range(num_top):
    #print ]]) + "\t" + labels.a[top_indegs[i]]
    print "Indegree: {:2d}, id: {:s},".format(indegs.a[top_indegs[i]],ids[g.vertex(top_indegs[i])]) + "\t" + labels[g.vertex(top_indegs[i])]

