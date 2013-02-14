
var doc_text = ""; // the only global should be a json object with all the data: svg, text, and rdf.
var dirs_with_ann_files = undefined
var DATADIR = '/Users/jjc/Sites/Ann2DotRdf/chartex/'

/**************** Only toggles the doc_text display ****************/
function hideme() {
    $('#doc_text_display').toggle('fast');
    $('#doc_text').empty();
}

/*******************************************/
/* offsetArray is an array of offset tuples
/*******************************************/
function replaceOffset(str, offsetArray, tag) {
    tag = tag || '<span class="doc-highlight">';
    var arr = str.split('');
    for (i = 0; i < offsetArray.length; i++) {
        var start = offsetArray[i][0];
        var end = offsetArray[i][1];
        arr[start] = tag + arr[start];
        arr[end] = "</span>" + arr[end];
    }
    return arr.join('');
}

/************************/
/* Graphme gets pydata. deployData just deploys it client side
/**************************/
function deployData(pydata) {
    var dataIn = pydata.split('<filedelimiter>'); // use json instead of this
    var svg = $(dataIn[0]).find('svg');
    var rdf = dataIn[1];
    var doc_text = dataIn[2]
    
// beware the trailing newline: much of this possibly not necessary
//     var str = '';
//     for (str = 0; str < doc_text.length; str++) {
//         if (!doc_text[str].length) {
//             doc_text.splice(str, 1);
//         }
//     }
//     doc_text = doc_text.join(' ');
    
    $('#doc_text').empty();
    $('#doc_text_display').hide();
    $("#dotimg").empty();
    $("#dotimg").append(dataIn[0]);

    $("#rdfout").html('<pre>' + rdf + '</pre>');    
    //document.getElementById("rdfout").innerText = "\nThe same graph rendered as RDF/n3:\n\n" + rdf; //innerText is a MS invention, not standards compliant.
    
    
    // click function for graph nodes: show doc_text w/offsets highlighted.
    $('.node').click(function(e) {
        var $that = $(this);
        var offsets = [];

    // gather the offsets from the Literals containing them
        $that.find('text').contents().each(function(i) {
            var regexp = /\((\d+),\s(\d+)\)/g;
            var match = regexp.exec(this.data);
            if (match !== null) {
                offsets.push([match[1], match[2]]);
            }
        });

    // call replaceOffset to highlight occurrences of Literal text in the document text.
        var fillColor = $(this).find('ellipse').css('fill');
        $("#doc_text").html(replaceOffset(doc_text, offsets, '<span style="background-color:' + fillColor + '">'));
        var X = e.pageX - 200;
        var Y = e.pageY + 16;
        $('#doc_text_display').hide();
        $('#doc_text_display').css('overflow-y', 'auto');
        $('#doc_text_display').css({
            left: X,
            top: Y
        }).toggle('slow');
    });
    
    // get and set size of the graph so that we can toggle it.
        var gwidth = $("svg")[0].width.baseVal.value;
        var gheight = $("svg")[0].height.baseVal.value;
        $("svg")[0].width.baseVal.value = 800;
        $("svg")[0].height.baseVal.value = 800;

    // toggle full-sized graph
        $("#export_svg").toggle(
            function(){
                $('#doc_text_display').hide();
                $("svg")[0].width.baseVal.value = gwidth;
                $("svg")[0].height.baseVal.value = gheight;
            },
            function(){
                $('#doc_text_display').hide();
                $("svg")[0].width.baseVal.value = 800;
                $("svg")[0].height.baseVal.value = 800;
            } 
        );

    $('html, body').animate({
        scrollTop: $("#remove_graphs").offset().top
    }, 2000);    

}



/*********************** this is redundant
/* Generate dot graph from search result click.
/* Ajax call to server and call to deployData()
/***********************/
function graphme(filepath){
    $.ajax({
        url: "chartexCGI.py",
        dataType: 'text',
        data: {'fp': filepath},
        error: function(jqXHR, textStatus, errorThrown) {
            //console.log(jqXHR.response, textStatus, errorThrown);
        },
        success: function(pydata) {
            if (pydata.search("<filedelimiter>") >= 0) {
                $(".expanded a").first().trigger('click');
                deployData(pydata);
                $('html, body').animate({
                    scrollTop: $("#dotimg").offset().top
                }, 2000);    
            }
            
            else {alertError(pydata);}
        }
    });
}

/**************************/
/* Alert on 'no annotations'
/**************************/
function alertError(pydata) {
    $('#doc_text_display').hide();
    $("#dotimg").empty();
    $("#rdfout").empty();
    $("#doc_text").empty();
    doc_text = "";
    alert("that file has no annotations");
}


/************************************
/* Response handler for gbooks search
/************************************/
function handleResponse(response) {
    //Alan de Quixlay is the example that started it for gBooks
    if (response.items.length > 0){
        $(".loader").hide();
        $("#result-div").remove();
        $("#searchAndResult").append('<div id="result-div"><table id="result-table" class="tablesorter"><thead><tr><th>Title (click to see in gBooks)</th><th>Date</th><th>Found snippet</th></tr></thead><tbody id="result"></tbody></table></div>');
        
        for (var i = 0; i < response.items.length; i++) {
            var item = response.items[i];
            var title = item.volumeInfo.title;
            var date = item.volumeInfo.publishedDate;
            var link = item.accessInfo.webReaderLink;
            var snippet = (typeof item.searchInfo.textSnippet === 'undefined') ? "no snippet text" : item.searchInfo.textSnippet;
            
            // in production code, item.text should have the HTML entities escaped.
            //document.getElementById("content").innerHTML += "<br>" + item.volumeInfo.title;
            $("#result").append('<tr><td>' + '<a href="' + link + '"><img src="ex-link.png" />&nbsp;' + title + '</a></td><td>' + date + '</td><td>' + snippet + '</td></tr>');
            $("#result-table").tablesorter();
        }
    }
}

/************************************
/* Utility: show ajax result in modal
/************************************/
function showModal(response){
    response = response.replace(/</g, "&lt;");
    response = response.replace(/>/g, "&gt;");
    $("#modalsink").html('<pre>' + response + '</pre>');
    $("#modalsink").modal({
        minWidth: 600,
        maxWidth: 1000,
        maxHeight: 450,
        overlayClose:true,
        opacity:80
    });
    $(".loader").hide();
}

/*********************************************************
* some of this stuff does not have to be in document.ready
**********************************************************/

$(document).ready(function() {
//populate the 'directoriesToSearch' dropdown list
    $.ajax({
        url: "jqueryFileTree.py",
        dataType: 'json',
        data: {
            'dirs': DATADIR
        },
        error: function(jqXHR, textStatus, errorThrown) {
            //console.log(jqXHR.response, textStatus, errorThrown);
        },
        success: function(pydata) {
            dirs_with_ann_files = pydata;
            for (i=0; i<dirs_with_ann_files.length; i++){
                $("#serializeDirs, #ADSserializeDirs, #directoriesToSearch, #grepDirs").append('<option value="'+ dirs_with_ann_files[i] +'">' + dirs_with_ann_files[i].split('/').slice(6).join('/') + '</option>');
            }
        }
    });


/*****************************/
/* Stupid UI tricks 
/* this is pretty clumsy: use a jQuery ui widget instead.
/*****************************/

    /* remember that the following depends on classes being in the right order eg .swap .levSearch */    
    $(".swap").click(function(){
        $('#doc_text').empty();
        $('#doc_text_display').hide();
        $("#dotimg").empty();
        $("#rdfout").empty();
        $("#result-div").remove();
        $(".searchform").each(function(){this.reset()});
        var searchSection = this.classList[1];
        $(".searchbox").hide(750);
        $("." + searchSection).show(750);
    });

// Call FileTree
// populate the filetree selection list
    $('#ftcontainer').fileTree({
        root: DATADIR,
        script: 'jqueryFileTree.py',
        expandSpeed: 300,
        collapseSpeed: 300,
        multiFolder: false
    }, function(file) { //NB the 'file' argument root + filename
        $.ajax({
            url: "chartexCGI.py",
            dataType: 'text',
            data: {
                'fp': file
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log(jqXHR.response, textStatus, errorThrown);
            },
            success: deployData
        });
    });

/*****************************/
/*Levenshtein distance search*/
/*****************************/
    $('#submitButton').click(function(){
        // similar string search function
        var dirToSearch = $("select#directoriesToSearch").val();
        var EntityToSearch = $("select#EntityToSearch").val();
        var editDistance = $("select#editDistance").val();
        var targetString = $("input#searchstring").val();
        $(".loader").show();
        $.ajax({
            type: "get",
            url: "chartexCGI.py",
            data: {'searchstring': targetString, 'entity': EntityToSearch, 'editDistance': editDistance, 'dirToSearch': dirToSearch},
            dataType: 'json',
            success: function(pydata){
                if (pydata.length > 0) {
                    $("#result-div").remove();
                    $(".loader").hide();
                    $("#searchAndResult").append('<div id="result-div"><table id="result-table" class="tablesorter"><thead><tr><th>found string</th><th>edit distance</th><th>file: click on the file to graph it below</th></tr></thead><tbody id="result"></tbody></table></div>');
                    for (match in pydata){
                    //TODO: better to use the DATADIR constant and generate
                    //the filename server-side as in the grepSearch below.
                        $("#result").append('<tr><td>' + pydata[match].text + '</td><td class="distance-cell">' + pydata[match].distance + '</td><td>' + '<a onclick="graphme(\'' + pydata[match].file + '\')" href="#">' + pydata[match].file.split('/').slice(6).join('/') + '</a></td></tr>');
                    }
                    $("#result-table").tablesorter();
                } else {
                    $("#result-div").remove();
                    $(".loader").hide();
                    alert("No Result");
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                //console.log(jqXHR.response, textStatus, errorThrown);
            }
        });
        return false;
    });
    
/*****************************/
/* *NIX grep function search 
/*****************************/
    $('#grepButton').click(function(){
        var dirToSearch = $(".grepSearch option:selected").val();
        var filetype = $(".grepSearch input:radio:checked").val();
        var targetString = $(".grepSearch input:text").val();
        $(".loader").show();

        $.ajax({
            type: "get",
            url: "chartexCGI.py",
            data: {'searchstring': targetString, 'filetype': filetype, 'dirToSearch': dirToSearch},
            dataType: 'json',
            success: function(pydata){
                if (pydata.length > 0) {
                    $("#result-div").remove();
                    $(".loader").hide();
                    
                    if (filetype == 'ann'){
                    
                        $("#searchAndResult").append('<div id="result-div"><table id="grep-result-table" class="tablesorter"><thead><tr><th>annotation&nbsp;file</th><th>entity&nbsp;or&nbsp;relation</th><th>matched string</th></tr></thead><tbody id="result"></tbody></table></div>');
                        for (match in pydata){
                            $("#result").append('<tr><td><a href="#" onclick="graphme(\'' + DATADIR + pydata[match][0] + '\');">' + pydata[match][0] + '</a></td><td>' + pydata[match][1] + '</td><td>' + pydata[match][2] + '</td></tr>');
                        }
                    
                    } else if (filetype == 'txt'){
                    
                        $("#searchAndResult").append('<div id="result-div"><table id="grep-result-table" class="tablesorter"><thead><tr><th>annotation&nbsp;file</th><th>document text</th></tr></thead><tbody id="result"></tbody></table></div>');
                        for (match in pydata){
                            $("#result").append('<tr><td><a href="#" onclick="graphme(\'' + DATADIR + pydata[match][0] + '\');">' + pydata[match][0] + '</a></td><td>' + pydata[match][1] + '</td></tr>');
                        }
                    }
                    
                    $("#grep-result-table").tablesorter();
                } else {
                    $(".loader").hide();
                    $("#result-div").remove();
                    alert("No Result");
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                //console.log(jqXHR.response, textStatus, errorThrown);
            }
        });
        return false;
    });
    
    
/*****************************/
/* Google books search
/*****************************/
    $("#gbooksButton").click(function(){
        var targetString = $(".gbookSearch input:text").val();
        $(".loader").show();
        $.ajax({
            url: "https://www.googleapis.com/books/v1/volumes?",
            datatype: 'json',
            data: "q=" + targetString + "&callback=handleResponse",
            success: handleResponse,
            error: function(jqXHR, textStatus, errorThrown) {
                console.log(jqXHR.response, textStatus, errorThrown);
            }
        })
        return false;
    });

/*****************************/
/* Just Serialize
/*****************************/

    $("#serializeButton").click(function(){
        var serialDir = $("#serializeDirs option:selected").val();
        var serialFormat = $("#serFormat option:selected").val();
        $(".loader").show();
        
        $.ajax({
            type: "get",
            url: "chartexCGI.py",
            data: {"serialDir": serialDir, "serialFormat": serialFormat},
            dataType: 'text',
            success: showModal,
            error: function(jqXHR, textStatus, errorThrown) {
                //console.log(jqXHR.response, textStatus, errorThrown);
            }
        
        });
        return false;
    });

/*****************************/
/* ADS serialize
/*****************************/

    $("#ADSserializeButton").click(function(){
        var ADSserialDir = $("#ADSserializeDirs option:selected").val();
        var serialFormat = "turtle";
        $(".loader").show();
        
        $.ajax({
            type: "get",
            url: "chartexCGI.py",
            data: {"serialDir": ADSserialDir, "serialFormat": serialFormat},
            dataType: 'text',
            success: showModal,
            error: function(jqXHR, textStatus, errorThrown) {
                //console.log(jqXHR.response, textStatus, errorThrown);
            }
        
        });
        return false;
    });
    
    $("#ADSaddButton").click(function(){
        var addDir = $("#ADSserializeDirs option:selected").val();
        $(".loader").show();
        $.ajax({
            type: "get",
            url: "chartexCGI.py",
            data: {"ADSadd": "True", "addDir": addDir},
            dataType: 'text',
            success: showModal,
            error: function(jqXHR, textStatus, errorThrown) {
                console.log(jqXHR.response, textStatus, errorThrown);
            }

        });
        
        return false;
    });

    $("#ADSgetButton").click(function(){
        $(".loader").show();
        $.ajax({
            type: "get",
            url: "chartexCGI.py",
            data: {"ADSget": true},
            dataType: 'text',
            success: showModal
        });
        
        return false;
    });

    $("#ADSdeleteButton").click(function(){
        $(".loader").show();
        $.ajax({
            type: "get",
            url: "chartexCGI.py",
            data: {"ADSdelete": "True"},
            dataType: 'text',
            success: showModal
        });
        
        return false;
    });


/*****************************/
/* SPARQL search
/*****************************/
    $("#sparqlButton").click(function(){
        var query = $("#sparqlQuery").setSelection(0, 10000);
        var text = $("#sparqlQuery").getSelection().text;
        $(".loader").show();
    
        $.ajax({
            type: "get",
            url: "chartexCGI.py",
            data: {'sparqlQuery': text},
            dataType: 'text',
            success: showModal,
            error: function(jqXHR, textStatus, errorThrown) {
                //console.log(jqXHR.response, textStatus, errorThrown);
            }
        });
        
        return false;
    });
    
    $("#remove_graphs").click(function(){
        $("#dotimg, #rdfout").empty();
        $(".expanded a").first().trigger('click');
        $('#doc_text').empty();
        $('#doc_text_display').hide();
        return false;
    });
});
