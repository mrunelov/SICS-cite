import random as r
from itertools import tee,izip

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

def get_startgraph():
	return '  <graph id="G" edgedefault="directed">\n'

def get_node(id, attrs=[]):
	node = '    <node id="n' + str(id) + '">\n'
	for key,value in pairwise(attrs):
		node += '      <data key="' + key + '">' + str(value) + '</data>\n'
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
	for key,value in pairwise(attrs):
		edge += '      <data key="' + key + '">' + str(value) + '</data>\n'
	edge += '    </edge>\n'
	return edge

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)

test()