import graph_tool.all as gt
import matplotlib
import pickle
import numpy as np

g = gt.load_graph("co-citation.graphml")
g.set_directed(False)
titles = g.vertex_properties["title"]
authors = g.vertex_properties["authors"]
print "Loaded a graph with " + str(g.num_vertices()) + " nodes"
#g = gt.GraphView(g, vfilt=gt.label_largest_component(g))

vp, ep = gt.betweenness(g)
top_vp = vp.a.argsort()[::-1]
# can't pickle vertex objects atm, but convert to int then save might work.
# so, maybe try looping vp.a

#bg = gt.GraphView(g, vfilt=lambda v: vp[v] > vp.a.max() / 4)
#print "Number of nodes after filtering: " + str(bg.num_vertices())



i = 0
for i in range(32):
#for v in bg.vertices():
    v = top_vp[i]
    print "##############"
    print "###   " + str(i+1) + "   ###"
    print "##############"
    print titles[v] 
    print authors[v]
    print "Betweenness: " + str(vp[v])
    auths = authors[v]
    auths = auths.split(";")
    for a in auths:
        is_fellow(a,reverse=True)
    print "##############"
    i += 1
    #if i > 10:
        #break

print "Calculating layout..." 
pos = gt.fruchterman_reingold_layout(g,n_iter=10) 
print "Done calculating layout. Plotting."

gt.graph_draw(g, pos=pos, vertex_fill_color=vp,
        vertex_size=gt.prop_to_size(vp, mi=5, ma=15),
        edge_pen_width=gt.prop_to_size(ep, mi=0.5, ma=5),
        vcmap=matplotlib.cm.gist_heat,
        vorder=vp, output="co-citation_betweenness.pdf")
