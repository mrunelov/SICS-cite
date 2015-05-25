from scipy.stats.stats import pearsonr
import graph_tool.all as gt
import numpy as np
import pickle

g = gt.load_graph("AAN-preprocessed.xml")
in_degs = g.degree_property_map("in")
N = g.num_vertices()
in_degs.a = in_degs.a.astype("float")
#in_degs.a /= N # normalize indegree
#in_degs_sorted = in_degs.a.argsort()[::-1]

with open("vpa.pickle", "rb") as f:
    between_a = np.asarray(pickle.load(f))
#between_sorted = vpa.argsort()[::-1]

a = list(between_a)
b = list(in_degs.a)
print "Length of first list:  " + str(len(a))
print "Length of second list: " + str(len(b))
print "Pearson's correlation coefficient (PCC) for betweenness and indegree:"
pcc = pearsonr(list(between_a), list(in_degs.a))
print pcc


