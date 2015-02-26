import gml # local
import json
from pprint import pprint
import pickle
import os

inputdir = "rawdata/"
datadir = "data/"
tmpdir = datadir + "tmp/"
# Whether to include parsed citations that aren't in the data set (doesn't have a refId)
include_unknown = True
# Whether to pickle adjacency lists for later writing (need to be written after nodes)
# or store in memory
keep_edges_in_memory = True


def get_id_generator():
	"""
	ID generator that generates ID's starting at ID's larger than the ones in the CORE data set.
	Used for creating new nodes based on e.g. citations to publications not in the set (no refID).
	"""
	num = 80000000001
	while(True):
		yield num
		num += 1

id_gen = get_id_generator()
# print(id_gen.next())
# print(id_gen.next())
# print(id_gen.next())
# print(id_gen.next())

def parse():
	num_nodes = 0
	num_unknown_nodes = 0
	num_edges = 0
	edges = {}

	write_headers()

	with open(datadir + 'core.graphml','w+') as graph,\
		 open(datadir + 'paperid-title.txt', 'a') as pt,\
		 open(datadir + 'paperid-authors.txt', 'a') as pa:
		for f in os.listdir(inputdir): # loop pickled edge lists and write to graph file
			if f.endswith(".json"):	
				print("Parsing " + f + "...")
				with open(inputdir + f, 'r') as infile:
					edges = {}
					for line in infile: # one entry per line
						jsonobj = json.loads(line)
						id = jsonobj["identifier"]
						# (All entries seem to have "bibo:cites")
						if not all(key in jsonobj for key in ["dc:date", "bibo:shortTitle", "bibo:AuthorList"]):
							continue
						date = jsonobj["dc:date"]
						title = jsonobj["bibo:shortTitle"]
						authors = jsonobj["bibo:AuthorList"]
						cites = jsonobj["bibo:cites"]
						cites_ids = [x["refDocId"] for x in cites if "refDocId" in x.keys()]

						unknowncites_ids = []
						unknowncites_titles = []
						unknowncites_authors = []
						if include_unknown:
							# extract data from cited publications that don't have refIds (aren't in the set)
							unknowncites_titles = [x["bibo:shortTitle"] for x in cites if "refDocId" not in x.keys() and "bibo:shortTitle" in x.keys()]
							unknowncites_authors = [x["authors"] for x in cites if "refDocId" not in x.keys() and "authors" in x.keys()]
							# generate IDs for all new publications
							unknowncites_ids = [id_gen.next() for _ in range(len(unknowncites_titles))]
							cites_ids.extend(unknowncites_ids)
						if cites_ids: # pickle to file to keep memory low
							if keep_edges_in_memory:
								edges[id] = cites_ids
							else: # TODO: Maybe rewrite to use less files. Currently one per adj. list.
								with open(tmpdir + str(id) + '.tmp', 'w+') as tmpedges:
									pickle.dump(cites_ids, tmpedges)

						citedBy = jsonobj["bibo:citedBy"]
						if len(authors) == 0 or (len(citedBy) == 0 and len(cites) == 0): # no authors or no links. ignore.
							continue
							#print "No citations for " + str(id) + ". Continuing..."
						else:
							write_data(id,title,authors, graph, pt, pa)
							num_nodes += 1
							if include_unknown:
								for i in range(len(unknowncites_ids)):
									write_data(unknowncites_ids[i], unknowncites_titles[i], unknowncites_authors[i], graph, pt, pa)
									num_unknown_nodes += 1

	if keep_edges_in_memory: # write edges dictionary to file
		num_edges = write_edges(edges)
	if not keep_edges_in_memory: # write pickled edges to file
		num_edges = append_edges()

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

def write_edges(edges):
	num_edges = 0
	with open(datadir + 'core.graphml','a') as graph:
		for source,targets in edges.iteritems():
				for target in targets:
					graph.write(gml.get_edge(source,target))
					num_edges += 1
		graph.write(gml.get_footer())
	return num_edges

def append_edges():
	"""
	Append all adjacency lists pickled to temporary files in tmp.
	Also writes the closing tags using get_footer().
	"""
	with open(datadir + 'core.graphml','a') as graph:
		num_edges = 0
		for f in os.listdir(tmpdir): # loop pickled edge lists and write to graph file
				source = int(f[:-4]) # skip '.tmp' extension
				targets = pickle.load(open(tmpdir + f,'rb'))
				for target in targets:
					graph.write(gml.get_edge(source, target))
					num_edges += 1
				os.remove(tmpdir + f) # remove temporary pickle file
		graph.write(gml.get_footer())
		return num_edges

parse()
