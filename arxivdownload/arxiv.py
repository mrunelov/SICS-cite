import urllib
from xml_parsing import get_article_url

base_url = "http://export.arxiv.org/api/query?search_query="

def query(title, authors):
    query = base_url
    title_set = False
    if title is not None:
        query += "ti:" + title
        title_set = True
    for author in authors:
        query += "+AND+au:" + author
    if not title_set:
        query.replace("query=+AND+","query=")
    #print("Query: " + query)
    xml_result = urllib.urlopen(query).read()
    return xml_result


def get_article_urls_from_title_and_authors(data):
    """
    Takes title + authors and queries arXiv looking for matches.

    Using exact titles is a problem since Parscit often fails to get them 100% correct.
    But, using any other form will often give us too many hits...

    In the sample paper we get 1 more correct hit "...Pare rank..." but 1 more incorrect
    if we remove the quotes from the title. We can't do it in general.
    """
    urls = []
    for entry in data:
        title = entry[0]
        if title is not None:
            title = entry[0].encode('ascii','ignore')
            title = "%22" + title + "%22" # add quotes to match exact
        authors = [a.encode('ascii','ignore') for a in entry[1]]
        xml_response = query(title, authors)
        url = get_article_url(xml_response)
        if url is not None:
            print(title)
            urls.append(url)
        #else: # try again, with quoted authors and without title
            #authors = ["%22" + a + "%22" for a in authors]
            #xml_response = query(None, authors)
    return urls  
