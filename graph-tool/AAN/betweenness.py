import sys
import graph_tool.all as gt
import matplotlib
import pickle
import numpy as np
from sets import Set
from find_fellows import *

"""
Calculates betweenness centrality for a co-citation network and prints info and plots the top results
"""

num_top = 1000

g = gt.load_graph("co-citation.graphml")
g.set_directed(False)
titles = g.vertex_properties["title"]
authors = g.vertex_properties["authors"]
in_degs = g.degree_property_map("in")
print "Loaded a graph with " + str(g.num_vertices()) + " nodes"
#g = gt.GraphView(g, vfilt=gt.label_largest_component(g))

vp, ep = gt.betweenness(g)
#vp = gt.closeness(g)

# TODO: find out if we can pickle betweenness scores with correct indexes
# and then just load that array of floats
#betweens = []
#for b in vp.a:
    #betweens.append(b)


#closeness = []
#for c in vp.a:
    #closeness.append(c)
#with open("vpa-closeness.pickle","wb") as f:
    #pickle.dump(betweens,f)
    #pickle.dump(closeness,f)
#print "vpa pickled!"

#with open("vpa-between.pickle","rb") as f:
    #vpa = np.asarray(pickle.load(f))

top_vp = vpa.argsort()[::-1]#[:num_top]

# write betweenness along with corresponding title to a csv file
with open("betwenness.csv","w+") as csv:
    for i,v_i in enumerate(top_vp):
        v = g.vertex(v_i)
        line = titles[v].strip().replace(",","") + "," + str(vpa[v]) + "\n"
        csv.write(line)

#with open("top_vp.pickle","wb") as f:
    #pickle.dump(top_vp,f)

#with open("top_vp.pickle","rb") as f:
    #top_vp = pickle.load(f)

# can't pickle vertex objects atm, but convert to int then save might work.
# so, maybe try looping vp.a

i = 0
fellow_articles = 0
fellows = Set(range(32))
#for i in range(num_top):
#for v in bg.vertices():
total = len(top_vp)
for i,v_i in enumerate(top_vp):
    sys.stderr.write("looping node " + str(i+1) + " / " + str(total) + "\r")
    sys.stderr.flush()
    #v = g.vertex(top_vp[i])
    v = g.vertex(v_i)
    print "##############"
    print "###   " + str(i+1) + "   ###"
    print "##############"
    print titles[v] 
    print authors[v]
    print "Betweenness: " + str(vpa[v])
    auths = authors[v]
    auths = auths.split(";")
    found_fellow = False
    for a in auths:
        fellow_index = find_fellow(a,reverse=True)
        if fellow_index is not -1:
            fellow_articles += 1
            if fellow_index in fellows:
                fellows.remove(fellow_index)
    if len(fellows) == 1: # found all fellows except Tou Ng
        break
    print "###################################################"
    i += 1


print "Fellow articles: " + str(fellow_articles) + " / " + str(num_top)
print "Fellows remaining: " + str(fellows)

#bg = gt.GraphView(g, vfilt=lambda v: vp[v] > vp.a.max() / 4)
#top_nodes = [g.vertex(v) for v in top_vp]
#bg = gt.GraphView(g, vfilt=lambda v: v in top_nodes)
#print "Number of nodes after filtering: " + str(bg.num_vertices())

#print "Calculating layout..." 
#pos = gt.fruchterman_reingold_layout(bg,n_iter=10) 
#print "Done calculating layout. Plotting."

#gt.graph_draw(bg, pos=pos, #vertex_fill_color=vpa,
        #vertex_size=gt.prop_to_size(in_degs, mi=7, ma=25),
        ##edge_pen_width=gt.prop_to_size(ep, mi=0.5, ma=5),
        #vcmap=matplotlib.cm.gist_heat,
        #output="co-citation_betweenness.pdf") #vorder=vpa, 
