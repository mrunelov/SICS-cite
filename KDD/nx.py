import networkx as nx
from collections import Counter
import pickle
import os.path

def get_indegree(G): 
	if os.path.isfile('pickles/KDD-indegrees.pickle'):
		with open('pickles/KDD-indegree.pickle', 'rb') as f:
			return pickle.load(f)
	else:
		indegrees = G.in_degree(G.nodes_iter())
		with open('pickles/KDD-indegrees.pickle', 'wb') as f:
			pickle.dump(indegrees,f)
		return indegrees

		
def di_triangles():
	"""
	Finds triangles in a directed graph of the type:
    
    A------>B
	 \     /
	  \   /
	   >C<

	i.e. where A points to B and C, and B also points to C
	"""
	pass

def get_gml_graph():
	if os.path.isfile('pickles/KDD.pickle'):
		with open('pickles/KDD.pickle', 'rb') as f:
			print("Reading pickled graph...")
			G = nx.read_gpickle(f)
			print("Done reading graph.")
			return G

	print("Reading graphml file...")
	G = nx.read_graphml('data/KDD.graphml')
	print("Done reading graph of type " + str(type(G)))
	print("Read " + str(G.number_of_nodes()) + " nodes and " + str(G.number_of_edges()) + " edges.")
	is_dag = nx.is_directed_acyclic_graph(G)
	#print("Is DAG: " + str(is_dag))
	if not is_dag:
		selfloop_edges = G.selfloop_edges()
		biconnected_edges = []
		for u,v in G.edges_iter():
			if G.has_edge(v,u):
				biconnected_edges.extend([(u,v),(v,u)])
		#print("Number of self-loops: " + str(len(selfloop_edges)))
		#print("Number of biconnected pairs of nodes: " + str(len(biconnected_edges)))
		#print("Removing self-loops and biconnected pairs of nodes...")
		G.remove_edges_from(selfloop_edges)
		G.remove_edges_from(biconnected_edges)

		#print("New number of edges: " + str(G.number_of_edges()))
		#print("Is DAG now?..."),
		#is_dag = nx.is_directed_acyclic_graph(G)
		#print(str(is_dag))
		#print("Cycles: " + str(len(list(nx.simple_cycles(G)))))
	#print("Returning graph.")
	with open('pickles/KDD.pickle', 'wb') as f:	
		nx.write_gpickle(G, f)
	return G

def main():
	G = get_gml_graph()

	pr = nx.pagerank(G, alpha=0.5, max_iter=10)
	eigen_centrality = nx.eigenvector_centrality_numpy(G)
	indegree = get_indegree(G)
	#closeness = nx.closeness_centrality(G)
	#betweenness = nx.betweenness_centrality(G)

	top_pr = Counter(pr).most_common(10) # top 10 pageranks
	for n, rank in top_pr:
		rank = rank*10000.0

		print(G.node[n]['label'])
		print("\tPR: %0.2f"%(rank))
		print("\tIn-degree: %d"%(indegree[n]))
		#print("\tBetweenness centrality: %0.5f"%(betweenness[n]))
		#print("\tCloseness centrality: %0.5f"%(closeness[n]))
		print("\tEigenvector centrality: %0.5f"%(eigen_centrality[n]))
	
	#print [d for n,d in G.nodes_iter(data=True)] # prints all dictionaries of label-title pairs

main()