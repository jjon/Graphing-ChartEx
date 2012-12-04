#!/usr/local/bin/python2.7
# -*- coding: utf-8 -*- #

from rdflib import Graph, Namespace, Literal, RDF, RDFS, OWL, XSD
import re
import os


g = Graph()
g.bind("chartex", "http://yorkhci.org/chartex-schema#")
g.bind("crm", "http://www.cidoc-crm.org/rdfs/cidoc-crm-english-label#")
chartex = Namespace("http://yorkhci.org/chartex-schema#")
crm = Namespace("http://www.cidoc-crm.org/rdfs/cidoc-crm-english-label#")


def ann2rdf(annfile, ch_id):    
    this = Namespace("http://yorkhci.org/chartex-schema/"+ ch_id + "#")
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
    
    ## after generating the graph, edit it to reflect Entities having a particular attribute.
    for x in implied_siterefs:
        g.set((this[x], RDF.type, chartex.ImpliedSiteRef))
        g.set((this[x], chartex.textSpan, Literal("implied siteRef")))


def addText(g, chfiles):
    """ Add texts to their appropriate Document nodes """
    
    for sub in g.subjects(RDF.type, chartex["Document"]):
        id = os.path.split(str(sub.defrag()))
        f_path = os.path.join(chfiles, id[1] + '.txt')
        text = open(f_path, "r").read().replace('•','.').strip()
        g.add((sub, chartex.textData, Literal(text, datatype=XSD.string)))


if __name__ == "__main__":
    
    ## get this from varargs for command-line execution
    chfiles = "/Users/jjc/Sites/brat/data/chartex/deeds/"
    
    for f in os.listdir(chfiles):
        annotationFile = ''
        
        f_path = os.path.join(chfiles,f)
        ch_id, ext = os.path.splitext(f)

        if ext == '.ann':
            annotationFile = [line.replace('•','.') for line in open(f_path, "r").readlines()]
            
        ann2rdf(annotationFile, ch_id)
        addText(g, chfiles)
        
    print g.serialize(format="xml")