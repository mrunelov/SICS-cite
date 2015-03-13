if __name__ == '__main__' and __package__ is None:
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

#from __future__ import print_function
import algorithms.gml as gml
import json
from pprint import pprint
import pickle
import os
import sys
from sets import Set
from collections import defaultdict

inputdir = "rawdata/"
datadir = "data/"
#abstractdir = "rawdata/abstracts/"

def get_id_generator():
	"""
	ID generator that generates ID's starting at 0.
	"""
	num = 0
	while(True):
		yield num
		num += 1
edge_id_gen = get_id_generator()

def parse_citations():
	num_nodes = 0
	num_edges = 0
	edges = defaultdict(list)
	nodes = Set()
	#meta = parse_abstracts() # maps id's to a meta label (authors + title)

	graphfile = datadir + 'APS.graphml'
	write_headers(graphfile)
	with open(graphfile,'a') as graph,\
		 open(inputdir + 'aps-dataset-citations-2013.csv') as infile:
		next(infile) # skip first header line
		for line in infile: # one entry per line
			u,v = line.split(',')
			edges[u].append(v) # add to adjacency list
			if u not in nodes:
				nodes.add(u)
				label = "N/A" #meta[v] if v in meta else "N/A"
				attrs = ["label", label]
				write_node(u, graph, attrs)
				num_nodes += 1
			if v not in nodes:
				nodes.add(v)
				label = "N/A" #meta[v] if v in meta else "N/A"
				attrs = ["label", label]
				write_node(v, graph, attrs)
				num_nodes += 1
		num_edges = write_edges(edges,graph)

	print("Created a GraphML graph with " + str(num_nodes) + " nodes and " + str(num_edges) + " edges.")

# OBS: Old code for KDD!
def parse_abstracts():
	print("Parsing abstracts...")
	meta = {}
	for root, dirs, files in os.walk(abstractdir):
		for file in files:
			if file.endswith('.abs'):
				with open(root + "/" + file, 'r') as abstract:
					meta_entry = ""
					for line in abstract:
						if line.startswith("Title: "):
							meta_entry += line[7:].replace("<","").replace(">","").replace("&","&amp;").rstrip()
						if line.startswith("Author: "):
							meta_entry += ", " + line[8:].replace("<","").replace(">","").replace("&","&amp;").rstrip()
							break
						if line.startswith("Authors: "):
							meta_entry += ", " + line[9:].replace("<","").replace(">","").replace("&","&amp;").rstrip()
							break
					meta[file[:-4]] = meta_entry
	print("Parsed " + str(len(meta)) + " abstracts.")          		
	return meta


def write_headers(graphfile):
	with open(graphfile,'w+') as graph:
		graph.write(gml.get_header())
		graph.write(gml.get_attr("label", "label", "string", "node"))
		graph.write(gml.get_startgraph())

# TODO: only open files once...
def write_node(id, graph, attrs=[]):
	graph.write(gml.get_node(id,attrs))

def write_edges(edges, graph):
	num_edges = 0
	for source,targets in edges.iteritems():
		for target in targets:
			graph.write(gml.get_edge(edge_id_gen.next(),source,target))
			num_edges += 1
	graph.write(gml.get_footer())
	return num_edges

parse_citations()