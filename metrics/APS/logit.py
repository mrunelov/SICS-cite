import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import statsmodels.api as sm
from sklearn.svm import SVC
from sklearn.cross_validation import train_test_split
from sklearn.grid_search import GridSearchCV
#from split import get_first,get_second

def get_data():
    #df = pd.read_csv("all_APS_with_fellows.csv")
    df = pd.read_csv("all_APS_with_fellows_and_pagerank.csv")
    #print df.mean()

    # Normalize
    for col in df: # normalize values
        if col == "gt_index":
            continue
        df[col] /= df[col].max()
    # log all progeny sizes, highly experimental
    #data["progeny_size"] = np.log2(data["progeny_size"])
    #data["progeny_size"] = data["progeny_size"].replace(float("-inf"),0)
    #data["combo1"] = data["progeny_size"]*data["progeny_size"]
    df["g"] = df["betweenness"]*df["burst_weight"]
    df["g2"] = df["betweenness"]*df["burst_weight"]*df["indegree"]
    
    for col in ["g","g2"]: # normalize values
        df[col] /= df[col].max()

    #data_sorted = data.sort(["fellow"],ascending=False)
    #print data_sorted.head(n=20)

    # Experiment with evaluating within similar progeny sizes
    #bins = range(0,30000,1000)
    #bins = np.linspace(df.progeny_size.min(), df.progeny_size.max(), 20)
    #ps_bins = df.progeny_size.groupby(pd.cut(df.progeny_size,bins),sort=True)
    
    #print type(ps_bins)
    #print ps_bins.head()
    #print ps_bins.max()
    #print ps_bins.max().dropna()

    #print ps_bins[ps_bins[ps_bins.max().notnull()]]

    #idx = ps_bins.transform(max) == df.progeny_size
    #print df[idx]

    return df 


def logit(traincol="fellow"):
    #cols = ["indegree","betweenness","hits","progeny_size","burst_weight"]
    data = get_data()
   
    #data["intercept"] = 1.0
    to_drop = ["gt_index","fellow","hits_auth"]
    if traincol == "fellow":
        to_drop.append("boltzmann")
    elif traincol == "boltzmann":
        to_drop.append("fellow")
    train_set = data.drop(to_drop,axis=1)

    #print train_set.corr(method='spearman')
    #print train_set.describe()
    #plot_histograms(train_set) 

    logit = sm.Logit(data[traincol],train_set) #data[train_cols])
    result = logit.fit()
    data["fellow_prediction"] = result.predict(train_set)
    print result.summary()

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
    #plt.plot(data["hits"],data["fellow_prediction"],".",color="b",alpha=.4)
    #plt.plot(data["progeny_size"],data["fellow_prediction"],".",color="r",alpha=.4)
    # plt.plot(data["indegree"],data["fellow_prediction"],".",color="g",alpha=.4)
    # plt.plot(data["betweenness"],data["fellow_prediction"],".",color="y",alpha=.4)
    # plt.show()

def svm():
    data = get_data()
    to_drop = ["gt_index","fellow","hits_auth"]
    #if traincol == "fellow":
        #to_drop.append("boltzmann")
    #elif traincol == "boltzmann":
    to_drop.append("fellow")
    train_set = data.drop(to_drop,axis=1)

    svc_params = {
        'C': np.logspace(1, 4, 4),
        'gamma': np.logspace(-4, 0, 5),
    }

    gs_svc = GridSearchCV(SVC(), svc_params, cv=3, n_jobs=4)
    gs_svc.fit(train_set,data["fellow"])
    print gs_svc.best_params_
    print gs_svc.best_score_

    #X_train, X_test, y_train, y_test = train_test_split(train_set, data["fellow"], test_size=0.25, random_state=1)
    #svc.fit(train_set,data["fellow"])
    #print "Fitting SVM to training data"
    #svc = SVC().fit(X_train,y_train)
    #print "Done fitting SVM."
    #train_score = svc.score(X_train,y_train)
    #print train_score
    #test_score = svc.score(X_test,y_test)

def plot_histograms(data):
    for col in data:
        plot_attribute = col 
        fig,ax = plt.subplots()
        fig.set_facecolor("white")
        ax.set_yscale("log")
        ax.set_axisbelow(True)
        train_set[plot_attribute].hist(ax=ax,bottom=0.1,bins=100,color="#aaddaa", edgecolor='gray')
        plt.title(plot_attribute)
        plt.xlabel(plot_attribute)
        plt.ylabel("count")
        plt.show()
     


if __name__ == "__main__":
    logit()
    #svm()
    #get_data()
