import graph_tool.all as gt
import itertools
import config as conf

dataset = conf.settings['dataset']

G = gt.load_graph("../" + dataset + "/data/" + dataset + ".graphml") #"AAN-preprocessed.xml")

print "Loaded a graph with " + str(G.num_vertices()) + " vertices and " + str(G.num_edges()) + " edges."
CC = gt.Graph(G,directed=False)

for edge in G.edges():
    CC.remove_edge(edge)

weight = CC.new_edge_property("int")
CC.edge_properties["weight"] = weight
print G.list_properties()

N = str(G.num_vertices())
idx = 0
for n in G.vertices():
    if idx%10001 == 0:
        CC.save("tmp/co-citation-" + dataset + "-" + str(idx) + ".graphml")
    out_edges = list(n.out_edges())
    print "Looping node " + str(idx+1) + " / " + N + " with " + str(len(out_edges)) + " references" + "                \r",
    refs = [e.target() for e in out_edges]
    for i in range(len(refs)-1):
    #for u,v in itertools.combinations(refs,2):
        u = refs[i]
        for v in refs[i+1:]:
            edge = CC.edge(u,v)
            if edge is None:
                edge = CC.add_edge(u,v)
                weight[edge] = 0 # make sure weights start at 0
            weight[edge] += 1
    idx += 1


CC.save("co-citation-" + dataset + ".graphml")
