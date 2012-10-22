#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import cgi
import cgitb
import json
cgitb.enable()

form = cgi.FieldStorage()
dirs = form["dirs"].value if "dirs" in form else None
d = form["dir"].value if "dir" in form else None
## dirs = json.dumps([x[0] for x in os.walk('/Users/jjc/Sites/Ann2DotRdf/chartex') if not x[1]])

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
    ## r.append('<div id="directories" style="display:none">'+ dirs +'</dir>')
    return r

if d:
    print "content-type: text/html\n"
    
    print ''.join(getfiles())

if dirs:
    print "content-type: application/json\n"
    
    print json.dumps([x[0] for x in os.walk(dirs) if not x[1]])
    


