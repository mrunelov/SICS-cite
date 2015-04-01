import pandas as pd
import pylab as plt
import numpy as np
import statsmodels.api as sm

data = pd.read_csv("all_AAN_with_fellows.csv")
#data = pd.Series(np.random.normal(size=2000))

# Plot histogram. Not good with this data, maybe cause it's normalized [0,1]
#fig,ax = plt.subplots()
#data.hist(ax=ax,bottom=0.0000001,bins=100)
#ax.set_yscale("log")
#plt.show()


data["intercept"] = 1.0

train_cols = data.columns[1:-2] # all but title and the target, fellows.
#print train_cols
logit = sm.Logit(data["fellow"],data[train_cols])
result = logit.fit()
print result.summary()
