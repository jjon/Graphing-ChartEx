#!/usr/bin/env python
# -*- coding: utf-8 -*- #
import sys
sys.path.insert(1, "/Users/jjc/Sites/Ann2DotRdf/") # to get access to the chartexCGIconfig module
sys.path.insert(1, '/Users/jjc/ComputerInfo/RDF/rdflib') # to use the dev version
import os
import json
from pprint import pprint
from decimal import Decimal
import rdflib
from rdflib import ConjunctiveGraph, Graph, Namespace, BNode, URIRef, Literal, RDF, RDFS, OWL, XSD, plugin, query
import requests
import pygraphviz as pgv
import textwrap
from chartexCGIconfig import ADS_AUTH, VB_AUTH
import cProfile

## I run this from my editor, it is thus a very ad hoc sort of
## thing. Use it to generate the graph and examine it; then
## remove the commenting around the ADS UPLOAD code to upload the
## graph to ADS. 

# NOTA BENE: Before uploading new data, retrieve and make a record
# of the existing annotations on the server. With new data, entity
# ids will change. And then, don't forget to remove the existing
# data on the server before uploading new data
    
chartex = Namespace("http://chartex.org/chartex-schema#")
gid = Namespace("http://chartex.org/graphid/")
crm = Namespace("http://www.cidoc-crm.org/rdfs/cidoc-crm-english-label#")

#bmg_file = "/Users/jjc/Documents/ChartEx/Leiden-Arno-etal/johntest.bmg"
#bmg_file = "/Users/jjc/Sites/Ann2DotRdf/vc_candidates.bmg"
#bmg_file = "/Users/jjc/Documents/ChartEx/Leiden-Arno-etal/vc_candidates_truncated.bmg"

## Most recent bmg output. result: 75840 statements
bmg_file = "/Users/jjc/Documents/ChartEx/Leiden-Arno-etal/vicars-choral_PROBABILITIES_usedates_candidates.bmg"

######## PARSE THE INPUT FROM BMG FILES ########
# bmg lines like this: "# _attributes Person_1990 ShortName=Walter+de+Rome Summary=Walter+de+Rome,+deceased+husband+of+Agnes File=vicars-choral-english-390 Txs=T14T18 TextRange=(58,72)+(137,143) TextSpan=(Walter)+(Walter+de+Rome)"
entities = [line[14:-1] for line in open(bmg_file) if line[0] == '#']

# BMG lines like this: "Person_284 Person_1387 might_be goodness=0.8049"
relations = [tuple(line.split()) for line in open(bmg_file) if line[0] != '#']

entity_dict = {
    x.split()[0]:
        {y.split('=')[0]:
            y.split('=')[1].replace('+',' ') for y in x.split()[1:]
        } for x in entities
    }

# the result looks like this ('Document' nodes also have a 'TextData' field):
#     'Person_992': {   'File': 'vicars-choral-414',
#                       'ShortName': 'William de Waleby',
#                       'Summary': 'William de Waleby',
#                       'TextRange': '(1095,1112)',
#                       'TextSpan': '(William de Waleby)',
#                       'Txs': 'T20'},
#     'Person_996': {   'File': 'vicars-choral-414',
#                       'ShortName': 'mag. Simon de Evesham',
#                       'Summary': 'mag. Simon de Evesham, archdeacon of Rychemund',
#                       'TextRange': '(34,55) (617,627) (900,910)',
#                       'TextSpan': '(mag. Simon) (mag. Simon de Evesham)',
#                       'Txs': 'T5T21T22'},
#     'Place_1004': {   'File': 'vicars-choral-415',
#                       'ShortName': 'York',
#                       'Summary': 'York',
#                       'TextRange': '(151,155)',
#                       'TextSpan': '(York)',
#                       'Txs': 'T9'},

############ GENERATE THE GRAPH ###############
cg = ConjunctiveGraph(identifier=gid['VicarsChoralConfidenceGraph'])
for e in entity_dict:
    graph = Graph(cg.store, gid[entity_dict[e]['File']])
    
    # add entities to the graph
    graph.add(( chartex[e], RDF.type, chartex[e.split('_')[0]] ))
    
    # add Literal relations (bmg attributes)
    for k,v in entity_dict[e].items():
        graph.add(( chartex[e], chartex[k], Literal(v) ))
        
for rel in relations:
    s = chartex[rel[0]]
    p = chartex[rel[2]]
    o = chartex[rel[1]]    
    goodness = rel[3].split('=')[1] ## 73287
    
    ## this will add a context and triple for any relation whose confidence factor is less than 1, OR ALL might_be relations.
    ## AND it will add to the default graph a goodness triple: <context, goodness, decimalLiteral>
    ## For the current data, NO relation other than might_be will have a goodness of < 1
    ## So NO relation other than 'might_be' will have such a context and triples.
    if Decimal(goodness) < 1 or p == chartex['might_be']:
        rgraph = Graph(cg.store, gid[rel[0]+rel[2]+rel[1]])
        rgraph.add((s,p,o))
        cg.add(( rgraph.identifier, chartex['goodness'], Literal(goodness, datatype=XSD.decimal) ))
        ## I don't appear to gain anything by creating a separate graph to hold these statements, so we add them to the default graph. AG will figure out where to put them on upload???
    
    ## add the triple also to the appropriate document graph
    ## might_be is the only relation that can lie between entities in different documents
    ## if necessary, we can draw from a list of such relations if we want to add others
    g = cg.get_context(  gid[entity_dict[rel[0]]['File']]  )
    if p != chartex['might_be']:
        g.add((s,p,o))  
 

#cProfile.run('cg.serialize(format="trig")')
print rdflib.__version__
#print len([c for c in cg.contexts()])
#print cg.serialize(format='nquads')

# there may be a bug in the serialization of context-aware stores. Serializing a graph of 78k statements takes just under an hour
# in my (unmerged) version of rdflib repo, this is fixed


######################## UPLOAD TO THE ADS AllegroGraph TRIPLE-STORE ###########################
## Upload by the following means takes around 3 hours
## Next time I do this, try serializing as nquads first then upload with 'Content-Type': text/x-nquads
## this works good uploading to Vbox store: MUCH more efficient (the difference between about 30sec and 50min!), especially since my local branch of rdflib has fixed quad serialization functions.

######### ADS UPLOAD (deprecated! revise as below for Vbox AG server)############
# for c in cg.contexts():
#     r = requests.post(
#         "http://data.archaeologydataservice.ac.uk/sparql/repositories/chartex/statements",
#         headers={'Content-Type': 'text/turtle'},
#         data=c.serialize(format='turtle'),
#         auth=ADS_AUTH,
#         params={"context":"<" + c.identifier + ">", "commit":1000}
#     )
# 
# pprint(r.__dict__, indent=4)

#print cg.serialize(format="trig")


###### Upload to local Vbox AG server ######
## to figure out: what's the difference between http://localhost:9211/repositories/chartex/statements and http://localhost:9211/catalogs/system/repositories/chartex/statements ?
# r = requests.post(
#     "http://localhost:9211/repositories/chartex/statements",
#     headers={'Content-Type': 'text/x-nquads'},
#     data=cg.serialize(format='nquads'),
#     auth=VB_AUTH,
#     params={"commit":1000}
# )



 
############### UPLOAD BY URL? ###################
############### Currently, this does not work:
# r = requests.post(
#     "http://data.archaeologydataservice.ac.uk/sparql/repositories/chartex/statements",
#     headers={'Content-Type': 'text/plain', 'Accept': 'text/plain'},
#     auth=ADS_AUTH,
#     params={"URL": "http://neolography.com/staging/bmg_truncated", "context":"<test-context>"}
# )
# 
# 
# print r.content
# print "~~~~~~~~~"
# pprint(r.__dict__)



########### NOTES ON SPARQL QUERIES ###########
# for a given subject, get object of might_be, that object's text string and file id, and the ?goodness factor for that relationship.
# select ?entity ?text ?file ?goodness 
#     WHERE { 
#     ?entity   <http://chartex.org/chartex-schema#TextSpan>    ?text ;
#               <http://chartex.org/chartex-schema#File>        ?file .
#
#     GRAPH ?g  {<http://chartex.org/chartex-schema#Person_1876>  chartex:might_be ?entity . }
#
#     ?g chartex:goodness ?goodness . 
# }

# construct {?s ?p ?o .}
#     from named {
#         graph ?g { <http://chartex.org/graphid/vicars-choral-399>

# select distinct ?g
#     WHERE { GRAPH ?g { ?s ?p ?o } .
#     FILTER regex(str(?g), "vicars-choral")
# }

# q = """
# PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
# PREFIX chartex: <http://chartex.org/chartex-schema#>
# PREFIX xsd:<http://www.w3.org/2001/XMLSchema#>
# 
# select ?entity ?text ?file ?goodness 
#     WHERE { 
#     ?entity   <http://chartex.org/chartex-schema#TextSpan>    ?text ;
#               <http://chartex.org/chartex-schema#File>        ?file .
# 
#     GRAPH ?g  {<http://chartex.org/chartex-schema#Person_10343>  chartex:might_be ?entity . }
# 
#     ?g chartex:goodness ?goodness . 
# }
# """

# q = """select distinct ?g WHERE { GRAPH ?g { ?s ?p ?o } . FILTER regex(str(?g), "vicars-choral") }"""

