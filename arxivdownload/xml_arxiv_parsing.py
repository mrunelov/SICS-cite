# import xml.etree.ElementTree as ET

# arxiv_tag_prefix = "{http://www.w3.org/2005/Atom}"
# xml_dir = "parscit/"
# tree = ET.parse(xml_dir + '0904-2110-extract_citations.xml')
# root = tree.getroot()

# elems = root.iter()
# for e in elems:
#     print e.tag

# entries = root.findall('.//' + arxiv_tag_prefix + 'entry') # XPath
# if len(entries) == 0:
#     print("No entries found")
# else:
#     if len(entries) == 1:
#         id = entries[0].find(arxiv_tag_prefix + 'id')
#         if id is not None:
#             print(id.text)

