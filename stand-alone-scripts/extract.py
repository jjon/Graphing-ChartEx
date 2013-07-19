#!/usr/bin/python
# -*- coding: utf-8 -*-
import csv
import json
import re

keys = ["piece_ref","item_ref","scope/content","date_text","former_reference_department","note_text","piece_id","cat_level"]

f = open('/Users/jjc/Documents/ChartEx/initialSets/WARD2/WARD2catalog.csv', mode='r')
textpath = "/Users/jjc/Documents/ChartEx/initialSets/WARD2/markup-set/"

ward2 = csv.DictReader(open("/Users/jjc/Documents/ChartEx/initialSets/WARD2/WARD2catalog.csv","rU"), keys)

selected = [x for x in ward2 if "55/188" in x['piece_ref'] or "55A/188" in x['piece_ref'] or "59A/233" in x['piece_ref']]

for x in selected:
    d = {"date_text":x["date_text"],"piece_id":x["piece_id"]}
    
    docId = "Ward2_" + x['piece_ref'].replace('/', '_')
    doc = x["scope/content"].encode('utf-8').strip()
    ann_note = "#1	AnnotatorNotes T1	" + json.dumps(d)
    
    txt = file(textpath + docId + '.txt', mode='w')
    txt.write(docId.encode('utf-8') + '\n' + re.sub('\s+', ' ', doc).replace('.',u'•')) 
    
    ann = file(textpath + docId + '.ann', mode='w')
    ann.write("T1\tDocument 0 " + str(len(docId)) + "\t" + docId + '\n' + ann_note)
