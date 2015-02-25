import gml # local
import json
from pprint import pprint
import pickle
import os

inputdir = "."
datadir = "data/"
tmpdir = datadir + "tmp/"

def parse():
	withoutCitations = 0
	withCitations = 0
	# Loop all json files and write nodes and metadata. Pickle edges in tmp
	with open(datadir + 'core.graphml','w+') as graph:
		graph.write(gml.get_header())
		#graph.write(gml.get_attr(name="weight", attr_type="int", attr_for="edge",id="d0")) # write attribute definitions
		graph.write(gml.get_startgraph())
		for f in os.listdir(inputdir): # loop pickled edge lists and write to graph file
			if f.endswith(".json"):	
				with open(f, 'r') as infile,\
					 open(datadir + 'paperid-title.txt', 'a') as pt,\
					 open(datadir + 'paperid-authors.txt', 'a') as pa:
					edges = {}
					for line in infile: # one entry per line
						jsonobj = json.loads(line)
						id = jsonobj["identifier"]
						if not all(key in jsonobj for key in ["dc:date", "bibo:shortTitle", "bibo:AuthorList"]):
							continue
						date = jsonobj["dc:date"]
						title = jsonobj["bibo:shortTitle"]
						authors = jsonobj["bibo:AuthorList"]
						# refDocId identifies cited paper if it's in CORE. 
						cites = jsonobj["bibo:cites"]

						localcites = [x["refDocId"] for x in cites if "refDocId" in x.keys()]
						if localcites: # pickle to file to keep memory low
							with open(tmpdir + str(id) + '.tmp', 'w+') as tmpedges: 
								pickle.dump(localcites, tmpedges)

							#tmpedges.write(str(id) + "\t" + str(localcites))
							#edges[id] = localcites

						citedBy = jsonobj["bibo:citedBy"]
						if len(authors) == 0 or (len(citedBy) == 0 and len(cites) == 0): # no authors or no links. ignore.
							withoutCitations += 1
							#print "No citations for " + str(id) + ". Continuing..."
						else:
							withCitations += 1
							pt.write(str(id) + "\t" + title.encode('utf-8') + "\n") # tab delimited
							pa.write(str(id) + "\t" + str(authors) + "\n") # tab delimited
							graph.write(gml.get_node(id))

	append_edges() # append pickled edges



def append_edges():
	"""
	Append all adjacency lists pickled to temporary files in tmp.
	Also writes the closing tags using get_footer().
	"""
	with open(datadir + 'core.graphml','a') as graph:
		for f in os.listdir(tmpdir): # loop pickled edge lists and write to graph file
				source = int(f[:-4]) # skip '.tmp' extension
				targets = pickle.load(open(tmpdir + f,'rb'))
				for target in targets:
					graph.write(gml.get_edge(source, target))
				os.remove(tmpdir + f) # remove temporary pickle file
		graph.write(gml.get_footer())

parse()