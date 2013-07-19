#!/usr/bin/env python
# -*-coding: utf-8-*-

import re


f = file("/Users/jjc/Documents/ChartEx/initialSets/deeds-docs/InitialMarkupSetDEEDS2.txt", mode='r')

for line in f:
    m = re.match("^(\d+)\s(\d+(/\d+)?)\s(.*)", line)
    if m:
        md = (m.group(1), m.group(2), m.group(4))
        title = 'deeds-' + md[0] + '\n'
        doc = f.next().replace('.',u'•')
        if u'•' in doc: print title
        txt = file("/Users/jjc/Documents/ChartEx/initialSets/deeds-docs/markup-set2/deeds-" + md[0] + ".txt", mode='w')
        ann = file("/Users/jjc/Documents/ChartEx/initialSets/deeds-docs/markup-set2/deeds-" + md[0] + ".ann", mode='w')
        txt.write(title.encode('utf-8') + doc.encode('utf-8'))
        ann_note = "#1	AnnotatorNotes T1	{'editorial date':'" + md[1] + "', 'transaction type': '" + md[2] + "'}"
        ann.write("T1\tDocument 0 " + str(len(title)-1) + "\t" + title + ann_note)

# for line in f:
#     if line.strip().isdigit():
#         txt = file("/Users/jjc/Documents/ChartEx/initialSets/vicarsChoral/markup-set/vicars-choral-" + line.strip() + ".txt", mode='w')
#         title = 'vicars-choral-' + line.strip() + '\n'
#         doc = f.next()
#         txt.write(title.encode('utf-8') + doc.encode('utf-8')) #encoding step not necessary
#         ann = file("/Users/jjc/Documents/ChartEx/initialSets/vicarsChoral/markup-set/vicars-choral-" + line.strip() + ".ann", mode='w')
