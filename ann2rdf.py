#!/usr/bin/env python
# -*- coding: utf-8 -*- #

## Generates RDF triples graph from a directory full of .ann and .txt files and
## serializes it as one of 'xml', 'n3', 'turtle', 'nt', 'pretty-xml', or 'trix'
## Depends on rdflib. I don't know what it's like to install this library on
## windows. It might be as simple as: $ sudo easy_install rdflib
## Usage: python ann2rdf.py path-to-dir format
## (where format is one of: 'xml', 'n3', 'turtle', 'nt', 'pretty-xml', or 'trix')

from rdflib import Graph, Namespace, Literal, RDF, RDFS, OWL, XSD
import re
import os
import sys

# NB: g is global, ann2rdf and addText don't return anything,
# they just update this graph for each .ann and .txt file, and then generateGraph prints it
g = Graph()

g.bind("chartex", "http://yorkhci.org/chartex-schema#")
g.bind("crm", "http://www.cidoc-crm.org/rdfs/cidoc-crm-english-label#")
chartex = Namespace("http://yorkhci.org/chartex-schema#")
chartexDoc = Namespace("http://yorkhci.org/chartex-schema/")
crm = Namespace("http://www.cidoc-crm.org/rdfs/cidoc-crm-english-label#")

def ann2rdf(g, annfile, charter_id):
    """ Here is the crudest sort of parsing of the annotation file. Consider using brat's own annotation.py
    Note: if line[0] == "A" for 'A'ttributes which we're not currently using in our annotation scheme. """
    this = Namespace("http://yorkhci.org/chartex-schema/"+ charter_id + "#")
    implied_siterefs = []
        
    for line in annfile:
        if line[0] == 'T':
            eid, entity, start, end, text = re.split('\s+', line, maxsplit=4)
            g.add((this[eid], RDF.type, chartex[entity]))
            g.add((this[eid], chartex.textRange, Literal((int(start), int(end)))))
            g.add((this[eid], chartex.textSpan, Literal(text.strip())))

        if line[0] == 'R':
            key, prop, a1, a2, note = re.split('\s+', line, maxsplit=4)
            g.add((this[a1.split(':')[1]], chartex[prop], this[a2.split(':')[1]]))
        if line[0] == "*":
            key, prop, a1, a2, note = re.split('\s+', line, maxsplit=4)
            g.add((this[a1], chartex[prop], this[a2]))
        if line[0] == "A": # for example: A2	Implied-SiteRef T17 genitive
            id, attr, ent, val = re.split('\s+', line, maxsplit=3)
            implied_siterefs.append(ent) # Update a list of nodes having a particular attribute.
    
    ## after populating the graph, edit it to reflect Entities having a particular attribute.
    for x in implied_siterefs:
        g.set((this[x], RDF.type, chartex.ImpliedSiteRef))
        g.set((this[x], chartex.textSpan, Literal("implied siteRef")))


def addText(g, ann_files_dir):
    """ Add texts to their appropriate Document nodes """
    
    for sub in g.subjects(RDF.type, chartex["Document"]):
        id = os.path.split(str(sub.defrag()))
        f_path = os.path.join(ann_files_dir, id[1] + '.txt')
        text = open(f_path, "r").read().replace('•','.').strip()
        g.add((sub, chartex.textData, Literal(text, datatype=XSD.string)))



def generateGraph(ann_files_dir, serialization_format):
    for f in os.listdir(ann_files_dir):
        annotationFile = ''
        
        f_path = os.path.join(ann_files_dir,f)
        charter_id, ext = os.path.splitext(f)

        if ext == '.ann':
            annotationFile = [line.replace('•','.') for line in open(f_path, "r").readlines()]
            
        ann2rdf(g, annotationFile, charter_id)
        addText(g, ann_files_dir)
        
    print g.serialize(format=serialization_format)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit("""Usage: python ann2rdf.py path-to-dir format\n
        \t(where format is one of: 'xml', 'n3', 'turtle', 'nt', 'pretty-xml', or 'trix')\n""")
        
    elif not os.path.isdir(sys.argv[1]):
        sys.exit("unknown directory: %s" % sys.argv[1])
        
    elif os.path.isdir(sys.argv[1]):
        try:
            validfiles = (f for f in os.listdir(sys.argv[1]) if f.endswith('.ann')).next()
            generateGraph(sys.argv[1], sys.argv[2])
        except StopIteration:
            sys.exit("there are no brat annotation files in directory: %s" % sys.argv[1])
