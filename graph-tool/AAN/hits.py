import graph_tool.all as gt
from find_fellows import *
import pickle
import numpy as np

num_top = 10

g = gt.load_graph("AAN.graphml") #"AAN-preprocessed.xml")
#g.list_properties()
# date exists in this map. see code in other AAN folder for inspiration
# TODO: do HITS with different graph views. So, todo is: learn to filter on dates.

titles = g.vertex_properties["title"]
authors = g.vertex_properties["authors"]


#in_degs = g.degree_property_map("in")
#top_in_degs = in_degs.a.argsort()[::-1]
eig, auths, hubs = gt.hits(g)
top_auths = auths.a.argsort()[::-1]#[:num_top]
top_nodes = [g.vertex(v) for v in top_auths]
bg = gt.GraphView(g, vfilt=lambda v: v in top_auths)

with open("hits.csv", "w+") as csv:
    csv.write("title,gt_index,hits_auth\n")
    #for x in top_auths:
    i = 0
    for n in g.vertices():
        #v = g.vertex(x)
        line = titles[n].strip().replace(",","") +\
                "," + str(i) + "," + str(auths[n]) + "\n"
        i += 1
        csv.write(line)
print "Wrote hits.csv"

#i = 0
#fellow_articles = 0
#for i in range(num_top):
    #v = g.vertex(top_auths[i])
    #print "################"
    #print "###   " + str(i+1) + "   ###"
    #print "################"
    #print titles[v]
    #print authors[v]
    #print "Authority score: " + str(auths[v])
    #author_str = authors[v]
    #author_list = author_str.split(";")
    ## TODO: old code. see betweenness.py for how it's done now
    #found_fellow = False
    #for a in author_list:
        #if is_fellow(a,reverse=True):
            #found_fellow = True
    #if found_fellow:
        #fellow_articles += 1
    #print "#################"
    #i += 1

#print "Fellow articles: " + str(fellow_articles) + " / " + str(num_top)



# HITS returns:
#eig : float
    #The largest eigenvalue of the cocitation matrix.
#x : PropertyMap
    #A vertex property map containing the authority centrality values.
#y : PropertyMap
    #A vertex property map containing the hub centrality values.
