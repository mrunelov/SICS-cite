import graph_tool.all as gt
from find_fellows import *
import pickle

def get_authors_for_title(title):
    for n in g.vertices():
        if titles[n].strip().replace(",","") == title:
            return authors[n]
    return None


def add_fellows():
    num_fellows = 0
    num_boltzmann = 0
    with open("fellow_indexes.pickle", "rb") as f:
        fellow_indexes = set(pickle.load(f))
    with open("boltzmann_indexes.pickle", "rb") as f:
        boltzmann_indexes = set(pickle.load(f))
    with open("all_APS.csv","r") as old,\
        open("all_APS_with_fellows.csv", "w+") as new:
        header = old.next()
        new.write(header.strip() + ",fellow,boltzmann\n")
        for line in old:
            old_data = line.strip().split(",")
            gt_index = int(old_data[0])
            if gt_index in fellow_indexes:
                num_fellows += 1
                fellow = "1"
                fellow_indexes.remove(gt_index)
            else:
                fellow = "0"
            if gt_index in boltzmann_indexes:
                num_boltzmann += 1
                boltzmann = "1"
                boltzmann_indexes.remove(gt_index)
            else:
                boltzmann = "0"
            new_data = line.strip() + "," + fellow + "," + boltzmann + "\n"
            new.write(new_data)

    print "Added " + str(num_fellows) + " fellows and " + str(num_boltzmann)+ " boltzmann medal winners to all_APS"

def add_pagerank():
    g = gt.load_graph("/home/mrunelov/KTH/exjobb/SICS-cite/APS/data/APS.graphml")
    pr = gt.pagerank(g,damping=0.5)
    with open("all_APS_with_fellows.csv","r") as old,\
        open("all_APS_with_fellows_and_pagerank.csv", "w+") as new:
        header = old.next()
        new.write(header.strip() + ",pagerank\n")
        for line in old:
            old_data = line.strip().split(",")
            gt_index = int(old_data[0])
            new_data = line.strip() + "," + str(pr.a[gt_index]) + "\n"
            new.write(new_data)

add_pagerank()
