#!/usr/bin/env python
# -*-coding: utf-8-*-

import re
from pprint import pprint

###### Production:markup-set
# f = file("/Users/jjc/Documents/ChartEx/initialSets/vicarsChoral/VicarsChoralI.txt", mode='r')
# 
# records ={}
# m = re.search("\d{3}\. ", f.read())
# records = {m.group(0).replace('.','').strip(): ''}
# record = records.keys()[0]
# 
# f.seek(0)
# for line in f.readlines():
#     m = re.match("^\d{3}\.", line)
#     if m:
#         docid = m.group(0).replace('.','').strip()
#         record = docid
#         records[record] = line.replace(docid + '. ','')
#     
#     else: records[record] += line
# 
# for x in records:
#     title = 'vicars-choral-' + x
#     doc = records[x].replace('.','•').replace('\n','')
#     
#     txt = file("/Users/jjc/Documents/ChartEx/initialSets/vicarsChoral/tmp/" + title + ".txt", mode='w')
#     ann = file("/Users/jjc/Documents/ChartEx/initialSets/vicarsChoral/tmp/" + title + ".ann", mode='w')
#     
#     txt.write('vicars-choral-' + x + '\n' + doc)
#     ann.write("T1\tDocument 0 " + str(len(title)) + "\t" + title)

####### working on the full pdf text dump
f = file("/Users/jjc/Documents/ChartEx/initialSets/vicarsChoral/VCI.txt", mode='r')

records ={}
m = re.search("\d{1,3}?\.", f.read())
records = {m.group(0).replace('.','').strip(): ''}
record = records.keys()[0]

f.seek(0)
for line in f.readlines():
    m = re.match("^\d{1,3}\.", line)
    if m:
        docid = m.group(0).replace('.','').strip()
        record = docid
        records[record] = line.replace(docid + '. ','')
    
    else: records[record] += line

print len(records)
for x in records:
    title = 'vicars-choral-' + x
    doc = records[x].replace('\n','').replace('################','')
    
    txt = file("/Users/jjc/Documents/ChartEx/initialSets/vicarsChoral/VCI/" + title + ".txt", mode='w')
    
    txt.write('vicars-choral-' + x + '\n' + doc)


# count = 1
# for n in rubrics:
#     if n != count + 1:
#         print n
#     count += 1

#rubrics = set([x.replace(':','') for x in re.findall('[A-Z]{2,}:', text)])
#print text
## old:
# f = file("/Users/jjc/Documents/ChartEx/initialSets/vicarsChoral/VicarsChoral.txt", mode='r')
# 
# ## print [line for line in f.readlines() if re.match('^\d{3}\.\s', line)]
# 
# ## on prepared text VCextract.text, this works :
# f = file("/Users/jjc/Documents/ChartEx/initialSets/vicarsChoral/VCextract.txt", mode='r')
# 
# for line in f:
#     if line.strip().isdigit():
#         txt = file("/Users/jjc/Documents/ChartEx/initialSets/vicarsChoral/markup-set/vicars-choral-" + line.strip() + ".txt", mode='w')
#         title = 'vicars-choral-' + line.strip() + '\n'
#         doc = f.next()
#         txt.write(title.encode('utf-8') + doc.replace('.',u'•').encode('utf-8')) #encoding step not necessary
#         ann = file("/Users/jjc/Documents/ChartEx/initialSets/vicarsChoral/markup-set/vicars-choral-" + line.strip() + ".ann", mode='w')
# 
#         ann.write("T1\tDocument 0 " + str(len(title)-1) + "\t" + title)
