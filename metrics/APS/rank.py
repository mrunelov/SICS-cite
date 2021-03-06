import graph_tool.all as gt
import pickle
import numpy as np

num_top = 100

g = gt.load_graph("APS.graphml")
#g.list_properties()
labels = g.vertex_properties["label"]
ids = g.vertex_properties["_graphml_vertex_id"]

indegs = g.degree_property_map("in")
top_indegs = indegs.a.argsort()[::-1]

#print "Top " + str(num_top) + " indegrees:"
print "Indegree,id,title"
for i in range(num_top):
    #print ]]) + "\t" + labels.a[top_indegs[i]]
    print str(indegs.a[top_indegs[i]]) + "," + str(ids[g.vertex(top_indegs[i])]) + "," + labels[g.vertex(top_indegs[i])].replace(",",";")

