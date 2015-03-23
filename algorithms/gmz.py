import config as conf
dataset = conf.settings['dataset']
do_plot = conf.settings['do_plot']

import networkx as nx
from graphutils import get_gml_graph

if do_plot:
	import matplotlib.pyplot as plt
import numpy as np
import pickle
import random
from collections import Counter, defaultdict, deque
from sets import Set

"""
Influence, originality and similarity in directed acyclic graphs
  by Gualdi, Medo and Zhang

file:///C:/Users/Martin/Desktop/KTH/Exjobb/Litteraturstudie/Intressant/Ska%20anv%E4ndas/To%20read/SUPERINTRESSANT-Influence,%20originality%20and%20similarity%20in%20directed%20acyclic%20graphs.pdf

NetworkX pagerank source code for inspiration:
http://pydoc.net/Python/networkx/1.0/networkx.algorithms.pagerank/
"""


# Thoughts:
# Like pagerank without the damping factor, instead using progeny size.
# Should look into: see if damping factors of different kinds are better


def main():
	G = get_gml_graph('APS-backbone') # load networkx graph
	
	#print("Running pagerank...")
	#pr = nx.pagerank(G, alpha=1, max_iter=100)
	#print("Done running pagerank.")
	# Ix = pr.values()
	#top_pr = Counter(pr).most_common(100) # top 10 pageranks
	#pr2 = nx.pagerank(G, alpha=0.5, max_iter=100)
	#Ix = []
	Px = []
	#indegs = []
	nodes = []
	N = G.number_of_nodes()
	print("Calculating Px...")
	i = 1
	#for node, rank in pr.iteritems(): #top_pr:
	for node in G:
		print str(i) + " / " + str(N) + '\r'
		i += 1
		#indeg = G.in_degree(node)
		# if indeg < 40: # try with only less cited papers
		#	continue
		#indegs.append(indeg)
		#Ix.append(rank)
		px = len(nx.ancestors(G,node)) # progeny_size(G,node) #len(indirect_predecessors(G,node))
		Px.append(px)
		nodes.append(node)

	print("Done calculating. Pickling...")

	#with open('pickles/KDD-Ix.pickle', 'wb') as f1:
	#	pickle.dump(Ix, f1)
	with open('pickles/' + dataset + '-Px.pickle', 'wb') as f2:
		pickle.dump(zip(Px,nodes), f2)

	if do_plot:
		print("Plotting...")
		
		Ix = [x*N for x in Ix]
		Px = [x for x in Px]

		# Get top Ix-node for Px value of 17 after doing top_pr 100
		# seventeens_i = [i for i,x in enumerate(node) if Px[i] == 17]
		# best_17 = nodes[max(seventeens_i, key= lambda i: Ix[i])]
		# Currently n9407087
		# Monopole Condensation, And Confinement In N=2 Supersymmetric Yang-Mills, N. Seiberg and E. Witten
		# Not surprising since it gets high PageRank overall.
		#print best_17

		plt.subplot(1, 2, 1)
		#plt.xlim(12,19)
		plt.title('Px and Ix')
		plt.xlabel('Px')
		plt.ylabel('Ix')
		plt.plot(Px,Ix,'ro')
		
		plt.subplot(1, 2, 2)
		plt.title('Indegree and Ix')
		plt.xlabel('Indegree')
		plt.ylabel('Ix')
		plt.plot(indegs,Ix,'bo')


		#plt.plot(pr2.values(),Px,'bo')
		# bins=100
		# hist,bin_edges=np.histogram(I_P.values(),bins=bins)
		# plt.hist(hist, bins=bins)
		plt.show()

def indirect_predecessors(G,n):
	"""
	Note: If G is a DAG, nx.ancestors(G,source) can be used 
	(https://networkx.github.io/documentation/latest/reference/generated/networkx.algorithms.dag.ancestors.html)
	
	Finds all indirect predecessors of one node.
	TODO: A more efficient way calculates it for the entire graph at once, avoiding duplicate calculations
	"""
	queue = deque([n])
	ind_preds = Set()
	depth = 0
	while queue:
		curr = queue.popleft()
		preds = G.predecessors(curr)
		for p in preds:
			if p not in ind_preds:
				ind_preds.add(p)
				queue.append(p)
			# else:
			#	print("Reached node "),
			#	print p,
			#	print(" twice.")
			#	print("Currently at node "),
			#	print curr
	return list(ind_preds)

def single_source_shortest_path_length(G,source):
	"""Compute the shortest path lengths from source to all reachable nodes.

	Parameters
	----------
	G : NetworkX graph

	source : node
	   Starting node for path

	cutoff : integer, optional
		Depth to stop the search. Only paths of length <= cutoff are returned.

	Returns
	-------
	lengths : dictionary
		Dictionary of shortest path lengths keyed by target.

	Examples
	--------
	>>> G=nx.path_graph(5)
	>>> length=nx.single_source_shortest_path_length(G,0)
	>>> length[4]
	4
	>>> print(length)
	{0: 0, 1: 1, 2: 2, 3: 3, 4: 4}

	See Also
	--------
	shortest_path_length
	"""
	seen={}					 # level (number of hops) when seen in BFS
	level=0					 # the current level
	memoized=0
	nextlevel={source:1}  # dict of nodes to check at next level
	while nextlevel:
		thislevel=nextlevel  # advance to next level
		nextlevel={}		 # and start a new list (fringe)
		if len(thislevel) == 1 and thislevel.keys()[0] in progenies:
			memoized = progenies[thislevel.keys()[0]]
			return seen,memoized + 1 # count the node we're at
		for v in thislevel:
			if v not in seen:
				seen[v]=level # set the level of vertex v
				nextlevel.update(G[v]) # add neighbors of v
		level=level+1
	return seen,memoized  # return all path lengths as dictionary

progenies = {}
def progeny_size(G, source):
	"""Return all nodes having a path to `source` in G.

	Parameters
	----------
	G : NetworkX DiGraph
	source : node in G

	Returns
	-------
	ancestors : set()
	   The ancestors of source in G
	"""
	if not G.has_node(source):
		raise nx.NetworkXError("The node %s is not in the graph." % source)

	anc = []
	RG = G.reverse()
	#with nx.utils.reversed(G):
	paths,memo = single_source_shortest_path_length(G, source)
	px = memo + len(set(paths.keys())) - 1 # don't count source
	progenies[source] = px
	return px

#	 anc = set(nx.shortest_path_length(G, target=source).keys()) - set([source])
#	 return anc

# G = nx.DiGraph()
# G.add_node(1)
# G.add_node(2)
# G.add_node(3)
# G.add_edge(1,2)
# G.add_edge(2,3)
#G.add_edge(3,3)

#print indirect_predecessors(G,3)

main()
