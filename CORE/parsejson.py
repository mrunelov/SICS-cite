#from __future__ import print_function
import gml # local
import json
from pprint import pprint
import pickle
import os
import sys
from sets import Set

inputdir = "rawdata/"
datadir = "data/"
tmpdir = datadir + "tmp/"
# Whether to include parsed citations that aren't in the data set (doesn't have a refId)
include_unknown = True
# Whether to pickle adjacency lists for later writing (need to be written after nodes)
# or store in memory
keep_edges_in_memory = True


def get_unknown_id_generator(start=0):
	"""
	ID generator that generates ID's starting at ID's larger than the ones in the CORE data set.
	Used for creating new nodes based on e.g. citations to publications not in the set (no refID).
	"""
	num = 80000000001
	while(True):
		yield num
		num += 1

def get_id_generator():
	"""
	ID generator that generates ID's starting at 0.
	"""
	num = 0
	while(True):
		yield num
		num += 1

unknown_id_gen = get_unknown_id_generator(80000000001)
edge_id_gen = get_id_generator()
# print(id_gen.next())
# print(id_gen.next())
# print(id_gen.next())
# print(id_gen.next())

def parse():
	num_nodes = 0
	num_unknown_nodes = 0
	num_edges = 0
	edges = {}
	nodes = Set()

	write_headers()
	with open(datadir + 'core.graphml','a') as graph,\
		 open(datadir + 'paperid-title.txt', 'a') as pt,\
		 open(datadir + 'paperid-authors.txt', 'a') as pa:
		files = [f for f in os.listdir(inputdir) if f.endswith(".json")]
		parsed = 0
		for f in files: # loop pickled edge lists and write to graph file
			if f.endswith(".json"):	
				print "Parsing file " + str(parsed+1) + " / " + str(len(files)) + "\r",
				sys.stdout.flush()
				parsed += 1
				if parsed == len(files):
					print ""
				with open(inputdir + f, 'r') as infile:
					for line in infile: # one entry per line
						jsonobj = json.loads(line)
						# (All entries seem to have "bibo:cites")
						if not all(key in jsonobj for key in ["doi", "dc:date", "bibo:shortTitle", "bibo:AuthorList"]):
							continue
						id = jsonobj["identifier"] # or "doi"
						date = jsonobj["dc:date"]
						title = jsonobj["bibo:shortTitle"]
						authors = jsonobj["bibo:AuthorList"]
						cites = jsonobj["bibo:cites"]
						citedBy = jsonobj["bibo:citedBy"]
						if len(authors) == 0 or (len(citedBy) == 0 and len(cites) == 0): # no authors or no links. ignore.
							continue
						# if "<" in id or "&" in id: # forbidden symbols
						# 	continue

						cites_ids = [] 
						unknowncites_ids = []
						unknowncites_titles = []
						unknowncites_authors = []
						for c in cites:
							if "refDocId" in c.keys():
								cites_ids.append(c["refDocId"])
							elif include_unknown:
								unknowncites_ids.append(unknown_id_gen.next())
								if "bibo:shortTitle" in c.keys():
									unknowncites_titles.append(c["bibo:shortTitle"])
								if "authors" in c.keys():
									unknowncites_authors.append(c["authors"])
						cites_ids.extend(unknowncites_ids)

						if cites_ids: 
							if keep_edges_in_memory:
								edges[id] = cites_ids
							else: # TODO: Maybe rewrite to use less files. Currently one per adj. list.
								with open(tmpdir + str(id) + '.tmp', 'w+') as tmpedges:
									pickle.dump(cites_ids, tmpedges)


						write_data(id,title,authors, graph, pt, pa)
						num_nodes += 1
						if include_unknown:
							for i in range(len(unknowncites_ids)):
								nodes.add(unknowncites_ids[i])
								write_data(unknowncites_ids[i], unknowncites_titles[i], unknowncites_authors[i], graph, pt, pa)
								num_unknown_nodes += 1

	if keep_edges_in_memory: # write edges dictionary to file
		num_edges = write_edges(edges, nodes)
	if not keep_edges_in_memory: # write pickled edges to file
		num_edges = append_edges(nodes)

	print("Created a GraphML graph with " + str(num_nodes+num_unknown_nodes) + " nodes (" + str(num_unknown_nodes) + " unknown) and " + str(num_edges) + " edges.")


def write_headers():
	with open(datadir + 'core.graphml','w+') as graph:
		graph.write(gml.get_header())
		#graph.write(gml.get_attr(name="weight", attr_type="int", attr_for="edge",id="d0")) # write attribute definitions
		graph.write(gml.get_startgraph())

# TODO: only open files once...
def write_data(id, title, authors, graph, pt, pa):
	"""
	writes data to the open files graph, pt and pa
	"""
	if title: # skip the entire node if title is empty
		graph.write(gml.get_node(id))
		pt.write(str(id) + "\t" + title.encode('utf-8') + "\n")
		if authors:
			pa.write(str(id) + "\t" + str(authors) + "\n")

def write_edges(edges, valid_nodes):
	num_edges = 0
	with open(datadir + 'core.graphml','a') as graph:
		for source,targets in edges.iteritems():
				for target in targets:
					if target in valid_nodes:
						graph.write(gml.get_edge(edge_id_gen.next(),source,target))
						num_edges += 1
		graph.write(gml.get_footer())
	return num_edges

def append_edges(valid_nodes):
	"""
	Append all adjacency lists pickled to temporary files in tmp.
	Also writes the closing tags using get_footer().
	"""
	print("Appending pickled edges...")
	with open(datadir + 'core.graphml','a') as graph:
		num_edges = 0
		for f in os.listdir(tmpdir): # loop pickled edge lists and write to graph file
				source = int(f[:-4]) # skip '.tmp' extension
				targets = pickle.load(open(tmpdir + f,'rb'))
				for target in targets:
					if target in valid_nodes:
						graph.write(gml.get_edge(edge_id_gen.next(),source,target))
						num_edges += 1
				os.remove(tmpdir + f) # remove temporary pickle file
		graph.write(gml.get_footer())
		return num_edges

parse()
