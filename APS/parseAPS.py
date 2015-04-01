if __name__ == '__main__' and __package__ is None:
	from os import sys, path
	sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

#from __future__ import print_function
import algorithms.gml as gml
import json
from pprint import pprint
from datetime import datetime
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

def write_meta_CSV():
	in_edges = defaultdict(list)
	with open(inputdir + 'aps-dataset-citations-2013.csv') as infile:
		next(infile) # skip headers in infile
		for line in infile:
			u,v = line.split(',')
			u = u.strip()
			v = v.strip()
			in_edges[v].append(u)

	meta = parse_meta()
	num_cited_added = 0
	with open('APS-citations-with-date.csv','w+') as csv:
		csv.write('"citing_doi","cited_doi","citation_date"\n') # write headers
		for v, us in in_edges.iteritems():
			if len(us) <= 1:
				continue
			#else:
			#num_cited_added += 1
			for u in us:
				if u in meta and 'date' in meta[u]:
					date_list = meta[u]['date'].split("-")
					date = date_list[2] + "/" + date_list[1] + "/" + date_list[0] # dd/MM/yyyy
					line = u + "," + meta[v]['title'] + "," + date + "\n"
					csv.write(line)
			if num_cited_added > 20:
				return

def preprocess_CSV():
	num_rows = 5934522
	half = 5934522/2
	prev_target = ""
	with open('data/APS-citations-with-date.csv','r') as csv, \
	    open('data/APS-citations-with-date-part1.csv','w+') as csv1, \
	    open('data/APS-citations-with-date-part2.csv','w+') as csv2:
		i = 0
		for line in csv:
			if i < half:
				csv1.write(line)
				if i == half -1:
					prev_target = line.split(",")[1]
			elif i == half: # special case, don't split time series over multiple files!
				target = line.split(",")[1]
				while target == prev_target:
					csv1.write(line)
					line = csv.next()
					target = line.split(",")[1]
				csv2.write(line) # write first non-matching to second file
			else:
				csv2.write(line)
			i += 1

def parse_citations():
	num_nodes = 0
	num_edges = 0
	skipped_edges = 0
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
			if u in meta and v in meta:
				if "date" in meta[u] and "date" in meta[v] and is_backwards_in_time(meta[u]["date"],meta[v]["date"]):
					edges[u].append(v) # add to adjacency list
					for node in [u,v]:
						if node not in nodes and "title" in meta[node]:
							nodes.add(node)
							label = meta[node]["title"]
							date = meta[node]["date"]
							attrs = ["label", label, "date", date]
							write_node(node, graph, attrs)
							num_nodes += 1
				else:
					skipped_edges += 1
		num_edges = write_edges(edges,graph)

	print("Created a GraphML graph with " + str(num_nodes) + " nodes and " + str(num_edges) + " edges.")
	print("Skipped " + str(skipped_edges) + " edges due to incorrect dates")


dateformat = "%Y-%m-%d"
def is_backwards_in_time(date1, date2):
	u_date = datetime.strptime(date1,dateformat)
	v_date = datetime.strptime(date2,dateformat)
	if u_date > v_date:
		return True # citing backwards in time
	return False # citing forward in time


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

#parse_citations()
#write_meta_CSV()
#preprocess_CSV()
