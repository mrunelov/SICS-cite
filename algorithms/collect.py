from backbone import get_Px, get_impact_graph
from graphutils import get_gml_graph

# TODO: see why the csv file doesn't have 18158 rows like the preprocessed
# file AAN-preprocessed.xml, but only 18057 or so.

AAN_dir = '../AAN/'
burstfile = AAN_dir + 'data/Burst-detection-analysis-AAN.csv'
metrics_dir = '../graph-tool/AAN/'

title_index_map = {}


def create_csv_all_AAN():
	b = load_csv_as_map(metrics_dir + "betweenness.csv")
	i = load_csv_as_map(metrics_dir + "indegs.csv")
	h = load_csv_as_map(metrics_dir + "hits.csv")
	bursts = load_burst_map()
	progeny_sizes = load_progeny_sizes()
	# impacts = load_impacts()

	with open("all_AAN.csv", "w+") as csv:
		csv.write("gt_index,indegree,betweenness,hits,burst_weight,progeny_size\n")
		for k in b.keys():
			line = k + "," + str(i[k]) + "," + str(b[k]) + "," + str(h[k]) + ","
			if k in bursts:
				line += str(bursts[k])
			else:
				line += "0"
			line += ","
			if k in progeny_sizes:
				line += str(progeny_sizes[k])
			else:
				line += "0"
			# line += ","
			# if k in impacts:
			# 	line += str(impacts[k])
			# else:
			# 	line += "0"
			line += "\n"
			csv.write(line)


def load_progeny_sizes(normalize_values=False):
	G = get_gml_graph("AAN")
	Px_map = {}
	Px,nodes = get_Px()
	for i in range(len(nodes)):
		if "title" not in G.node[nodes[i]]:
			print "Skipping node..."
		else:
			title = G.node[nodes[i]]["title"].strip().replace(",","")
                        key = title_index_map[title]
			Px_map[key] = int(Px[i])
	if normalize_values:
		M = max(Px_map.values())
		for k in Px_map.keys():
			Px_map[k] /= float(M)
	return Px_map


# Not very useful since impact sums to 1, but can be used in other ways later maybe
# def load_impacts(normalize_values=False):
# 	G = get_impact_graph()
# 	impact_map = {}
# 	num_skipped = 0
# 	for n in G.nodes_iter(data=True):
# 		if "label" not in n[1]: # called label in this graph. it should be fixed..
# 			print n
# 			num_skipped += 1
# 			# print "Skipping node..."
# 		else:
# 			pred = G.predecessors(n[0])
# 			cumulative_impact = sum([G[x][n[0]]["impact"] for x in pred])
# 			title = n[1]["label"].strip().replace(",","")
# 			impact_map[title] = cumulative_impact
# 	if normalize_values:
# 		M = max(impact_map.values())
# 		for k in impact_map.keys():
# 			impact_map[k] /= float(M)
# 	print "Done loading impacts. Skipped " + str(num_skipped) + " nodes."
# 	return impact_map


def load_burst_map(normalize_values=False):
	# Word,Level,Weight,Length,Start,End (word is title.strip().replace(",",""))
	burst_map = {}
	with open(burstfile, "r") as f:
		next(f) # skip header
		for line in f:
			data = line.strip().split(",")
                        key = title_index_map[data[0]] # get gt_index from title
			burst_map[key]= float(data[2])
	if normalize_values:
		M = max(burst_map.values())
		for k in burst_map.keys():
			burst_map[k] /= M
	return burst_map


firstcall = True
def load_csv_as_map(filename, normalize_values=False):
	"""
	Loads a csv file with two values into a dictionary
	"""
	csv_map = {}
	with open(filename, "r") as f:
                next(f) # skip headers
		for line in f:
			title,key,value = line.strip().split(",")
                        title_index_map[title] = key
			csv_map[key] = float(value)
        if normalize_values:
            M = max(csv_map.values())
            for k in csv_map.keys():
                csv_map[k] /= M

	print "Loaded " + str(len(csv_map.keys())) + " lines"
        firstcall = False
	return csv_map

create_csv_all_AAN()
