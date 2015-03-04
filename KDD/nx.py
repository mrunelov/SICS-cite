import networkx as nx
from collections import Counter, defaultdict
import itertools
import pickle
import os.path

def sim_read_helper(G, a, b):
	"""
 	Calcuates the similarity between a and b from the reader's perspective
 	by counting co-citations. Skips multiplying by 1/indegree in order to
 	make the result usable by both a and b in the impact calculation (see impacts())
	"""
	offspring = G.in_edges([a,b])
	common_offspring = [u for u,v in offspring] # co-citing offspring! 
	sim_read = 0
	for o in common_offspring:
		sim_read += (1/G.out_degree(o))
	return sim_read

def sim_aut_helper(G, a, b):
	"""
	A two-step random walk from a to b
	that simulates author's (a and b) interpretations
	since the measure is based on their references
	"""
	parents = G.out_edges([a,b])
	common_parents = [v for u,v in parents]
	sim_aut = 0
	for p in common_parents:
		sim_aut += (1/G.in_degree(p))
	return sim_aut

def sim_read_pair(G, a, b):
	"""
	Calculates the read similarity for a and b
	"""
	a_ins = G.in_degree(a)
	b_ins = G.in_degree(b)
	sim_read = sim_read_helper(G,a,b)
	return [a_ins*sim_read, b_ins*sim_read]

def sim_aut_pair(G, a, b):
	"""
	Calculates the aut similarity for a and b
	"""
	a_outs = G.out_degree(a)
	b_outs = G.out_degree(b)
	sim_aut = sim_aut_helper(G,a,b)
	return [a_outs*sim_aut, b_outs*sim_aut]


def get_impacts(G, parent, children):
	"""
	The impact of a parent on its children
	"""
	impacts = defaultdict(int)
	f = 0.5 # weights for similarity measures
	 
	for a,b in itertools.combinations(children,2):
		sim_auts = sim_aut_pair(G,a,b)
		sim_reads = sim_read_pair(G,a,b)
		impacts[a] += sim_auts[0]*f + sim_reads[0]*(1-f)
		impacts[b] += sim_auts[1]*f + sim_reads[1]*(1-f)
	return impacts


def get_indegrees(G): 
	if os.path.isfile('pickles/KDD-indegrees.pickle'):
		with open('pickles/KDD-indegrees.pickle', 'rb') as f:
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

def calculate_all_impacts(G):
	"""
	Calculates the impact of a parent on a child for all edges
	Time complexity:
	O(e^2). However, this upper bound is only reached if 
	all edges share a common parent.

	The calculated impacts will be added as edge attributes 'impact'
	"""
	print("Calculating all impacts...")
	impacts = defaultdict(int)
	i = 1
	num_nodes = G.number_of_nodes()
	for parent in G.nodes_iter():
		print "Calculating impact for parent " + str(i) + " / " + str(num_nodes) + "\r",
		i += 1
		children = [u for u,v in G.in_edges(parent)]
		children_impacts = get_impacts(G, parent, children)
		for child in children:
			if (child,parent) in impacts:
				print("Adding to existing key!")
			impacts[(child,parent)] += children_impacts[child]
	nx.set_edge_attributes(G, 'impact', impacts)
	print
	print("Done calculating all impacts.")
	with open('pickles/KDD-with-impacts.pickle', 'wb') as f:	
		nx.write_gpickle(G, f)
	return G

def get_impact_graph():
	if os.path.isfile('pickles/KDD-with-impacts.pickle'):
		with open('pickles/KDD-with-impacts.pickle', 'rb') as f:
			print("Reading pickled graph with impacts...")
			G = nx.read_gpickle(f)
			print("Done reading graph.")
			return G

def get_impact(edge):
	return edge[2]['impact']


def get_backbone_graph(G):
	print("Generating backbone from impact graph...")
	backbone = []
	for n in G.nodes_iter():
		if G.out_degree(n) > 0: # OBS: disconnected nodes fall off here
			top_edge = max(G.out_edges(n,data=True), key=get_impact)
			backbone.append(top_edge)
	print("Done generating backbone.")
	return nx.DiGraph(backbone)

def get_backbone_node(G, n):
	if G.in_degree(n) == 0:
		raise ValueError("No incoming edge!")
	out_edge = G.out_edges(n)
	return out_edge[0][1]

def main():
	G = get_impact_graph()
	G2 = get_backbone_graph(G)
	labels = nx.get_node_attributes(G,'label')
	G2_labels = {}
	for n in G2.nodes_iter():
		G2_labels[n] = labels[n]
	nx.set_node_attributes(G2,'label', G2_labels)
	nx.write_graphml(G2, 'data/KDD-backbone.graphml')
	#G = get_gml_graph()
	#G = get_impact_graph()
	pr = nx.pagerank(G, alpha=0.5, max_iter=10)
	eigen_centralities = nx.eigenvector_centrality_numpy(G)
	indegrees = get_indegrees(G)
	#closeness = nx.closeness_centrality(G)
	#betweenness = nx.betweenness_centrality(G)

	top_pr = Counter(pr).most_common(10) # top 10 pageranks
	for n, rank in top_pr:
		rank = rank*10000.0
		print(G.node[n]['label'])
		print("\tBackbone node: " + G2.node[get_backbone_node(G2,n)]['label'])
		print("\tPR: %0.2f"%(rank))
		print("\tIn-degree: %d"%(indegrees[n]))
		#print("\tBetweenness centrality: %0.5f"%(betweenness[n]))
		#print("\tCloseness centrality: %0.5f"%(closeness[n]))
		print("\tEigenvector centrality: %0.5f"%(eigen_centralities[n]))
	
	#print [d for n,d in G.nodes_iter(data=True)] # prints all dictionaries of label-title pairs

main()