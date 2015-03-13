import networkx as nx
from graphutils import get_gml_graph
import matplotlib.pyplot as plt
import numpy as np
import random
from collections import Counter, defaultdict
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
	x = random.sample([random.random() for _ in range(1000)], 100)
	# print x
	# plt.bar(100, x)
	# plt.show()

	#bins=[0,1.0]
	# bins=10
	# hist,bin_edges=np.histogram(x,bins=bins)
	# plt.hist(hist, bins=bins)
	# plt.show()

	# MemoryError på APS just nu
	G = get_gml_graph('KDD') # load networkx graph

	cycles = nx.simple_cycles(G)
	# print("First cycle: ")
	# print next(cycles)

	pr = nx.pagerank(G, alpha=1, max_iter=100)
	# Ix = pr.values()
	#top_pr = Counter(pr).most_common(100) # top 10 pageranks
	#pr2 = nx.pagerank(G, alpha=0.5, max_iter=100)
	Ix = []
	Px = []
	indegs = []
	nodes = []
	for node, rank in pr.iteritems(): #top_pr:
		indeg = G.in_degree(node)
		if indeg > 50: # try with only less cited papers
			continue
		indegs.append(indeg)
		Ix.append(rank)
		px = len(indirect_predecessors(G,node))
		Px.append(px)
		nodes.append(node)
		
	print("Done calculating Ix and Px. Plotting...")
	
	N = G.number_of_nodes()
	Ix = [x*N for x in Ix]
	Px = [x/10**3 for x in Px]

	# Get top Ix-node for Px value of 17 after doing top_pr 100
	# seventeens_i = [i for i,x in enumerate(node) if Px[i] == 17]
	# best_17 = nodes[max(seventeens_i, key= lambda i: Ix[i])]
	# Currently n9407087
	# Monopole Condensation, And Confinement In N=2 Supersymmetric Yang-Mills, N. Seiberg and E. Witten
	# Not surprising since it gets high PageRank overall.
	print best_17

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

memo_preds = {}	

def indirect_predecessors(G,n):
	"""
	Finds all indirect predecessors of one node.
	TODO: A more efficient way calculates it for the entire graph at once, avoiding duplicate calculations
	"""
	stack = [n]
	ind_preds = Set()
	while stack:
		curr = stack.pop()
		preds = G.predecessors(curr)
		for p in preds:
			if p not in ind_preds:
				ind_preds.add(p)
				stack.append(p)
	return list(ind_preds)

# TODO: Make work with loops...
# def indirect_predecessors(G,n,preds=Set()):
# 	print "n = " + str(n)
# 	print preds
# 	if n in preds:
# 		return Set()
# 	direct_preds = G.predecessors(n)
# 	for p in direct_preds:
# 		if p not in preds:
# 			preds.add(p)
# 			next_preds = indirect_predecessors(G,p,preds=preds)
# 			for np in next_preds:
# 				if np not in preds:
# 					preds.add(np)
# 	memo_preds[n] = list(preds)
# 	return preds



# G = nx.DiGraph()
# G.add_node(1)
# G.add_node(2)
# G.add_node(3)
# G.add_edge(1,2)
# G.add_edge(2,3)
#G.add_edge(3,3)

#print indirect_predecessors(G,3)

# print memo_preds

main()