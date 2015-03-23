import config as conf
dataset = conf.settings['dataset']
do_plot = conf.settings['do_plot']

import networkx as nx
from graphutils import get_gml_graph
import matplotlib.pyplot as plt
import numpy as np
import pickle
import random
from collections import Counter, defaultdict, deque
from sets import Set
from datetime import datetime

dateformat = "%Y-%m-%d"
epoch = datetime(1890,1,1) # some year older than the oldest publication
def pr_avg_age(G):
	pr = nx.pagerank(G, alpha=0.5, max_iter=20)
	h,a = hits(G) # float division by zero
	top_pr = Counter(pr).most_common(10) # top 100 pageranks
	avg_age = 0
	for n, rank in top_pr:
		date = datetime.strptime(G.node[n]['date'],dateformat)
		age = (date-epoch).total_seconds()
		avg_age += age
	avg_age /= 10
	return avg_age
	
def secs_since_epoch(datestr):
	date = datetime.strptime(datestr,dateformat)
	secs = (date - epoch).total_seconds()
	return secs


def main():
	G = get_gml_graph(dataset) # load networkx graph

	years = range(1992,2004,1)
	times = []
	for y in years:
		for m in range(1,13):
			date = datetime(y,m,1)
			secs = (date - epoch).total_seconds()
			times.append(secs)
	print times

	pr_ages = []
	prev_avg = 1e12
	for t in times:
		Gy = G.subgraph([node for node, attrs in G.nodes_iter(data=True) if secs_since_epoch(attrs['date']) <= t])
		print("Num nodes: " + str(Gy.number_of_nodes()))
		if Gy.number_of_nodes() > 10:
			avg = pr_avg_age(Gy)
			if avg < prev_avg:
				print "Avg age dropped!"
			prev_avg = avg
			pr_ages.append(avg)
		else:
			pr_ages.append(0)

	print("Plotting...")

	#plt.title('')
	plt.xlabel('Year')
	plt.ylabel('Average age of top ranked nodes')
	plt.plot(times,pr_ages,'ro')


	#plt.plot(pr2.values(),Px,'bo')
	# bins=100
	# hist,bin_edges=np.histogram(I_P.values(),bins=bins)
	# plt.hist(hist, bins=bins)
	plt.show()

def hits(G,max_iter=100,tol=1.0e-8,nstart=None,normalized=True):
    """Return HITS hubs and authorities values for nodes.

    The HITS algorithm computes two numbers for a node.
    Authorities estimates the node value based on the incoming links.
    Hubs estimates the node value based on outgoing links.

    Parameters
    ----------
    G : graph
      A NetworkX graph

    max_iter : interger, optional
      Maximum number of iterations in power method.

    tol : float, optional
      Error tolerance used to check convergence in power method iteration.

    nstart : dictionary, optional
      Starting value of each node for power method iteration.

    normalized : bool (default=True)
       Normalize results by the sum of all of the values.

    Returns
    -------
    (hubs,authorities) : two-tuple of dictionaries
       Two dictionaries keyed by node containing the hub and authority
       values.

    Examples
    --------
    >>> G=nx.path_graph(4)
    >>> h,a=nx.hits(G)

    Notes
    -----
    The eigenvector calculation is done by the power iteration method
    and has no guarantee of convergence.  The iteration will stop
    after max_iter iterations or an error tolerance of
    number_of_nodes(G)*tol has been reached.

    The HITS algorithm was designed for directed graphs but this
    algorithm does not check if the input graph is directed and will
    execute on undirected graphs.

    References
    ----------
    .. [1] A. Langville and C. Meyer,
       "A survey of eigenvector methods of web information retrieval."
       http://citeseer.ist.psu.edu/713792.html
    .. [2] Jon Kleinberg,
       Authoritative sources in a hyperlinked environment
       Journal of the ACM 46 (5): 604-32, 1999.
       doi:10.1145/324133.324140.
       http://www.cs.cornell.edu/home/kleinber/auth.pdf.
    """
    if type(G) == nx.MultiGraph or type(G) == nx.MultiDiGraph:
        raise Exception("hits() not defined for graphs with multiedges.")
    if len(G) == 0:
        return {},{}
    # choose fixed starting vector if not given
    if nstart is None:
        h=dict.fromkeys(G.nodes_iter(),1.0/G.number_of_nodes())
    else:
        h=nstart
        # normalize starting vector
        s=1.0/sum(h.values())
        for k in h:
            h[k]*=s
    i=0
    while True: # power iteration: make up to max_iter iterations
        hlast=h
        h=dict.fromkeys(hlast.keys(),1)
        a=dict.fromkeys(hlast.keys(),1)
        # this "matrix multiply" looks odd because it is
        # doing a left multiply a^T=hlast^T*G
        for n in h:
            for nbr in G[n]:
                a[nbr]+=hlast[n]*G[n][nbr].get('weight',1)
        # now multiply h=Ga
        for n in h:
            for nbr in G[n]:
                h[n]+=a[nbr]*G[n][nbr].get('weight',1)
        # normalize vector
        s=1.0/sum(h.values())
        for n in h: h[n]*=s
        # normalize vector
        s=1.0/max(a.values())
        for n in a: a[n]*=s
        # check convergence, l1 norm
        err=sum([abs(h[n]-hlast[n]) for n in h])
        if err < tol:
            break
        if i>max_iter:
            raise NetworkXError(\
            "HITS: power iteration failed to converge in %d iterations."%(i+1))
        i+=1
    if normalized:
        s = 1.0/sum(a.values())
        for n in a:
            a[n] *= s
        s = 1.0/sum(h.values())
        for n in h:
            h[n] *= s
    return h,a

main()