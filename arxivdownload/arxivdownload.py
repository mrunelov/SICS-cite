from HTMLParser import HTMLParser
import json
import time
import requests
import urllib2
import subprocess
import os.path

from arxiv_api import *
from xml_parsing import extract_title_authors

base_url = "http://arxiv.org/"

def _decode_list(data):
    rv = []
    for item in data:
        if isinstance(item, unicode):
            item = item.encode('utf-8')
        elif isinstance(item, list):
            item = _decode_list(item)
        elif isinstance(item, dict):
            item = _decode_dict(item)
        rv.append(item)
    return rv

def _decode_dict(data):
    rv = {}
    for key, value in data.iteritems():
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        elif isinstance(value, list):
            value = _decode_list(value)
        elif isinstance(value, dict):
            value = _decode_dict(value)
        rv[key] = value
    return rv

def load_docs():
    try:
        with open('docs.json', 'r') as f:
            return json.load(f, object_hook = _decode_dict)
    except:
        return {}

def save_docs(docs):
    with open('docs.json', 'w') as f:
        json.dump(docs, f)

class PageParser(HTMLParser):
    global cookies
    def __init__(self):
        HTMLParser.__init__(self)
        self.doc = {'references':[], 'citedby':[]}
        self.section = None

    def handle_starttag(self, tag, attrs):
        if tag == 'meta':
            d = dict(attrs)
            if 'name' in d and d['name'].startswith('citation_'):
                name = d['name'][9:]
                content = d['content']
                self.doc[name] = content
        elif tag == 'a':
            d = dict(attrs)
            if 'name' in d:
                name = d['name']
                self.section = name if name in ['references', 'citedby'] else None
            if self.section is not None and 'href' in d and d['href'].startswith('citation.cfm?'):
                query = d['href'][13:]
                for p in query.split('&'):
                    a = p.split('=')
                    if a[0] == 'id':
                        self.doc[self.section].append(a[1])


def get_new_pdf_name():
    num = 0
    while(True):
        yield str(num) + ".pdf"
        num += 1
# infinitely generate pdf names
pdf_name_generator = get_new_pdf_name()
            
def download_pdf(article_url):
    uid = get_id_from_url(article_url)
    filename = uid.replace(".", "-") + ".pdf"
    if os.path.isfile(filename): # file exists
        print("File " + filename + " exists. Skipping.")
    else:
        print("Downloading pdf...")
        response = urllib2.urlopen(article_url)
        file = open(filename, 'w')
        file.write(response.read())
        file.close()
        print("Completed")

    return filename

def get_id_from_url(article_url):
    return article_url.split('/')[-1]

def get_pdf_url_from_id(uid):
    return base_url + "pdf/" + uid

def crawl(uid, maxdepth=1):
    article_url = get_pdf_url_from_id(uid)
    download_doc(article_url, 0, maxdepth)

cookies = {}
def download_doc(article_url, depth, maxdepth):
    # Download pdf
    try:
        filename = download_pdf(article_url) # return .pdf name
        filename = pdf_to_text(filename) # returns .txt name
        filename = parscit(filename, "citeExtract", "extract_citations")
        data = extract_title_authors(filename)
        article_urls = get_article_urls_from_title_and_authors(data)
        depth += 1
        if depth < maxdepth:
            for new_url in article_urls:
                download_doc(new_url, depth, maxdepth)
    except urllib2.HTTPError, e:
        if e.code == 404:
            print("404 - No such document page")
        else:
            raise # throw the rest to get more info


    #global cookies
    #url = base_url + "abs/" + str(uid)
    #r = requests.get(url, cookies = cookies, headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.114 Safari/537.36'})
    #cookies.update(r.cookies)
    #parser = PageParser()
    #parser.feed(r.content)
    #return parser.doc

def get_top_ranked(docs, missing):
    r = {uid:0 for uid in missing}
    c = {uid:0 for uid in missing}
    for doc in docs.values():
        for uid in doc['references']:
            if uid in r:
                r[uid] = r[uid] + 1
        for uid in doc['citedby']:
            if uid in c:
                c[uid] = c[uid] + 1
    queue = set()
    queue.add(max(r.items(), key = lambda x: x[1])[0])
    queue.add(max(c.items(), key = lambda x: x[1])[0])
    return queue

def download(orig, num_docs):
    all_docs = load_docs()

    docs = {}
    uids = set([orig])
    queue = set([orig])

    while len(docs) < num_docs:
        if len(queue) == 0:
            missing = uids - set(docs.keys())
            if len(missing) == 0:
                print 'No documents are missing, stopping.'
                exit()
            queue |= get_top_ranked(docs, missing)

        uid = queue.pop()
        if uid in all_docs:
            print '%s: Taking %s from store' % (len(docs) + 1, uid)
            doc = all_docs[uid]
        else:
            print '%s: Downloading %s...' % (len(docs) + 1, uid)
            doc = download_doc(uid)
            all_docs[uid] = doc
            save_docs(all_docs)

        docs[uid] = doc
        doc_uids = set(doc['references']) | set(doc['citedby'])
        uids |= doc_uids

        if uid == orig:
            queue |= doc_uids - set([orig]) # Possibly unnecessary, to guard against paper that references itself.

    return docs

def mostreferenced(docs, orig):
    rank = {uid:0 for uid in docs}

    for doc in docs.values():
        for uid in set(doc['references']):
            if uid in rank:
                rank[uid] = rank[uid] + 1

    rank = sorted(rank.items(), key = lambda x: -x[1])

    for i in range(min(100, len(docs))):
        uid, cnt = rank[i]
        doc = docs[uid]
        print '%3d, %8s, %3d (%3d), %s. %s: %s' % (i + 1, uid, cnt, len(doc['citedby']), doc['date'] if 'date' in doc else '??/??/????', doc['authors'] if 'authors' in doc else '???', doc['title'] if 'title' in doc else '???')

def info(docs, uid):
    doc = docs[uid]
    for (key, value) in doc.items():
        if key not in ['references', 'citedby']:
            print '%s: %s' % (key, value)

def remove_missing_meta():
    docs = load_docs()
    uids = list(docs.keys())
    for uid in uids:
        doc = docs[uid]
        if len(set(doc.keys()) - set(['references', 'citedby'])) == 0:
            del docs[uid]
    save_docs(docs)

def remove_uid(uid):
    docs = load_docs()
    if uid in docs:
        del docs[uid]
    save_docs(docs)

# converts a pdf file in the current dir to text and saves it to texts/
def pdf_to_text(filename):
    output = "texts/" + filename.replace(".pdf", ".txt")
    if os.path.isfile(output):
        print("File " + output + " exists. Skipping.")
    else:
        print("Converting " + filename + " to text...")
        subprocess.call(["pdfbox", "ExtractText", filename, output])
        print("Text saved in texts/")
    return output


def parscit(filename, script, arg):
    cmd = "../../ParsCit/bin/" + script + ".pl" 
    output = "parscit/" + filename.replace(".txt","").replace("texts/", "") + "-" + arg + ".xml"
    if os.path.isfile(output):
        print("File " + output + " exists. Skipping.")
    else:
        print("Running parscit...")
        subprocess.call([cmd, "-m", arg, filename, output])
        print("XML file created. Done.")
    return output


def get_citations():
    """
    Should return a list of dicts with some metadata such as author, title
    """
    return {}

#uid = '2387905'
#documents_to_download = 250
#docs = download(uid, documents_to_download)
#info(docs, uid)
#mostreferenced(docs, uid)
#remove_uid('2611484')
#remove_missing_meta()
