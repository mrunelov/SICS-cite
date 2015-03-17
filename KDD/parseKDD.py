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
from datetime import datetime 

inputdir = "rawdata/"
datadir = "data/"
abstractdir = "rawdata/abstracts/"

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
	skipped_forward_edges = 0
	edges = defaultdict(list)
	nodes = Set()
	meta = parse_abstracts() # maps id's to a meta label (authors + title)
	dates = parse_dates() # maps id's to dates

	write_headers()
	with open(datadir + 'KDD.graphml','a') as graph,\
		 open(inputdir + 'Cit-HepTh.txt') as infile:
		for line in infile: # one entry per line
			if line.startswith('#'): # ignore comments
				continue
			u,v = line.split()
			if is_backwards_in_time(u,v,dates):
				edges[u].append(v) # add to adjacency list
				for node in [u,v]:
					if node not in nodes:
						nodes.add(node)
						label = meta[node] if node in meta else "N/A"
						date = dates[node] if node in dates else "N/A"
						attrs = ["label", label, "date", date]
						write_node(node, graph, attrs)
						num_nodes += 1
				else:
					skipped_forward_edges += 1
		num_edges = write_edges(edges,graph)

	print("Created a GraphML graph with " + str(num_nodes) + " nodes and " + str(num_edges) + " edges.")
	print("Skipped forward-going edges: " + str(skipped_forward_edges))

dateformat = "%Y-%m-%d"
def is_backwards_in_time(u,v, dates):
	if u in dates and v in dates and dates[u] is not "N/A" and dates[v] is not "N/A":
		u_date = datetime.strptime(dates[u], dateformat)
		v_date = datetime.strptime(dates[v], dateformat)
		if u_date > v_date:
			return True # citing backwards in time
		return False # citing forward in time
	return False # not enough data available

def parse_dates():
	dates = {}
	print("Parsing dates...")
	with open(inputdir + 'Cit-HepTh-dates.txt','r') as f:
		for line in f:
			if line.startswith('#'):
				continue
			node,date = line.split()
			if node.startswith('11'):
				node = node[2:] # remove 11 marker, means it's cross-listed, but true id comes after.
			dates[node] = date
	print("Done parsing dates.")
	return dates


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


def write_headers():
	with open(datadir + 'KDD.graphml','w+') as graph:
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