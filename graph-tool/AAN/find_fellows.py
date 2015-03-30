import difflib
# Imports from betwenness.py
import sys
import graph_tool.all as gt
import matplotlib
import pickle
import numpy as np
from sets import Set

def parse_names(fullname, has_firstname=True, reverse=False):
    if fullname.count(",") == 1:
        names = fullname.split(",")
    else:
        names = fullname.split(" ")
    names[-1] = names[-1].strip() # remove newline
    if reverse: # first name is last, put it first
        r_i = len(names) - 1
        while r_i >= 0 and len(names[r_i]) <= 2: # move past e.g. "C." and such
            r_i -= 1
        names = names[r_i:] + names[:r_i]
    for name in names:
        name = name.replace(",","")
    if has_firstname:
        firstname = names[0]
        lastname = " ".join(names[1:])
    else:
        firstname = ""
        lastname = " ".join(names)
    return [firstname,lastname]

def names_to_str(names):
    return " ".join(names)

def parse_fellows():
    fellows = []
    with open("fellows.txt","r") as f:
        for line in f:
            name = parse_names(line)
            fellows.append(name)
    return fellows


fellows = parse_fellows()
def find_fellow(candidate, has_firstname=True, reverse=False, printstuff=True):
    fellow_index = -1
    if not candidate:
        return fellow_index
    name = parse_names(candidate,has_firstname=has_firstname, reverse=reverse)
    #print "Checking fellow: " + str(name)
    best_match = 0.0
    for i,fellow in enumerate(fellows):
        s = sim(fellow[1],name[-1])
        if s >= 0.7: 
            if has_firstname: # check first name if available
                s2 = sim(fellow[0],name[0])
                #print "Checked first names: " + fellow[0] + ", " + name[0] + " with similarity " + str(s2)
                if s2 < 0.7:
                    continue
            if s > best_match:
                fellow_index = i
                best_match = s
            if printstuff:
                print "Found probable match:"
                print names_to_str(fellow) + " MATCHES " + names_to_str(name) 
    return fellow_index 


def sim(a, b):
    #print "COMPARING " + a + " AND " + b
    seq = difflib.SequenceMatcher(a=a.lower(), b=b.lower())
    return seq.ratio()


def find_fellows_in_top_scores(scores, score_name, num_top=20, do_plot=False, printstuff=True):

    g = gt.load_graph("AAN-preprocessed.xml")
    titles = g.vertex_properties["title"]
    authors = g.vertex_properties["authors"]
    #print "Loaded a graph with " + str(g.num_vertices()) + " nodes"

    # TODO: find out if we can pickle betweenness scores with correct indexes
    # and then just load that array of floats
    #betweens = []
    #for b in vp.a:
        #betweens.append(b)

    #with open("vpa.pickle","wb") as f:
        #pickle.dump(betweens,f)

    #with open("top_vp.pickle","wb") as f:
        #pickle.dump(top_vp,f)

    #with open("top_vp.pickle","rb") as f:
        #top_vp = pickle.load(f)

    top_v = scores.argsort()[::-1][:num_top]

    i = 0
    fellow_articles = 0
    fellows = Set(range(32))
    for i,v_i in enumerate(top_v):
        sys.stderr.write("looping node " + str(i+1) + " / " + str(num_top) + "\r")
        sys.stderr.flush()
        v = g.vertex(v_i)
        if printstuff:
            print "##############"
            print "###   " + str(i+1) + "   ###"
            print "##############"
            print titles[v] 
            print authors[v]
            print score_name + ": " + str(scores[v])
        auths = authors[v]
        auths = auths.split(";")
        found_fellow = False
        for a in auths:
            fellow_index = find_fellow(a,reverse=True,printstuff=printstuff)
            if fellow_index is not -1:
                fellow_articles += 1
                if fellow_index in fellows:
                    fellows.remove(fellow_index)
        if len(fellows) == 1: # found all fellows except Tou Ng
            break
        i += 1
        #if i > 10:
            #break
    #print "Fellows remaining: " + str(fellows)
    print "Precision for " + score_name + ": " + str(fellow_articles) + " / " + str(num_top) + " = " + str(float(fellow_articles)/num_top)
    return fellow_articles

    return 

    if do_plot:
        top_nodes = [g.vertex(v) for v in top_v]
        bg = gt.GraphView(g, vfilt=lambda v: v in top_nodes)
        print "Number of nodes after filtering: " + str(bg.num_vertices())

        print "Calculating layout..." 
        pos = gt.fruchterman_reingold_layout(bg,n_iter=10) 
        print "Done calculating layout. Plotting."

        gt.graph_draw(bg, pos=pos, #vertex_fill_color=vpa,
                vertex_size=gt.prop_to_size(in_degs, mi=7, ma=25),
                #edge_pen_width=gt.prop_to_size(ep, mi=0.5, ma=5),
                vcmap=matplotlib.cm.gist_heat,
                output="co-citation_betweenness.pdf") #vorder=vpa, 


num_top = 1000
with open("vpa.pickle","rb") as f:
    vpa = np.asarray(pickle.load(f))
    tp = find_fellows_in_top_scores(vpa,"betweenness",num_top,printstuff=False)

g = gt.load_graph("AAN-preprocessed.xml")
in_degs = g.degree_property_map("in")
tp = find_fellows_in_top_scores(in_degs.a,"indegree",num_top,printstuff=False)

eig, auths, hubs = gt.hits(g)
tp = find_fellows_in_top_scores(auths.a,"HITS",num_top,printstuff=False)



#candidates = ["Kaplan", "Mercer", "Moore", "Tou Ng", "Palmer"]
#for c in candidates:
    #is_fellow(c,has_firstname=False)


