# SICS-cite

This is a thesis project done at [SICS](https://www.sics.se/). The overall goal of the project is to implement and evaluate a set of algorithms for citation analysis.


## Directories

* algorithms - Tools and algorithms used. *Note:* Additional library algorithms are used in the *metrics* directory.
* datasets - Parse files for the datasets used. There is no rawdata on GitHub due to space limitations.
* metrics - Parsing, calculation, and evaluation of metrics. Here be dragons.
* arxivdownload - an arXiv crawler and parser, slow, not tested much
* boost - Some very basic tests using the C++ `boost` library

The *algorithms* directory is dependent on the python graph package `NetworkX`
The *metrics* directory uses the python graph package `graph-tool` for all graph processing and `pandas` and `Statsmodels` for statistical analysis.

### Notes
The *algorithms* directory have been tested on both FreeBSD and Windows 8.	
The *metrics* directory have been tested on Arch Linux 4.0.2-1. The main problem is to get graph-tool up and running, which requires boost.
All OS's mentioned are x86-64 versions.

## Algorithms
Below is a list of algorithms used, along with source/package information:

* **The Backbone algorithm** as described in *'Tracing the Evolution of Physics on the Backbone of Citation Networks'*
by S. Gualdi, C. H. Yeung, Y.-C. Zhang - Found in `algorithms/backbone.py`, implemented with NetworkX.
* **Co-citation graph generation** - Found in `algorithms/co_citation.py` (graph-tool) and in `algorithms/graphutils.py` (`#build_co_citation_graph` (NetworkX)).
* **Indegree** and **betweenness** centralities - Done using graph-tool (indegree is a property for all graph-tool graphs)
* **PageRank** and **HITS** - Done using graph-tool in `metrics/` and using NetworkX in the test file `algorithms/pr_avg_age.py`
* **Burstness** - Done separately using the [Sci2](https://sci2.cns.iu.edu/) software. Saved as csv files.
