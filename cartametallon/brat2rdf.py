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
#print rdflib.__version__
from rdflib import ConjunctiveGraph, Graph, Namespace, BNode, URIRef, Literal, RDF, RDFS, OWL, XSD, plugin, query
import requests
import pygraphviz as pgv
import textwrap

sys.path.insert(1, "/Users/jjc/Sites/Ann2DotRdf/")
from localAGconfig import AG_AUTH, AGVM_VC_REPO, DATADIR, deedsN3

#tstdoc = DATADIR + "deeds/deeds-00880111.ann"
tstdoc = DATADIR + "Giovanni_Scriba/GScriba_DCCCLXI.ann"
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
 
def collapse_entity_relation(g, relation):
    # TODO: move this and other stuff into an RDF module.
    
    for ent in g.subjects():
        for p,o in g.predicate_objects(ent):
            if p == relation:
                newLiteral = list(g.objects(o,chartex.textSpan))[0] + ''.join(list(g.objects(o,chartex.textRange)))
                g.add((ent, chartex.textSpan, Literal(newLiteral)))
                g.remove((ent,p,o))
                
    return g
            
def delete_entities(g, ent):
    g.remove((None, RDF.type, ent))
        
    return g
                   
def ann2rdf(f_path):
    # Mac Path: /Users/jjc/Sites/Ann2DotRdf/chartex/Giovanni_Scriba/GScriba_DCCCLXI.ann
    g = Graph()
    x_path, ext = os.path.splitext(f_path)
    charter_id = os.path.basename(x_path)
    doc_path = x_path + '.txt'
    
    annfile = [line.replace('•','.') for line in open(f_path, "r").readlines()]
    doctext = open(doc_path, "r").read().replace('•','.')

    this = Namespace("http://chartex.org/document/"+ charter_id + "#")
    
    implied_siterefs = []
        
    for line in annfile:
        # text fragment example:
        # T6	Apparatus 800 814;832 839;854 859	observaverimus intrare idque
        if line[0] == 'T':
            eid, ent_and_offsets, text = line.split('\t')
            entity, offsets = ent_and_offsets.split(' ', 1)
            offsets = [list([int(y) for y in x.split()]) for x in offsets.split(';')]
            
            
            g.add((this[eid], RDF.type, chartex[entity]))
            g.add((this[eid], chartex.textRange, Literal(offsets)))
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
    
#print ann2rdf('/Users/jjc/Sites/Ann2DotRdf/chartex/Giovanni_Scriba/GScriba_DCCCLXI.ann').serialize(format='n3')
#print ann2rdf( DATADIR + "deeds/deeds-00880111.ann").serialize(format='n3')


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

import itertools # better: just define a little recursive list flattener.
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
            
        # smush multiple text ranges
        offset_lists = [eval(x) for x in list(graph.objects(new_sub, chartex.textRange))]
        offsets = list(itertools.chain.from_iterable(offset_lists))
        graph.remove((new_sub, chartex.textRange, None))
        graph.add((new_sub, chartex.textRange, Literal(offsets) ))
        
    return graph

def filter_witnesses(d):
    for x in d:
        d[x]['edges'] = [e for e in d[x]['edges'] if e[0] != chartex.is_witness_to]
    return {x:y for x,y in d.items()
        if not ("Person" in y['type'] and y['edges'] == [])
        }
    # this doesn't work yet: need a condition to remove d entries of 'type' Person where 'edges' is empty
    # {x:y for x,y in d.items() if not ("Person" in y['type'] and y['edges'] == [])}
    ## works, but just causes more trouble: and not all(item[0] == chartex.occupation_is for item in y['edges'])

    
def brat2dot(rdf, wits):
    if len(rdf) == 0:
        return "sorry, nothing there. the graph has no nodes"
    
    dg = pgv.AGraph(directed=True, fontname="Times-Roman")

    # make a dictionary of all the Entities.
    # This gets all the nodes for the graph because all the Entities
    # are 'subjects' of at least a 'type' relation
    # Remember: contents of the edges dict are rdflib.term objects!
    graphdict = {s: {'type': [ t.split('#')[-1] for t in rdf.objects(s, RDF.type) ],
                    'edges': [ (p,o) for p,o in rdf.predicate_objects(s) if isinstance(o,URIRef) and p != RDF.type ],
                    'offsets': [ eval(o) for p,o in rdf.predicate_objects(s) if p == chartex.textRange ],
                    'literals': [ o for p,o in rdf.predicate_objects(s) if p == chartex.textSpan ]
                    }
                for s in rdf.subjects()}
    
    # suppress witness nodes and edges:
    if wits:
        graphdict = filter_witnesses(graphdict)
        
    # add and style the nodes
    for s in graphdict:
        dg.add_node(
            s,
            label = '\\n'.join(textwrap.wrap(graphdict[s]['literals'][-1], 30))
                if len(graphdict[s]['literals']) == 1
                else '\\n'.join(graphdict[s]['literals']),
            style = 'filled',
            fillcolor = node_colors[graphdict[s]['type'][-1]],
            shape = 'ellipse',
            id = str(s),
            tooltip = str(s)
        )
    
    # add and style all the edges
    # Remember: contents of the edges dict are rdflib.term objects.
    # Ergo: generate tooltip from strings to avoid logger warnings re bad URIs
    for s in graphdict:
        for edge in graphdict[s]['edges']:
            dg.add_edge(
                s, edge[1],
                label = edge[0].split('#')[1],
                fontsize="11.0",
                tooltip = str(s) + ', ' + str(edge[0]) + ', ' + str(edge[1])                    
            )
                
    maxDegreeNode = max([x for x in dg.iterdegree()], key= lambda tup: tup[1]) ## iterdegree returns a tuple (node, degree)
    dg.graph_attr.update(root = maxDegreeNode[0], mindist=0, ranksep="0.5:0.3:0.2", overlap=False)
    
    # tinker with individual nodes like this:
    for dnode in [n for n in rdf.subjects(RDF.type, chartex.Document)]:
        dgdoc_node = dg.get_node(dnode)
        dgdoc_node.attr['label'] = "Charter:\\n" + dgdoc_node.attr['label']
        dgdoc_node.attr['fontcolor'] = "white"
        dgdoc_node.attr['fontsize'] = "18.0"
        dgdoc_node.attr['id'] = dnode

    return dg

if __name__ == "__main__":
    g = ann2rdf(tstdoc)
    g.serialize(format="n3")
    print brat2dot(smushSameAs(g), False)