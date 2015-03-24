import networkx as nx
from graphutils import get_gml_graph
from datetime import datetime
from collections import deque

def topsort(G,nbunch=None):
	if not G.is_directed():
		raise nx.NetworkXError("Topological sort not defined on undirected graphs.")

	# nonrecursive version
	seen={}
	order_explored=[] # provide order and 
	explored={}		  # fast search without more general priorityDictionary
					 
	if nbunch is None:
		nbunch = G.nodes_iter() 
	for v in nbunch:	 # process all vertices in G
		if v in explored: 
			continue
		fringe=[v]	 # nodes yet to look at
		while fringe:
			w=fringe[-1]  # depth first search
			if w in explored: # already looked down this branch
				fringe.pop()
				continue
			seen[w]=1	  # mark as seen
			# Check successors for cycles and for new nodes
			new_nodes=[]
			for n in G[w]:
				if n not in explored:
					if n in seen: #CYCLE !!
						trace_loop(G,n)
						#print_children(G,n)
						#print("Cycle detected at edge " + str(w) + "-->" + str(n))
						raise nx.NetworkXUnfeasible("Graph contains a cycle.")
					new_nodes.append(n)
			if new_nodes:	# Add new_nodes to fringe
				fringe.extend(new_nodes)
			else:			# No new nodes so w is fully explored
				explored[w]=1
				order_explored.insert(0,w) # reverse order explored
				fringe.pop()	# done considering this node
	return order_explored

dateformat = "%Y-%m-%d"
def trace_loop(G,n):
	queue = deque([n])
	while queue:
		u = queue.popleft()
		u_date = datetime.strptime(G.node[u]['date'],dateformat)	
		adj = G.successors(u)
		for v in adj:
			if v == n:
				print("Cycle completed. Exiting.")
				return
			try:
				v_date = datetime.strptime(G.node[v]['date'],dateformat)	
				if u < v:
					print("Violation found: " + str(u) + "-->" + str(v))
				queue.append(v)
			except KeyError as e:
				print "Date not found for node " + str(v)
				raise e
	


def print_children(G,n):
	print "Parent: " + G.node[n]['date'] + "\t" + G.node[n]['label']
	children = G.predecessors(n)
	for child in children:
		print G.node[child]['date'] + "\t" + G.node[child]['label']


def main():
	G = get_gml_graph('APS')
	top_sort = topsort(G)

main()
