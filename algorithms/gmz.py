import networkx as nx
from graphutils import get_gml_graph
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
	x = random.sample([random.random() for _ in range(1000)], 100)
	# print x
	# plt.bar(100, x)
	# plt.show()

	#bins=[0,1.0]
	# bins=10
	# hist,bin_edges=np.histogram(x,bins=bins)
	# plt.hist(hist, bins=bins)
	# plt.show()

	# if os.path.isfile('pickles/KDD-indegrees.pickle'):
 #        with open('pickles/KDD-indegrees.pickle', 'rb') as f:
 #            return pickle.load(f)
 #    else:

	# MemoryError on APS right now
	G = get_gml_graph('KDD') # load networkx graph
	
	print("Running pagerank...")
	pr = nx.pagerank(G, alpha=1, max_iter=100)
	print("Done running pagerank.")
	# Ix = pr.values()
	#top_pr = Counter(pr).most_common(100) # top 10 pageranks
	#pr2 = nx.pagerank(G, alpha=0.5, max_iter=100)
	Ix = []
	Px = []
	indegs = []
	nodes = []
	print("Calculating Px...")
	for node, rank in pr.iteritems(): #top_pr:
		indeg = G.in_degree(node)
		if indeg < 40: # try with only less cited papers
			continue
		indegs.append(indeg)
		Ix.append(rank)
		px = len(indirect_predecessors(G,node))
		Px.append(px)
		nodes.append(node)

	print("Done calculating. Pickling...")

	# with open('pickles/KDD-Ix.pickle', 'wb') as f1, open('pickles/KDD-Px.pickle', 'wb') as f2:
	# 	pickle.dump(Ix, f1)
 #        pickle.dump(Px, f2)

        """
        pickle not working:
	        Traceback (most recent call last):
		  File "C:\Users\Martin\Desktop\KTH\Exjobb\SICS-cite\algorithms\gmz.py", line 137, in <module>
		    main()
		  File "C:\Users\Martin\Desktop\KTH\Exjobb\SICS-cite\algorithms\gmz.py", line 71, in main
		    pickle.dump(Px, f2)
		  File "C:\Python27\lib\pickle.py", line 1370, in dump
		    Pickler(file, protocol).dump(obj)
		  File "C:\Python27\lib\pickle.py", line 224, in dump
		    self.save(obj)
		  File "C:\Python27\lib\pickle.py", line 286, in save
		    f(self, obj) # Call unbound method with explicit self
		  File "C:\Python27\lib\pickle.py", line 597, in save_list
		    write(MARK + LIST)
		  ValueError: I/O operation on closed file
        """

	print("Plotting...")
	
	N = G.number_of_nodes()
	Ix = [x*N for x in Ix]
	Px = [x/10**3 for x in Px]

 
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
			# 	print("Reached node "),
			# 	print p,
			# 	print(" twice.")
			# 	print("Currently at node "),
			# 	print curr
	return list(ind_preds)

# G = nx.DiGraph()
# G.add_node(1)
# G.add_node(2)
# G.add_node(3)
# G.add_edge(1,2)
# G.add_edge(2,3)
#G.add_edge(3,3)

#print indirect_predecessors(G,3)

main()