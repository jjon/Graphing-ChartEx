#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import urllib
import cgi
import json
import cgitb
cgitb.enable()

form = cgi.FieldStorage()
d = form["dir"].value

root = "bratData12-09-12/"


def getfiles():
    r=['<ul class="jqueryFileTree" style="display: none;">']    
    for f in os.listdir(root + d):
        fp = os.path.join(root,f)
        if os.path.isdir(fp):
            r.append('<li class="directory collapsed"><a href="#" rel="%s/">%s</a></li>' % (f,f))
        else:
            st = os.path.splitext(f)
            fp = root + d + f
            if st[1] == '.ann':
                e = st[1][1:] # get .ext and remove dot
                r.append('<li class="file ext_%s"><a href="#" rel="%s">%s</a></li>' % (e,fp,f))
    r.append('</ul>')
    return r

print "content-type: text/html\n"

print ''.join(getfiles())

