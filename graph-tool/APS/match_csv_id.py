import graph_tool.all as gt
import pickle


# 69197 lines to be read (minus header)

# Map Ids to their betweenness
id_between_map = {}
line_no = 2
with open("betweenness.csv", "r") as csv:
    next(csv) # skip header
    for line in csv:
        if line_no == 69197:
            break
        n_id, _, betweenness = line.strip().split(",")
        id_between_map[n_id] = betweenness
        line_no += 1
print "Loaded " + str(len(id_between_map.keys())) + " lines"

# Load graph to loop over ids and find matching gt_index
ids_gt_map = {}
g = gt.load_graph("APS.graphml")
ids = g.vertex_properties["_graphml_vertex_id"]
gt_idx = 0
for n in g.vertices():
    if ids[n] in id_between_map:
        ids_gt_map[ids[n]] = gt_idx
    gt_idx += 1

print "Found " + str(len(ids_gt_map.keys())) + " matching ids"

betweenness_array = [0]*g.num_vertices()
with open("betweenness2.csv", "w+") as newcsv:
    newcsv.write("id,gt_index,betweenness\n")
    for k in id_between_map.keys():
        line = k + "," + str(ids_gt_map[k]) + "," + id_between_map[k] + "\n"
        newcsv.write(line)
        betweenness_array[ids_gt_map[k]] = float(id_between_map[k])

with open("vpa-between2.pickle", "wb") as f:
    pickle.dump(betweenness_array,f)
print "Wrote betweenness array to pickle"
