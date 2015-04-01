import graph_tool.all as gt
from find_fellows import *

g = gt.load_graph("AAN-preprocessed.xml")
titles = g.vertex_properties["title"]
authors = g.vertex_properties["authors"]


def get_authors_for_title(title):
    for n in g.vertices():
        if titles[n].strip().replace(",","") == title:
            return authors[n]
    return None



with open("all_AAN.csv","r") as old,\
    open("all_AAN_with_fellows.csv", "w+") as new:
    header = old.next()
    new.write(header.strip() + ",fellow\n")
    for line in old:
        old_data = line.strip().split(",")
        title = old_data[0]

        author_list = get_authors_for_title(title).split(";")
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
            new_data = line.strip() + "," + str(fellow) + "\n"
            new.write(new_data)


