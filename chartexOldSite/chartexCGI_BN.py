#!/usr/bin/env python
# -*- coding: utf-8 -*- #

from rdflib import Graph, ConjunctiveGraph, Namespace, Literal, RDF, RDFS, OWL, XSD, BNode
import re
import os
import sys
import cgi
import cgitb
import json
from pprint import pprint
import requests
from collections import namedtuple

cgitb.enable(format = "text")
form = cgi.FieldStorage()
DATADIR = '/Users/jjc/Sites/Ann2DotRdf/chartex'


chartex = Namespace("http://yorkhci.org/chartex-schema#")
chartexDoc = Namespace("http://yorkhci.org/chartex-schema/")
crm = Namespace("http://www.cidoc-crm.org/rdfs/cidoc-crm-english-label#")

def ann2rdf_bn(f_path):
    g = Graph()
    Ent = namedtuple("Ent", ("eid", "entity", "start", "end", "text", "bn"))

    g.bind("chartex", "http://yorkhci.org/chartex-schema#")
    g.bind("crm", "http://www.cidoc-crm.org/rdfs/cidoc-crm-english-label#")
    
    x_path, ext = os.path.splitext(f_path)
    charter_id = os.path.basename(x_path)
    doc_path = x_path + '.txt'
    
    annfile = [line.replace('•','.') for line in open(f_path, "r").readlines()]
    doctext = open(doc_path, "r").read().replace('•','.')
    
    entities = [x for x in annfile if x.startswith('T')]
    relations = [x for x in annfile if x.startswith('R')]
    transitives = [x for x in annfile if x.startswith('*')]
    attributes = [x for x in annfile if x.startswith('A')]
    ents = {}
    for ent in entities:
        lst = ent.split(None,4)
        lst.append(BNode())
        e = Ent._make(lst)
        if e.eid not in ents:
            ents[e.eid] = e
        g.add((e.bn, RDF.type, chartex[e.entity]))
        g.add((e.bn, chartex.textRange, Literal((int(e.start), int(e.end)))))
        g.add((e.bn, chartex.textSpan, Literal(e.text.strip())))
        if e.entity == "Document":
            g.add(( e.bn, chartex.textData, Literal(doctext, datatype=XSD.string) ))
    
    
    for r in relations:
        key, prop, a1, a2, note = re.split('\s+', r, maxsplit=4)
        s = a1.split(':')[1]
        o = a2.split(':')[1]
        g.add((ents[s].bn, chartex[prop], ents[o].bn))
    
    for t in transitives:
        key, prop, nodes_string = t.split(None, 2)
        l = nodes_string.split()
        try:
            while l:
                g.add( (ents[l.pop()].bn, chartex[prop], ents[l[-1]].bn) )
        except IndexError:
            pass
        
        
    return g

def find_roots(graph,prop,roots=None): 
    """
    Ripped off from rdflib-extras. Much cleverer than the listcomp I had, use this instead
    """
    non_roots=set()
    if roots==None: roots=set()
    for x,y in graph.subject_objects(prop): 
        non_roots.add(x)
        if x in roots: roots.remove(x)
        if y not in non_roots: 
            roots.add(y)
    return roots

def smushSameAs(graph):
    firsts = find_roots(graph,chartex.same_as)
    smush_lists = [list(graph.transitive_subjects(chartex.same_as,x)) for x in firsts]
    for idlist in smush_lists:
        new_sub = ''.join(idlist)
        for id in idlist:
            for p,o in graph.predicate_objects(BNode(id)):
                if p != chartex.same_as: graph.add((BNode(new_sub),p,o))
            
            for s,p in graph.subject_predicates(BNode(id)):
                graph.remove((s,p,BNode(id)))
                graph.add((s,p,BNode(new_sub)))
                
            graph.remove((BNode(id),None,None))
    return graph


def generateDocumentGraph(filepath, serialization_format=None):
    g = ann2rdf_bn(filepath)
    smushSameAs(g)
    if serialization_format: print g.serialize(format=serialization_format)
    else: return g


def generateCorpusGraph(ann_files_dir, serialization_format):
    g = ConjunctiveGraph()
    g.bind("chartex", "http://yorkhci.org/chartex-schema#")
    g.bind("crm", "http://www.cidoc-crm.org/rdfs/cidoc-crm-english-label#")

    for f in os.listdir(ann_files_dir):
        annotationFile = ''
        if f.endswith('.ann'):
            docid = os.path.splitext(f)[0]
            f_path = os.path.join(ann_files_dir,f)
            ctxt = "<http://example.com/graph/" + docid + ">"
            graph = Graph(g.store, ctxt)
            for t in generateDocumentGraph(f_path).triples((None,None,None)):
                graph.add(t)
                
    if serialization_format:
        return g.serialize(format=serialization_format)
    else: return g


# filepath = "/Users/jjc/Sites/Ann2DotRdf/chartex/deeds/deeds-00880074.ann"
# print generateDocumentGraph(filepath, 'pretty-xml')


if __name__ == "__main__":
    try:
        if "ADSUpload" in form:
            sd = form["serialDir"].value
            outgoingGraph = generateCorpusGraph(sd, serialization_format=None)
            for c in outgoingGraph.contexts():
                r = requests.post("http://data.archaeologydataservice.ac.uk/sparql/repositories/chartex/statements", headers={'Content-Type': 'text/turtle'}, data=c.serialize(format='turtle'), auth=('ctuser', 'Tex4+char'), params={"context":c.identifier, "commit":200})
            
            print "Content-Type: text/plain\n\n"
            print "We've added %s statements to our ADS triple store" % r.content
           
        elif "serialDir" in form:
            print "Content-Type: text/plain\n\n"
            sd = form["serialDir"].value
            sf = form["serialFormat"].value
            if not os.path.isdir(sd):
                print "Content-Type: text/plain\n\n"
                print "unknown directory: %s" % sd
            else:
                print "Content-Type: text/plain\n"
                print generateCorpusGraph(sd, sf)  
                
        
    except StandardError as e:
        print "Content-Type: text/html\n"
        
        print e
