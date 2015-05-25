import pickle
import os.path
import networkx as nx
import itertools

"""
Utility functions for graphs
"""

def get_gml_graph(dataset,co_citation=False):
	"""
	Loads a graphml file into a networkx graph object.
	The graph object is pickled after the first time is read,
	and subsequent calls load the pickle
	"""
	picklefile = 'pickles/' + dataset + '.pickle'
	if False:#os.path.isfile(picklefile):
		with open(picklefile, 'rb') as f:
			print("Reading pickled graph...")
			G = nx.read_gpickle(f)
			print("Done reading graph.")
			return G

	# build filename
	graphmlfile = '../' + dataset + '/data/' + dataset
	if co_citation:
		 graphmlfile += 'co-citation'
	graphmlfile += '.graphml'

	if not os.path.isfile(graphmlfile):
		raise ValueError('No dataset files were found. Looked for:\n' + picklefile + '\n' + graphmlfile + '\n')

	print("Reading graphml file...")
	G = nx.read_graphml(graphmlfile)
	G = nx.DiGraph(G)
	print("Done reading graph of type " + str(type(G)))
	print("Read " + str(G.number_of_nodes()) + " nodes and " + str(G.number_of_edges()) + " edges.")
	is_dag = nx.is_directed_acyclic_graph(G)
	print("Is DAG: " + str(is_dag))
	if not is_dag: # try to make DAG or closer to DAG by pruning nodes and edges
		print "Removing self-loops and isolates..." #...biconnected nodes, 
		selfloop_edges = G.selfloop_edges()
		# biconnected_edges = []
		# for u,v in G.edges_iter(): # find bi-edges where two papers cite each other
		# 	if G.has_edge(v,u):
		# 		biconnected_edges.extend([(u,v),(v,u)])
		# G.remove_edges_from(biconnected_edges) # delete biconnecting edges
		G.remove_edges_from(selfloop_edges) # delete self-loops
		print(str(G.number_of_nodes()) + " nodes and " + str(G.number_of_edges()) + " edges remaining after removing self-loops.")
		G.remove_edges_from(nx.isolates(G)) # delete isolates
		print(str(G.number_of_nodes()) + " nodes and " + str(G.number_of_edges()) + " edges remaining after removing isolates.")
		print("Is DAG now?..."),
		is_dag = nx.is_directed_acyclic_graph(G)
		print(str(is_dag))
		print(str(G.number_of_nodes()) + " nodes and " + str(G.number_of_edges()) + " edges remaining after preprocessing.")
		#print("Cycles: " + str(len(list(nx.simple_cycles(G)))))
	with open('pickles/' + dataset + '.pickle', 'wb') as f:	
		nx.write_gpickle(G, f)
	return G


def build_time_slices(G,s):
	"""
	Create time slices of a graph G of size s.
	"""
	pass


# OBS: super slow with networkx, fast graph-tool version in co_citation.py
def build_co_citation_graph(G,dataset):
	print "Building co-citation graph for " + dataset
	cc = nx.Graph()
	i = 1
	num_nodes = G.number_of_nodes()
	for n in G:
		refs = G.successors(n)
		print "Looping node " + str(i) + " / " + str(num_nodes) + " (with " + str(len(refs)) + " refs)" +  "\r",
		i += 1
		for u,v in itertools.combinations(refs,2): # loop all co-citations
			if cc.has_edge(u,v):
				G.edge[u][v]['weight'] += 1
			else:
				G.add_edge(u,v,weight=1)
	print "Done. Writing Graphml file..."
	nx.write_graphml(cc, '../' + dataset + '/data/' + dataset + '-co-citation.graphml')
	print "Done. Wrote a graph with " + str(cc.number_of_nodes()) + " nodes and " + str(cc.number_of_edges()) + " edges."

#G = get_gml_graph('AAN')
