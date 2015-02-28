#from __future__ import print_function
import gml # local
import json
from pprint import pprint
import pickle
import os
import sys
from sets import Set
from collections import defaultdict

inputdir = "rawdata/"
datadir = "data/"

def get_id_generator():
	"""
	ID generator that generates ID's starting at 0.
	"""
	num = 0
	while(True):
		yield num
		num += 1

edge_id_gen = get_id_generator()

def parse():
	num_nodes = 0
	num_edges = 0
	edges = defaultdict(list)
	nodes = Set()

	write_headers()
	with open(datadir + 'KDD.graphml','a') as graph,\
		 open(inputdir + 'hep-th-citations.txt') as infile:
		for line in infile: # one entry per line
			u,v = line.split()
			edges[u].append(v) # add to adjacency list
			if u not in nodes:
				nodes.add(u)
				write_node(u, graph)
				num_nodes += 1
			if v not in nodes:
				nodes.add(v)
				write_node(v, graph)
				num_nodes += 1
		num_edges = write_edges(edges,graph)

	print("Created a GraphML graph with " + str(num_nodes) + " nodes and " + str(num_edges) + " edges.")


def write_headers():
	with open(datadir + 'KDD.graphml','w+') as graph:
		graph.write(gml.get_header())
		graph.write(gml.get_startgraph())

# TODO: only open files once...
def write_node(id, graph):
	graph.write(gml.get_node(id))

def write_edges(edges, graph):
	num_edges = 0
	for source,targets in edges.iteritems():
		for target in targets:
			graph.write(gml.get_edge(edge_id_gen.next(),source,target))
			num_edges += 1
	graph.write(gml.get_footer())
	return num_edges

parse()
