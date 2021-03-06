import random as r
from itertools import tee,izip

"""
Utility file for creating GraphML files
"""

valid_attr_types = ["boolean", "int", "long", "float", "double", "string"]

def test(directory=""):
	with open(directory + 'test.graphml', 'w+') as f:
		f.write(get_header()) # write xml header
		f.write(get_attr(name="weight", attr_type="int", attr_for="edge",id="d0")) # write attribute definition
		f.write(get_startgraph())
		for i in xrange(10): # write nodes
			f.write(get_node(i))
		for i in xrange(10): # write edges
			f.write(get_edge(i, r.randint(i,9),["d0",1]))
		f.write(get_footer()) # write footer (</graph> and </graphml>)

def get_header():
	return """<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">\n"""

def get_footer():
	return "  </graph>\n" + \
		"</graphml>"

def get_attr(id, name, attr_type, attr_for):
	if attr_for not in ["node", "edge"]:
		raise ValueError("'for' must be either 'node' or 'edge'")
	if attr_type not in valid_attr_types:
		raise ValueError('Invalid attr_type. Must be one of ' + str(valid_attr_types))
	return '  <key attr.name="' + name + '" attr.type="' + attr_type + '" for="' + attr_for + '" id="' + id + '" />\n'

def get_startgraph(directed=True):
	if directed:
		edgedefault = "directed"
	else:
		edgedefault = "undirected"
	return '  <graph id="G" edgedefault="' + edgedefault + '">\n'

def get_node(id, attrs=[]):
	node = '    <node id="n' + str(id) + '">\n'
	#if len(attrs) % 2 == 1:
	#	raise ValueError("Attributes must come in (key,value) pairs")
	for i in range(0,len(attrs),2):
		# OBS: encoding should be done before instead...
		key = attrs[i]
		value = attrs[i+1]
		if key == "authors" or key == "title":
			try:
				key = key.encode('ascii','ignore') #.decode('utf-8')
				#value = value.decode('utf-8')
				value = value.encode('ascii','ignore') #.decode('utf-8')
			except:
				print "Exception caught in gml encode/decode"
				print value
		node += '      <data key="' + key + '">' + value + '</data>\n'
	node += "    </node>\n"
	return node
def get_edge(id, u, v, attrs=[]):
	"""
	id: the edge ID
	u: source node ID
	v: target node ID
	attrs: an even list of key,value pairs of attribute keys and values.
		example: ["d0", 1] where "d0" is a key (id) specified via get_attr
	"""
	edge = '    <edge id="e' + str(id) + '" source="n' + str(u) + '" target="n' + str(v) + '">\n'
	# TODO: check if this works with bools (str(bool) = ?)
	#if len(attrs) % 2 == 1:
	#	raise ValueError("Attributes must come in (key,value) pairs")
	for i in range(0,len(attrs),2):
		key = attrs[i]
		value = attrs[i+1]
		edge += '      <data key="' + key + '">' + str(value) + '</data>\n'
	edge += '    </edge>\n'
	return edge

