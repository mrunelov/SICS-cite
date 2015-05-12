from backbone import get_Px, get_impact_graph
from graphutils import get_gml_graph

# Handle APS and AAN differently.
# Make use of the insertion order from graph-tool
# since that's the only way to get constant lookup (can't use attributes for that)

AAN_dir = '../AAN/'
APS_dir = '../APS/'
burstfile = AAN_dir + 'data/Burst-detection-analysis-AAN.csv'
burstfile1 = APS_dir + 'data/Burst-detection-analysis-part1.csv'
burstfile2 = APS_dir + 'data/Burst-detection-analysis-part2.csv'
metrics_dir = '../graph-tool/APS/'

title_index_map = {}

def create_csv_all():
	i = load_csv_as_map(metrics_dir + "indegs.csv")
	b = load_csv_as_map(metrics_dir + "betweenness.csv")
	h = load_csv_as_map(metrics_dir + "hits.csv")
	bursts1 = load_burst_map(burstfile=burstfile1)
	bursts2 = load_burst_map(burstfile=burstfile2)
	#bursts = load_burst_map()

	progeny_sizes = load_progeny_sizes_APS()
	# impacts = load_impacts()

	with open("all_APS.csv", "w+") as csv:
		csv.write("gt_index,indegree,betweenness,hits_auth,burst_weight,progeny_size\n")
		for k in i.keys():
                        betweenness = b[k] if k in b else 0
			line = k + "," + str(int(i[k])) + "," + str(betweenness) + "," + str(h[k]) + ","
			if k in bursts1:
				line += str(bursts1[k])
			if k in bursts2:
				line += str(bursts2[k])
			else:
				line += "0"
			line += ","
			if k in progeny_sizes:
				line += str(progeny_sizes[k])
			else:
				line += "0"
			line += "\n"
			csv.write(line)

def load_progeny_sizes_APS():
    Px_map = {}
    Px,ids = get_Px()
    for i in range(len(Px)):
        Px_map[title_index_map[ids[i]]]= Px[i]
    return Px_map
    


def load_progeny_sizes_AAN(normalize_values=False):
	Px_map = {}
	Px,titles = get_Px()
        num_skipped = 0
	for i in range(len(Px)):
                title = titles[i].strip().replace(",","")
                title = title.encode("utf-8")
                key = title_index_map[title]
                Px_map[key] = int(Px[i])
	if normalize_values:
		M = max(Px_map.values())
		for k in Px_map.keys():
			Px_map[k] /= float(M)
        print "Skipped " + str(num_skipped) + " nodes"
	return Px_map


def load_burst_map(normalize_values=False,burstfile=burstfile):
	# Word,Level,Weight,Length,Start,End (word is title.strip().replace(",",""))
	burst_map = {}
	with open(burstfile, "r") as f:
		next(f) # skip header
		for line in f:
			data = line.strip().split(",")
                        try:
                            key = title_index_map["n" + data[0]] # get gt_index from title
                            burst_map[key]= float(data[2])
                        except KeyError as e:
                            print "No mapping for " + data[0]
	if normalize_values:
		M = max(burst_map.values())
		for k in burst_map.keys():
			burst_map[k] /= M
	return burst_map


firstcall = True
def load_csv_as_map(filename, normalize_values=False):
	"""
	Loads a csv file (title,gt_index,value) into a dictionary
	that maps gt_index to value
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

# create_csv_all_AAN()
create_csv_all()
