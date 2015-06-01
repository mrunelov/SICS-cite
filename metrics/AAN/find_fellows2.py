import difflib
# Imports from betwenness.py
import sys
import graph_tool.all as gt
import matplotlib
import pickle
import numpy as np
from sets import Set
from logit import logit
from logit2 import svm
from collections import defaultdict
from datetime import datetime
import matplotlib.pyplot as plt
from random import shuffle

num_top = 13589 #18158
# OBS: Remember to change manual total!

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

def parse_fellows():
    fellow_map = defaultdict(list) # maps first letter of last name to list of fellows
    fellows = []
    with open("fellows.txt","r") as f:
    #with open("boltzmann.txt","r") as f:
        for line in f:
            names = parse_names(line,reverse=False) # True for fellows!
            fellow_map[names[-1][0]].append(names)
            fellows.append(names)
    return fellow_map,fellows


fellow_map,fellows = parse_fellows()
#non_fellows = ["Yuri Feldman", "Jirong Shi", "Ulrich Becker", "Ji Li", "Michel Baranger", "Michael Brunner", "Robert Blinc", "Jian Wang", "Qiang Zhao", "Robert Gomer", "Robert J. Maurer", "Quiang Wang", "Baiwen Li", "Xiaoguang Wang", "George Sterman", "Richard C. Greene", "Michael Unger", "Y. Okimoto"]
def find_fellow(candidate, has_firstname=True, reverse=False, printstuff=True):
    fellow_index = -1
    if len(candidate) <= 4:
        return -1
    #if candidate in non_fellows:
        #return fellow_index
    name = parse_names(candidate,has_firstname=has_firstname, reverse=reverse)
    if name[-1] == "":
        return -1 
    #print "Checking fellow: " + str(name)
    best_match = 0.8 # should keep high to minimize false positives
    firstchar = name[-1][0]
    if firstchar.isupper():
        to_check = fellow_map[firstchar]
    else:
        #print "Checking author that does not start with a capital letter: " + names_to_str(name)
        to_check = fellows
    for i,fellow in enumerate(to_check):
        # Special case, short name, fellow.
        if name[0] == "Ng" and name[1] == "Hwee Tou":
            return i
        # TODO: maybe force check that last char is correct. Spelling errors in the middle is common, and 
        # different last letters often indicate that it's a different person, e.g. "s"-suffixes
        s = sim(fellow[1],name[-1])
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
                        if s2 < 0.9:
                            not_fellow = True
                            break
                if not_fellow:
                    continue
                #if len(name[0]) == 1 or name[0][1] == ".": # avoid comparing e.g. "M." to "Martin"
                    #if name[0][0].lower() != fellow[0][0].lower():
                        #continue
                #else:
                    #s2 = sim(fellow[0],name[0])
                    ##print "Checked first names: " + fellow[0] + ", " + name[0] + "(" + names_to_str(name) + ") with similarity " + str(s2) 
                    #if s2 < 0.9: # TOOD: maybe use 0.9 with "M." and such handled above
                        #continue
            if s == 1.0: # if we're kinda sure, return mid-loop
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


def find_fellow_indexes():
    g = gt.load_graph("AAN.graphml")
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
        #print "Looping node " + str(idx+1) + "\r",
        #if i%1000 == 0:
            #print "-----------------------------------------"
            #print "---------- Looping node " + str(i) + " -----------"
            #print "-----------------------------------------"
        for a in auths:
            if find_fellow(a,reverse=True) != -1:
                fellow_indexes.append(i)
                break
        idx += 1
    print "Num fellow articles found: " + str(len(fellow_indexes))
    with open("fellow_indexes3.pickle","w+") as f:
    #with open("boltzmann_indexes.pickle","w+") as f:
        pickle.dump(fellow_indexes,f)
    return fellow_indexes


with open("fellow_indexes3.pickle", "rb") as f:
#with open("boltzmann_indexes.pickle", "rb") as f:
    fellow_indexes = pickle.load(f)

def find_fellows_in_top_scores(scores, score_name, num_top=20, do_plot=False, printstuff=True, use_first=True):
    # oldest date: 1965
    prs = [] # precision and recall every 10 results
    result = []
    dcgs = []
    #total = len(fellow_indexes)
    total = 1197 # manual total within cutoff
    cutoff = datetime(2000,1,1)
    print "Total fellow articles: " + str(total)

    if printstuff:
        titles = g.vertex_properties["title"]
        authors = g.vertex_properties["authors"]
        #print "Loaded a graph with " + str(g.num_vertices()) + " nodes"

    top_v = scores.argsort()[::-1]#[:num_top]
    #if score_name == "indegree":
        #print [scores[x] for x in top_v[:100]]
    fellows = Set(fellow_indexes)
    fellow_articles = 0
    #fellows = Set(range(32))
    i = 0
    for v_i in top_v:
        if True:
        #if (use_first and v_i in first) or (not use_first and v_i in second): 
            sys.stderr.write("looping node " + str(i+1) + " / " + str(num_top) + "\r")
            sys.stderr.flush()
            v = g.vertex(v_i)
            date = datetime.strptime(dates[v],dateformat)
            if date < cutoff:
                continue
            else:
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
            #auths = authors[v]
            #auths = auths.split(";")
            #if score_name == "All with logit coefficients" and scores[v_i] < 0.7:
                #print "logit prob below 0.8 at index " + str(i)
            
                #break
            #found_fellow = False
            #for a in auths:
                #fellow_index = find_fellow(a,reverse=True,printstuff=printstuff)
                #if fellow_index is not -1:
                    #fellow_articles += 1
                    #if fellow_index in fellows:
                        #fellows.remove(fellow_index)
            i += 1
            if i%10 == 0:
                prs.append([float(fellow_articles)/total,float(fellow_articles)/i])
                #dcg2 = dcg_at_k(result,fellow_indexes,i)
                #dcgs.append(dcg2)
            if i == num_top:
                break
            if not fellows:
                print "ALL FELLOW ARTICLES FOUND after " + str(i) + " articles"
                break

    #print "\nNum fellow articles within cutoff: " + str(fellow_articles) + "\n"
    #print "Fellows remaining: " + str(fellows)
    print score_name + ":                                                              \n " +\
            "\tPrecision: " + str(fellow_articles) + " / " + str(num_top) + " = " + str(float(fellow_articles)/num_top)
    #dcg2 = dcg_at_k(top_v, fellow_indexes,num_top)
    # TODO: make dcgs work with date skipping
    #print "\tDCG1: " + str(dcg1) + ", DCG2: " + str(dcg2)
    #print "DCG2: " + str(dcg2)

    #return fellow_articles
    return prs
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
    #dcg1 = rel[0] + np.sum(rel[1:] / np.log2(np.arange(2, rel.size + 1)))
    # Maybe use exponential version with more emphasis on higher rankings:
    dcg2 = np.sum(((2**rel)-1) / np.log2(np.arange(2, rel.size + 2)))
    #return dcg1,dcg2
    return dcg2

    

def main():
    # build score array with logit coefficients
    lra1 = svm() #logit()
    lra2 = logit()
    
    geometric_mean = None
    #with open("vpa-between.pickle","rb") as f:
        #geometric_mean = np.asarray(pickle.load(f))
        #geometric_mean /= geometric_mean.max()
        
    #g = gt.load_graph("APS.graphml")
    #g = gt.load_graph("/home/mrunelov/KTH/exjobb/SICS-cite/APS/data/APS.graphml")
    in_degs_gt = g.degree_property_map("in")
    in_degs = in_degs_gt.a.astype("float")
    in_degs = in_degs/in_degs.max()
    #geometric_mean *= in_degs

    #burst_list = [0]*len(in_degs)
    #with open("all_APS_with_fellows.csv", "r") as f:
        #next(f) # skip header
        #for line in f:
            #values = line.strip().split(",")
            #gt_index = int(values[0])
            #burst_weight = values[4]
            #burst_list[gt_index] = burst_weight
    #with open("burst_list.pickle", "wb") as f:         
        #pickle.dump(burst_list,f)

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

    #geometric_mean *= ba
    #geometric_mean = np.sqrt(geometric_mean)
    #numzero = len(geometric_mean[geometric_mean == 0])
    #print "Number of zero values for geometric mean:" + str(numzero)

    tp = find_fellows_in_top_scores(lra2,"All with logit coefficients",num_top,printstuff=False)
    tp = find_fellows_in_top_scores(lra1,"SVM",num_top,printstuff=False)
    tp = find_fellows_in_top_scores(pxa_n, "progeny size", num_top, printstuff=False)
    tp = find_fellows_in_top_scores(ba,"betweenness",num_top,printstuff=False)
    tp = find_fellows_in_top_scores(geometric_mean,"sqrt(between*burst)",num_top,printstuff=False)
    geometric_mean *= np.sqrt(in_degs)
    tp = find_fellows_in_top_scores(geometric_mean,"sqrt(between*burst*indegs)",num_top,printstuff=False)
    tp = find_fellows_in_top_scores(ba + pxa_n + in_degs,"betweenness + progeny size + cc",num_top,printstuff=False)
    
    #with open("vpa-closeness.pickle","rb") as f:
        #vpa = np.asarray(pickle.load(f))
        #tp = find_fellows_in_top_scores(vpa,"closeness",num_top,printstuff=False)

    tp = find_fellows_in_top_scores(in_degs,"indegree",num_top,printstuff=False)

    pr = gt.pagerank(g,damping=0.5)
    tp = find_fellows_in_top_scores(pr.a,"PageRank alpha 0.5",num_top,printstuff=False)
    #plotxy(pxa,pr.a,"Backbone Progeny Size","PageRank (alpha=0.5)")

    #eig, auths, hubs = gt.hits(g)
    #tp = find_fellows_in_top_scores(auths.a,"HITS authority",num_top,printstuff=False)

    
    #tp = find_fellows_in_top_scores(geometric_mean,"sqrt(between*burst)",num_top,printstuff=False)

def pr_curves():
    plt.figure().set_facecolor('white')

    lra1 = svm()
    lra2 = logit()

    in_degs_gt = g.degree_property_map("in")
    in_degs = in_degs_gt.a.astype("float")
    in_degs = in_degs/in_degs.max()

    with open("burst_list.pickle", "rb") as f:
        bla = np.asarray(pickle.load(f)).astype("float")
        bla /= bla.max()

    with open("vpa-between.pickle","rb") as f:
        ba = np.asarray(pickle.load(f))
        ba /= ba.max()

    geometric_mean = bla
    geometric_mean *= ba
    geometric_mean = np.sqrt(geometric_mean)

    with open("Px_list.pickle","rb") as f:
        pxa = np.asarray(pickle.load(f)).astype("float")
        pxa_n = pxa/pxa.max()


    plots = [[] for _ in range(7)]
    print "Calculating for num_top = " + str(num_top)
    plots[0] = find_fellows_in_top_scores(in_degs,"indegree",num_top,printstuff=False)
    plots[1] = find_fellows_in_top_scores(ba,"betweenness",num_top,printstuff=False)
    plots[2] = find_fellows_in_top_scores(pxa_n, "progeny size", num_top, printstuff=False)
    plots[3] = find_fellows_in_top_scores(lra2,"All with logit coefficients",num_top,printstuff=False)
    plots[4] = find_fellows_in_top_scores(geometric_mean,"sqrt(between*burst)",num_top,printstuff=False)
    geometric_mean *= np.sqrt(in_degs)
    plots[5] = find_fellows_in_top_scores(geometric_mean,"sqrt(between*burst*indegs)",num_top,printstuff=False)
    pr = gt.pagerank(g,damping=0.5)
    plots[6] = find_fellows_in_top_scores(pr.a,"PageRank, alpha=0.5",num_top,printstuff=False)

    
    #plots_first = [[] for _ in range(7)]
    #plots_second = [[] for _ in range(7)]
    #print "Calculating for num_top = " + str(num_top)
    #plots_first[0] = find_fellows_in_top_scores(in_degs,"indegree",num_top,printstuff=False,use_first=True)
    #plots_first[1] = find_fellows_in_top_scores(ba,"betweenness",num_top,printstuff=False,use_first=True)
    #plots_first[2] = find_fellows_in_top_scores(pxa_n, "progeny size", num_top, printstuff=False,use_first=True)
    #plots_first[3] = find_fellows_in_top_scores(lra2,"All with logit coefficients",num_top,printstuff=False,use_first=True)
    ##plots[4] = find_fellows_in_top_scores(lra1,"SVM",num_top,printstuff=False)
    #plots_first[4] = find_fellows_in_top_scores(geometric_mean,"sqrt(between*burst)",num_top,printstuff=False,use_first=True)
    #geometric_mean *= np.sqrt(in_degs)
    #plots_first[5] = find_fellows_in_top_scores(geometric_mean,"sqrt(between*burst*indegs)",num_top,printstuff=False,use_first=True)
    #pr = gt.pagerank(g,damping=0.5)
    #plots_first[6] = find_fellows_in_top_scores(pr.a,"PageRank alpha 0.5",num_top,printstuff=False,use_first=True)
    
    #plots_second[0] = find_fellows_in_top_scores(in_degs,"indegree",num_top,printstuff=False,use_first=False)
    #plots_second[1] = find_fellows_in_top_scores(ba,"betweenness",num_top,printstuff=False,use_first=False)
    #plots_second[2] = find_fellows_in_top_scores(pxa_n, "progeny size", num_top, printstuff=False,use_first=False)
    #plots_second[3] = find_fellows_in_top_scores(lra2,"All with logit coefficients",num_top,printstuff=False,use_first=False)
    ##plots[4] = find_fellows_in_top_scores(lra1,"SVM",num_top,printstuff=False)
    #plots_second[4] = find_fellows_in_top_scores(geometric_mean,"sqrt(between*burst)",num_top,printstuff=False,use_first=False)
    #geometric_mean *= np.sqrt(in_degs)
    #plots_second[5] = find_fellows_in_top_scores(geometric_mean,"sqrt(between*burst*indegs)",num_top,printstuff=False,use_first=False)
    #pr = gt.pagerank(g,damping=0.5)
    #plots_second[6] = find_fellows_in_top_scores(pr.a,"PageRank alpha 0.5",num_top,printstuff=False,use_first=False)
    
    for p in plots:
        plt.plot(*zip(*p),linewidth=2.0)
    #plt.plot([0,0],[1.0,1.0],linestyle="--",c="0.5",linewidth=2.0)
    ax = plt.subplot()
    #total_fellow_articles = len(fellow_indexes)
    total_fellow_articles = 1197 # hard-coded for 2000 cutoff
    y_random = float(total_fellow_articles) / num_top 
    ax.plot([0.0,1.0],[y_random,y_random], ls="--",c="0.5",linewidth=2.0)
    leg = plt.legend([r'$\mathrm{Indegree}$', r'$\mathrm{Betweenness}$', r'$\mathrm{Backbone\/ progeny\/ size}$', r'$\mathrm{Logit}$',r'$\sqrt{\mathrm{betweenness}\times\/\mathrm{burstness}}$',r'$\sqrt{\mathrm{betweenness}\times\/\mathrm{burstness}\times\/\mathrm{indegree}}$',r'$\mathrm{PageRank,\/} \alpha=0.5$',r'$\mathrm{Random\/ retrieval}$'], loc='best',fontsize=18)
    for obj in leg.legendHandles:
        obj.set_linewidth(2.0)
    plt.xlabel(r'$\mathrm{Recall}$',fontsize=24)
    plt.ylabel(r'$\mathrm{Precision}$',fontsize=24)
    plt.show()

    line_width = 2.0
    if num_top <= 1000:
        fig = plt.figure(2)
        plt.title(r"$\mathrm{Precision\/ @\/ X}$")
        plt.figure().set_facecolor('white')
        plt.xlabel(r'$\mathrm{@}$',fontsize=24)
        #plt.ylabel(r'$\mathrm{Precision}$',fontsize=24)
        plt.ylabel(r'$\mathrm{DCG}$',fontsize=24)
        xs = range(10,num_top+1,10)
        for p in plots:
        #plt.subplot(121)
        #for p in plots_first:
            #ys = [point[1] for point in p]
            ys = p # for DCGs
            plt.plot(xs,ys,linewidth=line_width)
        #ax = plt.subplot()
        #y_random = float(len(fellow_indexes)) / 18158
        #ax.plot([0.0,num_top],[y_random,y_random], ls="--",c="0.5",linewidth=2.0)
        #leg = plt.legend([r'$\mathrm{Indegree}$', r'$\mathrm{Betweenness}$', r'$\mathrm{Backbone\/ progeny\/ size}$', r'$\mathrm{Logit}$',r'$\sqrt{\mathrm{betweenness}\times\/\mathrm{burstness}}$',r'$\sqrt{\mathrm{betweenness}\times\/\mathrm{burstness}\times\/\mathrm{indegree}}$',r'$\mathrm{PageRank,\/} \alpha=0.5$',r'$\mathrm{Random\/ retrieval}$'], loc='best',fontsize=18)
        leg = plt.legend([r'$\mathrm{Indegree}$', r'$\mathrm{Betweenness}$', r'$\mathrm{Backbone\/ progeny\/ size}$', r'$\mathrm{Logit}$',r'$\sqrt{\mathrm{betweenness}\times\/\mathrm{burstness}}$',r'$\sqrt{\mathrm{betweenness}\times\/\mathrm{burstness}\times\/\mathrm{indegree}}$',r'$\mathrm{PageRank,\/} \alpha=0.5$'], loc='best',fontsize=18)
        for obj in leg.legendHandles:
            obj.set_linewidth(line_width)
        
        #plt.subplot(122)
        #for p in plots_second:
            #ys = [point[1] for point in p]
            #plt.plot(xs,ys,linewidth=2.0)
            #leg = plt.legend([r'$\mathrm{Indegree}$', r'$\mathrm{Betweenness}$', r'$\mathrm{Backbone\/ progeny\/ size}$', r'$\mathrm{Logit}$',r'$\sqrt{\mathrm{betweenness}\times\/\mathrm{burstness}}$',r'$\sqrt{\mathrm{betweenness}\times\/\mathrm{burstness}\times\/\mathrm{indegree}}$',r'$\mathrm{PageRank,\/} \alpha=0.5$'], loc='best',fontsize=16)
            #for obj in leg.legendHandles:
                #obj.set_linewidth(2.0)
        ##plt.subplots_adjust(wspace=0.1,hspace=0.1)
        #plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    #fi = find_fellow_indexes()
    g = gt.load_graph("AAN.graphml")
    indexes = range(18158)
    shuffle(indexes)
    first = indexes[:len(indexes)/2]
    second = indexes[len(indexes)/2:]
    dates = g.vertex_properties["date"]
    dateformat = "%Y"
    #main()
    pr_curves()

#candidates = ["Kaplan", "Mercer", "Moore", "Tou Ng", "Palmer"]
#for c in candidates:
    #is_fellow(c,has_firstname=False)
