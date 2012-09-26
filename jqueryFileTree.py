#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import cgi
import cgitb
cgitb.enable()

form = cgi.FieldStorage()
rel_folder = form["dir"].value
root = '/Users/jjc/Sites/Ann2DotRdf/bratData12-09-12'
d = os.path.join(root,rel_folder)

def getfiles():
    r=['<ul class="jqueryFileTree" style="display: none;">']    
    for f in os.listdir(d):
        fp = os.path.join(d,f)
        if os.path.isdir(fp):
            r.append('<li class="directory collapsed"><a href="#" rel="%s/">%s</a></li>' % (fp,f))
        else:
            st = os.path.splitext(f)
            if st[1] == '.ann':
                e = st[1][1:] # get .ext and remove dot
                r.append('<li class="file ext_%s"><a href="#" rel="%s">%s</a></li>' % (e,fp,f))
    r.append('</ul>')
    return r

print "content-type: text/html\n"

print ''.join(getfiles())
