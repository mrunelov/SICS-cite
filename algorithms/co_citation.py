import graph_tool.all as gt
import itertools
import config as conf

dataset = conf.settings['dataset']

G = gt.load_graph("../" + dataset + "/data/" + dataset + ".graphml") #"AAN-preprocessed.xml")
print "Loaded a graph with " + str(G.num_vertices()) + " vertices and " + str(G.num_edges()) + " edges."

del G.properties[("v","date")]
del G.properties[("v","label")]

G2 = gt.GraphView(G, vfilt=lambda v: v.in_degree() > 0,
        efilt=lambda e: e.source().out_degree >= 2)
print "After filtering there are " + str(G2.num_vertices()) + " vertices and " + str(G2.num_edges()) + " edges."
G2.purge_vertices()

#CC = gt.Graph(G2) #gt.load_graph("tmp/co-citation-APS-10000.graphml") 
#CC = gt.GraphView(CC,efilt=lambda e: False)
#CC.purge_edges()
#CC.set_directed(False)
CC = gt.load_graph("tmp/co-citation-APS-80000.graphml") # load partly processed graph

weight = CC.new_edge_property("int") #CC.edge_properties["weight"] 
CC.edge_properties["weight"] = weight

N = str(CC.num_vertices())
idx = -1
for n in G2.vertices():
    idx += 1
    if idx <= 80000:
        continue
    if idx%10000 == 0:
        CC.save("tmp/co-citation-" + dataset + "-tmp.graphml")
    out_edges = list(n.out_edges())
    if len(out_edges) <= 1:
        continue
    print "Looping node " + str(idx+1) + " / " + N + " with " + str(len(out_edges)) + " references" + "                \r",
    refs = [e.target() for e in out_edges]
    #for i in range(len(refs)-1):
    for u,v in itertools.combinations(refs,2):
        #u = refs[i]
        #for v in refs[i+1:]:
        edge = CC.edge(u,v)
        if edge is None:
            edge = CC.add_edge(u,v)
            weight[edge] = 0 # make sure weights start at 0
        weight[edge] += 1

print "Saving co-citation graph with " + str(CC.num_vertices()) + " nodes and " +\
        str(CC.num_edges()) + " edges."
CC.save("co-citation-" + dataset + ".graphml")
