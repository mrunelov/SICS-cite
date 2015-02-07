from arxivdownload import *
import json

# One example with DBLP refs link that links back to arXiv
# http://arxiv.org/abs/1312.2877

# The citations for this one doesn't seem to exist in arXiv. Or bad parsing all the way (some cases of bad parscit parsing was noted).
download_doc("0904.2110")

#download_doc("1309.5256")
#download_doc("1010.0703")

# crawl 3 docs down
#root = "1458082.1458122"
#docs = download(root,3)
#print(json.dumps(docs,indent=4, separators=(',',':')))
#save_docs(docs)
