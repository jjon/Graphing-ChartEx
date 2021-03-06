#!/usr/bin/env python
# -*- coding: utf-8 -*- #

# Adapted from process_GScribaV2_OCR

import re
import json
# import cgi # use cgi.escape() if we need to escape the charter text for the HTML
from pprint import pprint
from collections import OrderedDict, defaultdict
## Giovanni Scriba vol.1: starting with charter 1, ending with 803, but with p. 214 missing

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

def htmlBlob(text, **values):
	'''
	Interpolate values into text, then remove newlines and the whitespace following them. If putting attributes on new lines for clarity, don't forget the terminal space. This will also escape double quotes in the result, for insertion into a quoted json environment. (note: with % we can enforce type too)]
	Note: didn't need the second call to re.sub because simplejson takes care of excaping the double quotes!
	'''
	return (text % values)


def return_iso(s):
    """just experimenting here"""
    for m in summary_date.finditer(s):
            try:
                    return datetime.date( int(m.group(3)), Ital2int[m.group(2).strip()], int(m.group(1)) )
            except:
                    return "date won't parse", sys.exc_info()[0]


### NB. romstr is a crude filter for text beginning with I,V,X,L,C,D, or M.
### Single character occurance of these numerals will be missed out and must be manually edited.

romstr = re.compile("\s?[IVXLCDM]{2,}") # we'll have to manually find ch nos w/leading whitespace
pgno = re.compile("~~~~~ PAGE (\d+) ~~~~~")
slug = re.compile("(\[~~~~\sGScriba_)(.*)\s::::\s(\d+)\s~~~~\]")
fol = re.compile("\[fo\.\s?\d+\s?[rv]\.\s?\]")
n = 0
this_charter = ''
this_folio  = '[fo. 1 r.]'
this_page = 1
charters = dict() #OrderedDict()    ### watch out for this: an OrderedDict is not a Dict.

######### Using Levenshtein Distance metric to isolate page headers ###########
# Here we replace all the page headers with a temporary slug, we'll remove them
# en masse when we've decided we don't need that information any more. Now we
# move on to dividing the file up into charters rather than pages.
### First page is unnumbered and recto.
### last page is 431 and recto.
### the following finds 430 page headers, which is right because the OCR output for p. 214 is missing
#
# fin = open("/Users/jjc/Documents/GiovanniScriba/V1/GScribaV1_base.txt", 'r')
# fout = open("/Users/jjc/Desktop/temp.txt", 'w')
# txtlist = fin.readlines()
# 
# for line in txtlist:
#     recto_lev_score = lev(line, 'IL CARTOLARE DI GIOVANNI SCRIBA')
#     verso_lev_score = lev(line, 'MARIO CHIAUDANO - MATTIA MORESCO')
#     if recto_lev_score < 26 :
#         n += 1
#         print "recto: %s %s" % (recto_lev_score, line)
#         #fout.write("~~~~~ PAGE HEADER ~~~~~\n\n")
#     elif verso_lev_score < 26 :
#         n += 1
#         print "verso: %s %s" % (verso_lev_score, line)
#         #fout.write("~~~~~ PAGE HEADER ~~~~~\n\n")
#     else:
#         #fout.write(line)
#         pass
#     
# print n

##################### Isolate and count charter numbers #######################
# We're fixing problems manually as we find them, so keep close track of what's
# the latest input file. v1test_out.txt got tinkered with manually, so the input
# file for this script is v1test_out2.txt. Use the first script to manually
# repair v1test_out2.txt, then when the charter numbers are all fixed, write out
# a new file based on the fixed v1test_out2.txt to produce v1test_out3.text
#
### To get everything numbered right, we're going to have
###     the roman numerals fixed and on a separate line
###     the folio markers fixed and on a separate line
#
### finding roman doc numbers:
### this will identify the problems with the charter numbers and 
### give the line number in the source file. This will also find
### problems with the folio markers because it expects the Roman
### charter numbers to be at the beginning of lines: .match().
#
### !!! don't get fin and fout mixed up !!!
fin = open("/Users/jjc/Documents/GiovanniScriba/V1/v1test_out.txt", 'r')
# fout = open("/Users/jjc/Documents/GiovanniScriba/V1/v1test_out3.txt", 'w')
# 
# GScriba = fin.readlines()
# for line in GScriba:
#     if romstr.match(line):
#         rnum = line.strip().strip('.')
#         n += 1
#         try:
#             if n != rom2ar(rnum):
#                 print n, "something missing, line number ", GScriba.index(line), " reads: ", line
#                 n = rom2ar(rnum)
#         except KeyError:
#             print n, "KeyError, line number ", GScriba.index(line), " reads: ", line
            
### We keep running this script repeatedly, fixing stuff as we find it until we
### get only the following errors:
#     5 something missing, line number  35  reads:  VI. 
#     10 something missing, line number  71  reads:  XI.
#     50 something missing, line number  360  reads:  LI.
#     100 something missing, line number  717  reads:  CI.
#     404 something missing, line number  2945  reads:  CDVI.
#     500 something missing, line number  3634  reads:  DI.
### 5,10,50,100, and 500 because they're single digit roman numerals, and 404 because p.214 is missing
#
# ### now that we've found and fixed all the charter numbers, comment out the
# ### script above and then generate a slug for them and output a new file:
# 
# for line in GScriba:
#     if romstr.match(line) or line.strip().strip('.') in ['I','V','X','L','C','D']:
#         rnum = line.strip().strip('.')
#         num = rom2ar(rnum)
#         fout.write("[~~~~ GScriba_%s :::: %d ~~~~]\n" % (rnum, num))
#     else:
#         fout.write(line)

#################### Folio Markers and Italian Summaries ######################
### now using: v1test_out3
### FIX FOLIATION. Clean up extra spaces, periods, and any other typos in the
### folio marks until all folios are represented, both recto and verso.
### All folio marks from ch headers should be on their own line; folio marks
### within charter texts remain there; all must conform to the fol regex.
### Check to see that no line has more than 1 folio marker,
# for line in GScriba:
#     i = fol.finditer(line)
#     if len(list(i)) > 1: print line
### but be alert for the possibility that a charter may span more than one folio.


# GScriba = fin.readlines()
# for line in GScriba:
#     match = fol.search(line)
#     if match:
#         print GScriba.index(line), match.group(0)

### FIX ITALIAN SUMMARY LINES
### the following script finds me cases in which the line following the charter
### header does not end with a date formatted thus: \(\d+.*\d+\) and reports the
### charter number. Repeat this script until it returns no unaccounted for
### errors.
#     charter: 1 because no preceding charter
#     charter: 66 because 65 date = (?)
#     charter: 176 because 175 date = (senza data)
#     charter: 406 because p.214 data are missing (2)
#     accounted for errors: 5
#     number of italian summaries:  797
#     797 + 5 = 802 = expected number of charters.
#
# slug_and_firstline = re.compile("(\[~~~~\sGScriba_)(.*)\s::::\s(\d+)\s~~~~\]\n(.*)(\(\d?.*\d+\))")
# num_firstlines = 0
# fin = open("/Users/jjc/Documents/GiovanniScriba/V1/v1test_out4.txt", 'r')
# GScriba = fin.read() # NB: not a list of lines, but a single string
# 
# i = slug_and_firstline.finditer(GScriba)
# for x in i:
#     num_firstlines += 1
#     chno = int(x.group(3))
#     if chno != n + 1:
#         print "charter: %d" % (n + 1) #NB: this will miss consecutive problems.
#     n = chno
# 
# print "number of italian summaries: ", num_firstlines
### now save as v1test_out4.txt

############################## Enumerate Pages ################################
### first lets get proper page numbers, shoulda done this first when replacing
### page header data
#
# pgno = 1
# fin = open("/Users/jjc/Documents/GiovanniScriba/V1/v1test_out4.txt", 'r')
# fout = open("/Users/jjc/Documents/GiovanniScriba/V1/v1test_out5.txt", 'w')
# GScriba = fin.readlines()
# pg = re.compile("~~~~~ PAGE HEADER ~~~~~")
# for line in GScriba:
#     if pg.match(line):
#         pgno += 1
#         fout.write("~~~~~ PAGE %d ~~~~~" % pgno)
#     else: fout.write(line)

########################### Regularize note markers ###########################
# search regexes like this to clean up as much as possible:
# \(\d;
# \(\d1
# \(\dl
# \(\d\]
# \(\d+'
# and likewise: ;\d\) or `\d\) etc.
# Then do this to find out where the problems lie. This script will report page
# numbers and a list of fn markers and fn numbers for cases in which any fn
# marker does not appear twice (i.e. (1) appearing in the text AND again at the
# bottom of the page). After doing minimal cleanup with regex as above, this
# script reported 62 pages (out of 432) where this condition is not met.
### of the 62 pages mentioned 3 are printer's errors, not OCR errors:
# 58 [1] fn (1) not in the text, perhaps it refers to 'retractabimus' on the previous page?
# 90 [1, 2, 3, 1, 2, 3, 4] fn (4): no corresponding marker appears in the text.
# 346 [1, 2, 1, 2, 3] fn (3) no corresponding marker appears in the text
# 
# from collections import Counter
# fin = open("/Users/jjc/Documents/GiovanniScriba/V1/v1test_out5.txt", 'r')
# GScriba = fin.readlines()
# r = re.compile("\(\d{1,2}\)")
# pg = re.compile("~~~~~ PAGE \d+ ~~~~~")
# pgno = 0
# pgfnlist = []
# for line in GScriba:
#     if pg.match(line):
#         pgno += 1
#         if pgfnlist:
#             c = Counter(pgfnlist)
#             if list(set(c.values()))[0] != 2: print pgno, pgfnlist
#             pgfnlist = []
#     i = r.finditer(line)
#     for mark in [eval(x.group(0)) for x in i]:
#         pgfnlist.append(mark)

########################## Fix page numbering (again!) ########################
# Going through those 62 pages brings a page numbering error to light: we missed
# a page header using the Levenshtein method: "292	.NO MATTIA n[or.:_sca"
# This meant that the page numbering thereafter was wrong and now has to be
# corrected thus:
# fin = open("/Users/jjc/Documents/GiovanniScriba/V1/v1test_out5.txt", 'r')
# fout = open("/Users/jjc/Documents/GiovanniScriba/V1/temp.txt", 'w')
# GScriba = fin.readlines()
# r = re.compile("\(\d{1,2}\)")
# pg = re.compile("~~~~~ PAGE (\d+) ~~~~~")
# pgno = 0
# for line in GScriba:
#     m = pg.match(line)
#     if m:
#         pgno = eval(m.group(1))
#         if pgno >= 292:
#             pgline = "~~~~~ PAGE %d ~~~~~\n" % (pgno + 1)
#             fout.write(pgline)
#         else: fout.write(line)
#     else:
#         fout.write(line)

############# Generate Python Dictionary from revised OCR text ################
# saved manually v1test_out5.txt to v1test_out6.txt
### for some of the last elements of the available metadata, it will be more
### convenient to have a regular data structure rather than simply a list of
### lines; and indeed, that's what we're aiming for: a regular, and reliable
### data structure that we can deploy for whatever purpose is appropriate. The
### following 'for' loop will generate a python dictionary for each charter and
### then populate it with the available metadata fields. Once this loop disposes
### of the easily searched lines (folio, page, and charter header), the
### fallthrough default will be to add the remaining lines to the text field,
### which is a python list.

### Note: if efficiency is an issue, multiple iterations over the dict may not be a good idea. Maybe better to use a dictview. After this loop populates the dict, subsequent iterations could be over

fin = open("/Users/jjc/Documents/GiovanniScriba/V1/v1test_out6.txt", 'r')
GScriba = fin.readlines()

for line in GScriba:
    if fol.match(line):
        this_folio = fol.match(line).group(0)
        continue # update the variable but otherwise do nothing with this line.
    if slug.match(line):
        m = slug.match(line)
        this_charter = m.group(0)
        chid = "GScriba_" + m.group(2)
        chno = int(m.group(3))
        charters[chno] = {}
        templist = [] # this works because we're proceeding in document order: templist continues to exist as we iterate through each line in the charter, then is reset to the empty list when we start a new charter(slug.match(line))
        continue # we generate the entry, but do nothing with the text of this line.
    if chno:
        d = charters[chno]
        d['footnotes'] = []
        d['chid'] = chid
        d['chno'] = chno
        d['folio'] = this_folio
        d['pgno'] = this_page
        if re.match('^\(\d+\)', line):
            continue # this line is footnote text, we'll deal with it later
        if pgno.match(line):
            this_page = int(pgno.match(line).group(1)) # if line is a pagebreak, update the variable
        elif fol.search(line):
            this_folio = fol.search(line).group(0) # if folio changes within the text, update variable
            templist.append(line)
        else:
            templist.append(line)
        d['text'] = [x for x in templist if not x == '\n'] # strip empty lines

# ##### Check & Correct 'summary' and 'marginal' lines and add to metadata ######
# ### Once we have a data structure like that, we can iterate through each of the
# ### charter dictionaries and look at the lines in the text field by index
# ### number. We can do that with a loop like the one below. In all cases, the
# ### first line should be the Italian summary as we have insured above. The
# ### second line in MOST cases, represents a kind of marginal notation (which
# ### I've inaccurately refered to in the code as a 'rubric')  usually ended by
# ### the ']' character (which OCR misreads alot). We have to find the cases that
# ### do not meet this criterion, supply or correct the missing ']', and in the
# ### cases where there is no marginal notation I've supplied "no marginal]"
# # for ch in charters:
# #     txt = charters[ch]['text']
# #     try:
# #         line1 = txt[0]
# #         line2 = txt[1]
# #         if line2 and ']' in line2:
# #             n += 1
# #             print "charter: %d\ntext, line 1: %s\ntext, line 2: %s" % (ch, line1, line2)
# #     except:
# #         print ch, "oops" # to pass the charters from the missing page 214
# #
# ### Once we're satisfied that line 1 and line 2 in the 'text' field for each
# ### charter are the Italian Summary and the marginal notation respectively, we
# ### can make another iteration of the charters dictionary, removing those lines
# ### from the text field and creating new fields in the charter entry for them.
# ### NOTA BENE: we are now modifying a data structure in memory rather than
# ### editing successive text files.
# 
# ######### Assign footnotes to respective charters and add to metadata #########
# # The next tricky bit is to get the footnote texts appearing at the bottom of
# # the page associated with their appropriate charters. For this we go back to
# # the same list of lines that we built the dictionary from. We're depending on
# # all the footnote markers appearing within the charter text, i.e. none of them are at
# # the beginning of a line. And, each of the footnote texts is on a separate line
# # beginning with '(1)' etc.
# 
# 
notetext = re.compile(r"^\(\d+\)")
notemark = re.compile(r"\(\d+\)(?<!^\(\d\))") # lookbehind to see that the (1) marker does not begin a line
this_charter = 1
#r = re.compile("\(\d{1,2}\)")
pg = re.compile("~~~~~ PAGE (\d+) ~~~~~")
pgno = 1
fndict = {}

for line in GScriba:
    nmarkers = notemark.findall(line)
    ntexts = notetext.findall(line)
    if pg.match(line):
        for fn in fndict:
            chid = fndict[fn]['chid']
            fntext = fndict[fn]['fntext']
            charters[int(chid)]['footnotes'].append((fn, fntext))  
        pgno += 1
        fndict = {}     
    if slug.match(line):
        this_charter = int(slug.match(line).group(3))
    if nmarkers:
        for marker in [eval(x) for x in nmarkers]:
            fndict[marker] = {'chid':this_charter, 'fntext': ''}
    if ntexts:
        for text in [eval(x) for x in ntexts]:
            try:
                fndict[text]['fntext'] = re.sub('\(\d+\)', '', line).strip()
            except KeyError:
                pass #print "printer's error? ", "pgno:", pgno, line
# #                 
## sequentially renumber footnotes here?

for ch in charters:
    d = charters[ch]
    try:
        d['summary'] = d['text'].pop(0).strip()
        d['marginal'] = d['text'].pop(0).strip().strip('.').strip()
    except IndexError: # this will report that the charters on p 214 are missing
        pass #print "missing charter ", ch
#     
# # ####### repair charter 404
charters[404]['summary'] = ''
# 
# 
# 
# 
# # We now have a regular data structure in which the available metadata has been abstracted away from the text of the charter itself. That text is still full of OCR errors, of course, but it's now possible to do some machine processing of the corpus of charters as a whole without the page-bound infrastructure getting in the way. For example, we might simply want an HTML representation of the charters so that we can control the styling of the various elements. This is a huge advantage all by itself: proofreaders have a much easier time of it when the elements of the corpus aren't just a mass of undifferentiated lines of text.
# 
# # Or we might want to generate some SQL statements that will insert our data in a relational database, output some rudimentary TEI/xml, or get an RDF graph from our data. All kinds of things are now possible when we have a regular data structure rather than just a mass of error-filled OCR output.
# 
# 
# ############## correcting and parsing dates ###############
# # # find and repair misspelled month names:
# # import sys
# # from collections import Counter
# # summary_date = re.compile('\((\d{1,2})?(.*?)(\d{1,4})?\)')
# # c = Counter()
# # 
# # for x in charters:
# #     d = charters[x]
# #     try:
# #         i = summary_date.finditer(d['summary'])
# #         dt = list(i)[-1]
# #         c.update([dt.group(2).strip()])
# #     except:
# #         pass # print d['chno'], "Unexpected error:", sys.exc_info()[:2]
# # 
# # months = [x[0] for x in c.most_common(12)] # or just make a list with the correct spellings.
# # print months
# 
# # summary_date = re.compile('\((\d{1,2})?(.*?)(\d{1,4})?\)')
# # Ital2int = {'luglio': 7, 'marzo': 3, 'agosto': 8, 'febbraio': 2, 'settembre': 9, 'giugno': 6, 'dicembre': 12, 'ottobre': 10, 'novembre': 11, 'gennaio': 1, 'maggio': 5, 'aprile': 4}
# # 
# # import sys
# # for ch in charters:
# #     try:
# #         d = charters[ch]
# #         i = summary_date.finditer(d['summary'])
# #         dt = list(i)[-1]
# #         if dt.group(2).strip() not in Ital2int.keys():
# #             print "chno. %d fix the month %s" % (d['chno'], dt.group(2))
# #     except:
# #         print d['chno'], "The usual suspects: ", sys.exc_info()[:2]
# 
# # # count the dates to be sure every charter has one:
# # for ch in charters:
# #     try:
# #         d = charters[ch]
# #         i = summary_date.finditer(d['summary'])
# #         dt = list(i)[-1]
# #         print dt.group(0)
# #     except:
# #         print d['chno'], "Unexpected error:", sys.exc_info()[:2]
# 
# ################## parse the dates and add to metadata.
# # # Out of 803 charters, 29 have dates that won't parse. Most of them because
# # # they are only mo and yr, some for other reasons including printer's errors
# # # like "31 settembre 1160"
# 
# # Dates are hard. Students of British history cling to (Cheyney)[http://www.worldcat.org/oclc/41238508] as to a spar on a troubled ocean. And, given the way the Gregorian calendar was adopted so gradually, correct date reckoning for medieval sources will always require care and local knowledge. Nevertheless, here too Python can be of some help.
# # 
# # Our Italian summary line invariably contains a date drawn from the text, and it's conveniently set off from the rest of the line by parentheses. So we can parse them and create Python `date` object. Then, if we want, we can to some simple calendar arithmetic.
# # 
# # First we have to find and correct all the dates in the same way as we have done for the other metadata elements. Devise a script that will report the errors, and then fix them:
# # 
import sys
import datetime
summary_date = re.compile('\((\d{1,2})?(.*?)(\d{1,4})?\)')

Ital2int = {'luglio': 7, 'marzo': 3, 'agosto': 8, 'febbraio': 2, 'settembre': 9, 'giugno': 6, 'dicembre': 12, 'ottobre': 10, 'novembre': 11, 'gennaio': 1, 'maggio': 5, 'aprile': 4}

summary_date = re.compile('\((\d{1,2})?(.*?)(\d{1,4})?\)')
for ch in charters:
    c = charters[ch]
    i = summary_date.finditer(c['summary'])
    
    for m in i:
        try:
            c['date'] = datetime.date( int(m.group(3)), Ital2int[m.group(2).strip()], int(m.group(1)) )
        except:
            c['date'] = "date won't parse, see summary line"


########### Sequentially renumbering footnotes ############
#enumerate fnlist for d['footnotes']:
# [(t[0],t[1][1]) for t in enumerate(fns)] OR [(fns.index(t)+1, t[1]) for t in fns]
# 
# #and for d['text'] we can do:
# t = ' '.join([x.strip() for x in d['text']])
# 
# #this ridiculous one-liner will renumber the in-text footnote references (*whew*)
# ntregex = re.compile(r"\(\d+\)")
# ''.join(["(%s)" % str(x[0]) +  x[1] for x in enumerate(re.split(ntregex, t))]).replace('(0)', '').strip()
# 
# # or we could write it out:
# t = ' '.join([x.strip() for x in d['text']])
# fnrefs_enumerated = enumerate(re.split(ntregex, t))
# fnlst = ["(%s)" % str(x[0]) +  x[1] for x in fnrefs_enumerated]
# charter_text = ''.join(fnlst).replace('(0)', '').strip()

# >>> ntregex = re.compile(r"\(\d+\)")
# >>> t = "a string (2) another (3) another string (1) and another (2) more (3) strings"
# >>> fnrefs_enumerated = enumerate(re.split(ntregex, t))
# >>> fnlst = ["(%s)" % str(x[0]) +  x[1] for x in fnrefs_enumerated]
# >>> charter_text = ''.join(fnlst).replace('(0)', '').strip()
# >>> charter_text
# 'a string (1) another (2) another string (3) and another (4) more (5) strings'
# 
# # or the one-liner:
# >>> t
# 'a string (2) another (3) another string (1) and another (2) more (3) strings'
# >>> ''.join(["(%s)" % str(x[0]) +  x[1] for x in enumerate(re.split(ntregex, t))]).replace('(0)', '').strip()
# 'a string (1) another (2) another string (3) and another (4) more (5) strings'
#
#### fails where there's a numbered footnote reference in either the summary or the marginal lines
#### it's really not worth fixing this. (errrg!)
# ntregex = re.compile(r"\(\d+\)")
# for ch in charters:
#     d = charters[ch]
#     d['footnotes'] = [(t[0]+1,t[1][1]) for t in enumerate(d['footnotes'])]
#     
#     # to include sum and marg lines, do this in an earlier pass?
#     t = ' '.join([x.strip() for x in d['text']])
#     d['text'] = ''.join(["(%s)" % str(x[0]) +  x[1] for x in enumerate(re.split(ntregex, t))]).replace('(0)', '').strip()

##pprint(charters)

 
# ###### Dealing with None #########
# # for ch in charters:
# #     c = charters[ch]
# #     dt = summary_date.search(c['summary'])
# #     print dt.group(0) if dt else "FOOBAR"
#     
# ### roman numeral noodling ###
# # for ch in charters:
# #     txt = ' '.join(charters[ch]['text'])
# #     print re.findall('[DdCcLlXxVvIi]{2,}', txt)
# 
# ### simple word frequency table ###
# # import string
# # # join() all the text fields in each charter and join() the result for an aggregate txt
# # txt = ' '.join([' '.join(charters[x]['text']) for x in charters])
# # # jetison the punctuation
# # txt = txt.translate(string.maketrans("",""), string.punctuation)
# # from collections import Counter
# # c = Counter(txt.split())
# # # gets us a list of frequencies
# # 
# # # how long the longest?
# # just = max([len(x) for x in c])
# # 
# # # print out the most common pretty:
# # for x in c.most_common():
# #     print "%s: %s" % (x[0].rjust(just), str(x[1]).ljust(just))
# 
# # Maybe we want to have a look at the frequency of mostly proper names: if x[0][0].isupper():
import datetime
week = datetime.timedelta(weeks=1)
years = []        

######## this works, but seems ridiculous:
for ch in charters:
    d = charters[ch]
    try:
        years.append(d['date'].year)
    except: pass
    
result = {}

for year in set(years):
    result[year] = []
    for ch in charters:
        try:
            dt = charters[ch]['date']
            christmas = datetime.date(year,12,25)
            if abs(dt - christmas) < week * 3:
                result[year].append((charters[ch]['chno'], dt.isoformat()))
        except TypeError:
            pass #print charters[ch]['date']
        except KeyError:
            pass #print charters[ch]['chno'], sys.exc_info()[:2]

for c in range(315, 335):
    pprint(charters[c])

# # 
# ########### Output HTML ###############
# # # Here's a simple script to output some vanilla HTML: (NB there are some much more able templating engines than this for getting HTML out of python data structures)
# # fout = open("/Users/jjc/Documents/GiovanniScriba/V1/GScriba_Vol1.html", 'w')
# # 
# fout = open("/Users/jjc/Desktop/temp.html", 'w')
# fout.write("""
# <!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN">
# 
# <html>
# <head>
#   <title>Giovanni Scriba Vol. I</title>
#   <style>
#     h1 {text-align: center; color: #800; font-size: 16pt; margin-bottom: 0px; margin-top: 16px;}
#     ul {list-style-type: none;}
#     .sep {color: #800; text-align: center}
#     .charter {width: 650px; margin-left: auto; margin-right: auto; margin-top: 60px; border-top: double #800;}
#     .folio {color: #777;}
#     .summary {color: #777; margin: 12px 0px 12px 12px;}
#     .marginal {color: red}
#     .charter-text {margin-left: 16px}
#     .footnotes
#     .page-number {font-size: 60%}
#   </style></head>
# 
# <body>
# """)
# 
# for x in charters:
#     if "societas" in charters[x]['summary']:
#         d = charters[x].copy()
#         try:
#             if d['footnotes']: # remember, this is a list of tuples
#                 fnlist = ["<li>(%s) %s</li>" % t for t in d['footnotes']]
#                 d['footnotes'] = "<ul>" + ''.join(fnlist) + "</ul>"
#             else:
#                 d['footnotes'] = ""
#     
#             d['text'] = ' '.join(d['text'])
#         
#             blob = """
#                 <div>
#                     <div class="charter">
#                         <h1>%(chid)s</h1>
#                         <div class="folio">%(folio)s (pg. %(pgno)d)</div>
#                         <div class="summary">%(summary)s</div>
#                         <div class="marginal">%(marginal)s</div>
#                         <div class="text">%(text)s
#                         </div>
#                         <div class="footnotes">%(footnotes)s</div>
#                         </div>
#                     </div>
#                 </div>
#                 """
#             
#             fout.write(blob % d)
#             fout.write("\n\n")
#         except:
#             # insert entries noting the absence of charters on the missing pg. 214
#             erratum = """
#                 <div>
#                     <div class="charter">
#                         <h1>Charter no. %d is missing because the scan for Pg. 214 was ommited</h1>
#                     </div>
#                 </div>
#                 """  % d['chno']
#             
#             fout.write(erratum)
#         
# fout.write("""</body></html>""")