import xml.etree.ElementTree as ET


def extract_title_authors(filename):
    """
    Extracts title and authors from a Parscit XML file
    """
    tree = ET.parse(filename)
    root = tree.getroot()
    citationList = root.find('.//citationList') # XPath
    citations = citationList.findall('citation')
    
    data = []

    for citation in citations:
        #if citation.attrib['valid']:
        title = citation.find('title')
        #if title_elem is not None:
        authors = citation.findall('.//author')
        a_texts = [author.text for author in authors if len(author.text) > 3]
        if a_texts: # if any authors were identified, add to result
            if title is not None:
                data.append([title.text,a_texts])
            else:
                data.append([None,a_texts])
    return data


def get_article_url(xml):
    """
    Extracts arXiv article urls from arXiv atom XML responses
    """
    tag_prefix = "{http://www.w3.org/2005/Atom}" # namespace issue
    tree = ET.ElementTree(ET.fromstring(xml))
    root = tree.getroot()
    entries = root.findall('.//' + tag_prefix + 'entry')
    if len(entries) > 1:
        print("More than one article in XML. Choosing last.")
        return entries[len(entries)-1].find(tag_prefix + 'id').text
    elif len(entries) == 0:
        print("No article found in XML. Returning.")
        return None
    else: # len == 1
        print("Found an article!")
        return entries[0].find(tag_prefix + 'id').text
    return None # unreachable
    
