# Graphing-ChartEx


Graphing medieval charters: BioNLP Shared Task format to Graphviz and RDF

This repo contains the essential files for my first set of experiments with our marked-up charters and RDF. There is also code for interaction with our AllegroGraph store that should be ported to the cartametallon eventually. No point in re-inventing the wheel. The main distinction between this work and the cartametallon is that this works directly with the output data from BRAT, as below. The cartametallon works with the biomine .bmg files.

The [BRAT](http://brat.nlplab.org/) (Brat Rapid Annotation Tool), as used in the ChartEx project for marking up medieval charters, Generates stand-off markup that is a version of the [BioNLP Shared Task](http://2011.bionlp-st.org/) format. eg.:

    T1	Transaction 188 270	dederunt concesserunt et presenti scripto cirographato confirmauerunt in escambium
    T2	Document 0 14	deeds-00110292
    T3	Date 15 65	Anno domini millesimo cc quinquagesimo mense Julii
    R1	is_dated Arg1:T2 Arg2:T3	
    T4	Institution 96 110	conuentum de n
    T5	Person 81 92	w[] priorem
    R2	is_officeholder_in Arg1:T5 Arg2:T4	
    R3	is_grantor_in Arg1:T5 Arg2:T1	
    T6	Person 116 133	Michaelem Boueton
    T7	Place 137 144	Goldint
    R4	is_of Arg1:T6 Arg2:T7	
    R5	is_recipient_in Arg1:T6 Arg2:T1	
    T8	Person 277 278	m
    *	same_as T8 T6 T31
    #1	AnnotatorNotes T2	same_as, and especially, not_same_as continue to present problems of complexity and useability in situations like this where 'terram' refers to multiple different sites. Also, can I say that 'iacet super' is synonymous with is_located_in?

And like that. Strings for Entities are identified by id and text offsets, Relations by id, predicate, subject and object.

Simple smushing is done for Entities marked as same\_as.


## Requires:
(I've not included library dependencies in the repo)

* *nix for the grep search
* Python 2.7, and:
    * requests
        * This is a vast improvement over doing REST stuff with the standard libraries like urllib2 etc.
    * rdflib (3.1.0)
    * pygraphviz
    * textwrap
* JavaScript
    * jquery-1.7.1
    * jqueryFileTree.js (jQuery plugin for access to filesystem)
    * jquery.tablesorter.min.js (jQuery plugin to sort html tables) 
