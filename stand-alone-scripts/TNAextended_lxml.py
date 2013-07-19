#!/usr/bin/python
#-*- coding: utf-8 -*-

########################
## MSword.doc 2 brat docs
## Structured data in a word processing document in two column table
## 1. open .doc in NeoOffice
## 2. save as docbook xml file
## 3. use etree to extract row elements (.//tgroup[@cols="2"]/tbody/row) elements
## 4. read them into a python dictionary
## 5. write out to .txt and .ann files for brat
## because we're processing the row elements in document order 
## we can sequentially add document id dictionary keys and then 
## populate them with data dictionaries even though the dict doesn't store them in any order
########################foo

import re
from lxml import etree
import json

tree = etree.parse('/Users/jjc/Documents/ChartEx/initialSets/WARD2/TNAextended_docbook.xml')
root = tree.getroot()
textpath = "/Users/jjc/Documents/ChartEx/initialSets/WARD2/WARD2extended/"

d = {}
rows = [x for x in root.xpath('.//tgroup[@cols="2"]/tbody/row', namespaces=root.nsmap)]
for row in rows:
    k,v = row.findall('entry') # in 2 columns, row always has 2 entries
    x,y = (k.find('para').text.replace(':',''), # keys always have 1 para
        ' '.join([x.text for x in v.findall('para') if x.text is not None])) # values can have multiple paras
    if re.match('WARD.*', y):
        id = y.replace('WARD ', '').replace('/', '_')
        d[id] = {}
    else:
        d[id][x] = y

for docid in d:
    txt = file(textpath + docid + '.txt', mode='w')
    ann = file(textpath + docid + '.ann', mode='w')

    txt.write(docid + '\n' + d[docid].pop('Scopecontent').replace('.',u'•').encode('utf-8'))
    
    ann_note = "#1	AnnotatorNotes T1	" + json.dumps(d[docid])
    ann.write("T1\tDocument 0 " + str(len(docid)) + "\t" + docid + '\n' + ann_note)
