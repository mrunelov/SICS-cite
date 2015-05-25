import graph_tool.all as gt
import pickle

g = gt.load_graph("AAN.graphml")
titles = g.vertex_properties["title"]
authors = g.vertex_properties["authors"]

with open("fellow_indexes.pickle","rb") as f:
    fellow_indexes = pickle.load(f)

for x in fellow_indexes:
    #print titles[g.vertex(x)]
    print authors[g.vertex(x)]
