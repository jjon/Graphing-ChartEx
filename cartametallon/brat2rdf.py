#!/usr/bin/env python
# -*- coding: utf-8 -*- #

import cgi
import cgitb
import re
import os
import sys
import json
import fnmatch
from hashlib import sha1
from pprint import pprint
from decimal import Decimal

sys.path.insert(0, "/Users/jjc/ComputerInfo/RDF/rdflib/")
import rdflib ## problem n3 parsing problem in visualizeDocumentGraph doesn't go away with import of dev version of rdflib.
from rdflib import ConjunctiveGraph, Graph, Namespace, BNode, URIRef, Literal, RDF, RDFS, OWL, XSD, plugin, query

import requests
import pygraphviz as pgv
import textwrap

sys.path.insert(1, "/Users/jjc/Sites/Ann2DotRdf/")
from localAGconfig import localAG_AUTH, AGVM_VC_REPO, DATADIR, deedsN3

tstdoc = DATADIR + "deeds/deeds-00880132.ann"
chartex = Namespace("http://chartex.org/chartex-schema#")
chartexDoc = Namespace("http://chartex.org/chartex-schema/")
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


def ann2rdf(f_path):
    g = Graph()
    x_path, ext = os.path.splitext(f_path)
    charter_id = os.path.basename(x_path)
    doc_path = x_path + '.txt'
    
    annfile = [line.replace('•','.') for line in open(f_path, "r").readlines()]
    doctext = open(doc_path, "r").read().replace('•','.')

    this = Namespace("http://chartex.org/document/"+ charter_id + "#")
    
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
            key, prop, nodes_string = line.split(None, 2)
            l = nodes_string.split()
            try:
                while l:
                    g.add( (this[l.pop()], chartex[prop], this[l[-1]]) )
            except IndexError:
                continue
            
        if line[0] == "A": # for example: A2	Implied-SiteRef T17 genitive
            id, attr, ent, val = re.split('\s+', line, maxsplit=3)
            g.add((this[ent], RDF.type, chartex.ImpliedSiteRef))
            g.add((this[ent], chartex.caseAttr, chartex[val]))
            
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
        new_frag = ''.join([x.rpartition('#')[-1] for x in idlist])
        new_sub = x.defrag() + '#' + new_frag
        for id in idlist:
            for p,o in graph.predicate_objects(id):
                if p != chartex.same_as: graph.add((URIRef(new_sub),p,o))
            
            for s,p in graph.subject_predicates(id):
                graph.remove((s,p,id))
                graph.add((s,p,URIRef(new_sub)))
                
            graph.remove((id,None,None))
    return graph
    
def makeBratCharterdot(rdfgraph):
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
                labl += '\\n'.join(textwrap.wrap(o + '\\n', 30))
            
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

