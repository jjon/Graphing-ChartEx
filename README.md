# Graphing-ChartEx


Graphing medieval charters: BioNLP Shared Task format to Graphviz and RDF

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


2013-02-14: Lots of uncommitted and uncommented development locally. Now that we finally have a triple store, I'm gradually adding AllegroGraph functionality. Also refactored all the old stuff. ann2rdf_dot.py, ann2rdf, index.html, no longer relevant. Have now split out the js and the css into their own files.

2012-11-07: Added Google Books search, with comments on the shortcomings of Google Books.

2012-10-27: Added grep search. The Levenshtein search may not scale well. It opens and searches each annotation file using os.walk() in the python code. We might refactor the levenshtein search to use grep instead (that's a TODO). This search uses subprocess.Popen(), and passes the target string directly to grep. It accepts Perl-style regexes and is case insensitive. This will search either the annotation files (\*.ann), for any marked up entity, or the charter text files themselves (\*.txt).

2012-10-22: Added Damerau-Levenshtein distance metric functionality: Search the selected corpus of annotation files (*.ann) for marked up entities of the type selected that are similar to the target string. Selecting a Levenshtein distance of '0' will return exact matches. This search is case-insensitive, and uses the python regex module, so it accepts Perl-style regexes. There are lots of Python implementations of the Levenshtein distance algorithms, this one, from From [Michael Homer's blog:](http://mwh.geek.nz/2009/04/26/python-damerau-levenshtein-distance/) is elegant and efficient.


## Requires:
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
