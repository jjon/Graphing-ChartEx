#!/usr/bin/python
# -*- coding: utf-8 -*-

## replaced full stops with bullets. checked char length and file encoding
## revised Jun.5 to include Transaction entity on first line.

from lxml import etree
from pprint import pprint
import re
import json

filepath = "/Users/jjc/Documents/ChartEx/initialSets/BorthwickEADdocs/markup-set/"

#### get ids out of steffania's cut and pasted text
f = open("/Users/jjc/Desktop/50 Charters Borthwick Yarbourgh Muniment.txt", mode='r')
charts = f.read()

m = re.findall('\n\n[A-Z]+\/[A-Z]+\/[A-Z]+\/\d+\n', charts)
ids = [x.replace('\n', '') for x in m]


#### dig out text and MD from the xml

xml = open("/Users/jjc/Documents/ChartEx/initialSets/BorthwickEADdocs/193-ym_2-2.sgm.xml", mode='r')
root = etree.parse(xml)

# NB: did elements vary, not all have <unittitle label="Title" and some elements can have children.
# <c level="file"> looks like this:
#   <c level="file">
#     <did>
#       <unitid label="Reference Code" encodinganalog="311" countrycode="GB" repositorycode="193">YM/D/KIRK/2</unitid>
#       <unittitle label="Title" encodinganalog="312">Feoffment</unittitle>
#       <unitdate label="Creation Dates" type="inclusive" encodinganalog="3132">22 November 1552</unitdate>
#     </did>
#     <scopecontent encodinganalog="331">
#       <head>Scope and Content</head>
#       <p>Robert Hoppey of Kirksmeaton, yeoman; Edmund, his son.</p>
#       <p>Lands at Kirksmeaton, formerly belonging to Roche abbey, and now in the tenure or occupation of Hoppey.</p>
#       <p>Robert appoints Geoffrey Wright and William Scaill as his attorneys.</p>
#     </scopecontent>
#   </c>

# docs is a list of <c level="file"> elements
# i = the document Reference Code, got w/xpath //unitid
# e = the <c level="file"> ancestor, got with .getparent().getparent()
docs = [x for x in 
    [e.getparent().getparent() for e in 
    [i for i in root.findall('//unitid') if i.text in ids]]]


for doc in docs:
    d = {'text': ' '.join([t.text for t in doc.find('scopecontent').iterchildren('p')])}
    for x in doc.find('did').iterchildren():
        d.update([(x.attrib['label'], x.text)]) # Watch out, it may be that not all have 'label' attr.
    
    docId = d.pop("Reference Code")
    title = d.setdefault('Title','')
    doc = d.pop("text")
    doc = doc.replace('.',u'•').encode('utf-8')
    ann_note = "#1	AnnotatorNotes T1	" + json.dumps(d)
    
    def semicol(ti):
        if len(ti) > 0:
            return '; '
        else:
            return ''
    
    txt = file(filepath + docId.replace('/', '_') + '.txt', mode='w')
    txt.write(docId.encode('utf-8') + semicol(title) + title + '\n' + re.sub('\s+', ' ', doc)) 
    
    ann = file(filepath + docId.replace('/', '_') + '.ann', mode='w')
    
    ## the following if/else could be cleaner, using .join? or smarter use of dict?
    if len(title) > 0:
        ann.write(
            "T1\tDocument 0 " + str(len(docId)) + "\t" + docId + '\n'
            + "T2\tTransaction" + " " + str(len(docId)+2)+ " " + str(len(title)+len(docId)+2) + "\t" + title + '\n'
            + ann_note
        )
    else:
        ann.write(
            "T1\tDocument 0 " + str(len(docId)) + "\t" + docId + '\n' + ann_note) ## add transaction here too
        
## In this selection the following records had no Transaction (title) string:
# YM/D/SN/24    
# YM/D/SN/29    
# YM/D/WOM/3    
# YM/D/WOM/4    
# YM/D/WOM/5    
