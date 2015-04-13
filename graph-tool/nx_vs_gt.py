import graph_tool.all as gt
import networkx as nx
# Test loop order when loading graphml in networkx and graph-tool
# If they're the same we can do slower but correct calculations on the SICS server...

g = gt.load_graph("AAN/AAN.graphml")

G = nx.read_graphml("AAN/AAN.graphml")

titles = g.vertex_properties["title"]

idx = 0
for n in G:
    # TODO: compare nodes somehow
    gt_idx = int(n[1:]) - 1
    print G.node[n]["title"]
    print titles[g.vertex(gt_idx)]
    print "----------------------------------------------------------------------------------------"
    if idx > 5:
        break
    idx += 1

# TODO: maybe map G order to g order
