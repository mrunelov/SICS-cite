import graph_tool.all as gt
from find_fellows import *

num_top = 100

g = gt.load_graph("APS.graphml")
g.list_properties() # TODO: check if node id can be used or needs to be rewritten as a separate attribute

# in_degs = g.degree_property_map("in")

# labels = g.vertex_properties["label"]

# # write id,gt_index,indegree to csv file:
# with open("indegs.csv", "w+") as csv:
#     csv.write("id,gt_index,indegree\n")
#     i = 0
#     for n in g.vertices():
#         line = labels[n].strip().replace(",","") +\
#                 "," + str(i) + "," + str(in_degs[n]) + "\n"
#         i += 1
#         csv.write(line)
# print "Wrote indegs.csv"
