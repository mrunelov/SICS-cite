import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import statsmodels.api as sm
from sklearn.svm import SVC
from sklearn.cross_validation import train_test_split
from sklearn.grid_search import GridSearchCV
from sklearn import cross_validation
from sklearn.cross_validation import cross_val_score

def get_data():
    data = pd.read_csv("all_AAN_with_fellows.csv")
    # log all progeny sizes, highly experimental
    #data["progeny_size"] = np.log2(data["progeny_size"])
    #data["progeny_size"] = data["progeny_size"].replace(float("-inf"),0)
    
    for col in data: # normalize
        if col == "gt_index":
            continue
        data[col] /= data[col].max()

    data["combo"] = data["burst_weight"]*data["betweenness"]
    data["combo2"] = data["burst_weight"]*data["betweenness"]*data["indegree"]
    #data["combo"] = data["progeny_size"]*data["burst_weight"]*data["indegree"]
    #data["combo2"] = data["progeny_size"]*data["burst_weight"]
    #data["combo3"] = data["progeny_size"]*data["progeny_size"]
    #data["comb4"] = data["burst_weight"]*data["burst_weight"]
    #data["combo5"] = data["progeny_size"]*data["betweenness"]
    #data["combo6"] = data["progeny_size"]*data["betweenness"]*data["indegree"]
    #data["combo6"] = data["progeny_size"]*data["betweenness"]*data["indegree"]*data["burst_weight"]
    
    #data["intercept"] = 1.0
    train_set = data.drop(["fellow","gt_index","hits"], axis=1)
    #print train_set.corr()
    train_set = sm.add_constant(train_set)
    
    return train_set, data

def logit(traincol="fellow"):
    #cols = ["indegree","betweenness","hits","progeny_size","burst_weight"]
    data = get_data()

    # Normalize
    for col in data: # normalize values
        if col == "gt_index":
            continue
        data[col] /= data[col].max()
    # log all progeny sizes, highly experimental
    #data["progeny_size"] = np.log2(data["progeny_size"])
    #data["progeny_size"] = data["progeny_size"].replace(float("-inf"),0)
    #data["combo1"] = data["progeny_size"]*data["progeny_size"]
    #data["combo2"] = data["betweenness"]*data["burst_weight"]
    #data["combo3"] = data["betweenness"]*data["burst_weight"]*data["indegree"]

    #data_sorted = data.sort(["fellow"],ascending=False)
    #print data_sorted.head(n=20)

   
    #print data.head(n=5)
    #print data["gt_index"]
    #data["intercept"] = 1.0
    to_drop = ["gt_index","fellow","hits_auth"]
    if traincol == "fellow":
        to_drop.append("boltzmann")
    elif traincol == "boltzmann":
        to_drop.append("fellow")
    train_set = data.drop(to_drop,axis=1)

    #print train_set.corr()
    #print train_set.describe()

    # Plot histograms
    #for col in cols:
        #plot_attribute = col #"progeny_size"
        #fig,ax = plt.subplots()
        #fig.set_facecolor("white")
        #ax.set_yscale("log")
        #ax.set_axisbelow(True)
        #train_set[plot_attribute].hist(ax=ax,bottom=0.1,bins=100,color="#aaddaa", edgecolor='gray')
        #plt.title(plot_attribute)
        #plt.xlabel(plot_attribute)
        #plt.ylabel("count")
        #plt.show()
     
    logit = sm.Logit(data[traincol],train_set) #data[train_cols])
    result = logit.fit()
    data["fellow_prediction"] = result.predict(train_set)
    #print result.summary()

    #lp = result.params
    #print "Odds ratios:"
    #print np.exp(result.params)

    pred = data[["gt_index","fellow_prediction"]]
    pred = pred.sort(["gt_index"])
    return pred["fellow_prediction"].values

    # lp = result.params
    # intercept = -lp["intercept"] / lp["indegree"]
    #slope = -lp["hits"] / lp["indegree"]
    #plt.plot(np.array([0, 10000]), intercept + slope * np.array([0, 1.0]), '-', color = '#461B7E')

    # fig = plt.figure(figsize=(10,8))
    # fig.set_facecolor("white")
    #data["hits"] /= data["hits"].max()
    #data["indegree"] /= data["indegree"].max()
    #data["progeny_size"] /= data["progeny_size"].max()
    # data["betweenness"] /= data["betweenness"].max()
    #plt.plot(data["hits"],data["fellow_prediction"],".",color="b",alpha=.4)
    #plt.plot(data["progeny_size"],data["fellow_prediction"],".",color="r",alpha=.4)
    # plt.plot(data["indegree"],data["fellow_prediction"],".",color="g",alpha=.4)
    # plt.plot(data["betweenness"],data["fellow_prediction"],".",color="y",alpha=.4)
    # plt.show()

def svm():
    X, data = get_data()
    y = data["fellow"]

    #svc_params = {
        #'C': np.logspace(1, 4, 4),
        #'gamma': np.logspace(-4, 0, 5),
    #}
    #gs_svc = GridSearchCV(SVC(), svc_params, cv=3, n_jobs=4)
    #gs_svc.fit(train_set,data["fellow"])
    #print gs_svc.best_params_
    #print gs_svc.best_score_
    # Results: C = 10, gamma = 0.0001

    
    X_train, X_test, y_train, y_test = train_test_split(X, y,test_size=0.25, random_state=1)
    svc = SVC(kernel='linear',C=10,gamma=0.0001)

    #cv = cross_validation.ShuffleSplit(len(X), n_iter=10, test_size=0.2,
            #random_state=0)
    #test_scores = cross_val_score(svc, X, y, cv=cv, n_jobs=4) # n_jobs = 4 if you have a quad-core machine ...
    #print test_scores

    svc.fit(X_train, y_train)
    #svc.fit(X,y)

    data["fellow_prediction"] = svc.predict(X)
    pred = data[["gt_index","fellow_prediction"]]
    pred = pred.sort(["gt_index"])
    return pred["fellow_prediction"].values

if __name__ == "__main__":
    #logit()
    svm()
    #get_data()
