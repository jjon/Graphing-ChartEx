#!/usr/bin/env python
# -*- coding: utf-8 -*- #


from rdflib import ConjunctiveGraph, Graph, Namespace, Literal, RDF, RDFS, OWL, XSD, plugin, query
from subprocess import Popen, PIPE
import pygraphviz as pgv
import re
import os
import sys
import textwrap
import cgi
import cgitb
import json
import requests
from chartexCGIconfig import ADS_AUTH, DATADIR, deedsN3

cgitb.enable(format="text")

plugin.register(
  "sparql", query.Processor,
  "rdfextras.sparql.processor", "Processor")
plugin.register(
  "sparql", query.Result,
  "rdfextras.sparql.query", "SPARQLQueryResult")


chartex = Namespace("http://yorkhci.org/chartex-schema#")
chartexDoc = Namespace("http://yorkhci.org/chartex-schema/")
crm = Namespace("http://www.cidoc-crm.org/rdfs/cidoc-crm-english-label#")
node_colors = {
    'Actor': '#0000ff',
    'Person': '#00ffff',
    'Occupation': '#00aaff',
    'Institution': '#00a8aa',
    'Place': '#ff5577',
    'PlaceRef':'#ff5577',
    'Site':'#ff0000',
    'SiteRef': '#ff0000',
    'ImpliedSiteRef': '#ff0000',
    'Event':'#ffcc00',
    'Transaction':'#ff9500',
    'Date':'#90ee90',
    'Document':'#007700',
    'Apparatus':'#00aa00'
    }

def ann2rdf(g, f_path):
    x_path, ext = os.path.splitext(f_path)
    charter_id = os.path.basename(x_path)
    doc_path = x_path + '.txt'
    
    annfile = [line.replace('•','.') for line in open(f_path, "r").readlines()]
    doctext = open(doc_path, "r").read().replace('•','.')

    this = Namespace("http://yorkhci.org/chartex-schema/"+ charter_id + "#")
    
    implied_siterefs = []
        
    for line in annfile:
        if line[0] == 'T':
            eid, entity, start, end, text = re.split('\s+', line, maxsplit=4)
            g.add((this[eid], RDF.type, chartex[entity]))
            g.add((this[eid], chartex.textRange, Literal((int(start), int(end)))))
            g.add((this[eid], chartex.textSpan, Literal(text.strip())))
            if entity == "Document":
                g.add(( this[eid], chartex.textData, Literal(doctext, datatype=XSD.string) ))

        if line[0] == 'R':
            key, prop, a1, a2, note = re.split('\s+', line, maxsplit=4)
            g.add((this[a1.split(':')[1]], chartex[prop], this[a2.split(':')[1]]))
        if line[0] == "*":
            key, prop, a1, a2, note = re.split('\s+', line, maxsplit=4)
            g.add((this[a1], chartex[prop], this[a2]))
        if line[0] == "A": # for example: A2	Implied-SiteRef T17 genitive
            id, attr, ent, val = re.split('\s+', line, maxsplit=3)
            g.add((this[ent], RDF.type, chartex.ImpliedSiteRef))
            g.add((this[ent], chartex.caseAttr, chartex[val]))

def smush_sameas(g, f_path):
    """ concatenate entity ids of entities marked same_as,
    use the result as the subject in aggregated statements,
    then delete the original entity statements from the graph.
    """
    x_path, ext = os.path.splitext(f_path)
    charter_id = os.path.basename(x_path)
    this = Namespace("http://yorkhci.org/chartex-schema/"+ charter_id + "#")

    annfile = [line.replace('•','.') for line in open(f_path, "r").readlines()]
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

def makedot(rdfgraph):
    dg = pgv.AGraph(strict=False, directed=True, ranksep="2.5", fontname="Times-Roman")
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
    
    gdoc_node = rdfgraph.subjects(RDF.type, chartex.Document).next() ## NB. more than 1 Document element will break this.
    
    dgdoc_node = dg.get_node(gdoc_node)
    dgdoc_node.attr['label'] = 'Document: ' + '\\n'.join(x for x in rdfgraph.objects(gdoc_node, chartex.textSpan)).replace('\n','')
    dgdoc_node.attr['fontcolor'] = "white"
    dgdoc_node.attr['fontsize'] = "18.0"
    dgdoc_node.attr['id'] = "doc_node"
    
    ## generate the edges from the edges dict, rather than from the rdflib graph
    for sub in edges:
        for ob in edges[sub][1:]:
            dg.add_edge(sub, ob[0], taillabel = ob[1], labelfontsize="11.0", labelangle=0, labeldistance=6, labelfloat=False)
    
    ## identify the maximum in-degree node, and make that the root of the digraph
    ## this makes for a less cluttered layout via the twopi algorithm
    maxDegreeNode = max([x for x in dg.iterdegree()], key= lambda tup: tup[1]) ## iterdegree returns a tuple (node, degree)
    dg.graph_attr.update(root = maxDegreeNode[0], ranksep="3 equally", overlap=False)
    
    
    ##print json.dumps(edges, indent=4)
    return dg

def generateCorpusGraph(ann_files_dir, serialization_format):
    g = ConjunctiveGraph()
    g.bind("chartex", "http://yorkhci.org/chartex-schema#")
    g.bind("crm", "http://www.cidoc-crm.org/rdfs/cidoc-crm-english-label#")

    for f in os.listdir(ann_files_dir):
        annotationFile = ''
        if f.endswith('.ann'):
            f_path = os.path.join(ann_files_dir,f)
            ann2rdf(g, f_path)
        
    return g.serialize(format=serialization_format)

def generateDocumentGraph(filepath, serialization_format):
    g = Graph()
    g.bind("chartex", "http://yorkhci.org/chartex-schema#")
    g.bind("crm", "http://www.cidoc-crm.org/rdfs/cidoc-crm-english-label#")
    
    ann2rdf(g, filepath)
    smush_sameas(g, filepath)
    
    textData = g.objects(None, chartex.textData).next()
    dgsvg = makedot(g).draw(format='svg', prog='twopi')
    rdf = g.serialize(format=serialization_format).replace('<',"&lt;")
    
    return dgsvg + '<filedelimiter>' + rdf + '<filedelimiter>' + textData

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

def levDistance(searchstring, entity, editDistance, dirToSearch):
    ##TODO: bug in document text highlight - client
    if dirToSearch == "All":
        annfiles = [os.path.join(t[0],f) for t in os.walk(DATADIR) for f in t[2] if f.endswith('ann')]
    else:
        annfiles = [os.path.join(dirToSearch,x) for x in os.listdir(dirToSearch) if x.endswith('ann')]
    result = []
    for f in annfiles:
        entities = [line for line in open(f,'r').readlines() if line.startswith('T')]
        for line in entities:
            eid, entype, start, end, text = re.split('\s+', line, maxsplit=4)
            if entype == entity:
                distance = lev(searchstring.lower(),text.strip().lower())
                if distance <= int(editDistance):
                    result.append({'file':f, 'eid':eid, 'start':start, 'end':end, 'text':text.strip(), 'distance':distance}) 
        
    return json.dumps(result)

def grep(arg, dirpath, ext):
    """ -R to recurse, -P to get perl type regexes
        TODO: change use of 'file' as variable here: don't shadow file()
        This is pretty clumsy. after line.split('\x00'),
        really have to do something smarter with the result."""
    dirpath = DATADIR if dirpath == 'All' else dirpath
    suffix = "*." + ext
    p = Popen(['grep', '-RPZi', arg, dirpath, '--include', suffix], stdout=PIPE)
    stdout, stderr = p.communicate()
    
    lines = []
    for line in stdout.split('\n'):
        if line:
            path, data = line.split('\x00')
            file = os.path.relpath(path, start=DATADIR)
            if ext == 'ann': ## have to parse AnnotatorNotes separately?
                eid, entity, start, end, text = re.split('\s+', line, maxsplit=4)
                if entity == "AnnotatorNotes":
                    lines.append((file, entity, data))
                else:
                    lines.append((file, entity, text))
            elif ext == 'txt':
                lines.append((re.sub('.txt', '.ann', file), data))

    return json.dumps(lines)

def sparql(deedsN3, query):
    testgraph = Graph()
    testgraph.parse(deedsN3, format='n3')
    result = testgraph.query(query)
    print result.serialize(format='n3')

def addTriples(dir):
    graph = generateCorpusGraph(dir, 'turtle')
    
    return requests.post("http://data.archaeologydataservice.ac.uk/sparql/repositories/chartex/statements", headers={'Content-Type': 'text/turtle'}, data=graph, auth=ADS_AUTH, params={"commit":200})
    
def deleteTriples():
    return requests.delete("http://data.archaeologydataservice.ac.uk/sparql/repositories/chartex/statements", auth=ADS_AUTH)
    
def getTriples():
    return requests.get("http://data.archaeologydataservice.ac.uk/sparql/repositories/chartex/statements", headers={'Accept': 'text/rdf+n3'})

form = cgi.FieldStorage()

if __name__ == "__main__":
    try:
        if "fp" in form:
            print "Content-Type: text/plain\n"
            print generateDocumentGraph(form["fp"].value, 'n3')
        
        if "editDistance" in form:
            print "Content-Type: application/json\n"
            
            print levDistance(
                form["searchstring"].value,
                form["entity"].value,
                form["editDistance"].value,
                form["dirToSearch"].value
                )
            
        if "filetype" in form:
            print "Content-Type: application/json\n"
            
            print grep(
                form["searchstring"].value,
                form["dirToSearch"].value,
                form["filetype"].value
                )

        if "sparqlQuery" in form:
            print "Content-Type: text/html\n"
            
            print sparql(deedsN3, form["sparqlQuery"].value)
            
        if "serialDir" in form:
            sd = form["serialDir"].value
            sf = form["serialFormat"].value
            if not os.path.isdir(sd):
                print "Content-Type: text/plain\n\n"
                print "unknown directory: %s" % sd
            else:
                print "Content-Type: text/plain\n"
                print generateCorpusGraph(sd, sf)                
        
        if 'ADSadd' in form:
            d = form["addDir"].value
            print "Content-Type: text/plain\n"
            
            print "added: %s triples to our ADS triple store" % addTriples(d).content
        
        if 'ADSget' in form:
            print "Content-Type: text/plain\n"
            
            print getTriples().content
                        
        if 'ADSdelete' in form:
            print "Content-Type: text/plain\n"
            
            print "deleted all the triples (%s) from our ADS triple store" % deleteTriples().content
        
    except StandardError as e:
        print "Content-Type: text/html\n"
        
        print e
