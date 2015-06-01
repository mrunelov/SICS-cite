import difflib
# Imports from betwenness.py
import sys
import graph_tool.all as gt
import matplotlib
import pickle
import numpy as np
from collections import defaultdict
from plotter import plotxy
from datetime import datetime
import matplotlib.pyplot as plt
from random import shuffle

from logit import logit
from split import split_graph,get_first,get_second,get_gt_graphs

"""
This script parses fellows and calculates precision and recall for metric rankings

TODO:
Break up into multiple files. We should separate fellow parsing, metric evaluation, and plotting
Lots of hard-coded things and things that are changed by commenting/uncommenting blocks...
"""



num_top = 500 #527129 #427735 
use_cutoff = False 
# total : 527129
# 1980 filter: 427735
# fellow articles within 1980 filter: 139755

with open("fellow_indexes.pickle", "rb") as f:
    fellow_indexes = set(pickle.load(f))

#prefixes = ["von","di","de","af"]
def parse_names(fullname, has_firstname=True, reverse=False):
    fullname = fullname.rstrip()
    if fullname.count(",") > 0:
        names = fullname.split(",")
        names = [n.strip() for n in names]
    else:
        if fullname.count(" ") == 1:
            names = fullname.split(" ")
        else:
            # put "C." and such in first name, rest in lastname
            tmp_names = fullname.split(" ")
            dot_index = 1
            for name in tmp_names[1:-1]:
                if len(name) == 2 and name[1] == ".":
                    dot_index += 1
                else:
                    break
            names = []
            firstname = " ".join(tmp_names[:dot_index])
            lastname = " ".join(tmp_names[dot_index:])
            names.append(firstname)
            names.append(lastname) 
            #print "Firstname: " + firstname + ", Lastname: " + lastname
    if reverse: # first name is last, put it first
        r_i = len(names) - 1
        while r_i >= 0 and len(names[r_i]) <= 2:
            r_i -= 1
        names = names[r_i:] + names[:r_i][::-1]
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

def parse_fellows(filename="APS-fellows.txt"):
    fellow_map = defaultdict(list) # maps first letter of last name to list of fellows
    fellows = []
    with open(filename,"r") as f:
        for line in f:
            names = parse_names(line,reverse=False) # True for fellows!
            fellow_map[names[-1][0]].append(names)
            fellows.append(names)
    return fellow_map,fellows


fellow_map,fellows = parse_fellows()
def find_fellow(candidate, has_firstname=True, reverse=False, printstuff=True):
    """
    Takes a candidate name and checks all fellows for a match

    """
    FIRSTNAME_THRESHOLD = 0.9 # minimum similarity between firstnames
    fellow_index = -1
    if len(candidate) <= 4:
        return -1
    name = parse_names(candidate,has_firstname=has_firstname, reverse=reverse)
    if name[-1] == "": # No lastname
        return -1
    best_match = 0.96 # Keep high to minimize false positives
    firstchar = name[-1][0]
    if firstchar.isupper():
        to_check = fellow_map[firstchar]
    else:
        to_check = fellows
    for i,fellow in enumerate(to_check):
        # TODO: maybe force check that last char is correct. Spelling errors in the middle is common, and 
        # different last letters often indicate that it's a different person, e.g. "s"-suffixes
        s = sim(fellow[-1],name[-1])
        if s > best_match:
            #if has_firstname: # check first name if available
            if name[0]:
                not_fellow = False
                firstnames = name[0].split(" ") # this logic can be moved to the parsing step, we're doing it back and forth now, not very effective
                fellow_firstnames = fellow[0].split(" ")
                shortest = min(len(firstnames),len(fellow_firstnames))
                for i in range(shortest):
                    if len(firstnames[i]) == 1 or firstnames[i][1] == "." or len(fellow_firstnames[i]) == 1 or fellow_firstnames[i][1] == ".":
                        if fellow_firstnames[i][0].lower() != firstnames[i][0].lower():
                            not_fellow = True
                            break
                    else:
                        s2 = sim(fellow_firstnames[i],firstnames[i])
                        if s2 < FIRSTNAME_THRESHOLD:
                            not_fellow = True
                            break
                if not_fellow:
                    continue
            if s == 1.0:
                if printstuff:
                    print names_to_str(fellow) + " MATCHES " + names_to_str(name) + "  (" + str(s) + ")"
                return i
            fellow_index = i
            best_match = s
            if printstuff:
                print names_to_str(fellow) + " MATCHES " + names_to_str(name) + "  (" + str(s) + ")"
    return fellow_index 

def sim(a, b):
    seq = difflib.SequenceMatcher(a=a.lower(), b=b.lower())
    return seq.ratio()

def find_fellow_indexes(g):
    authors = g.vertex_properties["authors"]
    author_array = []
    for n in g.vertices():
        author_array.append(authors[n])
    #with open("author_array.pickle", "wb") as f:
        #pickle.dump(author_array,f)
        #print "pickled numpy array of authors"
    #with open("author_array.pickle","rb") as f:
        #author_array = pickle.load(f)
    fellow_indexes = []
    idx = 0
    for i,authors in enumerate(author_array):
        auths = authors.split(";")
        print "Looping node " + str(idx+1) + "\r",
        if i%1000 == 0:
            print "-----------------------------------------"
            print "---------- Looping node " + str(i) + " -----------"
            print "-----------------------------------------"
        for a in auths:
            if find_fellow(a) != -1:
                fellow_indexes.append(i)
                break
        idx += 1
    with open("fellow_indexes_first.pickle","w+") as f:
    #with open("boltzmann_indexes.pickle","w+") as f:
        pickle.dump(fellow_indexes,f)
    return fellow_indexes

def find_fellows_in_top_scores(scores, score_name, num_top=20, do_plot=False, printstuff=True,use_first=True,to_use=None):
    global g,dates
    prs = [] # precision and recall every 10 results
    result = []
    dcgs = []
    total = len(fellow_indexes)
    #total = 139755 # manual total within 1980 filter
    cutoff = datetime(1980,1,1)
    print "Total fellow articles: " + str(total)

    if printstuff:
        titles = g.vertex_properties["title"]
        authors = g.vertex_properties["authors"]
        #print "Loaded a graph with " + str(g.num_vertices()) + " nodes"

    top_v = scores.argsort()[::-1]#[:num_top]
    fellows = set(fellow_indexes)
    fellow_articles = 0
    i = 0
    for v_i in top_v:
        if to_use is not None and to_use[v_i]:
            continue
        sys.stderr.write("looping node " + str(i+1) + " / " + str(num_top) + "\r")
        sys.stderr.flush()
        if use_cutoff:
            v = g.vertex(v_i)
            date = datetime.strptime(dates[v],dateformat)
            if date < cutoff:
                continue
        result.append(v_i)
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
            print score_name + ": " + str(scores[v_i])
        i += 1
        if i%10 == 0:
            prs.append([float(fellow_articles)/total,float(fellow_articles)/i])
            #dcg1,dcg2 = dcg_at_k(result,fellow_indexes,i)
            #dcgs.append(dcg2)
        if i == num_top:
            break
        if not fellows:
            print "ALL FELLOW ARTICLES FOUND after " + str(i) + " articles"

    print "\nNum fellow articles within filter: " + str(fellow_articles) + "\n"
    print score_name + ":                                                              \n " +\
            "\tPrecision: " + str(fellow_articles) + " / " + str(num_top) + " = " + str(float(fellow_articles)/num_top) 
    #dcg1,dcg2 = dcg_at_k(result, fellow_indexes,num_top)
    #print "\tDCG1: " + str(dcg1) + ", DCG2: " + str(dcg2)

    return prs # return precisions and recalls for every 10 articles
    #return fellow_articles
    #return dcgs

def dcg_at_k(argsorted, fellows, k):
    """
    Calcualate the discounted cumulative gain given
    an array of each article's score position and the gold standard (fellow list)
    """
    rel = [0]*len(argsorted)
    for i in range(k):
        rel[i] = 1 if argsorted[i] in fellows else 0

    rel = np.asfarray(rel)
    dcg1 = rel[0] + np.sum(rel[1:] / np.log2(np.arange(2, rel.size + 1)))
    # exponential version with more emphasis on higher rankings:
    dcg2 = np.sum(((2**rel)-1) / np.log2(np.arange(2, rel.size + 2)))
    return dcg1,dcg2    

def pr_curves():
    plt.figure().set_facecolor('white')

    lra = logit()

    in_degs_gt = g.degree_property_map("in")
    in_degs = in_degs_gt.a.astype("float")
    in_degs = in_degs/in_degs.max()

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

    with open("Px_list_weighted.pickle","rb") as f:
        pxwa = np.asarray(pickle.load(f)).astype("float")
        pxwa_n = pxwa/pxwa.max()

    plots = [[] for _ in range(8)]
    print "Calculating for num_top = " + str(num_top)
    plots[0] = find_fellows_in_top_scores(in_degs,"indegree",num_top,printstuff=False)
    plots[1] = find_fellows_in_top_scores(ba,"betweenness",num_top,printstuff=False)
    plots[2] = find_fellows_in_top_scores(pxa_n, "progeny size", num_top, printstuff=False)
    plots[3] = find_fellows_in_top_scores(lra,"All with logit coefficients",num_top,printstuff=False)
    plots[4] = find_fellows_in_top_scores(geometric_mean,"sqrt(between*burst)",num_top,printstuff=False)
    geometric_mean *= np.sqrt(in_degs)
    plots[5] = find_fellows_in_top_scores(geometric_mean,"sqrt(between*burst*indegs)",num_top,printstuff=False)
    pr = gt.pagerank(g,damping=0.5)
    plots[6] = find_fellows_in_top_scores(pr.a,"PageRank alpha 0.5",num_top,printstuff=False)
    plots[7] = find_fellows_in_top_scores(pxwa_n,"Weighted progeny size",num_top,printstuff=False)
    
    #print "Plotting..."
    # Precision-Recall
    #for p in plots:
        #plt.plot(*zip(*p),linewidth=2.0)
    #ax = plt.subplot()
    #total_fellow_articles = len(fellow_indexes)
    ##total_fellow_articles = 139755 # manual total within 1980 filter
    #y_random = float(total_fellow_articles) / num_top #527130
    #ax.plot([0.0,1.0],[y_random,y_random],ls="--",c="0.5",linewidth=2.0)
    #leg = plt.legend([r'$\mathrm{Indegree}$', r'$\mathrm{Betweenness}$', r'$\mathrm{Backbone\/ progeny\/ size}$', r'$\mathrm{Logit}$', r'$\sqrt{\mathrm{betweenness}\times\/\mathrm{burstness}}$',r'$\sqrt{\mathrm{betweenness}\times\/\mathrm{burstness}\times\/\mathrm{indegree}}$',r'$\mathrm{PageRank,\/} \alpha=0.5$',r'$\mathrm{Random\/ retrieval}$'], loc='best',fontsize=18)
    #for obj in leg.legendHandles:
        #obj.set_linewidth(4.0)

    #plt.xlabel(r'$\mathrm{Recall}$',fontsize=24)
    #plt.ylabel(r'$\mathrm{Precision}$',fontsize=24)
    #plt.show()

    # Precision @ n
    if num_top <= 1000:
        lss = ["-"]*8
        lss[0] = [":"]
        lss[6] = [":"]
        plt.figure(2)
        plt.title(r"$\mathrm{Precision\/ @\/ X}$")
        #plt.title(r"$\mathrm{DCG\/ @\/ X}$")
        plt.figure().set_facecolor('white')
        plt.xlabel(r'$\mathrm{@}$',fontsize=24)
        plt.ylabel(r'$\mathrm{Precision}$',fontsize=24)
        #plt.ylabel(r'$\mathrm{DCG}$',fontsize=24)
        xs = range(10,num_top+1,10)
        for i,p in enumerate(plots[:-1]):
            ys = [point[1] for point in p]
            #ys = p # for DCGs
            plt.plot(xs,ys,linewidth=2.0,ls=lss[i])
        ys = [point[1] for point in plots[-1]]
        plt.plot(xs,ys,linewidth=2.0,color='r',ls="--")
        ax = plt.subplot()
        if use_cutoff:
            total_fellow_articles = 139755 # manual total within 1980 filter
            y_random = float(total_fellow_articles) / 427735 #527129 # 427735 is for cutoff
        else:
            total_fellow_articles = len(fellow_indexes)
            y_random = float(total_fellow_articles) / 527129
        ax.plot([0.0,num_top],[y_random,y_random],ls="--",c="0.5",linewidth=2.0)
        #leg = plt.legend([r'$\mathrm{Indegree}$', r'$\mathrm{Betweenness}$', r'$\mathrm{Backbone\/ progeny\/ size}$', r'$\mathrm{Logit}$', r'$\sqrt{\mathrm{betweenness}\times\/\mathrm{burstness}}$',r'$\sqrt{\mathrm{betweenness}\times\/\mathrm{burstness}\times\/\mathrm{indegree}}$',r'$\mathrm{PageRank,\/} \alpha=0.5$',r'$\mathrm{Random\/ retrieval}$'], loc='best',fontsize=16)
        leg = plt.legend([r'$\mathrm{Indegree}$', r'$\mathrm{Betweenness}$', r'$\mathrm{Backbone\/ progeny\/ size}$', r'$\mathrm{Logit}$', r'$\sqrt{\mathrm{betweenness}\times\/\mathrm{burstness}}$',r'$\sqrt{\mathrm{betweenness}\times\/\mathrm{burstness}\times\/\mathrm{indegree}}$',r'$\mathrm{PageRank,\/} \alpha=0.5$',r'$\mathrm{Weighted\/ progeny\/ size}$',r'$\mathrm{Random\/ retrieval}$'], loc='best',fontsize=18)
        for obj in leg.legendHandles:
            obj.set_linewidth(4.0)
        plt.show()

def plot_random_metrics(metric):
    """
    Random mean + std plotting for indegree and PageRank
    """
    global g
    plots = []
    for i in range(1,11):
        num = str(i)
        first = get_first(num)
        second = get_second(num)
        g1,g2 = get_gt_graphs(g,first,second)
        if metric == "indeg":
            m1 = g1.degree_property_map("in")
            m2 = g2.degree_property_map("in")
        elif metric == "pagerank":
            m1 = gt.pagerank(g1,damping=0.5)
            m2 = gt.pagerank(g2,damping=0.5)
        ys1 = find_fellows_in_top_scores(m1.a, metric, num_top, printstuff=False) 
        ys1 = [p[1] for p in ys1]
        plots.append(ys1)
        ys2 = find_fellows_in_top_scores(m2.a, metric, num_top, printstuff=False) 
        ys2 = [p[1] for p in ys2]
        plots.append(ys2)

    if metric == "pagerank":
        original = gt.pagerank(g,damping=0.5)
    elif metric == "indeg":
        original = g.degree_property_map("in")
    g_plot = find_fellows_in_top_scores(original.a,metric,num_top,printstuff=False)
    g_plot = [p[1] for p in g_plot]

    plt.figure()
    plt.title(r"$\mathrm{Precision\/ @\/ X}$")
    plt.figure().set_facecolor('white')
    #plt.xlabel(r'$\mathrm{Recall}$',fontsize=24)
    plt.xlabel(r'$\mathrm{@}$',fontsize=24)
    plt.ylabel(r'$\mathrm{Precision}$',fontsize=24)
    xs = range(10,num_top+1,10)
    #for i,p in enumerate(plots):
        #ys = p
        #plt.plot(xs,ys,linewidth=1.0,color='b',ls=":")
    
    if metric == "indeg":
        clr = 'b'
    elif metric == "pagerank":
        clr = 'k'
    plt.plot(xs,g_plot,color=clr,linewidth=4.0)
    plot_mean_std(xs,plots,color=clr,ls=':')
    #leg = plt.legend([r'$\mathrm{\/ progeny\/ size}$', r'$\mathrm{Backbone\/ progeny\/ size}$', r'$\mathrm{Random\/ retrieval}$'],fontsize=18,loc='best')
    ax = plt.subplot()
    if use_cutoff:
        total_fellow_articles = 139755 # manual total within 1980 filter
        y_random = float(total_fellow_articles) / 427735 
    else:
        total_fellow_articles = len(fellow_indexes)
        y_random = float(total_fellow_articles) / 527129
    ax.plot([0.0,num_top],[y_random,y_random],ls="--",c="0.5",linewidth=4.0)
    if metric == "pagerank":
        leg = plt.legend([r'$\mathrm{PageRank,\/} \alpha=0.5$', r'$\mathrm{PageRank\/ random\/ mean,\/} \alpha=0.5$',r'$\mathrm{Random\/ retrieval}$'],fontsize=32,loc='lower right')
    elif metric == "indeg":
        leg = plt.legend([r'$\mathrm{Indegree}$', r'$\mathrm{Indegree\/ random\/ mean}$',r'$\mathrm{Random\/ retrieval}$'],fontsize=32,loc='lower right')
    for obj in leg.legendHandles:
        obj.set_linewidth(4.0)
    plt.show()

def plot_bps():
    """
    Random mean + std plotting for BPS
    """
    global num_top
    global g,dates,fellow_indexes
    #g1,g2 = split_graph(g)

    plots = [] #= [[] for _ in range(4)]

    for i in range(1,11):
        for part in ["first","second"]:
            with open("pickles/Px_list_" + part + str(i) + ".pickle","rb") as f:
                pxa1 = np.asarray(pickle.load(f)).astype("float")
                pxa1 = pxa1/pxa1.max()
            ys = find_fellows_in_top_scores(pxa1, "progeny size first half", num_top, printstuff=False) 
            ys = [p[1] for p in ys]
            plots.append(ys)

    all_pxa = np.array(plots)
    all_means = np.mean(all_pxa,axis=0)
    all_stddev = np.std(all_pxa,axis=0)

    with open("Px_list.pickle","rb") as f:
        pxa = np.asarray(pickle.load(f)).astype("float")
        pxa_n = pxa/pxa.max()

    ys = find_fellows_in_top_scores(pxa_n, "progeny size", num_top, printstuff=False) 
    ys = [p[1] for p in ys]

    plt.figure(2)
    plt.title(r"$\mathrm{Precision\/ @\/ X}$")
    #plt.title(r"$\mathrm{DCG\/ @\/ X}$")
    plt.figure().set_facecolor('white')
    #plt.xlabel(r'$\mathrm{Recall}$',fontsize=24)
    plt.xlabel(r'$\mathrm{@}$',fontsize=24)
    plt.ylabel(r'$\mathrm{Precision}$',fontsize=24)
    xs = range(10,num_top+1,10)
    #linestyles = ["--",":","-"]
    #for i,p in enumerate(plots):
        #ys = p
        #plt.plot(*zip(*p),linewidth=2.0, ls=linestyles[i],color='r')
        #plt.plot(xs,ys,linewidth=1.0,color='r',ls="--")
    #all_means = all_means[:,1]
    #all_stddev = all_stddev[:,1]
    #all_stddev = all_stddev - all_means
    plt.plot(xs,ys,color='r',linewidth=4.0)
    plt.errorbar(xs,all_means,yerr=all_stddev,color='r',linewidth=4.0,elinewidth=1.0,ls=':')
    ax = plt.subplot()
    if use_cutoff: # num within 1980 filter
        total_fellow_articles = 139755 
        y_random = float(total_fellow_articles) / 427735
    else:
        total_fellow_articles = len(fellow_indexes)
        y_random = float(total_fellow_articles) / 527129
    ax.plot([0.0,num_top],[y_random,y_random],ls="--",c="0.5",linewidth=4.0)
    leg = plt.legend([r'$\mathrm{Backbone\/ progeny\/ size}$', r'$\mathrm{Backbone\/ progeny\/ size\/ random\/ mean}$', r'$\mathrm{Random\/ retrieval}$'],fontsize=32,loc='best')
    for obj in leg.legendHandles:
        obj.set_linewidth(4.0)
    plt.show()


def plot_mean_std(xs,ys_list,color='r',ls='-'):
    ys_array = np.array(ys_list)
    all_means = np.mean(ys_array,axis=0)
    all_stddev = np.std(ys_array,axis=0)
    plt.errorbar(xs,all_means,yerr=all_stddev,color=color,linewidth=2.0,elinewidth=1.0,ls=ls)


if __name__ == "__main__":
    #fi = find_fellow_indexes()
    g = gt.load_graph("APS.graphml")
    dates = g.vertex_properties["date"]
    dateformat = "%Y-%m-%d"
    #pr_curves()
    plot_bps()
    plot_random_metrics("indeg")
    plot_random_metrics("pagerank")