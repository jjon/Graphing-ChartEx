#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib, sys, json, os, re, BeautifulSoup
from BeautifulSoup import BeautifulStoneSoup

def get_page(url):
    """Fetches an arbitrary page from the web and prints it."""
    try:
        location = urllib.urlopen(url)
    except IOError, (errno, strerror):
        sys.exit("I/O error(%s): %s" % (errno, strerror))
    content = location.read()

    # Clear out all troublesome whitespace
    content = content.replace("\n", "")
    content = content.replace("\r", "")
    content = content.replace("\t", "")
    content = content.replace("> ", ">")
    content = content.replace("  ", " ")

    location.close()
    return content

# print get_page('http://neolography.com')

def generate_tree(page):
    """Converts a string of HTML into a document tree."""
    return BeautifulSoup.BeautifulSoup(page, convertEntities="html")


def scrape_file(file_path):
    f = open(file_path, mode='r')
    docin = f.read()
    soup = generate_tree(docin)
    f.close()
    
    dortext = ''
    
    ## todo: rationalize these error correction routines:

    if soup.find(attrs={'id' : 'pagtext'}): ## There must be a better way to do this!
        soup.find(attrs={'id' : 'pagtext'}).contents[0].replaceWith("peskyspace")
    
    if soup.find(attrs={'id' : 'dortext'}): ## There must be a better way to do this!
        dortext = soup.find(attrs={'id' : 'dortext'}).text
        soup.find(attrs={'id' : 'dortext'}).contents[0].replaceWith("peskyspace")
        
    if soup.find('span', attrs={'id' : 'correct'}): ## This is ridiculous!
        elist = soup.find('span', attrs={'id' : 'correct'}).contents
        for e in elist: # loop made necessary because of the text nodes: .contents -> [u'{', <i>corr:</i>, u' pago}']
            e.replaceWith("peskyspace")

    
    ## assemble return tuple:
    docid = "cluny-" + soup.find('td', 'typotext').text.replace(' ', '_')
    title = soup.find('div', 'regestbox').text
    text = soup.find('div', 'urkundenbox').text.replace('peskyspace', ' ').replace('.', u'•')
    text = re.sub('\s+', ' ', text).strip()
    
    d = {'title summary' : title, 'dorsal text' : dortext}
    print json.dumps(d)
    return docid, title, dortext, text

# print scrape_file("/Users/jjc/Documents/ChartEx/initialSets/Cluny/scrapedHTML/cluny-1607.html")




###### First Scrape the web pages to local files #####################
# docNos = [60, 67, 68, 69, 82, 84, 93, 94, 100, 189, 190, 275, 441, 469, 489, 548, 664, 777, 884, 1108, 1109, 1150, 1151, 1177, 1192, 1244, 1261, 1283, 1398, 1412, 1413, 1416, 1483, 1591, 1592, 1594, 1600, 1606, 1607, 1614, 1684, 1729, 1730, 1731, 1737, 1738, 1825, 2259, 2262, 2614]

docNos = [101,102,103,104,105,106]

#### the form for the urls:
# http://www.uni-muenster.de/Fruehmittelalter/Projekte/Cluny/CCE/php/view.php?medium=text&urkunde=15920 gets text of 1592
# http://www.uni-muenster.de/Fruehmittelalter/Projekte/Cluny/CCE/php/view.php?medium=text&urkunde=11080 gets 1108
# http://www.uni-muenster.de/Fruehmittelalter/Projekte/Cluny/CCE/php/view.php?medium=text&urkunde=01000 gets 100
## rjust(4, '0') to get left zero padding

###  probably should use get_page() above but, quick and dirty:
###  better to use: params = urllib.urlencode({'spam': 1, 'eggs': 2, 'bacon': 0})
###  and: f = urllib.urlopen("http://www.musi-cal.com/cgi-bin/query", params)
# for docNo in docNos:
#     doc = urllib.urlopen('http://www.uni-muenster.de/Fruehmittelalter/Projekte/Cluny/CCE/php/view.php?medium=text&urkunde='+ str(docNo).rjust(4, '0') +'0')
#     fout = open('/Users/jjc/Documents/ChartEx/initialSets/Cluny/intercodeScraped/cluny-' + str(docNo).rjust(4, '0') + '.html', mode='w')
#     fout.write(doc.read())
#     doc.close()


##### Then Scrape the local html files and write to .txt and .ann files #############
scrapedPages = [os.path.join('/Users/jjc/Documents/ChartEx/initialSets/Cluny/intercodeScraped/', f) for f in os.listdir('/Users/jjc/Documents/ChartEx/initialSets/Cluny/intercodeScraped/')][1:]

for page in scrapedPages:
    docid, title, dortext, text = scrape_file(page)
    txt = file("/Users/jjc/Documents/ChartEx/initialSets/Cluny/intercodeFiles/" + docid + ".txt", mode='w')
    ann = file("/Users/jjc/Documents/ChartEx/initialSets/Cluny/intercodeFiles/" + docid + ".ann", mode='w')
    
    txt.write(docid + '\n' + text)
    ann_note = "\n#1	AnnotatorNotes T1	{'title summary':'" + title + "', 'dorsal text':'" + dortext + "'}" # tabs in the string, not explicit \t
    ann.write("T1\tDocument 0 " + str(len(docid)) + "\t" + docid + ann_note)


