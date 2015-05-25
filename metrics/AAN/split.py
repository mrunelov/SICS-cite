import pickle
import numpy as np
import graph_tool.all as gt
from random import shuffle

def create(postfix=""):
    indexes = range(18158)
    shuffle(indexes)
    first = indexes[:len(indexes)/2]
    second = indexes[len(indexes)/2:]

    with open("pickles/first" + postfix + ".pickle", "wb") as f:
        pickle.dump(first,f)
    with open("pickles/second" + postfix + ".pickle", "wb") as f:
        pickle.dump(second,f)

def get_first(num=""):
    with open("pickles/first" + num + ".pickle","rb") as f:
        first = pickle.load(f)
        first_a = np.zeros(527129)
        for f_i in first:
            first_a[f_i] = 1
        return first_a

def get_second(num=""):
    with open("pickles/second" + num + ".pickle","rb") as f:
        second = pickle.load(f)
        second_a = np.zeros(527129)
        for s_i in second:
            second_a[s_i] = 1
        return second_a

def split_graph(g):
    first = get_first()
    second = get_second()
    g_first = gt.GraphView(g,vfilt=first)
    g_second = gt.GraphView(g,vfilt=second)
    return g_first,g_second

def get_gt_graphs(g, first, second):
    g_first = gt.GraphView(g,vfilt=first)
    g_second = gt.GraphView(g,vfilt=second)
    return g_first,g_second


def test_get_graphs():
    g1,g2 = get_gt_graphs()
    print "g1: nodes: " + str(g1.num_vertices()) + ", edges: " + str(g1.num_edges())
    print "g2 nodes: " + str(g2.num_vertices()) + ", edges: " + str(g2.num_edges())

#test_get_graphs()


for i in range(1,11):
    create(str(i))
