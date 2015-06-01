import matplotlib.pyplot as plt

def plotxy(x,y,xlabel,ylabel):
	print("Plotting...")
	plt.figure().set_facecolor('white')
	
	# plt.subplot(2, 1, 1)
	# plt.subplots_adjust(hspace=0.5)
	# #plt.xlim(12,19)
	# #plt.title('')
	# plt.xlabel('Indegree')
	# plt.ylabel('Pagerank')
	# plt.plot(indegs,prs,'ro')
	
	# plt.subplot(1, 2, 2)
	# #plt.title('')
	# plt.xlabel('Indegree')
	# plt.ylabel('Pagerank with weights')
	# plt.plot(indegs,prs_w,'ro')

	#plt.title('')
	plt.xlabel(xlabel)
	plt.ylabel(ylabel)
	ax = plt.subplot()
	#ax.set_xscale('log')
	#ax.set_yscale('log')
	ax.plot(x, y, 'go', alpha=0.3)
	#ax.plot(ax.get_xlim(), ax.get_ylim(), ls="--",alpha=0.5,c='0.3')

	# Plot backbone from 1 node
	# plt.figure(1,figsize=(8,8))
	# todraw = [top_pr[3][0]]
	# for _ in range(2):
	# 	todraw.append(get_backbone_node(G2,todraw[-1]))
	# print todraw
	# SG = G.subgraph(todraw)
	# pos=nx.spring_layout(SG)
	# nx.draw(SG, pos)
	# nx.draw_networkx_labels(SG, pos)

	# plt.axis('off')
	# #plt.savefig("foo.png") # save as png
	
	plt.show() # display
	print("Done.")


def test_errorbar():
    x = [0,1,2,3,4,5]
    y = [3,4,5,6,7,8]
    xerr = [0.05,0.05,0.01,0.1,0.1,0.05]
    yerr = [0.1,0.5,0.2,0.3,0.7,0.1]

    plt.figure()
    #plt.errorbar(x,y,xerr=xerr,yerr=yerr)
    plt.errorbar(x,y,yerr=yerr)
    plt.show()

    
#test_errorbar()
