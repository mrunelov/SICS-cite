import xml.etree.ElementTree as ET
import difflib # SequenceMatcher used for string similarity measure

#
# Utility module that parses xml from the arXiv API, extracting certain fields
#


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
    MIN_LEN_THRESHOLD = 20 # lower bound on title lengths to check
    #print xml
    tag_prefix = "{http://www.w3.org/2005/Atom}" # namespace issue
    arxiv_tag_prefix = "{http://arxiv.org/schemas/atom}"
    tree = ET.ElementTree(ET.fromstring(xml))
    root = tree.getroot()
    entries = root.findall('.//' + tag_prefix + 'entry')
    best_entry = None
    if len(entries) > 1:
        if title is not None:
            best_entry_similarity = -1
            for i,entry in enumerate(entries):
                entry_title = entry.find(tag_prefix + 'title').text
                #if doi is not None:
                    #print doi.text
                s = similarity(title, entry_title)
                if s > best_entry_similarity:
                    best_entry_similarity = s
                    best_entry = entry
                    if s > 0.9:
                        break
                min_len = len(min(title,entry_title))
                if min_len > MIN_LEN_THRESHOLD: # only check titles of sufficient length
                    # cut off at min length of the two. avoids problem of subtitles
                    s = similarity(title[:min_len], entry_title[:min_len]) 
                    if s > best_entry_similarity:
                        best_entry_similarity = s
                        best_entry = entry
                        if s > 0.9:
                            break
            if best_entry_similarity < similarity_threshold:
                best_entry = None
    elif len(entries) == 1: 
        best_entry = entries[0]
    if best_entry is not None:
        entry_id = best_entry.find(tag_prefix + 'id').text
        doi_element = best_entry.find(arxiv_tag_prefix + "doi")
        if doi_element is not None:
            doi = doi_element.text
            with open("data/arxiv_id-doi.txt", "a+") as f:
                f.write(entry_id + "\t" + doi + "\n")
        return entry_id
    return None
    
def similarity(seq1, seq2):
    # print("Comparing:")
    # print(seq1)
    # print(seq2)
    # print("Similarity: " + str(difflib.SequenceMatcher(a=seq1.lower(), b=seq2.lower()).ratio()))
    return difflib.SequenceMatcher(a=seq1.lower(), b=seq2.lower()).ratio()
