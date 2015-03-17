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
metadir = "rawdata/aps-dataset-metadata-2013"
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
	meta = parse_meta()

	graphfile = datadir + 'APS.graphml'
	write_headers(graphfile)
	with open(graphfile,'a') as graph,\
		 open(inputdir + 'aps-dataset-citations-2013.csv') as infile:
		next(infile) # skip header line
		for line in infile: # one entry per line
			u,v = line.split(',')
			u = u.strip()
			v = v.strip()
			# TODO: add edges even if nodes fail?
			edges[u].append(v) # add to adjacency list
			for node in [u,v]:
				if node not in nodes:
					nodes.add(node)
					if node in meta and "date" in meta[node] and "title" in meta[node]:
						label = meta[node]["title"]
						date = meta[node]["date"]
						attrs = ["label", label, "date", date]
						write_node(node, graph, attrs)
						num_nodes += 1
		num_edges = write_edges(edges,graph)

	print("Created a GraphML graph with " + str(num_nodes) + " nodes and " + str(num_edges) + " edges.")


def parse_meta():
	if os.path.isfile('pickles/meta.pickle'):
		print("Loading pickled metadata.")
		with open('pickles/meta.pickle', 'rb') as f:
			return pickle.load(f)

	print("Parsing metadata...")
	meta = {}
	for root, dirs, files in os.walk(metadir):
		for file in files:
			if file.endswith('.json'):
				with open(root + "/" + file, 'r') as metafile:
					data = json.load(metafile)
					if "id" not in data or "title" not in data:
						continue
					meta_entry = {}
					meta_entry["title"] = data["title"]["value"]
					if "date" in data:
						meta_entry["date"] = data["date"]
					meta[data["id"]] = meta_entry
					
	print("Parsed " + str(len(meta)) + " abstracts.")
	with open('pickles/meta.pickle', 'wb') as f:
		pickle.dump(meta,f)      		
	return meta


def write_headers(graphfile):
	with open(graphfile,'w+') as graph:
		graph.write(gml.get_header())
		graph.write(gml.get_attr("label", "label", "string", "node"))
		graph.write(gml.get_attr("date", "date", "string", "node"))
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
