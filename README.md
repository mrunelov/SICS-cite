# SICS-cite

This is a thesis project done at SICS. The overall goal of the project is to implement and evaluate a set of algorithms for citation analysis.


## Directories

The root-level dataset directories contain code related to the parsing of the datasets. Due to space limitations the datasets are not present on GitHub.

The only datasets that have been used in the rest of the project is AAN and APS.

An overview of all other top-level directories is presented below:

* algorithms - tools and algorithms used on both datasets
* arxivdownload - an arXiv crawler and parser, slow, not tested much
* boost - Some very basic tests with the C++ `boost` library
* metrics - Parsing and calculations related to metrics and evaluation

The 'algorithms' directory is dependent on the python graph package `NetworkX`
The 'metrics' directory is dependent on the python graph package `graph-tool`

### Notes
All OS's used had x86-64 architectures.
The 'algorithms' directory have been tested on both FreeBSD and Windows 8.
The 'metrics' directory have been tested on Arch Linux 4.0.2-1 
