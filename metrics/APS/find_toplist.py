import graph_tool.all as gt
import numpy as np
import pickle
from datetime import datetime


g = gt.load_graph("/home/mrunelov/KTH/exjobb/SICS-cite/APS/data/APS.graphml")
titles = g.vertex_properties["title"]
authors = g.vertex_properties["authors"]
dates = g.vertex_properties["date"]
dateformat = "%Y-%m-%d"

with open("fellow_indexes.pickle", "rb") as f:
    fellow_indexes = pickle.load(f)
with open("boltzmann_indexes.pickle", "rb") as f2:
    boltzmann_indexes = pickle.load(f2)

in_degs_gt = g.degree_property_map("in")
in_degs = in_degs_gt.a
#in_degs = in_degs/in_degs.max()

with open("burst_list.pickle", "rb") as f:
    bla = np.asarray(pickle.load(f)).astype("float")
    bla /= bla.max()

with open("vpa-between2.pickle","rb") as f:
    ba = np.asarray(pickle.load(f))
    ba /= ba.max()

geometric_mean = bla
geometric_mean *= ba
geometric_mean = np.sqrt(geometric_mean)

with open("Px_list.pickle","rb") as f:
    pxa = np.asarray(pickle.load(f)).astype("float")
    pxa_n = pxa/pxa.max()

geometric_mean2 = geometric_mean*np.sqrt(in_degs)
    
with open("Px_list.pickle","rb") as f:
    pxa = np.asarray(pickle.load(f)).astype("float")
    pxa_n = pxa/pxa.max()


top_i = in_degs.argsort()[::-1]
#top_burst = bla.argsort()[::-1]
top_between = ba.argsort()[::-1]
top_g = geometric_mean.argsort()[::-1]
top_g2 = geometric_mean2.argsort()[::-1]
top_px = pxa_n.argsort()[::-1]

print "writing csv file"
#with open("results/sqrt_all_3_toplist.csv", "w+") as f:
with open("results/progeny.csv", "w+") as csv:
    csv.write("gt_index,rank,title,authors,date,indegree,indegree_rank,g_rank,g2_rank,boltzmann,fellow\n")
    i = 0
    count = 0
    cutoff = datetime(1800,1,1)
    while count < 20:
    #for v_i in top_g2[:20]:
        #v_i = top_g[i]
        v_i = top_px[i]
        v = g.vertex(v_i)
        date = datetime.strptime(dates[v],dateformat)
        i += 1
        if date < cutoff:
            continue
        count += 1
        title = titles[v]
        auths = authors[v]
        indeg = in_degs[v]
        if v_i in fellow_indexes:
            f = "Yes"
        else:
            f = "No"
        if v_i in boltzmann_indexes:
            b = "Yes"
        else:
            b = "No"
        #px_rank = np.where(top_px==v_i)[0][0] 
        g_rank = np.where(top_g==v_i)[0][0]
        g2_rank = np.where(top_g2==v_i)[0][0]
        indeg_rank = np.where(top_i==v_i)[0][0]
        line = str(v_i) + "," + str(i) + "," + title + "," + auths + "," + dates[v] + "," + str(indeg) + "," + str(indeg_rank) + "," + str(g_rank) + "," + str(g2_rank) + "," + b + "," + f + "\n"
        csv.write(line)
