import graph_tool.all as gt
from find_fellows import *
import pickle

def get_authors_for_title(title):
    for n in g.vertices():
        if titles[n].strip().replace(",","") == title:
            return authors[n]
    return None


num_fellows = 0
with open("fellow_indexes.pickle", "rb") as f:
    fellow_indexes = set(pickle.load(f))
with open("all_APS.csv","r") as old,\
    open("all_APS_with_fellows.csv", "w+") as new:
    header = old.next()
    new.write(header.strip() + ",fellow\n")
    for line in old:
        old_data = line.strip().split(",")
        gt_index = int(old_data[0])
        if gt_index in fellow_indexes:
            num_fellows += 1
            fellow = "1"
            fellow_indexes.remove(gt_index)
        else:
            fellow = "0"
        new_data = line.strip() + "," + str(fellow) + "\n"
        new.write(new_data)

print "Added " + str(num_fellows) + " fellows to all_APS"
