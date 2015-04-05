import graph_tool.all as gt
import itertools
import config as conf

dataset = conf.settings['dataset']

G = gt.load_graph("../" + dataset + "/data/" + dataset + ".graphml") #"AAN-preprocessed.xml")

CC = gt.Graph(G,directed=False)
for edge in G.edges():
    CC.remove_edge(edge)

weight = CC.new_edge_property("int")
CC.edge_properties["weight"] = weight
print G.list_properties()

N = str(G.num_vertices())
i = 1
for n in G.vertices():
    i += 1
    out_edges = list(n.out_edges())
    print "Looping node " + str(i) + " / " + N + " with " + str(len(out_edges)) + " references" + "\r",
    refs = [e.target() for e in out_edges]
    for u,v in itertools.combinations(refs,2):
        edge = CC.edge(u,v)
        if edge is None:
            edge = CC.add_edge(u,v)
            weight[edge] = 0 # make sure weights start at 0
        weight[edge] += 1
        if weight[edge] == 0:
            print "WTF?"


CC.save("co-citation-" + dataset + ".graphml")
