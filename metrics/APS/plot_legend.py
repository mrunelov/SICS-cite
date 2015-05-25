import matplotlib.pyplot as plt
import pylab
        

fig = pylab.figure()
figlegend = pylab.figure(figsize=(10,5))
ax = fig.add_subplot(111)
lines = ax.plot(range(10), pylab.randn(10), range(10), pylab.randn(10),range(1),range(1),range(1),range(1),range(1),range(1),range(1),range(1),range(1),range(1),range(1),range(1))
#for _ in range(8):
    #line = ax.plot([0,0],[1,1])
    #lines.append(line)

leg = figlegend.legend(lines,[r'$\mathrm{Indegree}$', r'$\mathrm{Betweenness}$', r'$\mathrm{Backbone\/ progeny\/ size}$', r'$\mathrm{Logit}$', r'$\sqrt{\mathrm{betweenness}\times\/\mathrm{burstness}}$',r'$\sqrt{\mathrm{betweenness}\times\/\mathrm{burstness}\times\/\mathrm{indegree}}$',r'$\mathrm{PageRank,\/} \alpha=0.5$'], 'center', fontsize=22)

for obj in leg.legendHandles:
    obj.set_linewidth(4.0)

fig.show()
figlegend.show()
figlegend.savefig("legend.png")

#plt.show()


