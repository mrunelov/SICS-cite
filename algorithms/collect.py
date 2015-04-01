AAN_dir = '../AAN/'
burstfile = AAN_dir + 'data/Burst-detection-analysis-AAN.csv'
metrics_dir = '../graph-tool/AAN/'


def create_csv_all_AAN():
	b = load_csv_as_map(metrics_dir + "betweenness.csv")
	i = load_csv_as_map(metrics_dir + "indegs.csv")
	h = load_csv_as_map(metrics_dir + "hits.csv")
	bursts = load_burst_map()

	with open("all_AAN.csv", "w+") as csv:
		csv.write("title,indegree,betweenness,hits,burst_weight\n")
		for k in b.keys():
			line = k + "," + str(i[k]) + "," + str(b[k]) + "," + str(h[k]) + ","
			if k in bursts:
				line += bursts[k]
			else:
				line += "0"
			line += "\n"
			csv.write(line)


def load_burst_map():
	# Word,Level,Weight,Length,Start,End (word is title.strip().replace(",",""))
	burst_map = {}
	with open(burstfile, "r") as f:
		next(f) # skip header
		for line in f:
			data = line.strip().split(",")
			burst_map[data[0]] = data[2]
	return burst_map



def load_csv_as_map(filename):
	"""
	Loads a csv file with two values into a dictionary
	"""
	csv_map = {}
	with open(filename, "r") as f:
		for line in f:
			key,value = line.strip().split(",")
			csv_map[key] = value
	print "Loaded " + str(len(csv_map.keys())) + " lines"
	return csv_map

create_csv_all_AAN()