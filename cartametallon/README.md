__2014-02-12 Update:__ The ADS has updated their instance of the AllegroGraph triple store, the code here has been modified accordingly. ADS will continue to host our data for the time being, and the CARTAMETALLON at Neolography will continue to work against that data; however, continued development will be conducted against a local AllegroGraph instance running in a virtual machine and that code will be reflected in files: localAGVM\*.* Further development aims to

* incorporate earlier code that generated RDF directly from BRAT output in addition to translating biomine graphs into RDF.

# CARTAMETALLON
A tool for browsing/annotation the DM biomine output. Leiden's .bmg files contain all the information found in our manually marked-up charters, and in addition adds assertions about the likelihood that certain of our entities `might_be` the same as entities appearing in other documents. One of the stand-alone scripts (q.v.) translates the .bmg graph data into RDF and uploads it to our AllegroGraph triple store. Drawing on that RDF data, this web-application permits users to graph the entities and relations within one of our charters; identify those entities that `might_be` the same as entities in other documents; examine the text of those documents; and record in the triple-store user-generated annotations of those assertions

## Requires:

* graphviz

* Python 2.7, and:
    * requests
        * This is a vast improvement over doing REST stuff with the standard libraries like urllib2 etc.
    * rdflib (4.0.1)
    * pygraphviz

* JavaScript
    * jquery-1.9.1.js
    * jquery.ui.core.js
    * jquery.ui.widget.js
    * jquery.ui.mouse.js
    * jquery.ui.draggable.js
    * jquery.ui.resizable.js
    * jquery.tablesorter.min.js (jQuery plugin to sort html tables) 

And other stuff I'm not thinking of right now -- more later --