import graph_tool.all as gt
from find_fellows import *

dataset = "AAN" # "APS"
num_top = 100

graph_file = dataset + "/" + dataset + ".graphml" 
g = gt.load_graph(graph_file)

in_degs = g.degree_property_map("in")

top_in_degs = in_degs.a.argsort()[::-1]

titles = g.vertex_properties["title"]

authors = g.vertex_properties["authors"]

with open("csvs/indegs- " + dataset + ".csv", "w+") as csv:
    csv.write("title,gt_index,indegree\n")
    #for x in top_in_degs:
    i = 0
    for n in g.vertices():
        line = titles[n].strip().replace(",","") +\
                "," + str(i) + "," + str(in_degs[n]) + "\n"
        i += 1
        csv.write(line)
print "Wrote indegs.csv"

#top_authors = []
#fellow_articles = 0
#for i in range(num_top):
    #node = top_in_degs[i]
    #citations = in_degs.a[node]
    #print "##############################"
    #print "#####   " + str(i+1) + "   #####"
    #print "##############################"
    #print "Citations: " + str(citations) 
    #print "Title: " + titles[g.vertex(node)]
    #print "Authors: " + authors[g.vertex(node)]
    #auths = authors[g.vertex(node)]
    #auths = auths.split(";")
    ## TODO: old code. the new one is "find_fellow" and returns an index. 
    ## see betweenness.py for usage hints
    #found_fellow = False
    #for a in auths:
        #if is_fellow(a,reverse=True):
            #found_fellow = True
    #if found_fellow:
        #fellow_articles += 1

#print "Fellow articles: " + str(fellow_articles) + " / " + str(num_top)
