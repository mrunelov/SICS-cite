import graph_tool.all as gt
from find_fellows2 import *
#from find_fellows import *

g = gt.load_graph("AAN.graphml") #"AAN-preprocessed.xml")
titles = g.vertex_properties["title"]
authors = g.vertex_properties["authors"]

def get_authors_for_title(title):
    for n in g.vertices():
        if titles[n].strip().replace(",","") == title:
            return authors[n]
    return None


def add_fellows():
    fellow_indexes = []
    with open("all_AAN.csv","r") as old,\
        open("all_AAN_with_fellows.csv", "w+") as new:
        header = old.next()
        new.write(header.strip() + ",fellow\n")
        for line in old:
            old_data = line.strip().split(",")
            gt_index = int(old_data[0])
            v = g.vertex(gt_index)
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
                    fellow_indexes.append(gt_index)
                new_data = line.strip() + "," + str(fellow) + "\n"
                new.write(new_data)

    # can't pickle with defaultdict and lambda...
    with open("fellow_indexes2.pickle", "wb") as f:
        pickle.dump(fellow_indexes,f)


def add_pagerank():
    pr = gt.pagerank(g,damping=0.5)
    with open("all_AAN_with_fellows.csv","r") as old,\
        open("all_AAN_with_fellows_and_pagerank.csv", "w+") as new:
        header = old.next()
        new.write(header.strip() + ",pagerank\n")
        for line in old:
            old_data = line.strip().split(",")
            gt_index = int(old_data[0])
            new_data = line.strip() + "," + str(pr.a[gt_index]) + "\n"
            new.write(new_data)

add_pagerank()
