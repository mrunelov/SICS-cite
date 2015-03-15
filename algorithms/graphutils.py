import pickle
import os.path
import networkx as nx

def get_gml_graph(dataset):
	"""
	Loads a graphml file into a networkx graph object.
	The graph object is pickled after the first time is read,
	and subsequent calls load the pickle
	"""
	picklefile = 'pickles/' + dataset + '.pickle'
	if os.path.isfile(picklefile):
		with open(picklefile, 'rb') as f:
			print("Reading pickled graph...")
			G = nx.read_gpickle(f)
			print("Done reading graph.")
			return G

	graphmlfile = '../' + dataset + '/data/' + dataset + '.graphml'
	if not os.path.isfile(graphmlfile):
		raise ValueError('No dataset files were found. Looked for:\n' + picklefile + '\n' + graphmlfile + '\n')

	print("Reading graphml file...")
	G = nx.read_graphml(graphmlfile)
	G = nx.DiGraph(G)
	print("Done reading graph of type " + str(type(G)))
	print("Read " + str(G.number_of_nodes()) + " nodes and " + str(G.number_of_edges()) + " edges.")
	is_dag = nx.is_directed_acyclic_graph(G)
	#print("Is DAG: " + str(is_dag))
	if not is_dag: # try to make DAG or closer to DAG by pruning nodes and edges
		selfloop_edges = G.selfloop_edges()
		biconnected_edges = []
		for u,v in G.edges_iter(): # find bi-edges where two papers cite each other
			if G.has_edge(v,u):
				biconnected_edges.extend([(u,v),(v,u)])
		G.remove_edges_from(nx.isolates(G)) # delete isolates
		G.remove_edges_from(selfloop_edges) # delete self-loops
		G.remove_edges_from(biconnected_edges) # delete biconnecting edges
		print("Is DAG now?..."),
		is_dag = nx.is_directed_acyclic_graph(G)
		print(str(is_dag))
		#print("Cycles: " + str(len(list(nx.simple_cycles(G)))))
	with open('pickles/' + dataset + '.pickle', 'wb') as f:	
		nx.write_gpickle(G, f)
	return G