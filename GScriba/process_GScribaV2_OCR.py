#!/usr/bin/env python
# -*- coding: utf-8 -*- #

# This is how I've proceeded with Giovanni v2. It is my hope that, while this
# will never be a turn-key system for ordering OCR output text files, these
# scripts and regexes can form the nucleus of a method that can be applied to
# the other volumes as well.
# 
# The python file is chronological (sort of): below the "######## OCR..." line
# is a lot of comment and old code that starts from the bottom and
# the most recent stuff is at the top. Above the same line is chronological in
# the opposite direction: at the top are earlier functions that I may still
# need, and below that is the code that I'm currently working on.
# 
# this code is sloppy, and naive, and unlikely to be suitable for any purpose,
# and is here simply to serve as a backup and a record of what I've learned;
# however, if you have use for it, feel free to use it under the most liberal
# interpretation of the GNU General Public License, version 2 (GPL-2.0)

import re
import json
import cgi
from pprint import pprint
from collections import OrderedDict, defaultdict
## Giovanni Scriba vol.2: starting with charter 804, ending with 1306 total of 503

def htmlBlob(text, **values):
	'''
	Interpolate values into text, then remove newlines and the whitespace following them. If putting attributes on new lines for clarity, don't forget the terminal space. This will also escape double quotes in the result, for insertion into a quoted json environment. (note: with % we can enforce type too)]
	Note: didn't need the second call to re.sub because simplejson takes care of excaping the double quotes!
	'''
	try:
	    return re.sub('(^\n*|\n+)[ \t]*', '', text % values)
	except:
	    print values

def replace_all(text, d):
    for x, y in d.iteritems():
        text = text.replace(x, y)
    return text

def lev(seq1, seq2):
    """ Return Levenshtein distance metric
    (ripped from http://pydoc.net/Python/Whoosh/2.3.2/whoosh.support.levenshtein/)
     """
    oneago = None
    thisrow = range(1, len(seq2) + 1) + [0]
    for x in xrange(len(seq1)):
        twoago, oneago, thisrow = oneago, thisrow, [0] * len(seq2) + [x + 1]
        
        for y in xrange(len(seq2)):
            delcost = oneago[y] + 1
            addcost = thisrow[y - 1] + 1
            subcost = oneago[y - 1] + (seq1[x] != seq2[y])
            thisrow[y] = min(delcost, addcost, subcost)
            # This block deals with transpositions
            if (x > 0 and y > 0 and seq1[x] == seq2[y - 1]
                and seq1[x-1] == seq2[y] and seq1[x] != seq2[y]):
                thisrow[y] = min(thisrow[y], twoago[y - 2] + 1)
    return thisrow[len(seq2) - 1]

def rom2ar(rom):
    """ From the Python tutor mailing list:
    János Juhász janos.juhasz at VELUX.com
    returns arabic equivalent of Roman numeral """
    roman_codec = {'M':1000, 'D':500, 'C':100, 'L':50, 'X':10, 'V':5, 'I':1}
    roman = rom.upper()
    roman = list(roman)
    roman.reverse()
    decimal = [roman_codec[ch] for ch in roman]
    result = 0
    
    while len(decimal):
        act = decimal.pop()
        if len(decimal) and act < max(decimal):
            act = -act
        result += act
    
    return result

### NB. romstr is a crude filter for text beginning with I,V,X,L,C,D, or M.
### Single character occurance of these numerals will be missed out and must be manually edited.

fin = open("/Users/jjc/Sites/Ann2DotRdf/GScriba/GScribaV2_working.txt", 'r')
romstr = re.compile("\s?[IVXLCDM]{2,}") 
slug = re.compile("(\[~~~~\sGScriba_)(.*)\s::::\s(\d+)\s~~~~\]")
fol = re.compile("\[fo\.\s?\d+\s?[rv]\.\s?\]")
notetext = re.compile(r"^\(\d\)")
notemark = re.compile(r"\(\d\)(?<!^\(\d\))")
fndict = {}
n = 0
this_charter = ''
this_folio = '[fo. 101 r.]' ### modify this depending on doc number xrange()

txtlist = fin.readlines()
dir_out = "/Users/jjc/Documents/GiovanniScriba/testCorpus/"
# doc numbers: 1176-87, 1219-1230.

charters = dict() #OrderedDict()    ### watch out for this: an OrderedDict is not a Dict.

### text to hash: better way to do this than iteration over a list of lines?
for line in txtlist:
    line = re.sub("\s\s+" , " ", line)
    # if a header is found, establish variables for the dict fields: in scope in the for loop
    if slug.match(line):
        m = slug.match(line)
        this_charter = m.group(0)
        chid = "GScriba_" + m.group(2)
        chno = int(m.group(3))
        charters[chno] = {}
        templst = []
        
    # create the dict entry for charter and read lines in for each 'for' iteration that match the conditionals
    if int(chno):# in xrange(1176, 1187) or int(chno) in xrange(1219, 1230):
        d = charters[chno]
    
        if not re.match('[\n\t]+', line):
            d['chid'] = chid
            d['chno'] = chno
            d['folio'] = this_folio
            d['footnote'] = []
            if slug.match(line):
                templst.append(chid + '\n')
            elif fol.match(line):
                this_folio = line.strip() ## update the variable instead of appending to templst
                continue
            elif line == '':
                continue
            else:
                templst.append(line)
            try:
                d['summary'] = templst[1] ## this fails until the line is written to templst
            except: ## this use of try/except seems clumsy and fragile. Must be a better way.
                pass 
            d['text'] = templst[0] + ''.join(templst[2:]).strip()
            
            if fol.search(d['text']):
                # this fails in 11 cases:
                # 992, 1000, 1006, 1008, 1047, 1093, 1140, 1171, 1173, 1196, 1212
                # where, for example, 1212 [fo. 154 r.][fo. 154 r.]
                # should be: 1212 [fo. 153 v.][fo. 154 r.]
                # still not clear why; multiple text lines? footnote interference?
                
                this_folio = fol.search(d['text']).group(0)
                d['folio'] = d['folio'] + fol.search(d['text']).group(0)

## SECOND PASS: charters is now an existing data structure. The following for loop acts upon the same list of lines to find footnote markers and footnote texts, store them in a temporary structure (fndict) and then write them out to the 'footnote' field of the 'charters' dictionary.
for line in txtlist:
    if slug.match(line):
        this_charter = slug.match(line).group(3)
    nmarkers = notemark.findall(line)
    ntexts = notetext.findall(line)
        
    if nmarkers:
        for marker in [eval(x) for x in nmarkers]:
            fndict[marker] = {'id':this_charter, 'fntext': ''}
    if ntexts:
        for foot in [eval(x) for x in ntexts]:
            try:
                fndict[foot]['fntext'] = ' '.join(line.split()[1:])
                if len(fndict) == foot:
                    for n in fndict:
                        chid, text = int(fndict[n]['id']), fndict[n]['fntext']
                        charters[chid]['footnote'].append((n, text))
                        
                        
                    for fn in fndict:
                        if fndict[fn]['fntext'] == '':
                            print "missing text for footnote: %s" % (fn)
                    
                    fndict = {}

            except KeyError:
                print "KeyError in charter: %s\nFrom Line: \"%s\""  % (this_charter, line)


## THIRD PASS: delete footnote texts from charter 'text' field
textnotes = re.compile(r"\n\(\d\).*")
for ch in charters:
    txt = charters[ch]['text']
    notes = textnotes.findall(txt)
    
    if notes:
        repl = {x: ' ' for x in notes}
        charters[ch]['text'] = replace_all(txt, repl)

## FOURTH PASS: strip out rubrics into metadata and strip whitespace from remaining text in 'text' field.
for ch in charters:
    txt_lines = charters[ch]['text'].split('\n')
    charters[ch]['rubric'] = txt_lines[1]
    charters[ch]['text'] = ' '.join([t.strip() for t in txt_lines[2:]])
## OK, that works, but it leaves out charters with no rubric, eg. " ......], so we fixed the rubrics manually"    
            


pprint (charters)

########### Output HTML ###############
# for x in charters:
#     if charters[x]['footnote']:
#         fnlst = charters[x]['footnote']
#         fns = ""
#         for i in fnlst:
#             fns += "<li>(%s) %s</li>" % (i[0], i[1])
#     else:
#         fns = ""   
#         
#     blob = htmlBlob(
#         """
#         <div>
#             <div class="charter">
#                 <h1>%(head)s</h1>
#                 <div class="folio">%(folio)s</div>
#                 <div class="summary">%(summary)s</div>
#                 <div class="rubric">%(rubric)s</div>
#                 <div class="charter-text">%(charter_text)s</div>
#                 <div class="footnotes"><ul>%(footnote)s</ul></div>
#             </div>
#         </div>
#         """,
#         head = charters[x]['chid'],
#         folio = charters[x]['folio'],
#         summary = charters[x]['summary'],
#         rubric = charters[x]['rubric'],
#         charter_text = charters[x]['text'],
#         footnote = fns,
#     )
#     
#     print blob

################################ OCR cleanup routines ####################################
## Commented out sections below were ad-hoc routines to divide up the ocr text into charters and clean it up a bit in order to run the code above to get a dictionary of texts and metadata.


## watch out for footnotes split across pages as for no. 1149 n.1: (fixed in working)

## All summary lines end with "(date)". Find broken summary lines:
## pprint(sorted([(charters[x]['chno'], charters[x]['summary']) for x in charters if '(' not in charters[x]['summary']]))

## this finds the date at the end of summaries 503 found
# for x in charters:
#     print re.search("\(.*\)", charters[x]['summary']).group(0)


### footnote hunting:
## search '\(\d+1' and '\(\d\s' which will find dates, useful to make sure they're all on the same line as the ital. summary. 
## also \(l or \(ll
## Also lines beginning with a number '^\d+', and lines beginning with '\(' or ' +\('


# mighta taken this route too: fin.read() instead of fin.readlines()
# for x in re.split("\[~~~~\sGScriba_.*\s::::\s\d+\s~~~~\]", txt):
#     print "~~~~~~~~~~~~~\n" + x            
    
## foliation ids:
# fol = re.compile("\[fo\.\s?\d+\s?[rv]\.\s?\]")
# txt = fin.read()
# for x in fol.findall(txt): print x

#################### find and reorder folio number / charter number

# fout = open("/Users/jjc/Documents/GiovanniScriba/RomanOutTestingV2", 'w')
# fol = re.compile("^\s?(\[\s?fo\.\s?\d+\s?[rv]\.\s?\]).*?([IVXLCDM]{1,})")
# for line in fin.readlines():
#     if fol.match(line):
#         m = fol.match(line)
#         print (m.group(2), m.group(1))
#         fout.write("\n\n%s\n%s\n" % (m.group(2), m.group(1)))
#     else:
#         fout.write(line)


# txt = fin.read()
# for x in fol.findall(txt): print x

#################### generate charter headers and check numbering

# fout = open("/Users/jjc/Documents/GiovanniScriba/RomanOutTestingV2", 'w')
# for line in fin.readlines():
#     if romstr.match(line):
#         m = romstr.match(line).group(0).strip()
#         n + 804
#         if not rom2ar(m) == n:
#             print "[~~~~ consecutive? GScriba_%s :::: %d ~~~~] :::: %s" % (m, rom2ar(m), line)
#             fout.write("[~~~~ consecutive? GScriba_%s :::: %d ~~~~]\n" % (m, rom2ar(m)))
#         else:
#             fout.write("[~~~~ GScriba_%s :::: %d ~~~~]\n" % (m, rom2ar(m)))
#         
#         
#         n = rom2ar(m) + 1
#     
#     else: fout.write(line)
    
## so check again for consecutive numbers:

# for line in fin.readlines():
#     if slug.match(line):
#         m = slug.match(line).group(3)
#         if not int(m) == n + 1:
#             print m
#         n = int(m)

## now check for consecutive roman numerals and then folio numbering
# for line in fin.readlines():
#     if slug.match(line):
#         m = slug.match(line).group(2)
#         print m
#         if not rom2ar(m) == n + 1:
#             print m
#         n = rom2ar(m)
#         
# print n

#################### Using Levenshtein Distance metric to isolate page headers:    

### v. 2: 123 recto headers 122 verso 245 total
# for line in fin.readlines():
#     if lev(line, 'IL CARTOLARE DI GIOVANNI SCRIBA') < 24 :
#         n += 1
#         fout.write("\r~~~~~ PAGE HEADER ~~~~~\r")
#         
#     elif lev(line, 'MARIO CHIAUDANO') < 11 :
#         n += 1
#         fout.write("\r~~~~~ PAGE HEADER ~~~~~\r")
#         
#     else: fout.write(line)
#         
# print n

### v. 1: this finds 431 page headers, which is right because the scan of p. 214 is missing
# for line in fin.readlines():
#     if lev(line, 'IL CARTOLARE DI GIOVANNI SCRIBA') < 26 :
#         n += 1
#         fout.write("~~~~~ PAGE HEADER ~~~~~\r\r")
#         
#     elif lev(line, 'MARIO CHIAUDANO - MATTIA MORESCO') < 26 :
#         n += 1
#         fout.write("~~~~~ PAGE HEADER ~~~~~\r\r")
#         
#     else:
#         fout.write(line)
#         
# print n

#### examples of bad page headers
# for line in fin.readlines():
#     recto_lev_score = lev(line, 'IL CARTOLARE DI GIOVANNI SCRIBA')
#     verso_lev_score = lev(line, 'MARIO CHIAUDANO - MATTIA MORESCO')
#     
#     if recto_lev_score == 5 :
#         n += 1
#         print str(recto_lev_score) + '\t' + line
#         
#     elif verso_lev_score < 8 :
#         n += 1
#         print str(verso_lev_score) + '\t' + line
#         
# print n
# 
# ### headers with a levenshtein score over 16 and under 26:
# # Levenshtein distance: 17 ::::260	11141110 CH[AUDANO MATTIA MORESCO
# # Levenshtein distance: 18 ::::IL CIRTOL4RE DI CIOVINN1 St'Itlltl	269
# # Levenshtein distance: 18 ::::IL CJIRTOL.%RE DI G:OVeNNl FIM P%	297
# # Levenshtein distance: 18 ::::IL CIP.TQLIRE DI G'OVeNNI SCI Dt	r.23
# # Levenshtein distance: 18 ::::332	T1uu:0 CHIAUDANO M:11TIA MGRESCO
# # Levenshtein distance: 19 ::::IL CIRTOL.'RE DI G:OV.I\N( sca:FR	339
# # Levenshtein distance: 17 ::::342	NI .\ßlO CHIAUDANO 9LtTTIA MORESCO
# # Levenshtein distance: 18 ::::350	M:R0 CIIIAL'D►NO MATTIA MORESCO
# # Levenshtein distance: 20 :::: 352	1111R0 CHIAUD1NO = M4r r% MORESCO
# # Levenshtein distance: 25 ::::•	354	M:1R'O CIIRAt'D.%NO CrTIA MORtSCO
# # Levenshtein distance: 21 ::::356	I1t1RO CHI.. 4NO 141 VITI MORESCO
# # Levenshtein distance: 21 ::::360	M:\RVO CHl Rl'D:tNO MATTIA MOR?SC')
# # Levenshtein distance: 22 ::::IL C IRTOLARC Di G:011.':' I SCR:B:I	367

# for line in fin.readlines():
#     recto_lev_score = lev(line, 'IL CARTOLARE DI GIOVANNI SCRIBA')
#     
#     if recto_lev_score < 7 :
#         n += 1
#         print "Levenshtein distance: " + str(recto_lev_score) + " ::::" + line

### finding roman doc numbers:
# roman = re.compile('\s+[XVILDC]+\.')
# 
# GScriba = fin.read()
# it = roman.finditer(GScriba)
# print len([x.group(0).strip().strip('.') for x in it])

################# Q & A #####################
# 887: misprint in original?: 'Testes Todescus Cantarus, Martinus, Petrus Ferrarii et Lahfran \xe2\x80\xa2 Testes Todescus Cantarus, Martinus, Petrus Ferrarii et Lanfran'
# 1090: superscript a in text? currency designation?: 'pro .xvi.•'