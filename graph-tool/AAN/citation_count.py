import graph_tool.all as gt
from find_fellows import *

g = gt.load_graph("AAN-preprocessed.xml")

in_degs = g.degree_property_map("in")

top_in_degs = in_degs.a.argsort()[::-1]

titles = g.vertex_properties["title"]
authors = g.vertex_properties["authors"]

top_authors = []
for i in range(32):
    node = top_in_degs[i]
    citations = in_degs.a[node]
    print "##############################"
    print "#####   " + str(i+1) + "   #####"
    print "##############################"
    print "Citations: " + str(citations) 
    print "Title: " + titles[g.vertex(node)]
    print "Authors: " + authors[g.vertex(node)]
    auths = authors[g.vertex(node)]
    auths = auths.split(";")
    for a in auths:
        is_fellow(a,reverse=True)
