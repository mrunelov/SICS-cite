# SICS-cite

This is a thesis project done at SICS. The overall goal of the project is to implement and evaluate a set of algorithms for citation analysis.


## Directories

* algorithms - Tools and algorithms used on both datasets.
* arxivdownload - an arXiv crawler and parser, slow, not tested much
* boost - Some very basic tests with the C++ `boost` library
* metrics - Parsing and calculations related to metrics and evaluation.

The *algorithms* directory is dependent on the python graph package `NetworkX`
The *metrics* directory uses the python graph package `graph-tool` for all graph processing and `pandas` and `Statsmodels` for statistical analysis.

### Notes
The 'algorithms' directory have been tested on both FreeBSD and Windows 8.
The 'metrics' directory have been tested on Arch Linux 4.0.2-1. The main problem is to get graph-tool up and running, which requires boost.
All OS's are x86-64 architectures.

## Algorithms
Below is a list of algorithms used, along with source/package information:

* **The Backbone algorithm** as described in 'Tracing the Evolution of Physics on the Backbone of Citation Networks' 
by S. Gualdi, C. H. Yeung, Y.-C. Zhang - Found in `algorithms/backbone.py`, implemented with NetworkX.
