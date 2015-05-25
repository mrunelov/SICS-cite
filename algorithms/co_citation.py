import graph_tool.all as gt
import itertools
import config as conf

dataset = conf.settings['dataset']

G = gt.load_graph("../" + dataset + "/data/" + dataset + ".graphml") #"AAN-preprocessed.xml")
print "Loaded a graph with " + str(G.num_vertices()) + " vertices and " + str(G.num_edges()) + " edges."


with open("../graph-tool/APS/pickles/first1.pickle","rb") as f:
    first = pickle.load(f)
    first_a = np.zeros(527129)
    for f_i in first:
        first_a[f_i] = 1

with open("../graph-tool/APS/pickles/second1.pickle","rb") as f:
    second = pickle.load(f)
    second_a = np.zeros(527129)
    for s_i in second:
        second_a[s_i] = 1

del G.properties[("v","date")]
del G.properties[("v","label")]

G2 = gt.GraphView(G, vfilt=lambda v: v.in_degree() > 0,
        efilt=lambda e: e.source().out_degree >= 2)

G_first = gt.GraphView(G2,vfilt=first_a)
G_second = gt.GraphView(G2,vfilt=second_a)

print "After filtering there are " + str(G_first.num_vertices()) + " vertices and " + str(G_first.num_edges()) + " edges in first" 
print "After filtering there are " + str(G_second.num_vertices()) + " vertices and " + str(G_second.num_edges()) + " edges in second" 

G_first.purge_vertices()
G_second.purge_vertices()

#CC = gt.Graph(G2) #gt.load_graph("tmp/co-citation-APS-10000.graphml") 
CC1 = gt.GraphView(G_first,efilt=lambda e: False)
CC2 = gt.GraphView(G_second,efilt=lambda e: False)
#CC.purge_edges()
CC1.set_directed(False)
CC2.set_directed(False)
#CC = gt.load_graph("tmp/co-citation-APS-80000.graphml") # load partly processed graph

weight = CC1.new_edge_property("int") #CC.edge_properties["weight"] 
weight = CC2.new_edge_property("int") #CC.edge_properties["weight"] 
CC1.edge_properties["weight"] = weight
CC2.edge_properties["weight"] = weight


def build_co_citation(CC):
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
