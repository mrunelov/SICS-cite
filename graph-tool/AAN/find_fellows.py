import difflib
# Imports from betwenness.py
import sys
import graph_tool.all as gt
import matplotlib
import pickle
import numpy as np
from sets import Set
from logit import logit

# There are 1667 / 18158 fellow-articles in total
num_top = 200


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

with open("fellow_indexes.pickle", "rb") as f:
    fellow_indexes = pickle.load(f)

def find_fellows_in_top_scores(scores, score_name, num_top=20, do_plot=False, printstuff=True):
    g = gt.load_graph("AAN.graphml") #"AAN-preprocessed.xml")
    titles = g.vertex_properties["title"]
    authors = g.vertex_properties["authors"]
    #print "Loaded a graph with " + str(g.num_vertices()) + " nodes"

    top_v = scores.argsort()[::-1][:num_top]
    fellows = Set(fellow_indexes)
    fellow_articles = 0
    #fellows = Set(range(32))
    for i,v_i in enumerate(top_v):
        sys.stderr.write("looping node " + str(i+1) + " / " + str(num_top) + "\r")
        sys.stderr.flush()
        v = g.vertex(v_i)
        found_fellow = False
        if v_i in fellows:
            fellow_articles += 1
            fellows.remove(v_i)
            found_fellow = True
        if printstuff:
            print "##############"
            print "###   " + str(i+1) + "   ###"
            print "##############"
            print titles[v] 
            print authors[v]
            if found_fellow:
                print "Has fellow author ---------------------------------------------------"
            else:
                print "No fellow authors"
            print score_name + ": " + str(scores[v])
        auths = authors[v]
        auths = auths.split(";")
        
        if not fellows:
            print "ALL FELLOW ARTICLES FOUND after " + str(i) + " articles"
            break
        #found_fellow = False
        #for a in auths:
            #fellow_index = find_fellow(a,reverse=True,printstuff=printstuff)
            #if fellow_index is not -1:
                #fellow_articles += 1
                #if fellow_index in fellows:
                    #fellows.remove(fellow_index)
        #if len(fellows) == 1: # found all fellows except Tou Ng
            #break
        #if i > 10:
            #break
    #print "Fellows remaining: " + str(fellows)
    print "Precision for " + score_name + ": " + str(fellow_articles) + " / " + str(num_top) + " = " + str(float(fellow_articles)/num_top)
    print "DCG: " + str(dcg_at_k(top_v, fellow_indexes,num_top))

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

def dcg_at_k(argsorted, fellows, k):
    """
    Calcualate the discounted cumulative gain given
    an array of each article's score position and the gold standard (fellow list)
    """

    rel = [0]*len(argsorted)
    for i in range(k):
        fellow = 1 if argsorted[i] in fellows else 0
        rel[i] = fellow

    rel = np.asfarray(rel)
    return rel[0] + np.sum(rel[1:] / np.log2(np.arange(2, rel.size + 1)))
    # TODO: maybe implement exponential version with more emphasis on higher rankings 
    


def main():
    # build score array with logit coefficients
    lp = logit()
    geometric_mean = None
    with open("vpa-between.pickle","rb") as f:
        vpa = np.asarray(pickle.load(f))
        geometric_mean = vpa.copy()
        vpa *= lp["betweenness"]
        
    g = gt.load_graph("AAN.graphml")
    in_degs = g.degree_property_map("in")
    vpa += in_degs.a*lp["indegree"]

    eig, auths, hubs = gt.hits(g)
    vpa += auths.a*lp["hits"]


    # Generate Px and burst pickles with correct graph-tool ordering
    # (need to match csv titles to graph-tool titles)
    # Unfortunately this is O(n^2) since there's not O(1) attribute lookup in graph-tool
    #titles = g.vertex_properties["title"]
    ##Px = g.new_vertex_property("int")
    #bursts = g.new_vertex_property("double")
    #i = 1
    #with open("all_AAN_with_fellows.csv", "r") as csv:
        #for line in csv:
            #print "Checking line " + str(i) + "\r",
            #values = line.split(",")
            #title = values[0]
            ##px = values[5]
            #burst = values[4]
            #for v in g.vertices():
                #if title == titles[v]:
                    ##Px[v] = px
                    #bursts[v] = burst
            #i += 1

    #Px_list = []
    #burst_list = []
    #for px in Px.a:
        #Px_list.append(px)
    #with open("Px_list.pickle","wb") as f:
        #pickle.dump(Px_list,f)
    #print "wrote Px_list to pickle!"

    #for b in bursts.a:
        #burst_list.append(b)
    #with open("burst_list.pickle","wb") as f:
        #pickle.dump(burst_list,f)
    #print "wrote burst_list to pickle!"


    with open("Px_list.pickle","rb") as f:
        pxa = np.asarray(pickle.load(f))
    vpa += pxa*lp["progeny_size"]

    with open("burst_list.pickle","rb") as f:
        ba = np.asarray(pickle.load(f))
    vpa += ba*lp["burst_weight"]
    geometric_mean *= ba
    geometric_mean = np.sqrt(geometric_mean)

    tp = find_fellows_in_top_scores(vpa,"All with logit coefficients",num_top,printstuff=False)

    tp = find_fellows_in_top_scores(pxa, "progeny size", num_top, printstuff=False)

    with open("vpa-between.pickle","rb") as f:
        vpa = np.asarray(pickle.load(f))
        tp = find_fellows_in_top_scores(vpa,"betweenness",num_top,printstuff=False)
    
    with open("vpa-closeness.pickle","rb") as f:
        vpa = np.asarray(pickle.load(f))
        tp = find_fellows_in_top_scores(vpa,"closeness",num_top,printstuff=False)


    g = gt.load_graph("AAN.graphml")
    in_degs = g.degree_property_map("in")
    tp = find_fellows_in_top_scores(in_degs.a,"indegree",num_top,printstuff=False)

    eig, auths, hubs = gt.hits(g)
    tp = find_fellows_in_top_scores(auths.a,"HITS authority",num_top,printstuff=False)

    
    tp = find_fellows_in_top_scores(geometric_mean,"sqrt(between*burst)",num_top,printstuff=False)

if __name__ == "__main__":
    main()

#candidates = ["Kaplan", "Mercer", "Moore", "Tou Ng", "Palmer"]
#for c in candidates:
    #is_fellow(c,has_firstname=False)


