import matplotlib.pyplot as plt

def plotxy(x,y):
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
	plt.xlabel('Indegree')
	plt.ylabel('Backbone progeny size')
	ax = plt.subplot()
	ax.set_xscale('log')
	ax.set_yscale('log')
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
