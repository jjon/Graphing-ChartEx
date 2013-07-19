#!/usr/bin/env python
# -*-coding: utf-8-*-

import re

f = file("/Users/jjc/Documents/ChartEx/initialSets/vicarsChoral/VicarsChoral.txt", mode='r')

print [line for line in f.readlines() if re.match('^\d{3}\.\s', line)]

## on prepared text VCextract.text, this works :
# f = file("/Users/jjc/Documents/ChartEx/initialSets/vicarsChoral/VCextract.txt", mode='r')
# 
# for line in f:
#     if line.strip().isdigit():
#         txt = file("/Users/jjc/Documents/ChartEx/initialSets/vicarsChoral/markup-set/vicars-choral-" + line.strip() + ".txt", mode='w')
#         title = 'vicars-choral-' + line.strip() + '\n'
#         doc = f.next()
#         txt.write(title.encode('utf-8') + doc.encode('utf-8')) #encoding step not necessary
#         ann = file("/Users/jjc/Documents/ChartEx/initialSets/vicarsChoral/markup-set/vicars-choral-" + line.strip() + ".ann", mode='w')
# 

####################################
# for line in f:
#     m = re.match("^\d{3}\.", line)
#     docid = m.group(0)
#     while docid: yield line
# for line in f:
#     m = re.match("^\d{3}\.", line)
#     if m:
#         print m.group(0)
#         if f.next():
#             print f.next()
#     m = re.match("^\d{3}\.", line)
#     if m:
#         doc = "Vicars Choral Charter no. " + m.group(0) + '\n'
#         print doc
#         fi = file("/Users/jjc/Documents/ChartEx/deeds-docs/markup-set/deeds-" + line.strip() + ".txt", mode='w')
#         title = 'deeds-' + line.strip() + '\n'
#         doc = f.next()
#         fi.write(title.encode('utf-8') + doc.encode('utf-8')) #encoding step not necessary
# deeds set      
