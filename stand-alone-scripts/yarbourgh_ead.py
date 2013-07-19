#!/usr/bin/python
# -*- coding: utf-8 -*-

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
        d.update([(x.attrib['label'], x.text)])
    
    docId = d.pop("Reference Code")
    doc = d.pop("text")
    ann_note = "#1	AnnotatorNotes T1	" + json.dumps(d)
    
    txt = file(filepath + docId.replace('/', '_') + '.txt', mode='w')
    txt.write(docId.encode('utf-8') + '\n' + re.sub('\s+', ' ', doc)) 
    
    ann = file(filepath + docId.replace('/', '_') + '.ann', mode='w')
    ann.write("T1\tDocument 0 " + str(len(docId)) + "\t" + docId + '\n' + ann_note)

