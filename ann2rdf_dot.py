#!/usr/bin/python
# -*- coding: utf-8 -*- #

from rdflib import Graph, Namespace, Literal, RDF, RDFS, OWL, XSD
import pygraphviz as pgv
import textwrap
import subprocess
import cgi
import cgitb
import json
import os
import re

cgitb.enable()
form = cgi.FieldStorage()
DATADIR = '/Users/jjc/Sites/Ann2DotRdf/chartex'

## Because bbedit doesn't access env. vars and so can't find twopi at /usr/local/bin
os.environ['PATH'] = "/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

## Annotation file to graph
## filepath = "/Users/jjc/Sites/Ann2DotRdf/chartex/deeds/deeds-00880188.ann"
filepath = form["fp"].value if "fp" in form else None
searchstring = form["searchstring"].value if "searchstring" in form else None
entity = form["entity"].value if "entity" in form else None
editDistance = form["editDistance"].value if "editDistance" in form else None
dirToSearch = form["dirToSearch"].value if "dirToSearch" in form else None
filetype = form["filetype"].value if "filetype" in form else None

## graph, instance of rdflib.Graph
g = Graph()

## digraph, instance of pygraphviz.AGraph
dg = pgv.AGraph(strict=False, directed=True, ranksep="2.5", fontname="Times-Roman")

## namespaces for rdflib. REMEMBER: you can access these via dot notation, like this: this.T1
g.bind("chartex", "http://yorkhci.org/chartex-schema#")
g.bind("crm", "http://www.cidoc-crm.org/rdfs/cidoc-crm-english-label#")
this = Namespace("#")
chartex = Namespace("http://yorkhci.org/chartex-schema#")
crm = Namespace("http://www.cidoc-crm.org/rdfs/cidoc-crm-english-label#")

## colors for output nodes
node_colors = {
    'Person': '#00ffff',
    'Occupation': '#00aaff',
    'Institution': '#00a8aa',
    'Place': '#ff5577',
    'PlaceRef':'#ff5577',
    'Site':'#ff0000',
    'SiteRef': '#ff0000',
    'Event':'#ffcc00',
    'Transaction':'#ff9500',
    'Date':'#90ee90',
    'Document':'#007700',
    'Apparatus':'#00aa00'
    }

def ann2rdf(annfile, docstr):
    """still to deal with annotator's notes.
    This returns a raw graph with no smushing
    """
    
    for line in annfile:
        if line[0] == 'T':
            eid, entity, start, end, text = re.split('\s+', line, maxsplit=4)
            g.add((this[eid], RDF.type, chartex[entity]))
            g.add((this[eid], chartex.textRange, Literal((int(start), int(end)))))
            g.add((this[eid], chartex.textSpan, Literal(text)))
        if line[0] == 'R':
            key, prop, a1, a2, note = re.split('\s+', line, maxsplit=4)
            g.add((this[a1.split(':')[1]], chartex[prop], this[a2.split(':')[1]]))
        if line[0] == "*":
            key, prop, a1, a2, note = re.split('\s+', line, maxsplit=4)
            g.add((this[a1], chartex[prop], this[a2]))
            
    s = g.subjects(RDF.type, chartex.Document).next()
    g.add((s, chartex.textData, Literal(docstr,datatype=XSD.string)))
    return g
    
def smush_sameas(annfile):
    """ concatenate entity ids of entities marked same_as,
    use the result as the subject in aggregated statements,
    then delete the original entity statements from the graph.
    """
    sameas = [re.split('\s+', x)[2:-1] for x in annfile if 'same_as' in x]
    for idlist in sameas:
        new_sub = ''.join(idlist)
        
        for id in idlist:
            # add new aggregate subject, and add p,o from the old subjects.
            for p,o in g.predicate_objects(this[id]):
                g.add((this[new_sub],p,o))
                
            # remove triples pointing to old individual subjects,
            # replace w/triples pointing to new aggregate subject
            for s,p in g.subject_predicates(this[id]):
                g.remove((s,p,this[id]))
                g.add((s,p,this[new_sub]))
            
            # remove old individual subjects
            g.remove((this[id],None,None))
    return g
    
def makedot(rdfgraph):
    edges = {}

    for s in rdfgraph.subjects(): ## s will be the entity nodes. For each node key we'll wind up w/a list like this as value:
    ## [u'Person', (rdflib.term.URIRef('#T27T24'), u'is_a_previous_tenant_of'), (rdflib.term.URIRef('#T4'), u'is_daughter_of')]
        edges[s] = []
        labl = ""
        
        ## build label and chose edges to show edges[x][0] for entity type
        for p,o in rdfgraph.predicate_objects(s):
            if p.split('#')[1] == 'type':
                edges[s].insert(0, o.split('#')[1])
                continue
            
            ## Literals will be part of label for output node
            if isinstance(o,Literal):
                labl += '\\n'.join(textwrap.wrap(o + '\\n', 30))
            
            ## remaining object, predicate tuples appended to edges[x]
            elif o not in edges[s]:
                edges[s].append((o, p.split('#')[1]))
        
        ## add the output nodes
        dg.add_node(s, label=labl, style='filled', fillcolor=node_colors[edges[s][0]], shape='ellipse', id="node" + str(s).replace('#',''))
    
    gdoc_node = g.subjects(RDF.type, chartex.Document).next() ## NB. more than 1 Document element will break this.
    
    dgdoc_node = dg.get_node(gdoc_node)
    dgdoc_node.attr['label'] = 'Document: ' + '\\n'.join(x for x in g.objects(gdoc_node, chartex.textSpan)).replace('\n','')
    dgdoc_node.attr['fontcolor'] = "white"
    dgdoc_node.attr['fontsize'] = "18.0"
    dgdoc_node.attr['id'] = "doc_node"
    
    for sub in edges:
        for ob in edges[sub][1:]:
            dg.add_edge(sub, ob[0], label = ob[1], labelfontsize="11", labelangle=0, labeldistance=3, labelfloat=False)
    
    ## identify the maximum in-degree node, and make that the root of the digraph
    ## this makes for a less cluttered layout via the twopi algorithm
    maxDegreeNode = max([x for x in dg.iterdegree()], key= lambda tup: tup[1]) ## iterdegree returns a tuple (node, degree)
    dg.graph_attr.update(root = maxDegreeNode[0], ranksep="3 equally", overlap=False)
    
    
    ##print json.dumps(edges, indent=4)
    return dg

def graphPage(f,s):
    fin = open(f,'r')
    annotationFile = fin.readlines()
    if len(annotationFile) <= 1: ## This isn't the right way to catch errors!
        print "Content-Type: text/plain\n"
    
        print "<annFileError>"
    else:
        annotationFile = [line.replace('•','.') for line in annotationFile]
        txtfile = open(f.replace('.ann','.txt')).readlines()
        txtfile = [line.replace('•','.') for line in txtfile]
        docid = re.split('\s+', [line for line in annotationFile if re.match('^T\d+\tDocument',line)][0], maxsplit=4)[-1]
        docstr = ''.join(txtfile)
        
        ann2rdf(annotationFile, docstr)
        smush_sameas(annotationFile)
        
        dgsvg = makedot(g).draw(format='svg', prog='twopi')
        
        print "Content-Type: text/plain\n"
    
        print dgsvg
    
        print '<filedelimiter>'
        
        print g.serialize(format = s)
        
        print '<filedelimiter>'
        
        print docstr

def lev(seq1, seq2):
    """
    From Michael Homer's blog:
    http://mwh.geek.nz/2009/04/26/python-damerau-levenshtein-distance/
    
    Calculate the Damerau-Levenshtein distance between sequences.

    This distance is the number of additions, deletions, substitutions,
    and transpositions needed to transform the first sequence into the
    second. Although generally used with strings, any sequences of
    comparable objects will work.

    Transpositions are exchanges of *consecutive* characters; all other
    operations are self-explanatory.

    This implementation is O(N*M) time and O(M) space, for N and M the
    lengths of the two sequences.

    >>> dameraulevenshtein('ba', 'abc')
    2
    >>> dameraulevenshtein('fee', 'deed')
    2

    It works with arbitrary sequences too:
    >>> dameraulevenshtein('abcd', ['b', 'a', 'c', 'd', 'e'])
    2
    """
    # codesnippet:D0DE4716-B6E6-4161-9219-2903BF8F547F
    # Conceptually, this is based on a len(seq1) + 1 * len(seq2) + 1 matrix.
    # However, only the current and two previous rows are needed at once,
    # so we only store those.
    oneago = None
    thisrow = range(1, len(seq2) + 1) + [0]
    for x in xrange(len(seq1)):
        # Python lists wrap around for negative indices, so put the
        # leftmost column at the *end* of the list. This matches with
        # the zero-indexed strings and saves extra calculation.
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

def splitAnnLine(line):
    #eid, entity, start, end, text
    return re.split('\s+', line, maxsplit=4)

def levDistance(searchstring, entity, editDistance, dirToSearch):
    ##TODO: change use of 'file' as variable here: don't shadow file()
    
## can't just feed these to splitAnnLine(): fewer elements, use different split
#2	AnnotatorNotes T2	Summary identical to 32, though originals are not identical
#1	AnnotatorNotes T1	{"piece_id": "5471224", "date_text": "1505 Nov 24"}
    if dirToSearch == "All":
        annfiles = [os.path.join(t[0],file) for t in os.walk(DATADIR) for file in t[2] if file.endswith('ann')]
    else:
        annfiles = [os.path.join(dirToSearch,x) for x in os.listdir(dirToSearch) if x.endswith('ann')]
    result = []
    for file in annfiles:
        entities = [line for line in open(file,'r').readlines() if line.startswith('T')]
        for line in entities:
            eid, entype, start, end, text = splitAnnLine(line)
            if entype == entity:
                distance = lev(searchstring.lower(),text.strip().lower())
                if distance <= int(editDistance):
                    result.append({'file':file, 'eid':eid, 'start':start, 'end':end, 'text':text.strip(), 'distance':distance}) 
        
    return json.dumps(result)
                

def match_span_with_context(m, ctxt_len, s):
    """ get m from re.finditer() which returns a generator of matches """
    m = m.span()
    theMatch = s[m[0]:m[1]]
    start = max(0, m[0]-ctxt_len)
    finish = min(m[1]+ctxt_len, len(s))
    lstr = s[start:m[0]]
    rstr = s[m[1]:finish]
    return "...%s<span class=\"match-highlight\">%s</span>%s...<br />" % (lstr, theMatch, rstr)


def simpleSearch(searchstring, dirToSearch):
    """ TODO: not implemented client-side. Let's go with the grep function below instead
        TODO: change use of 'file' as variable here: don't shadow file() """
        
    if dirToSearch == "All":
        txtfiles = [os.path.join(t[0],file) for t in os.walk(DATADIR) for file in t[2] if file.endswith('txt')]
    else:
        txtfiles = [os.path.join(dirToSearch,x) for x in os.listdir(dirToSearch) if x.endswith('txt')]

    for file in txtfiles:
        f = open(file)
        text = re.sub('\n',' ',f.read())
        f.close()
        rpath = os.path.relpath(file, start=DATADIR)
        keyword = re.compile(searchstring, re.IGNORECASE)
        
        for m in re.finditer(keyword, text):
            return "%s: %s" % (rpath, match_span_with_context(m, 30, text.encode('utf-8')))

def grep(arg, dirpath, ext):
    """ -R to recurse, -P to get perl type regexes
        TODO: change use of 'file' as variable here: don't shadow file()
        This is pretty clumsy. after line.split('\x00'),
        really have to do something smarter with the result."""
    dirpath = DATADIR if dirpath == 'All' else dirpath
    suffix = "*." + ext
    p = subprocess.Popen(['grep', '-RPZi', arg, dirpath, '--include', suffix], stdout=subprocess.PIPE)
    stdout, stderr = p.communicate()
    
    lines = []
    for line in stdout.split('\n'):
        if line:
            path, data = line.split('\x00')
            file = os.path.relpath(path, start=DATADIR)
            if ext == 'ann': ## have to parse AnnotatorNotes separately?
                eid, entity, start, end, text = splitAnnLine(data)
                if entity == "AnnotatorNotes":
                    lines.append((file, entity, data))
                else:
                    lines.append((file, entity, text))
            elif ext == 'txt':
                lines.append((re.sub('.txt', '.ann', file), data))

    return json.dumps(lines)

    
if __name__ == "__main__":
    if filepath:
        graphPage(filepath, 'n3')
    
    elif editDistance:
        print "Content-Type: application/json\n"
        
        print levDistance(searchstring, entity, editDistance, dirToSearch)
    
    elif filetype:
        print "Content-Type: application/json\n"
        
        print grep(searchstring, dirToSearch, filetype)
        


###############################################################################
#T1	Document 0 17	vicars-choral-413
#['T43', 'Person', '847', '864', 'Roger de Grendale\n']
#['R19', 'is_recipient_in', 'Arg1:T24', 'Arg2:T23', '']
# 'R19': {'arg1': 'T24', 'arg2': 'T23', 'note': '', 'prop': 'is_recipient_in'}
# *	same_as T48 T7 T55 T56 T57 T58 T62 T63
# >>> g.add((statementId, RDF.type, RDF.Statement))
# >>> g.add((statementId, RDF.subject, URIRef(u'http://rdflib.net/store/ConjunctiveGraph')))
# >>> g.add((statementId, RDF.predicate, RDFS.label))
# >>> g.add((statementId, RDF.object, Literal("Conjunctive Graph")))
#   <rdf:Property rdf:ID="P131F.is_identified_by">
#     <rdfs:comment>This property identifies a name used specifically to identify an E39 Actor. This property is a specialisation of P1 is identified by (identifies) is identified by.</rdfs:comment>
#     <rdfs:domain rdf:resource="#E39.Actor" />
#     <rdfs:range rdf:resource="#E82.Actor_Appellation" />
#     <rdfs:subPropertyOf rdf:resource="#P1F.is_identified_by" />
#   </rdf:Property>

