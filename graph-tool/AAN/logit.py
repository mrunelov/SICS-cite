import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import statsmodels.api as sm


def logit():
    cols = ["indegree","betweenness","hits","progeny_size","burst_weight"]

    data = pd.read_csv("all_AAN_with_fellows.csv")
    # log all progeny sizes, highly experimental
    #data["progeny_size"] = np.log2(data["progeny_size"])
    #data["progeny_size"] = data["progeny_size"].replace(float("-inf"),0)
   
    #print data.head(n=5)
    #print data["gt_index"]
    data["intercept"] = 1.0
    train_set = data.drop(["fellow","gt_index"],axis=1)
    # print train_set.describe()

    # Plot histograms
    # for col in cols:
    # 	plot_attribute = col #"progeny_size"
    # 	fig,ax = plt.subplots()
    # 	fig.set_facecolor("white")
    # 	ax.set_yscale("log")
    # 	ax.set_axisbelow(True)
    # 	train_set[plot_attribute].hist(ax=ax,bottom=0.1,bins=100,color="#aaddaa", edgecolor='gray')
    # 	# plt.title(plot_attribute)
    # 	plt.xlabel(plot_attribute)
    # 	plt.ylabel("count")
    # 	plt.show()
     
    logit = sm.Logit(data["fellow"],train_set) #data[train_cols])
    result = logit.fit()
    data["fellow_prediction"] = result.predict(train_set)
    print result.summary()

    lp = result.params
    #print "Odds ratios:"
    #print np.exp(result.params)

    return lp


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

if __name__ == "__main__":
    logit()
