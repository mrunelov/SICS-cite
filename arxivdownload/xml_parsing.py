import xml.etree.ElementTree as ET
import difflib # SequenceMatcher used for string similarity measure


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


def find_article_match(title, xml, similarity_threshold=0.9):
    """
    Extracts arXiv article urls from arXiv atom XML responses
    """
    tag_prefix = "{http://www.w3.org/2005/Atom}" # namespace issue
    tree = ET.ElementTree(ET.fromstring(xml))
    root = tree.getroot()
    entries = root.findall('.//' + tag_prefix + 'entry')
    if len(entries) > 1:
        if title is not None:
            best_entry = None
            best_entry_similarity = -1
            for i,entry in enumerate(entries):
                b = entry.find(tag_prefix + 'title').text
                s = similarity(title, b)
                if s > best_entry_similarity:
                    best_entry_similarity = s
                    best_entry = entry
                    if s > 0.9:
                        break
                s = similarity(title[:len(min(title,b))], b[:len(min(title,b))]) # cut off at min length of the two. avoids problem of subtitles
                if s > best_entry_similarity:
                    best_entry_similarity = s
                    best_entry = entry
                    if s > 0.9:
                        break
            if best_entry is not None and best_entry_similarity > similarity_threshold:    
                return best_entry.find(tag_prefix + 'id').text
        return None
        #return entries[len(entries)-1].find(tag_prefix + 'id').text
    elif len(entries) == 0:
        #print("No article found in XML. Returning.")
        return None
    else: # len == 1, assume it's a good match.
        #print("Found an article!")
        return entries[0].find(tag_prefix + 'id').text
    return None # unreachable
    
def similarity(seq1, seq2):
    # print("Comparing:")
    # print(seq1)
    # print(seq2)
    # print("Similarity: " + str(difflib.SequenceMatcher(a=seq1.lower(), b=seq2.lower()).ratio()))
    return difflib.SequenceMatcher(a=seq1.lower(), b=seq2.lower()).ratio()
