if __name__ == '__main__' and __package__ is None:
	from os import sys, path
	sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

#from __future__ import print_function
import algorithms.gml as gml
import json
import HTMLParser
from pprint import pprint
import pickle
import os
import sys
from sets import Set
from collections import defaultdict
from datetime import datetime 

inputdir = "rawdata/release/"
datadir = "data/"
dateformat = "%Y"

def get_id_generator():
	"""
	ID generator that generates ID's starting at 0.
	"""
	num = 0
	while(True):
		yield num
		num += 1

edge_id_gen = get_id_generator()

skipped_forward_edges = 0
skipped_NA_nodes = 0

def parse_citations():
	global skipped_NA_nodes,skipped_forward_edges
	num_nodes = 0
	num_edges = 0
	
	meta = {}
	for i in range(2008, 2014):
			print "Parsing year " + str(i)
			base_dir = inputdir + str(i) + "/"
			year_meta = parse_meta(base_dir)
			meta.update(year_meta)

	write_headers()

	added_nodes = Set()
	with open(datadir + 'AAN.graphml','a') as graph:
		for i in range(2008, 2014):
			print "Parsing year " + str(i)
			base_dir = inputdir + str(i) + "/"
			nodes,edges = build_graph(base_dir) # parse one AAN graph (one year)
			for node in nodes:
				if node in added_nodes:
					continue
				added_nodes.add(node)
				if node in meta and 'date' in meta[node]:
					title = meta[node]['title']
					authors = meta[node]['authors']
					date = meta[node]['date']
					attrs = ["title", title, "authors", authors, "date", date]
					write_node(node,graph,attrs)

			# for u,vs in edges.iteritems():
			# 	if u not in meta:
			# 		skipped_NA_nodes += 1
			# 		continue
			# 	if u not in nodes:
				# 	nodes.add(u)
				# 	num_nodes += 1
				# 	label = meta[u]['title']
				# 	date = meta[u]['date']
				# 	attrs = ["label", label, "date", date]
				# 	write_node(u,graph,attrs)
			# 	for v in vs:
			# 		if v in meta: # both u and v have metadata. test date and possibly insert
			# 			dates = {u: meta[u]['date'], v: meta[v]['date']}
			# 			if is_backwards_in_time(u,v,dates):
			# 				if v not in nodes:
			# 					if v == "W02-2013":
			# 						print "ADDING THAT NODE, with date."
				# 				nodes.add(v)
				# 				label = meta[v]['title']
				# 				date = meta[v]['date']
				# 				attrs = ["label", label, "date", date]
				# 				write_node(v,graph,attrs)
		num_edges = write_edges(edges,graph)
	print("Created a GraphML graph with " + str(len(nodes)) + " nodes and " + str(num_edges) + " edges.")
	print("Skipped forward-going edges: " + str(skipped_forward_edges))
	print("Skipped N/A nodes (no date): " + str(skipped_NA_nodes))

def is_backwards_in_time(u,v, dates):
	global skipped_NA_nodes,skipped_forward_edges
	if u in dates and v in dates and dates[u] is not "N/A" and dates[v] is not "N/A":
		try:
			u_date = datetime.strptime(dates[u], dateformat)
			v_date = datetime.strptime(dates[v], dateformat)
			if u_date > v_date:
				return True # citing backwards in time
			skipped_forward_edges += 1
			return False # citing forward in time, skip.
		except ValueError as e:
			print "error for: " + u + "\t" + v
			raise e

	if u not in dates or dates[u] is "N/A":
		skipped_NA_nodes += 1
	if v not in dates or dates[v] is "N/A":
		skipped_NA_nodes += 1
	return False # not enough data available. Skip these for AAN.


def parse_meta(base_dir):
	"""
	Sample metadata entry:
		id = {L08-1001}
		author = {Eichler, Kathrin; Hemsen, Holmer; Neumann, Gunter}
		title = {Unsupervised Relation Extraction From Web Documents}
		venue = {LREC}
		year = {2008}
	"""
	print "Parsing metadata..."
	meta = {}
	h = HTMLParser.HTMLParser()
	with open(base_dir + "acl-metadata.txt") as f:
		for line in f:
			if line.startswith("id"):
				line = line.strip()
				paperid = line[6:-1] # hard-coded to get e.g. L08-1001
				authors = f.next().strip()[10:-1]
				authors = h.unescape(authors.decode("iso-8859-2"))
				
				title = f.next().strip()[9:-1]
				title = h.unescape(title.decode("iso-8859-2"))
				next(f) # skip venue
				date = f.next().strip()
				if date.endswith("}"):
					date = date[8:-1]
				else:
					date = date[8:]
				meta[paperid] = {'date':date, 'title':title, 'authors':authors}
	print "Done parsing metadata"
	return meta

def write_headers():
	with open(datadir + 'AAN.graphml','w+') as graph:
		graph.write(gml.get_header())
		graph.write(gml.get_attr("title", "title", "string", "node"))
		graph.write(gml.get_attr("authors", "authors", "string", "node"))
		graph.write(gml.get_attr("date", "date", "string", "node"))
		graph.write(gml.get_startgraph())

# TODO: only open files once...
def write_node(id, graph, attrs=[]):
	graph.write(gml.get_node(id,attrs))

def write_edges(edges, graph):
	print "Writing edges..."
	num_edges = 0
	for source,targets in edges.iteritems():
		for target in targets:
			graph.write(gml.get_edge(edge_id_gen.next(),source,target))
			num_edges += 1
	graph.write(gml.get_footer())
	print "Done writing edges."
	return num_edges

def build_graph(year="2013", write_to_files=False):
	base_dir = year + "/"
	out_sep = "\t" # separates data in the output
	edge_sep = " ==> " # separates edges in the input

	#if len(sys.argv) == 1:
		#print("You must provide an input file")
		#sys.exit(0)
	#infile = sys.argv[1]

	#nodefile = "nodes.csv" # tab separated though!
	#relfile = "rels.csv" # tab separated though!

	# Currently ignores metadata which has different format for different years.
	# write_to_files WILL fail. However, it can still return nodes and edges

	#paperid_to_title = paperid_title_map(base_dir)
	#authorid_to_name = authorid_author_map(base_dir)
	#paperid_to_authors = paperid_authors_map(base_dir, authorid_to_name)

	#paperids = paperid_set(base_dir)
	#print("Read " + str(len(paperids)) + " nodes")
	edges = edge_list(base_dir) # edges as strings
	print("Read " + str(len(edges)) + " edges")

	paperids = Set() # this way, only nodes with an edge are added
	parsed_edges = defaultdict(list)
	for edge in edges:
		data = edge.split(edge_sep)
		data0 = data[0]
		data1 = data[1].rstrip()
		paperids.add(data0)
		paperids.add(data1)
		parsed_edges[data0].append(data1)
	print("Read " + str(len(paperids)) + " nodes with an edge")

	#if write_to_files:
		#with open(nodefile, "w+") as nodes, open(relfile, "w+") as rels:
			#nodes.write("paper_id:string:paper_ids" + out_sep + "title" + out_sep + "authors\n")
			#rels.write("paper_id:string:paper_ids" + out_sep + "paper_id:string:paper_ids" + out_sep + "type\n")
			
			#for edge in edges:
				## TODO maybe replace with parsed_edges loop.
				#data = edge.split(edge_sep)
				#data0 = data[0]
				#data1 = data[1].rstrip()
				#rels.write(data0 + out_sep + data1 + out_sep + "CITES\n")

			#for paper in paperids:
				#authors = paperid_to_authors[paper]
				#authors = ",".join(authors)
				#title = paperid_to_title[paper]
			#nodes.write(paper + out_sep + title + out_sep + authors + "\n")

	return (paperids, parsed_edges)


def edge_list(base_dir):
	edges = []
	with open(base_dir + "acl.txt") as f:
		edges = f.readlines()
	return edges


def paperid_title_map(base_dir):
	paperid_to_title = {}
	with open(base_dir + "paper_ids.txt") as f:
		for line in f:
			data = line.split("\t")
			paperid_to_title[data[0]] = data[1].rstrip()
	return paperid_to_title


def paperid_set(base_dir):
	"""
	Some years only have rows of paper ids, but e.g. 2013 has titles in this file
	"""
	paperids = Set()
	with open(base_dir + "paper_ids.txt") as f:
		for line in f:
			data = line.split("\t")
			paperids.add(data[0])
	return paperids

def paperid_authors_map(base_dir, authorid_to_name):
	paperid_to_authors = defaultdict(list)
	with open(base_dir + "paper_author_affiliations.txt") as f:
		f.readline() # skip first line. headers.
		for line in f:
			data = line.split("\t")
			author = data[1].rstrip()
			if ";" in author:
				authors = author.split(";")
				authors = [authorid_to_name[a] for a in authors]
				paperid_to_authors[data[0]].extend(authors)
			else:
				paperid_to_authors[data[0]].append(authorid_to_name[author])
	return paperid_to_authors

def authorid_author_map(base_dir):
	authorid_to_name = {}
	with open(base_dir + "author_ids.txt") as f:
		for line in f:
			data = line.split("\t")
			authorid_to_name[data[0]] = data[1].rstrip()
	return authorid_to_name

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
	with open('AAN-citations-with-date.csv','w+') as csv:
		csv.write('"citing_doi","cited_doi","citation_date"\n') # write headers
		for v, us in in_edges.iteritems():
			# if len(us) <= 1000:
			# 	continue
			# else:
			num_cited_added += 1
			for u in us:
				if u in meta and 'date' in meta[u]:
					date_list = meta[u]['date'].split("-")
					date = date_list[2] + "/" + date_list[1] + "/" + date_list[0] # dd/MM/yyyy
					line = u + "," + meta[v]['title'] + "," + date + "\n"
					csv.write(line)
			if num_cited_added > 20:
				return

# parse_citations()