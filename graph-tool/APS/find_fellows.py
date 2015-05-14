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
from split import split_graph,get_first,get_second

num_top = 500 #527129 #427735 
# total : 527130
# 1980 filter: 427735
# fellow articles within 1980 filter: 139755 

with open("fellow_indexes.pickle", "rb") as f:
#with open("boltzmann_indexes.pickle", "rb") as f:
    fellow_indexes = set(pickle.load(f))
# TODO: create fellow_indexes lists for the halves
# The below doesn't work for purged vertices, I think. Might need to rerun find_fellows completely on g1 and g2
first = get_first()
first_indexes = set([i for i,e in enumerate(first) if e])
second = get_second()
second_indexes = set([i for i,e in enumerate(second) if e])
first_fellow_indexes = first_indexes.intersection(fellow_indexes)
second_fellow_indexes = second_indexes.intersection(fellow_indexes)
print "len first: " + str(len(first))
print "len second: " + str(len(second))
print "len fellow_indexes: " + str(len(fellow_indexes))
print "len first_fellow_indexes: " + str(len(first_fellow_indexes))
print "len second_fellow_indexes: " + str(len(second_fellow_indexes))


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

def parse_fellows():
    fellow_map = defaultdict(list) # maps first letter of last name to list of fellows
    fellows = []
    with open("APS-fellows.txt","r") as f:
    #with open("boltzmann.txt","r") as f:
        for line in f:
            names = parse_names(line,reverse=False) # True for fellows!
            fellow_map[names[-1][0]].append(names)
            fellows.append(names)
    return fellow_map,fellows


fellow_map,fellows = parse_fellows()
#non_fellows = ["Yuri Feldman", "Jirong Shi", "Ulrich Becker", "Ji Li", "Michel Baranger", "Michael Brunner", "Robert Blinc", "Jian Wang", "Qiang Zhao", "Robert Gomer", "Robert J. Maurer", "Quiang Wang", "Baiwen Li", "Xiaoguang Wang", "George Sterman", "Richard C. Greene", "Michael Unger", "Y. Okimoto"]
def find_fellow(candidate, has_firstname=True, reverse=False, printstuff=True):
    if candidate == "Elisheva Cohen":
        print "---------------------------------Skipping Elisheva"
        return -1
    fellow_index = -1
    if len(candidate) <= 4:
        return -1
    #if candidate in non_fellows:
        #return fellow_index
    name = parse_names(candidate,has_firstname=has_firstname, reverse=reverse)
    if name[-1] == "":
        return -1 
    #print "Checking fellow: " + str(name)
    best_match = 0.96 # should keep high to minimize false positives
    firstchar = name[-1][0]
    if firstchar.isupper():
        to_check = fellow_map[firstchar]
    else:
        #print "Checking author that does not start with a capital letter: " + names_to_str(name)
        to_check = fellows
    for i,fellow in enumerate(to_check):
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


def find_fellow_indexes(g=None):
    #g = gt.load_graph("/home/mrunelov/KTH/exjobb/SICS-cite/APS/data/APS.graphml")
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

# TODO:loop through fellow indexes and sort out some of the incorrect values,mostly chinese. 
# Note: the fellow name is on the left, the matched name from the dataset is on the right.
#Some in the beginning and "Hui Li" vs "Shui Lai", "Hudong Chen" vs "Hung Cheng" and other short names.
# "Jing Shi" vs "Jirong Shi", "Ulrich Eckern" vs "Ulrich Becker", "Jie Liu" vs "Ji Li"

# "Uri Feldman" vs "Yuri Feldman" OBS: Might be same person...  
# "Michael Brunger" vs "Michel Baranger"
# "Michael Brunger" vs "Michael Brunner"
# "Michael Brenner" vs "Michael Brunner"
# "Robert H. Blick" vs "Robert Blinc"
# "Jin Wang" vs "Jian Wang" 
# "Jiang Zhao" vs "Qiang Zhao"
# "Robert H. Romer" vs "Robert Gomer"
# "Robert D. Maurer" vs "Robert J. Maurer"
# "Fuqiang Wang" vs "Quiang Wang"
# "Baowen Li" vs "Baiwen Li"
# "Xiaogang Wang" vs "Xiaoguang Wang"
# "George I. Stegeman" vs "George Sterman"
# "Richard L. Greene" vs "Richard C. Greene"
# "Michael Brunger" vs "Michael Unger"

# Yuko Okamoto" vs "Y. Okimoto"
# "Dongqi Li" vs "Dong li"
# Sarma vs Sharma (couldn't see more)
# "John M. Martinis" vs "J. L. Martins"
# "Hudong Chen" vs "Dong Chen"
# Robert Woodhouse Crompton vs Compton (couldn't see more)
# "James Valles" vs "J. W. F. Valle"
# Piero Martin" vs "P. C. Marin"
# "Mark A. Johnson" vs "M. Jonson"
# "Jack R. Leibowitz" vs "J. L. Lebowitz"
# "Gianfranco Vidali" vs "G. Vidal"
#  "Stephen Martin" vs "S. M. Matin"
# "Jeffrey Reimer" "J. N. Reimers"
# "Paul Heinrich Soding" vs "P. Sding"
# "Kevin F. McCarty" vs "K. T. McCarthy" 
# "Josep John Barrett" vs "J. Barrette"
# "John C. Mather" vs "J. V. Maher"
# "Kwok-Tsang Cheng" vs "K. Cheung"
# "Marcus Muller" vs "M. A. Mueller"
# "Howard Henry Wieman" vs "H. Weman"
# "Davies" vs "Davis"
# "Dana Zachery Anderson" vs "D. R. Andersson"
# "J. Michael Brown" vs "J. C. Browne"
# "Gabriel Lorimer" vs "G. Mller"

# "David Gershoni" vs "David Gershon"
# Kirill Menikov vs Kirill Melnikov
# Jose Luis Martins vs J. Martin
# John Lister vs J.D. Litser
# John Carlstrom vs Johan Carlstrm
# Peter D Zimmerman vs P. H. Zimmerman
# Peter J. Schmid vs P. H. Schmidt
# James M. Matthews vs J. A. D. Matthew
# Robert A. Johnson vs R. L. Johnston
# J. Douglas McDonald J. R. MacDonald
# Edward CHarles Blucher vs E. Bucher
# Dana Zachery Anderson vs D. R. Andersson
# David Attwood vs D. K. Atwood
#...

def find_fellows_in_top_scores(scores, score_name, num_top=20, do_plot=False, printstuff=True,use_first=True,to_use=None):
    global g,dates
    prs = [] # precision and recall every 10 results
    result = []
    dcgs = []
    total = len(fellow_indexes)
    # TODO: create totals for each half graph!
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
            #break

    print "\nNum fellow articles within filter: " + str(fellow_articles) + "\n"
    print score_name + ":                                                              \n " +\
            "\tPrecision: " + str(fellow_articles) + " / " + str(num_top) + " = " + str(float(fellow_articles)/num_top) 
    #dcg2 = dcg_at_k(result, fellow_indexes,num_top)
    #print "\tDCG1: " + str(dcg1) + ", DCG2: " + str(dcg2)
    #print "DCG2: " + str(dcg2)

    #return fellow_articles
    return prs # return precisions and recalls for every 10 articles
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
    lra = logit(traincol="fellow") # or "boltzmann"
    
    geometric_mean = None
    #with open("vpa-between.pickle","rb") as f:
        #geometric_mean = np.asarray(pickle.load(f))
        #geometric_mean /= geometric_mean.max()
        
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

    tp = find_fellows_in_top_scores(lra,"All with logit coefficients",num_top,printstuff=False)
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


    #plots_first = [[] for _ in range(7)]
    #plots_second = [[] for _ in range(7)]
    #print "Calculating for num_top = " + str(num_top)
    #plots_first[0] = find_fellows_in_top_scores(in_degs,"indegree",num_top,printstuff=False,use_first=True)
    #plots_first[1] = find_fellows_in_top_scores(ba,"betweenness",num_top,printstuff=False,use_first=True)
    #plots_first[2] = find_fellows_in_top_scores(pxa_n, "progeny size", num_top, printstuff=False,use_first=True)
    #plots_first[3] = find_fellows_in_top_scores(lra,"All with logit coefficients",num_top,printstuff=False,use_first=True)
    ##plots[4] = find_fellows_in_top_scores(lra1,"SVM",num_top,printstuff=False)
    #plots_first[4] = find_fellows_in_top_scores(geometric_mean,"sqrt(between*burst)",num_top,printstuff=False,use_first=True)
    #geometric_mean *= np.sqrt(in_degs)
    #plots_first[5] = find_fellows_in_top_scores(geometric_mean,"sqrt(between*burst*indegs)",num_top,printstuff=False,use_first=True)
    #pr = gt.pagerank(g,damping=0.5)
    #plots_first[6] = find_fellows_in_top_scores(pr.a,"PageRank alpha 0.5",num_top,printstuff=False,use_first=True)
    
    #plots_second[0] = find_fellows_in_top_scores(in_degs,"indegree",num_top,printstuff=False,use_first=False)
    #plots_second[1] = find_fellows_in_top_scores(ba,"betweenness",num_top,printstuff=False,use_first=False)
    #plots_second[2] = find_fellows_in_top_scores(pxa_n, "progeny size", num_top, printstuff=False,use_first=False)
    #plots_second[3] = find_fellows_in_top_scores(lra,"All with logit coefficients",num_top,printstuff=False,use_first=False)
    ##plots[4] = find_fellows_in_top_scores(lra1,"SVM",num_top,printstuff=False)
    #plots_second[4] = find_fellows_in_top_scores(geometric_mean,"sqrt(between*burst)",num_top,printstuff=False,use_first=False)
    #geometric_mean *= np.sqrt(in_degs)
    #plots_second[5] = find_fellows_in_top_scores(geometric_mean,"sqrt(between*burst*indegs)",num_top,printstuff=False,use_first=False)
    #pr = gt.pagerank(g,damping=0.5)
    #plots_second[6] = find_fellows_in_top_scores(pr.a,"PageRank alpha 0.5",num_top,printstuff=False,use_first=False)

    plots = [[] for _ in range(7)]
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
    
    #print "Plotting..."
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

    if num_top <= 1000:
        plt.figure(2)
        plt.title(r"$\mathrm{Precision\/ @\/ X}$")
        #plt.title(r"$\mathrm{DCG\/ @\/ X}$")
        plt.figure().set_facecolor('white')
        plt.xlabel(r'$\mathrm{@}$',fontsize=24)
        #plt.ylabel(r'$\mathrm{Precision}$',fontsize=24)
        plt.ylabel(r'$\mathrm{DCG}$',fontsize=24)
        xs = range(10,num_top+1,10)
        for p in plots:
            ys = [point[1] for point in p]
            #ys = p # for DCGs
            plt.plot(xs,ys,linewidth=2.0)
        #ax = plt.subplot()
        #ax.plot([0.0,num_top],[y_random,y_random],ls="--",c="0.5",linewidth=2.0)
        #leg = plt.legend([r'$\mathrm{Indegree}$', r'$\mathrm{Betweenness}$', r'$\mathrm{Backbone\/ progeny\/ size}$', r'$\mathrm{Logit}$', r'$\sqrt{\mathrm{betweenness}\times\/\mathrm{burstness}}$',r'$\sqrt{\mathrm{betweenness}\times\/\mathrm{burstness}\times\/\mathrm{indegree}}$',r'$\mathrm{PageRank,\/} \alpha=0.5$',r'$\mathrm{Random\/ retrieval}$'], loc='best',fontsize=16)
        leg = plt.legend([r'$\mathrm{Indegree}$', r'$\mathrm{Betweenness}$', r'$\mathrm{Backbone\/ progeny\/ size}$', r'$\mathrm{Logit}$', r'$\sqrt{\mathrm{betweenness}\times\/\mathrm{burstness}}$',r'$\sqrt{\mathrm{betweenness}\times\/\mathrm{burstness}\times\/\mathrm{indegree}}$',r'$\mathrm{PageRank,\/} \alpha=0.5$'], loc='best',fontsize=18)
        for obj in leg.legendHandles:
            obj.set_linewidth(4.0)
        plt.show()

def plot_bps():
    global num_top
    global g,dates,fellow_indexes
    g1,g2 = split_graph(g)

    in_degs = g.degree_property_map("in").a
    in_degs_first = g1.degree_property_map("in").a
    in_degs_second = g2.degree_property_map("in").a

    #g = gt.load_graph("/home/mrunelov/KTH/exjobb/SICS-cite/APS/data/APS.graphml")
    #dates = g.vertex_properties["date"]
    #dateformat = "%Y-%m-%d"
    plots = [[] for _ in range(3)]
    
    plots[0] = find_fellows_in_top_scores(in_degs_first, "Indegree first half", num_top, printstuff=False,to_use=first)
    plots[1] = find_fellows_in_top_scores(in_degs_second, "Indegree second half", num_top, printstuff=False,to_use=second)
    plots[2] = find_fellows_in_top_scores(in_degs, "Indegree", num_top, printstuff=False)


    #g = g1
    #g.purge_vertices()
    #fellow_indexes = first_fellow_indexes
    #dates = g1.vertex_properties["date"]
    #with open("Px_list_first.pickle","rb") as f:
        #pxa1 = np.asarray(pickle.load(f)).astype("float")
        #pxa1 = pxa1/pxa1.max()
    #plots[0] = find_fellows_in_top_scores(pxa1, "progeny size first half", num_top, printstuff=False,to_use=first)
    
    #g = g2
    #g.purge_vertices()
    #fellow_indexes = second_fellow_indexes
    #dates = g2.vertex_properties["date"]
    #with open("Px_list_second.pickle","rb") as f:
        #pxa2 = np.asarray(pickle.load(f)).astype("float")
        #pxa2 = pxa2/pxa2.max()
    #plots[1] = find_fellows_in_top_scores(pxa2, "progeny size second half", num_top, printstuff=False,to_use=second)

    #with open("Px_list.pickle","rb") as f:
        #pxa = np.asarray(pickle.load(f)).astype("float")
        #pxa = pxa/pxa.max()
    #plots[2] = find_fellows_in_top_scores(pxa, "progeny size", num_top, printstuff=False)


    plt.figure(2)
    plt.title(r"$\mathrm{Precision\/ @\/ X}$")
    #plt.title(r"$\mathrm{DCG\/ @\/ X}$")
    plt.figure().set_facecolor('white')
    #plt.xlabel(r'$\mathrm{Recall}$',fontsize=24)
    plt.xlabel(r'$\mathrm{@}$',fontsize=24)
    plt.ylabel(r'$\mathrm{Precision}$',fontsize=24)
    xs = range(10,num_top+1,10)
    linestyles = ["--",":","-"]
    for i,p in enumerate(plots):
        ys = [point[1] for point in p]
        #plt.plot(*zip(*p),linewidth=2.0, ls=linestyles[i],color='r')
        plt.plot(xs,ys,linewidth=2.0,color='b',ls=linestyles[i])
    ax = plt.subplot()
    total_fellow_articles = len(fellow_indexes)
    #total_fellow_articles = 139755 # manual total within 1980 filter
    y_random = float(total_fellow_articles) / 527129
    ax.plot([0.0,num_top],[y_random,y_random],ls="--",c="0.5",linewidth=2.0)
    leg = plt.legend([r'$\mathrm{Backbone\/ progeny\/ size}$', r'$\mathrm{Backbone\/ progeny\/ size\/ first\/ half}$', r'$\mathrm{Backbone\/ progeny\/ size\/ second\/ half}$', r'$\mathrm{Random\/ retrieval}$'], loc='best', fontsize=18)
    for obj in leg.legendHandles:
        obj.set_linewidth(4.0)
    plt.show()

if __name__ == "__main__":
    #fi = find_fellow_indexes()
    g = gt.load_graph("/home/mrunelov/KTH/exjobb/SICS-cite/APS/data/APS.graphml")
    #indexes = range(527130)
    #shuffle(indexes)
    #first = indexes[:len(indexes)/2]
    #second = indexes[len(indexes)/2:]
    dates = g.vertex_properties["date"]
    dateformat = "%Y-%m-%d"
    #main()
    #pr_curves()
    plot_bps()
    #g1,g2 = split_graph(g)
    #find_fellow_indexes(g1) # throws error on line 128, index out of bounds
