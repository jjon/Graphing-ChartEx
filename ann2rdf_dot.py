#!/usr/bin/python
# -*- coding: utf-8 -*- #

import os
import re
import pygraphviz as pgv
import textwrap
from pprint import pprint
from rdflib import Graph, Namespace, Literal, RDF, RDFS, OWL, XSD
import cgi
import cgitb


cgitb.enable()
form = cgi.FieldStorage()


## Because bbedit doesn't access env. vars and so can't find twopi at /usr/local/bin
os.environ['PATH'] = "/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

## Annotation file to graph
## filepath = "/Users/jjc/Sites/Ann2DotRdf/bratData12-09-12/deeds/deeds-00880188.ann"
filepath = form["fp"].value

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
    
#     for n in dg.nodes():
#         n.attr['URL'] = "javascript:showSpans();"
        #print n.attr
        
    gdoc_node = g.subjects(RDF.type, chartex.Document).next() ## NB. more than 1 Document element will break this.
    
    dgdoc_node = dg.get_node(gdoc_node)
    dgdoc_node.attr['label'] = 'Document: ' + '\\n'.join(x for x in g.objects(gdoc_node, chartex.textSpan)).replace('\n','')
    dgdoc_node.attr['fontcolor'] = "white"
    dgdoc_node.attr['fontsize'] = "18.0"
    dgdoc_node.attr['id'] = "doc_node"
    
    ## generate the edges from the edges dict, rather than from the rdflib graph
    for sub in edges:
        for ob in edges[sub][1:]:
            dg.add_edge(sub, ob[0], taillabel = ob[1], labelfontsize='11.0', labelfloat=False)
    
    ## identify the maximum in-degree node, and make that the root of the digraph
    ## this makes for a less cluttered layout via the twopi algorithm
    maxDegreeNode = max([x for x in dg.iterdegree()], key= lambda tup: tup[1]) ## iterdegree returns a tuple (node, degree)
    dg.graph_attr.update(root = maxDegreeNode[0], ranksep="3 equally", overlap=False)
    
    return dg


def main(f,s):
    fin = open(f,'r')
    annotationFile = fin.readlines()
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


if __name__ == "__main__":
    main(filepath, 'n3')
    
    

#############################    TODO     ################################
# Smushing by type and textSpan identity
# Operate on the rdf graph or on the graphviz graph?
