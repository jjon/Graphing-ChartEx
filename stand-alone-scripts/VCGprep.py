#!/usr/bin/env python
# -*- coding: utf-8 -*- #
import os
import re
os.chdir('/Users/jjc/Documents/ChartEx/initialSets')
vcg = os.listdir('./VCrevised')

VCG = '/Users/jjc/Documents/ChartEx/initialSets/VCrevised/'



fin = open('VC-revised.txt')

txts = fin.read().split('\n\n')
for t in txts:
    id = re.search('(.*)\n', t).group(1)
    fout = open(VCG + id + '.txt', 'w')
    fout.write(t)
    fout.close()
    print len(id)
    ann_out = open(VCG + id + '.ann', 'w').write("T1\tDocument 0 "+ str(len(id)) + "\t" + id)