#!/usr/bin/env python
# -*-coding: utf-8-*-

import re
from pprint import pprint
import os
import codecs

os.chdir('/Users/jjc/Documents/ChartEx/initialSets')
vcg = os.listdir('./VCGoodramgate')
root = '/Users/jjc/Documents/ChartEx/initialSets/VCGoodramgate'
VCG = '/Users/jjc/Documents/ChartEx/initialSets/VCG/'
VCP = '/Users/jjc/Documents/ChartEx/initialSets/VCP/'

def OpenTextFile(filename, mode='r', encoding='utf-8', check=False):
    """http://www.velocityreviews.com/forums/t328920-remove-bom-from-string-read-from-utf-8-file.html"""
	hasBOM = False
	if os.path.isfile(filename):
		f = open(filename,'rb')
		header = f.read(4)
		f.close()
		
		# Don't change this to a map, because it is ordered
		encodings = [ ( codecs.BOM_UTF32, 'utf-32' ),
			( codecs.BOM_UTF16, 'utf-16' ),
			( codecs.BOM_UTF8, 'utf-8' ) ]
		
		for h, e in encodings:
			if header.startswith(h):
				encoding = e
				hasBOM = True
				break
		
	f = codecs.open(filename,mode,encoding)
	
	if check and hasBOM:
	    print filename
	
	# Eat the byte order mark
	elif hasBOM:
		f.read(1)
	return f


for f in vcg:
    f_in = OpenTextFile(os.path.join(root, f))
    docid = f.replace('.txt', '')
    txt_in = f_in.read().replace('\t',' ')
    txt_in = re.sub('\r\n', '', txt_in)
    txt_out = open(VCG + f, 'w').write(re.sub('(vicars-choral-\d+)', r'\1\n', txt_in))
    ann_out = open(VCG + docid + '.ann', 'w').write("T1\tDocument 0 17\t" + docid)


## also need chardet: 
## detect encoding:
# >>> for f in os.listdir(root):
# ...     print f
# ...     chardet.detect(open(os.path.join(root, f), 'r').read())
# 
# ## and then fix it:
# open(os.path.join(root, 'vicars-choral-446.txt'), 'r').read().decode('ISO-8859-2').encode('utf-8')


#print codecs.open(os.path.join(root, f), encoding='utf8').read().startswith(u'\ufeff')
#T1	Document 0 17	vicars-choral-402

# >>> filein = ''
# >>> for f in vcg:
# ...     filein += open(os.path.join(root, f), 'r').read()
# ... 


# >>> root="/Users/jjc/Documents/ChartEx/initialSets/Vicars Choral Petergate.rar Folder"
# >>> for f in os.listdir(root):
# ...     chardet.detect(open(os.path.join(root, f), 'r').read())
# ... 
# {'confidence': 1.0, 'encoding': 'ascii'}
# {'confidence': 1.0, 'encoding': 'ascii'}
# {'confidence': 1.0, 'encoding': 'ascii'}
# {'confidence': 0.7520431316470925, 'encoding': 'ISO-8859-2'}
# {'confidence': 1.0, 'encoding': 'ascii'}
# {'confidence': 1.0, 'encoding': 'ascii'}
# {'confidence': 1.0, 'encoding': 'ascii'}
# {'confidence': 0.808129640166227, 'encoding': 'ISO-8859-2'}
# {'confidence': 1.0, 'encoding': 'ascii'}
# {'confidence': 1.0, 'encoding': 'ascii'}
# {'confidence': 1.0, 'encoding': 'ascii'}
# {'confidence': 1.0, 'encoding': 'ascii'}
# {'confidence': 1.0, 'encoding': 'ascii'}
# {'confidence': 1.0, 'encoding': 'ascii'}
# {'confidence': 1.0, 'encoding': 'ascii'}
# {'confidence': 1.0, 'encoding': 'UTF-8'}
# {'confidence': 1.0, 'encoding': 'UTF-8'}
# {'confidence': 1.0, 'encoding': 'ascii'}
# {'confidence': 1.0, 'encoding': 'ascii'}

# >>> root
# '/Users/jjc/Documents/ChartEx/initialSets/Vicars Choral Goodramgate.rar Folder'
# >>> for f in os.listdir(root):
# ...     chardet.detect(open(os.path.join(root, f), 'r').read())
# ... 
# {'confidence': 1.0, 'encoding': 'ascii'}
# {'confidence': 1.0, 'encoding': 'UTF-8'}
# {'confidence': 1.0, 'encoding': 'ascii'}
# {'confidence': 1.0, 'encoding': 'ascii'}
# {'confidence': 1.0, 'encoding': 'ascii'}
# {'confidence': 1.0, 'encoding': 'UTF-8'}
# {'confidence': 1.0, 'encoding': 'ascii'}
# {'confidence': 1.0, 'encoding': 'ascii'}
# {'confidence': 1.0, 'encoding': 'ascii'}
# {'confidence': 1.0, 'encoding': 'ascii'}
# {'confidence': 1.0, 'encoding': 'ascii'}
# {'confidence': 1.0, 'encoding': 'ascii'}
# {'confidence': 1.0, 'encoding': 'ascii'}
# {'confidence': 1.0, 'encoding': 'ascii'}
# {'confidence': 1.0, 'encoding': 'UTF-8'}
# {'confidence': 1.0, 'encoding': 'ascii'}
# {'confidence': 1.0, 'encoding': 'ascii'}
# {'confidence': 1.0, 'encoding': 'ascii'}
# {'confidence': 1.0, 'encoding': 'ascii'}
# {'confidence': 1.0, 'encoding': 'ascii'}
# {'confidence': 1.0, 'encoding': 'ascii'}
# {'confidence': 1.0, 'encoding': 'ascii'}
# {'confidence': 1.0, 'encoding': 'ascii'}
# {'confidence': 1.0, 'encoding': 'ascii'}
# {'confidence': 1.0, 'encoding': 'ascii'}
# {'confidence': 1.0, 'encoding': 'ascii'}
# {'confidence': 1.0, 'encoding': 'UTF-8'}
# {'confidence': 1.0, 'encoding': 'ascii'}
# {'confidence': 1.0, 'encoding': 'ascii'}
# {'confidence': 1.0, 'encoding': 'ascii'}
# {'confidence': 1.0, 'encoding': 'UTF-8'}
# {'confidence': 1.0, 'encoding': 'ascii'}
# {'confidence': 1.0, 'encoding': 'ascii'}
# {'confidence': 1.0, 'encoding': 'ascii'}
# {'confidence': 1.0, 'encoding': 'ascii'}
# {'confidence': 1.0, 'encoding': 'ascii'}
# {'confidence': 1.0, 'encoding': 'ascii'}
# {'confidence': 1.0, 'encoding': 'UTF-8'}
# {'confidence': 1.0, 'encoding': 'ascii'}
# {'confidence': 1.0, 'encoding': 'ascii'}
# {'confidence': 1.0, 'encoding': 'UTF-8'}
# {'confidence': 1.0, 'encoding': 'UTF-8'}
# {'confidence': 1.0, 'encoding': 'ascii'}
# {'confidence': 1.0, 'encoding': 'ascii'}
# {'confidence': 1.0, 'encoding': 'ascii'}
# {'confidence': 1.0, 'encoding': 'ascii'}
# {'confidence': 1.0, 'encoding': 'ascii'}
# {'confidence': 1.0, 'encoding': 'ascii'}
# {'confidence': 1.0, 'encoding': 'ascii'}
# {'confidence': 1.0, 'encoding': 'ascii'}
# {'confidence': 1.0, 'encoding': 'ascii'}
# {'confidence': 1.0, 'encoding': 'ascii'}


###### Production:markup-set ############## Original code ########################################
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
# f = file("/Users/jjc/Documents/ChartEx/initialSets/vicarsChoral/VCI.txt", mode='r')
# 
# records ={}
# m = re.search("\d{1,3}?\.", f.read())
# records = {m.group(0).replace('.','').strip(): ''}
# record = records.keys()[0]
# 
# f.seek(0)
# for line in f.readlines():
#     m = re.match("^\d{1,3}\.", line)
#     if m:
#         docid = m.group(0).replace('.','').strip()
#         record = docid
#         records[record] = line.replace(docid + '. ','')
#     
#     else: records[record] += line
# 
# print len(records)
# for x in records:
#     title = 'vicars-choral-' + x
#     doc = records[x].replace('\n','').replace('################','')
#     
#     txt = file("/Users/jjc/Documents/ChartEx/initialSets/vicarsChoral/VCI/" + title + ".txt", mode='w')
#     
#     txt.write('vicars-choral-' + x + '\n' + doc)


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
