import graph_tool.all as gt
from collections import defaultdict
from find_fellows import *

g = gt.load_graph("AAN.graphml") #"AAN-preprocessed.xml")
titles = g.vertex_properties["title"]
authors = g.vertex_properties["authors"]


def get_authors_for_title(title):
    for n in g.vertices():
        if titles[n].strip().replace(",","") == title:
            return authors[n]
    return None



index_fellow_map = defaultdict(lambda : False)
with open("all_AAN.csv","r") as old,\
    open("all_AAN_with_fellows.csv", "w+") as new:
    header = old.next()
    new.write(header.strip() + ",fellow\n")
    for line in old:
        old_data = line.strip().split(",")
        gt_index = old_data[0]
        v = g.vertex(int(gt_index))
        #title = titles[v]
        #print title
        #author_list = get_authors_for_title(title).split(";")
        author_list = authors[v].split(";")
        if author_list is None:
            print "Didn't find matching node for title:"
            print title
        else:
            for a in author_list:
                fellow = find_fellow(a,reverse=True)
                if fellow != -1:
                    fellow = 1
                    break
            if fellow == -1:
                fellow = 0
            else:
                index_fellow_map[gt_index] = True
            new_data = line.strip() + "," + str(fellow) + "\n"
            new.write(new_data)

# can't pickle with defaultdict and lambda...
#with open("index_fellow_map.pickle", "wb") as f:
    #pickle.dump(index_fellow_map,f)

