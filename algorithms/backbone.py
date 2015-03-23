import config as conf
dataset = conf.settings['dataset'] 
do_plot = conf.settings['do_plot']

import networkx as nx
from collections import Counter, defaultdict
import itertools
import pickle
import os.path
if do_plot:
	import matplotlib.pyplot as plt
from graphutils import get_gml_graph

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


def get_indegrees(G):
	if os.path.isfile('pickles/' + dataset + '-indegrees.pickle'):
		with open('pickles/' + dataset + '-indegrees.pickle', 'rb') as f:
			return pickle.load(f)
	else:
		indegrees = G.in_degree(G.nodes_iter())
		with open('pickles/' + dataset + '-indegrees.pickle', 'wb') as f:
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


def calculate_all_impacts(G):
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
	with open('pickles/' + dataset + '-with-impacts.pickle', 'wb') as f:    
		nx.write_gpickle(G, f)
	return G

def get_impact_graph(G):
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


def build_backbone_graph(G):
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
	labels = nx.get_node_attributes(G,'label')
	G2_labels = {}
	for n in G2.nodes_iter():
		if n in labels:
			G2_labels[n] = labels[n]
	nx.set_node_attributes(G2,'label', G2_labels)
	
	with open('pickles/' + dataset + '-backbone.pickle', 'wb') as f:    
		nx.write_gpickle(G2, f)
	nx.write_graphml(G2, '../' + dataset + '/data/' + dataset + '-backbone.graphml')

	return G2

def get_backbone_node(G, n):
	if n in G:
		if G.out_degree(n) > 0:
			return G.successors(n)[0]
	return None
		#out_edge = G.out_edges(n)
		#print G.node[out_edge[0][1]]
		#return G.node[out_edge[0][1]] # [0]: tuple (u,v).

def get_backbone_graph(G):
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



def main():
	G = get_gml_graph(dataset)
	G = get_impact_graph(G)
	#normalize_impacts(G)
	G2 = get_backbone_graph(G)
	
	pr = nx.pagerank(G, alpha=0.5, max_iter=10)
	#pr_w = nx.pagerank(G, alpha=0.5, max_iter=100,weight='impact')
	pr_b = nx.pagerank(G2, alpha=0.5, max_iter=10)
	top_pr = Counter(pr).most_common(10) # top 10 pageranks

	# eigen_centralities = nx.eigenvector_centrality_numpy(G)
	indegrees = get_indegrees(G)
	#closeness = nx.closeness_centrality(G)
	#betweenness = nx.betweenness_centrality(G)

	indegs = []
	prs = []
	#prs_w = []
	for n in G:
		prs.append(pr[n])
		#prs_w.append(pr_w[n])
		indegs.append(indegrees[n])

	# indegs2 = []
	# prs_b = []
	# for n in G2:
	# 	indegs2 = indegrees[n]
	# 	print pr_b[n]
	# 	prs_b = pr_b[n]


	#TODO: find top progeny sizes, compare with e.g. indegree
	# Px = {}
	# for node in G2:	
	# 	px = progeny_size(G2,node) #len(nx.ancestors(G,node)) #len(indirect_predecessors(G,node))
	# 	Px[node] = px


	for n, rank in top_pr:
		rank = rank*10000.0
		print(G.node[n]['label'])
		backbone_node = get_backbone_node(G2,n)
		if backbone_node is not None and 'label' in G2.node[backbone_node] :
			print("\tBackbone node: " + G2.node[backbone_node]['label'])
		print("\tDate: " + G.node[n]['date'])
		print("\tPR: %0.2f"%(rank))
		print("\tIn-degree: %d"%(indegrees[n]))
	# for n, rank in top_pr:
	#   rank = rank*10000.0
	#   print(G.node[n]['label'])
	#   print("\tBackbone node: " + G2.node[get_backbone_node(G2,n)]['label'])
	#   print("\tPR: %0.2f"%(rank))
	#   print("\tIn-degree: %d"%(indegrees[n]))
	#   #print("\tBetweenness centrality: %0.5f"%(betweenness[n]))
	#   #print("\tCloseness centrality: %0.5f"%(closeness[n]))
	#   print("\tEigenvector centrality: %0.5f"%(eigen_centralities[n]))

	if do_plot:
		print("Drawing...")
		#nx.draw_networkx_nodes(G,pos=nx.spring_layout(G),nodelist=[0,1])
		#nx.draw_networkx_edges(G,pos,alpha=0.5,width=6)
		#nx.draw_networkx_nodes(G,pos=nx.spring_layout(G),node_size=2000,nodelist=[4])
		#nx.draw_networkx_nodes(G,pos=nx.spring_layout(G),node_size=3000,nodelist=[0,1,2,3],node_color='b')


		plt.subplot(1, 2, 1)
		#plt.xlim(12,19)
		#plt.title('')
		plt.xlabel('Indegree')
		plt.ylabel('Pagerank')
		plt.plot(indegs,prs,'ro')
		
		# plt.subplot(1, 2, 2)
		# #plt.title('')
		# plt.xlabel('Indegree')
		# plt.ylabel('Pagerank with weights')
		# plt.plot(indegs,prs_w,'ro')

		plt.subplot(1, 2, 2)
		#plt.title('')
		plt.xlabel('Indegree')
		plt.ylabel('Pagerank for backbone')
		plt.plot(indegs2,prs_b,'ro')		
		


		# Plot backbone from 1 node
		# plt.figure(1,figsize=(8,8))
		# todraw = [top_pr[3][0]]
		# for _ in range(2):
		# 	todraw.append(get_backbone_node(G2,todraw[-1]))
		# print todraw
		# SG = G.subgraph(todraw)
		# pos=nx.spring_layout(SG)
		# nx.draw(SG, pos)
		# nx.draw_networkx_labels(SG, pos)

		# plt.axis('off')
		# #plt.savefig("foo.png") # save as png
		plt.show() # display
		print("Done.")

main()
