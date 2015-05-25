import config as conf
dataset = conf.settings['dataset'] 
do_plot = conf.settings['do_plot']

if do_plot:
	from plotter import *
import numpy as np
import networkx as nx
from collections import Counter, defaultdict
import itertools
import pickle
import os.path
import os.remove
from graphutils import get_gml_graph

"""
Implementation of the Backbone algorithm as described in 
'Tracing the Evolution of Physics on the Backbone of Citation Networks' 
by S. Gualdi, C. H. Yeung, Y.-C. Zhang
"""


def sim_read_helper(G, a, b):
	"""
	Calcuates the similarity between a and b from the reader's perspective
	by counting co-citations. Weighted by the co-citing paper's outdegree (random walk).
	Skips multiplying by 1/indegree in order to make the result usable by both a and b in the impact calculation 
	(see sim_read_pair() and impacts())
	"""
	offspring = G.in_edges([a,b])
	counts = Counter(offspring)
	common_offspring = [u for u,v in offspring if counts[v] == 2] # co-citations
	sim_read = 0
	for o in common_offspring:
			sim_read += (1.0/G.out_degree(o))
	return sim_read

def sim_aut_helper(G, a, b):
	"""
	A two-step random walk from a to b
	that simulates author's (a and b) interpretations
	since the measure is based on their references
	"""
	parents = G.out_edges([a,b])
	counts = Counter(parents)
	common_parents = [v for u,v in parents if counts[v] == 2] # co-citing something
	sim_aut = 0
	for p in common_parents:
			sim_aut += (1.0/G.in_degree(p))
	return sim_aut

def sim_read_pair(G, a, b):
	"""
	Calculates the read similarity for a and b
	"""
	a_ins = G.in_degree(a)
	b_ins = G.in_degree(b)
	if a_ins == 0 and b_ins == 0:
		return [0,0]
	sim_read = sim_read_helper(G,a,b)
	sim_read_a = (1.0/a_ins)*sim_read if a_ins else 0
	sim_read_b = (1.0/b_ins)*sim_read if b_ins else 0
	return [sim_read_a, sim_read_b]

def sim_aut_pair(G, a, b):
	"""
	Calculates the aut similarity for a and b
	"""

	a_outs = G.out_degree(a)
	b_outs = G.out_degree(b)
	if a_outs == 0 and b_outs == 0:
		return [0,0]
	sim_aut = sim_aut_helper(G,a,b)
	sim_aut_a = (1.0/a_outs)*sim_aut if a_outs else 0
	sim_aut_b = (1.0/b_outs)*sim_aut if b_outs else 0
	return [(1.0/a_outs)*sim_aut, (1.0/b_outs)*sim_aut]

# Keep in memory, no need to recalculate sim_reads since it depends on childrens' children.
sim_reads_map = {} 
def get_impacts(G, parent, children, f=0.5):
	"""
	The impact of a parent on its children
	f = weights for similarity measures aut and read. w_aut = f, w_read = (1-f)
	"""
	impacts = defaultdict(int)
	 
	for a,b in itertools.combinations(children,2): # loop all pairs of children
		sim_auts = sim_aut_pair(G,a,b)
		sim_reads = []
		if a in sim_reads_map and b in sim_reads_map:
			sim_reads = [sim_reads_map[a], sim_reads_map[b]]
		else:
			sim_reads = sim_read_pair(G,a,b)
			sim_reads_map[a] = sim_reads[0]
			sim_reads_map[b] = sim_reads[1]
		impacts[a] += sim_auts[0]*(1.0-f) + sim_reads[0]*f
		impacts[b] += sim_auts[1]*(1.0-f) + sim_reads[1]*f
	return impacts


def get_indegrees(G=None):
	if os.path.isfile('pickles/' + dataset + '-indegrees.pickle'):
		with open('pickles/' + dataset + '-indegrees.pickle', 'rb') as f:
			return pickle.load(f)
	else:
		return calculate_indegrees(G)

def calculate_indegrees(G):
	if G is None:
		raise ValueError("No graph provided for calculate_indegrees")
	indegrees = G.in_degree(G.nodes_iter())
	with open('pickles/' + dataset + '-indegrees.pickle', 'wb') as f:
		pickle.dump(indegrees,f)
	return indegrees


def get_Px(G=None):
	if os.path.isfile('pickles/' + dataset + '-backbone-Px.pickle'): # OBS: hardcoded backbone Px, since that's all we're interested in
		with open('pickles/' + dataset + '-backbone-Px.pickle', 'rb') as f:
			return zip(*pickle.load(f)) # return (Px, nodes) unzipped
	else:
		return calculate_Px(G)

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


def calculate_all_impacts(G,postfix=""):
	"""
	Calculates the impact of a parent on a child for all edges
	Time complexity:
	O(e^2). However, this upper bound is only reached if 
	all edges share a common parent.

	The calculated impacts will be added as edge attributes 'impact'
	"""
	print("Calculating all impacts...")
	impacts = {}
	i = 1
	num_nodes = G.number_of_nodes()
	for parent in G.nodes_iter():
		children = G.predecessors(parent)
		#children = [u for u,v in G.in_edges(parent)]
		print "Calculating impact for parent " + str(i) + " / " + str(num_nodes) + " (with " + str(len(children)) + " children)" +  "\r",
		i += 1
		if len(children) == 1:
			impacts[(children[0],parent)] = 1.0
			continue
		children_impacts = get_impacts(G, parent, children)
		for child in children:
			# if (child,parent) in impacts: # TODO: multi-edge. not allowed.
			#     print("Adding to existing key!")
			impacts[(child,parent)] = children_impacts[child]
	nx.set_edge_attributes(G, 'impact', impacts)
	print
	print("Done calculating all impacts.")
	with open('pickles/' + dataset + '-with-impacts-' + postfix + '.pickle', 'wb') as f:  
		nx.write_gpickle(G, f)
	return G

def get_impact_graph(G=None):
	if os.path.isfile('pickles/' + dataset + '-with-impacts.pickle'):
		with open('pickles/' + dataset + '-with-impacts.pickle', 'rb') as f:
			print("Reading pickled graph with impacts...")
			stored_G = nx.read_gpickle(f)
			print("Done reading graph.")
			return stored_G
	else:
		return calculate_all_impacts(G)

def get_impact(edge):
	return edge[2]['impact']


def build_backbone_graph(G,postfix=""):
	print("Generating backbone from impact graph...")
	backbone = []
	for n in G.nodes_iter():
		outdeg = G.out_degree(n)
		if  outdeg > 0: # OBS: isolated nodes skipped
			top_edge = max(G.out_edges(n,data=True), key=get_impact)
			backbone.append(top_edge)
		elif outdeg == 1:
			backbone.append(G.out_edges(n,data=True)[0])
	G2 = nx.DiGraph(backbone)
	print("Done generating backbone.")
	# add labels to backbone graph. Option: get subgraph directly from G.
	titles = nx.get_node_attributes(G,'title')
	G2_titles = {}
	for n in G2.nodes_iter():
		if n in titles:
			G2_titles[n] = titles[n]
	nx.set_node_attributes(G2,'title', G2_titles)
	
	with open('pickles/' + dataset + '-backbone-' + postfix + '.pickle', 'wb') as f:    
		nx.write_gpickle(G2, f)
	#nx.write_graphml(G2, '../' + dataset + '/data/' + dataset + '-backbone.graphml')

	return G2

def get_backbone_node(G, n):
	if n in G:
		if G.out_degree(n) > 0:
			return G.successors(n)[0]
	return None
		#out_edge = G.out_edges(n)
		#print G.node[out_edge[0][1]]
		#return G.node[out_edge[0][1]] # [0]: tuple (u,v).

def get_backbone_graph(G=None):
	if os.path.isfile('pickles/' + dataset + '-backbone.pickle'):
		with open('pickles/' + dataset + '-backbone.pickle', 'rb') as f:
			print("Reading pickled backbone graph...")
			stored_G = nx.read_gpickle(f)
			print("Done reading graph.")
			return stored_G
	else:
		return build_backbone_graph(G)


def normalize_impacts(G):
	for n in G:
		outs = G.out_edges([n],data=True)
		if len(outs) == 0:
			continue
		impacts = [get_impact(e) for e in outs]
		impact_sum = sum(impacts)
		if impact_sum == 0:
			#impacts = [1.0/len(outs)]*len(outs)
			pass
		else:
			#avg_impact = impact_sum/len(outs)
			#print("Avg impact: " + str(avg_impact))
			for i,e in enumerate(outs):
				G.add_edge(e[0],e[1], impact=impacts[i]/impact_sum)
			#G.edge[e]['impact'] = e['impact']/impact_sum 


def calculate_Px(G,postfix=""):
	"""
	Calculates and pickles Px (progeny sizes) for a graph.
	Returns the node order that was pickled
	"""
	if G is None:
		raise ValueError("No graph provided for calculate_Px")
	Px = []
	#nodes = []
	#titles = []
	ids = []
	print("Calculating Px...")
	for n in G.nodes_iter():
		px = len(nx.ancestors(G,n))
		Px.append(px)
		ids.append(n)
		#nodes.append(n)
                #titles.append(G.node[n]["title"])

	print("Done calculating Px.")
	Px_with_ids = zip(Px,ids)
	with open('pickles/' + dataset + '-backbone-Px-' + postfix + '.pickle', 'wb') as f:
		pickle.dump(Px_with_ids,f)
                print "Pickled " + dataset + "-backbone-Px.pickle"
	return Px,ids

def get_subset_list(foomap, keys):
	subset = []
	for k in keys:
		subset.append(foomap[k])
	return subset

def main():
	G = get_gml_graph(dataset)

	# Code for the randomization test, calculate for all 10 halves
	for i in range(1,11):
		for x in ["first","second"]:
			with open("pickles/" + x + str(i) + ".pickle","rb") as f:
				half = pickle.load(f)
			G_half = G.subgraph(half) # filter away half the graph
			postfix = x + str(i)
			G_half = calculate_all_impacts(G_half,postfix=postfix)
			G2_half = build_backbone_graph(G_half,postfix=postfix)
			calculate_Px(G2_half,postfix=postfix)
			# remove temp files, we just need Px
			os.remove('pickles/' + dataset + '-with-impacts-' + postfix + '.pickle')
			os.remove('pickles/' + dataset + '-backbone-' + postfix + '.pickle')

	#G = get_impact_graph(G)
	#normalize_impacts(G)
	
	#pr = nx.pagerank(G, alpha=0.5, max_iter=10)
	#top_pr = Counter(pr).most_common(10) # top 10 pageranks
	#pr_w = nx.pagerank(G, alpha=0.5, max_iter=100,weight='impact')
	#pr_b = nx.pagerank(G2, alpha=0.5, max_iter=10)
	#stop_pr_b = Counter(pr_b).most_common(10) # top 10 pageranks

	# eigen_centralities = nx.eigenvector_centrality_numpy(G)
	
	#top_indegrees = Counter(indegrees).most_common(1000) # top 10 pageranks
	#closeness = nx.closeness_centrality(G)
	#betweenness = nx.betweenness_centrality(G)
	#Px,nodes = get_Px(G2)
	#indegrees = get_indegrees(G)
	#backbone_indegs = get_subset_list(indegrees,nodes)

	# indegs = []
	# prs = []
	# #prs_w = []
	# for n in G:
	# 	prs.append(pr[n])
	# 	#prs_w.append(pr_w[n])
	# 	indegs.append(indegrees[n])
 
	# scores = sorted(zip(Px,prs_b,nodes))
	# buckets = defaultdict(list)
	# for x in scores:
	# 	buckets[x[0]].append(x)
	# for b in buckets.keys():
	# 	top_node = max(buckets[b], key = lambda x:x[1])[2]
	# 	print "Top node for bucket " + str(b) + ": ",
	# 	print("(indeg = " + str(G.in_degree(top_node)) + ", date = " + G.node[top_node]['date'] + ")"),
	# 	print G2.node[top_node]['label']

	#TODO: find top progeny sizes, compare with e.g. indegree
	# Px = {}
	# for node in G2:	
	# 	px = progeny_size(G2,node) #len(nx.ancestors(G,node)) #len(indirect_predecessors(G,node))
	# 	Px[node] = px


	# for n, rank in top_pr:
	# 	rank = rank*10000.0
	# 	print(G.node[n]['label'])
	# 	backbone_node = get_backbone_node(G2,n)
	# 	if backbone_node is not None and 'label' in G2.node[backbone_node] :
	# 		print("\tBackbone node: " + G2.node[backbone_node]['label'])
	# 	print("\tDate: " + G.node[n]['date'])
	# 	print("\tPR: %0.2f"%(rank))
	# 	print("\tIn-degree: %d"%(indegrees[n]))
	#   #print("\tBetweenness centrality: %0.5f"%(betweenness[n]))
	#   #print("\tCloseness centrality: %0.5f"%(closeness[n]))
	#   #print("\tEigenvector centrality: %0.5f"%(eigen_centralities[n]))
	

	# if do_plot:
	# 	plotxy(backbone_indegs,Px)


if __name__ == "__main__":
    main()
