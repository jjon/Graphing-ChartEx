#!/usr/bin/env python
# -*- coding: utf-8 -*- #
import cgi
import cgitb

cgitb.enable(format="text")

import re
import os
import sys
import json
import fnmatch
from hashlib import sha1
from pprint import pprint
from decimal import Decimal
from rdflib import ConjunctiveGraph, Graph, Namespace, BNode, URIRef, Literal, RDF, RDFS, OWL, XSD, plugin, query
import requests
import pygraphviz as pgv
import textwrap
sys.path.insert(1, "/Users/jjc/Sites/Ann2DotRdf/")
from chartexCGIconfig import ADS_AUTH, DATADIR, deedsN3


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

Entities = {
    'Actor': True,
    'Person': True,
    'Occupation': True,
    'Institution': True,
    'Place': True,
    'PlaceRef':True,
    'Site':True,
    'SiteRef': True,
    'ImpliedSiteRef': True,
    'Event':True,
    'Transaction':True,
    'Date':True,
    'Document':True,
    'Apparatus':True
    }

chartex = Namespace("http://chartex.org/chartex-schema#")
gid = Namespace("http://chartex.org/graphid/")
uid = Namespace("http://chartex.org/user/")
crm = Namespace("http://www.cidoc-crm.org/rdfs/cidoc-crm-english-label#")
oa = Namespace("http://www.w3.org/ns/oa#")

def getContexts():
    r = requests.get("http://data.archaeologydataservice.ac.uk/sparql/repositories/chartex/contexts", headers={'Accept': 'application/json'})        
    print "Content-Type: text/plain\n"
    return r.content

def getContextGraph(uri, rf=None):
    rf = rf if rf else "text/rdf+n3"
    r = requests.get("http://data.archaeologydataservice.ac.uk/sparql/repositories/chartex/statements", headers={'Accept': rf}, params={'context': uri})
    
    return r.content

def getSubjGraph(uri, rf=None):
    """TODO: revise this so that it's a general solution to retrieve a subgraph by name. Right now it breaks if rf is not 'application/json'"""
    rf = rf if rf else "text/rdf+n3"
    pred = "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>"
    r = requests.get("http://data.archaeologydataservice.ac.uk/sparql/repositories/chartex/statements", headers={'Accept': rf}, params={'subj': uri, 'pred': pred})

    guri = eval(r.content)[0][3]
    return guri

def getSPOG(subj=None, pred=None, obj=None, context=None, rf=None):
    p = locals()
    rf = p.pop('rf') or 'application/rdf+xml'
    r = requests.get("http://data.archaeologydataservice.ac.uk/sparql/repositories/chartex/statements", headers={'Accept': rf}, params=p)

    return r.content
   
## check to see 'if exists', by checking for number:         
## print getSPOG(rf='text/integer', pred="<http://www.w3.org/ns/oa#hasTarget>", obj="<http://chartex.org/graphid/Person_10434might_bePerson_10622>")

def ADSSparql(query, result_format=None):
    result_format = result_format if result_format else "application/json"
    
    r = requests.get("http://data.archaeologydataservice.ac.uk/sparql/repositories/chartex", headers={'Accept': result_format}, params={"query":query})
    
    return r.content

def makedot(rdfgraph):
    dg = pgv.AGraph(directed=True, fontname="Times-Roman")
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
                
#             if p.split('#')[1] == 'might_be':
#                 pass
            
            ## Literals will be part of label for output node
            if isinstance(o,Literal):
                labl = rdfgraph.objects(s, chartex.ShortName).next()
                #labl += '\\n'.join(textwrap.wrap(o + '\\n', 30))
            
            ## remaining object, predicate tuples appended to edges[x]
            elif o not in edges[s]:
                edges[s].append((o, p))
        
        ## add the output nodes
        dg.add_node(s, label=labl, style='filled', fillcolor=node_colors[edges[s][0]], shape='ellipse', id=str(s), tooltip = s)

## for bmg translation TODO: still need to revise this    
    try:
        gdoc_node = rdfgraph.subjects(RDF.type, chartex.Document).next() ## NB. more than 1 Document element will break this.
        dgdoc_node = dg.get_node(gdoc_node)
        dgdoc_node.attr['label'] = 'Document: ' + '\\n'.join(x for x in rdfgraph.objects(gdoc_node, chartex.File))
        dgdoc_node.attr['fontcolor'] = "white"
        dgdoc_node.attr['fontsize'] = "18.0"
        dgdoc_node.attr['id'] = "doc_node"
    except StopIteration:
        # do something smarter than this for the case where there is no "Document" element
        pass
    
    ## could use transaction nodes to coerce root?
    ## transaction_nodes = list(rdfgraph.subjects(RDF.type, chartex.Transaction))
    
    ## generate the edges from the edges dict, rather than from the rdflib graph
    for sub in edges:
        for ob in edges[sub][1:]:
            dg.add_edge(sub, ob[0], label = ob[1].split('#')[1], fontsize="11.0", tooltip = sub + ', ' + ob[1] + ', ' + ob[0])
            ## these don't work:, labelangle="-2.0", labeldistance="1.6", labelfloat=False ; how come?
    ## If we store the whole triple in the svg edge label tooltip, we can retrieve it from the client-side svg like this:
    ## document.getElementById("edge2").getElementsByTagName('a')[0].getAttribute('xlink:title').split(', ')

    ## identify the maximum in-degree node, and make that the root of the digraph
    ## this makes for a less cluttered layout via the twopi algorithm
    maxDegreeNode = max([x for x in dg.iterdegree()], key= lambda tup: tup[1]) ## iterdegree returns a tuple (node, degree)
    dg.graph_attr.update(root = maxDegreeNode[0], ranksep="1.0", overlap=False)
    
    
    ##print json.dumps(edges, indent=4)
    return dg

def singleDocConfidenceData(guri):
    """ for a given single document graph uri (guri) this retrieves
        subject (?s) might_be object (?o) in file (?f) with text (?text) with confidence value (?goodness)
    """
    
    q = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX chartex: <http://chartex.org/chartex-schema#>
    PREFIX xsd:<http://www.w3.org/2001/XMLSchema#>
    
    SELECT DISTINCT ?s ?o ?f ?goodness ?text
    WHERE {
        GRAPH %s {?s ?p1 ?p2 .}
        ?o chartex:File ?f .
        ?o chartex:ShortName ?text .
        GRAPH ?graph { ?s chartex:might_be ?o . }
        ?graph chartex:goodness ?goodness .
    }
    """ % (guri,)
    
    return ADSSparql(q)
    
def getText(pattern, root=os.curdir):
    """ somebody else's code. The generator is good, but, didn't I do this with GREP?"""
    for path, dirs, files in os.walk(os.path.abspath(root)):
        for filename in fnmatch.filter(files, pattern):
            dtext = open(os.path.join(path, filename)).read()
            yield dtext

def visualizeDocumentGraph(guri):
    gstring = getContextGraph(guri, "application/rdf+xml")
    g = Graph()
    g.parse(data=gstring)
    dgsvg = makedot(g).draw(format='svg', prog='twopi')
    dname = g.objects(None, chartex.File).next() + '.txt'

    try:
        dtext = getText(dname, root=DATADIR).next()
    except:
        dtext = "couldn't find the damned thing anywhere. drat!"
        
    cdata = json.loads(singleDocConfidenceData(guri))['values']
    
    confidenceObj = {}
    for x in cdata:
        if x[0] not in confidenceObj:
                confidenceObj[x[0]] = [{'obj':x[1], 'file':x[2], 'confidence':x[3], 'text':x[4]}]
        else:
                confidenceObj[x[0]].append({'obj':x[1], 'file':x[2], 'confidence':x[3], 'text':x[4]})
    
    d = {
        'svg': dgsvg,
        'n3': g.serialize(format='n3'),
        'entityAttributes':
            {s:{p.partition('#')[-1]:str(o) for p,o in g.predicate_objects(s) if isinstance(o,Literal)} for s in set(g.subjects())},
        'entityRelations':
            {s:{p.partition('#')[-1]:str(o) for p,o in g.predicate_objects(s) if not isinstance(o,Literal) and not p == RDF.type} for s in set(g.subjects())},
        'charterText': dtext,
        'confidence': confidenceObj
    }

    return json.dumps(d)

def exDoc(entID, filename): #TODO: get the offsets too, via sparql
    """ vicars-choral-403.txt, Person_10428 """
    q = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX chartex: <http://chartex.org/chartex-schema#>
    select ?o
    where {
        graph %s {%s chartex:TextRange ?o .}
    }   
    """  % ('<' + gid[filename.replace('.txt','') + '>'], '<' + chartex[entID] + '>')
    
    r = ADSSparql(q)
    offsets = json.loads(r)['values']
    
    res = {}
    res['text'] = getText(filename, root=DATADIR).next()
    res['color'] = node_colors[entID.split('_')[0]]
    res['offsets'] = offsets
    return json.dumps(res)

def annotationExists(id):
    return getSPOG(subj=id, rf='text/integer')

def annotateConfidence(target, un, con, com):
    # thisAnnotation id is the full string, eg:
    # http://chartex.org/user/jjon/annotation/dc9d7cbdd0ebefb583e46fc2b79bc8cedde34d68
    # the last element being a hash (hashlib.sha1(oa:hastarget).hexdigest()) of this full string:
    # http://chartex.org/graphid/Person_11139might_bePerson_11339 (this triple is actually in there, why?, weird!
    target = re.sub('[<>]', '', target)
    thisAnnotationURI =  "http://chartex.org/user/%s/annotation/%s" % (un, sha1(target).hexdigest())
    confidence = Literal(con) if con == 'nochange' else Literal(con,datatype=XSD.decimal)
    
    if (int(annotationExists('<' + thisAnnotationURI + '>')) > 0):
        return ("You've already annotated this statement: %s \nPresumably you could make a separate annotation with a different username. If you start doing that, you should keep track of all your usernames. When we have authentication and session logic, this won't be necessary.\n\nAnnotation triples:\n" % (target,), getSingleConfidenceAnnotation('<' + thisAnnotationURI + '>', 'application/rdf+xml'))
    else:
        thisann = URIRef(thisAnnotationURI)
        g = Graph()
        bodyNode = BNode()
        triples = [
            (thisann, RDF.type, oa.Annotation),
            (thisann, oa.hasTarget, URIRef(target)),
            (thisann, oa.hasBody, bodyNode),
            (bodyNode, chartex.suggestedConfidenceMetric, confidence),
            (bodyNode, chartex.userComment, Literal(com))
        ]
        for t in triples: g.add(t)
        r = requests.post(
            "http://data.archaeologydataservice.ac.uk/sparql/repositories/chartex/statements",
            headers={'Content-Type': 'text/turtle'},
            data=g.serialize(format='turtle'),
            auth=ADS_AUTH
        )

        return (g.serialize(format='pretty-xml'), r.__dict__)

def getSingleConfidenceAnnotation(annID, result_format=None):
    # NB: annID must be in brackets <>
    
    rf = result_format if result_format else 'application/json'
    qry = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX chartex: <http://chartex.org/chartex-schema#>
    PREFIX oa: <http://www.w3.org/ns/oa#>
    PREFIX xsd:<http://www.w3.org/2001/XMLSchema#>
    CONSTRUCT {
        %s a oa:Annotation ;
            oa:hasTarget ?target ;
            chartex:userComment ?uc;
            chartex:suggestedConfidenceMetric ?cm .
        }
    WHERE {
        %s ?p ?o .
        %s oa:hasTarget ?target .
        ?o chartex:userComment ?uc;
            chartex:suggestedConfidenceMetric ?cm .
        %s rdf:type oa:Annotation .
        }
    """ % (annID, annID, annID, annID)

    r = requests.get("http://data.archaeologydataservice.ac.uk/sparql/repositories/chartex", headers={'Accept': rf}, params={'query': qry})
    return r.content
    
# print getSingleConfidenceAnnotation('<http://chartex.org/user/jjon/annotation/849140ffd067b00929d3a37fbbee37e9b3a9cc59>', 'text/rdf+n3')



def retrieveConfidenceAnnotations(result_format=None):
    rf = result_format if result_format else 'application/json'
    qry = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX chartex: <http://chartex.org/chartex-schema#>
    PREFIX oa: <http://www.w3.org/ns/oa#>
    PREFIX xsd:<http://www.w3.org/2001/XMLSchema#>
    CONSTRUCT {
        ?s a oa:Annotation ;
            oa:hasTarget ?target ;
            chartex:userComment ?uc;
            chartex:suggestedConfidenceMetric ?cm .
        }
    WHERE {
        ?s ?p ?o .
        ?s oa:hasTarget ?target .
        ?o chartex:userComment ?uc;
            chartex:suggestedConfidenceMetric ?cm .
        ?s rdf:type oa:Annotation .
        }
    """

    r = requests.get("http://data.archaeologydataservice.ac.uk/sparql/repositories/chartex", headers={'Accept': rf}, params={'query': qry})
    return r.content

def deleteTriples(json):
    r = requests.post(
        "http://data.archaeologydataservice.ac.uk/sparql/repositories/chartex/statements/delete",
        headers={'Content-Type': 'application/json'},
        data=json,
        auth=ADS_AUTH
    )
    return r.content


form = cgi.FieldStorage()

if __name__ == "__main__":
    try:
        if 'getConfidenceAnnotations' in form:
            format = form.getvalue('format')
            print "Content-type: text/plain\n\n"
            print
            print retrieveConfidenceAnnotations(format)
                        
        if 'target' in form:
            target = form.getvalue('target')
            un = form.getvalue('username')
            con = form.getvalue('confidence')
            com = form.getvalue('comment')
            result, debug = annotateConfidence(target, un, con, com)
            print "Content-type: text/plain\n\n"
            print
            print result, debug

        if 'howto' in form:
            howto = open('/Users/jjc/Sites/Ann2DotRdf/cartametallon/howto.html', 'r').read()
            print "Content-Type: text/html\n\n"
            print
            print howto
            
        if 'exDoc' in form:
            filename = form.getvalue('exDoc')
            entID = form.getvalue('entID')
            print "Content-Type: application/json\r\n\r\n"
            print
            print exDoc(entID, filename)
            
        if 'getContexts' in form:
            print "Content-Type: text/plain\n\n"
            print getContexts()

        if 'mightBeGoodness' in form:
            entID = form.getvalue('mightBeGoodness')
            query = """PREFIX chartex: <http://chartex.org/chartex-schema#> select ?entity ?text ?file ?goodness WHERE { ?entity chartex:TextSpan ?text ; chartex:File ?file . GRAPH ?g {  chartex:%s  chartex:might_be ?entity . } ?g chartex:goodness ?goodness . }""" % (entID)
    
            print "Content-Type: application/json\r\n\r\n"
            print
            print ADSSparql(query)
            
        if 'getDocumentContexts' in form:
            query = """select distinct ?g WHERE { GRAPH ?g { ?s ?p ?o } . FILTER regex(str(?g), "vicars-choral") }"""

            print "Content-Type: application/json\r\n\r\n"
            print
            print ADSSparql(query)
            
        if 'graphMe' in form:
            charter = form.getvalue('graphMe')
            uri = "<http://chartex.org/graphid/" + charter + ">"
            
            print "Content-Type: application/json\r\n\r\n"
            print visualizeDocumentGraph(uri)
    
        if 'bugtest' in form:
            print "Content-Type: text/plain\n\n"
            print "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Quisque sollicitudin. Fusce varius pellentesque ligula. Proin condimentum purus a nunc tempor pellentesque.\n"
    
        if not form:
            
            print "Content-Type: text/plain\n"
            print "\n"
            print "lookin' for somthin' ?"
            
    except StandardError as e:
        print "Content-Type: text/html\n"
        
        print e.__dict__

# PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
# PREFIX chartex: <http://chartex.org/chartex-schema#>
# PREFIX xsd:<http://www.w3.org/2001/XMLSchema#>


# for a given subject, get object of might_be, that object's text string and file id, and the ?goodness factor for that relationship.
# select ?entity ?text ?file ?goodness 
#     WHERE { 
#     ?entity   <http://chartex.org/chartex-schema#TextSpan>    ?text ;
#               <http://chartex.org/chartex-schema#File>        ?file .

#     GRAPH ?g  {<http://chartex.org/chartex-schema#Person_1876>  chartex:might_be ?entity . }

#     ?g chartex:goodness ?goodness . 
# }

# construct {?s ?p ?o .}
#     from named {
#         graph ?g { <http://chartex.org/graphid/vicars-choral-399>

# 
# """
# select distinct ?g
#     WHERE { GRAPH ?g { ?s ?p ?o } .
#     FILTER regex(str(?g), "vicars-choral")
# }
# """