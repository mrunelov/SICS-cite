import gml # local
import json
from pprint import pprint
import pickle
import os

inputdir = "rawdata/"
datadir = "data/"
tmpdir = datadir + "tmp/"
# Whether to include parsed citations that aren't in the data set (doesn't have a refId)
include_unknown = False 
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
	# Loop all json files and write nodes and metadata. Pickle edges in tmp
	with open(datadir + 'core.graphml','w+') as graph:
		edges = {}
		graph.write(gml.get_header())
		#graph.write(gml.get_attr(name="weight", attr_type="int", attr_for="edge",id="d0")) # write attribute definitions
		graph.write(gml.get_startgraph())
		for f in os.listdir(inputdir): # loop pickled edge lists and write to graph file
			if f.endswith(".json"):	
				print("Parsing " + f + "...")
				with open(inputdir + f, 'r') as infile,\
					 open(datadir + 'paperid-title.txt', 'a') as pt,\
					 open(datadir + 'paperid-authors.txt', 'a') as pa:
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
						# refDocId identifies cited paper if it's in CORE. 
						cites = jsonobj["bibo:cites"]

						# extract internal ID's for cited publications
						cites_ids = [x["refDocId"] for x in cites if "refDocId" in x.keys()]

						unknowncites_ids = []
						unknowncites_titles = []
						if include_unknown:
							# extract titles for cited publications that don't have refIds (aren't in the set)
							unknowncites_titles = [x["bibo:shortTitle"] for x in cites if "refDocId" not in x.keys() and "bibo:shortTitle" in x.keys()]
							# generate IDs for all new publications
							unknowncites_ids = [id_gen.next() for _ in range(len(unknowncites_titles))]
							cites_ids.extend(unknowncites_ids)
						# TODO: Maybe rewrite to use less files. Currently one per adj. list.
						if cites_ids: # pickle to file to keep memory low
							if keep_edges_in_memory:
								edges[id] = cites_ids
							else:
								with open(tmpdir + str(id) + '.tmp', 'w+') as tmpedges:
									pickle.dump(cites_ids, tmpedges)

							#tmpedges.write(str(id) + "\t" + str(localcites))
							#edges[id] = localcites

						citedBy = jsonobj["bibo:citedBy"]
						if len(authors) == 0 or (len(citedBy) == 0 and len(cites) == 0): # no authors or no links. ignore.
							continue
							#print "No citations for " + str(id) + ". Continuing..."
						else:
							pt.write(str(id) + "\t" + title.encode('utf-8') + "\n") # tab delimited
							pa.write(str(id) + "\t" + str(authors) + "\n") # tab delimited
							graph.write(gml.get_node(id))
							num_nodes += 1
							if include_unknown:
								# TODO: write authors from unknown_cites. Always empty? (shouldn't be)
								for i in range(len(unknowncites_ids)):
									pt.write(str(unknowncites_ids[i]) + "\t" + unknowncites_titles[i].encode('utf-8') + "\n") # tab delimited
									graph.write(gml.get_node(unknowncites_ids[i]))
									num_unknown_nodes += 1
		if keep_edges_in_memory:
			for source,targets in edges.iteritems():
				for target in targets:
					graph.write(gml.get_edge(source,target))
					num_edges += 1
			graph.write(gml.get_footer())
	if not keep_edges_in_memory:
		num_edges = append_edges() # append pickled edges
	print("Created a GraphML graph with " + str(num_nodes+num_unknown_nodes) + " nodes (" + str(num_unknown_nodes) + " unknown) and " + str(num_edges) + " edges.")


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
