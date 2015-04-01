from graphutils import get_gml_graph
from datetime import datetime
import networkx as nx
import codecs

dateformat = "%Y"

def write_meta_CSV():
	G = get_gml_graph("AAN")
	print "Parsed AAN with " + str(nx.number_of_nodes(G)) + " nodes and " + str(nx.number_of_edges(G)) + " edges."
	with codecs.open('../AAN/data/AAN-citations-with-date.csv','w+', "utf-8") as csv:
		csv.write('"citing_doi","cited_doi","citation_date"\n') # write headers
		for v in G:
			if "title" not in G.node[v]:
				continue
			us = G.in_edges(v)
			for e in us:
				if "title" not in G.node[e[0]]:
					continue
				line = G.node[e[0]]["title"].strip().replace(",","") + \
					"," + G.node[v]["title"].strip().replace(",","") + \
					"," + G.node[e[0]]["date"].strip().replace(",","") + "\n"
				csv.write(line)

write_meta_CSV()