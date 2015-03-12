import urllib
from xml_parsing import find_article_match

base_url = "http://export.arxiv.org/api/query?search_query="

def query(title, authors):
    query_str = base_url
    title_set = False
    if title is not None:
        query_str += "ti:" + title
        title_set = True
    for author in authors:
        query_str += "+AND+au:" + author
    if not title_set:
        query_str = query_str.replace("query=+AND+","query=")
    query_str += "&max_results=5"
    #print("Query: " + query_str)
    xml_result = urllib.urlopen(query_str).read()
    return xml_result


def find_article_match_from_title_and_authors(data):
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
        original_title = title 
        if title is not None:
            title = entry[0].encode('ascii','ignore')
            if title.endswith(","):
                title = title[:-1] # remove the last character, the comma
                original_title = original_title[:-1]
            title = "%22" + title + "%22" # add quotes to match exact
        authors = [a.encode('ascii','ignore') for a in entry[1]]
        # first name and last name for all authors
        if all(len(author.split()) >= 2 for author in authors):
            # all first names are 1 character
            if all(len(author.split()[0]) == 1 for author in authors):
                authors = [author.split()[-1] for author in authors]

        xml_response = query(title, authors)
        url = find_article_match(original_title,xml_response)
        if url is not None:
            print("FOUND MATCH ------------------------------------------")
            urls.append(url)
        else: 
            # Try different queries. 
            # Querying the entire title without quotes defaults to an OR search. Too many matches.
            if title is not None: # let similarity in find_article_match do its checks. query using authors
                # try with longest word in title + authors
                title = title.replace("%22","")
                longest_title_word = max(title.split(),key=len) 
        #authors = ["%22" + a + "%22" for a in authors] # quote authors. Not needed
                xml_response = query(longest_title_word, authors)
                url = find_article_match(original_title, xml_response)
                if url is not None:
                    print("FOUND MATCH with 1 word from title -------- by: " + authors[0] + " et al.")
                    urls.append(url)
                # else: # try again, authors only:
                #     xml_response = query(None, authors)
                #     url = find_article_match(original_title, xml_response)
                #     if url is not None:
                #         print("FOUND MATCH without title -------- by: " + authors[0] + " et al.")
                #         urls.append(url)
    print("Found " + str(len(urls)) + " / " + str(len(data)))
    return urls  
