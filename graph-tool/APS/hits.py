import graph_tool.all as gt
import pickle
import numpy as np

num_top = 10

g = gt.load_graph("APS.graphml")
g.list_properties() # TODO: check if node id can be used or needs to be rewritten as a separate attribute
labels = g.vertex_properties["label"]


print "Running HITS..."
eig, auths, hubs = gt.hits(g) # Might take a while...
print "Done running HITS!"

# write to csv file
with open("hits.csv", "w+") as csv:
    csv.write("id,gt_index,hits_auth\n")
    i = 0
    for n in g.vertices():
        line = labels[n].strip().replace(",","") +\
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
