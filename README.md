# Graphing-ChartEx

The [ChartEx project](http://chartex.org) is an eighteen month international project funded by the [digging into data](http://www.diggingintodata.org/) challenge. It involved Medieval historians from York in the UK, Toronto, Washington, and Columbia, working in collaboration with researchers in Natural Language Processing at Brighton UK, Data Mining at Leiden, and HCI at York. Our aim was to explore the possibility of using NLP and DM to extract entity and relation information from digitized medieval charters.

To provide a training corpus for the NLP component, historians marked up a body of medieval charters from a variety of sources using the innovative [brat rapid annotation tool](brat.nlplab.org). The Data Mining component examined these documents looking for degrees of similarity between entities across the whole corpus.

The software in this repository consists of
    
* chartexOldSite: a series of experiments with the data output from the *brat*, transforming the [BioNLP Shared Task 2011](http://2011.bionlp-st.org/) data format into RDF triples within the Linked Open Data paradigm. The aim was to prepare for storing our data in a publicly accessible triple store. These files are not intended for production, and merely serve as a record of some of the code that would prove useful for the:

* CARTAMETALLON: a tool for browsing and annotating the data that emerged from the DM component. The DM system produced output data from the [Biomine Project](http://www.cs.helsinki.fi/group/biomine/) (.bmg files). This data, translated to RDF by python scripts (stand-alone-scripts), was stored on an [AllegroGraph](http://www.franz.com/agraph/) triple store maintained by the [Archaeology Data Service](http://archaeologydataservice.ac.uk/) at the University of York. Access to the triple store was solely via the http protocol provided by AllegroGraph. CARTAMETALLON (gk.: Charter Mine) is a python CGI driven web application. It 

    1. displays the entities and relations marked up in our charters as directed graphs (bubbles and arrows generated by the [graphviz](http://www.graphviz.org/) twopi algorithm)
    2. displays the text of the charters with entities highlighted in all the places where they occur.
    3. displays the assertions about those entities derived by the Data Mining component, along with a confidence metric for each assertion.
    4. permits annotation of those assertions. These annotations are formulated as RDF graphs using the [Open Annotation](http://www.openannotation.org/) data model. These graphs are then stored in the AG triple store.

* A series of python scripts serving a variety of functions: Preparing texts for input into the brat annotation tool; translating brat output into RDF; translating biomine output into RDF; uploading RDF graphs to the triple store via REST interations; Issuing arbitrary SPARQL queries to the triple store and parsing their responses. These are all <i>ad hoc</i> scripts and not intended for production use.

## Requires:
* Python 2.7 standard library, and modules:
    * requests (This is a vast improvement over doing REST stuff with the standard libraries like urllib2 etc.)
    * rdflib (4.0.1)
    * pygraphviz
    * textwrap
* JavaScript
    * jquery-1.9.1, and elements of the jquery UI framework
    * jqueryFileTree.js (jQuery plugin for access to filesystem)
    * jquery.tablesorter.min.js (jQuery plugin to sort html tables) 
* http access to an AllegroGraph triple store
* Graphviz

## *Caveats*
 This repository is merely a record of of software experiments I've made in support of an academic project in medieval studies. If this code can prove useful to you, so much the better, but I make no claim about this software's fitness for any particular purpose. With those caveats, this software is offered under the most generous possible interpretation of the [GNU General Public License, version 2 (GPL-2.0)](http://opensource.org/licenses/GPL-2.0) 
