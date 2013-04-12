var doc_text = "";
var items_for_annotation = {} // NB. this is global for debugging purposes only. It should be made private and passed to sendItemsToPy() in some other way.

var dirs_with_ann_files = undefined
var DATADIR = '/Users/jjc/Sites/Ann2DotRdf/chartex/'

/**************** Only toggles the doc_text display ****************/
function hideme() {
    $('#doc_text_display').toggle('fast');
    $('#doc_text').empty();
}

/**************** Hide this *******************/
function hidethis(what){
    $(what).empty();
    $(what).hide();
}


/********* string repr of object keys ***********/
function keyStrings(obj){
    var returnstring = "";
    for (k in obj){
        returnstring += k + "\n";
    }
    
    return returnstring;
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
    $("#localLoader").css({position: "absolute"}).hide();

}



function vizTriples(pydata){
    var dataIn = pydata.split('<filedelimiter>'); // use json instead of this
    var svg = $(dataIn[0]).find('svg');
    var rdf = dataIn[1];
    items_for_annotation = {};
    $('#doc_text').empty();
    $('#doc_text_display').hide();
    $("#dotimg").empty();
    $("#dotimg").append(dataIn[0]);
    $("svg")[0].width.baseVal.value = 400;
    $("svg")[0].height.baseVal.value = 400;    
    
    
    
    $('.node').on('contextmenu', function(){return false;}).mousedown(function(event) {
        switch (event.which) {
            case 1:
                var $that = $(this);
                var offsets = [];
                $that.find('text').contents().each(function(i) {
                    var regexp = /\((\d+),\s(\d+)\)/g;
                    var match = regexp.exec(this.data);
                    if (match !== null) {
                        offsets.push([match[1], match[2]]);
                    }
                });
        
                var fillColor = $(this).find('ellipse').css('fill');
                $("#doc_text").html(replaceOffset(doc_text, offsets, '<span style="background-color:' + fillColor + '">'));
                var X = event.pageX - 200;
                var Y = event.pageY + 16;
                $('#doc_text_display').hide();
                $('#doc_text_display').css('overflow-y', 'auto');
                $('#doc_text_display').css({
                    left: X,
                    top: Y
                }).toggle('slow');
                break;
            case 2:
                //alert('Middle mouse button pressed');
                break;
            case 3:
                var entity = $(this).find('a')[0].getAttribute('xlink:title').toString();
                // for the moment, let's just work with the edges below
                //if (!(entity in items_for_annotation)){items_for_annotation[entity] = true;};
                break;
            default:
                alert('You have a strange mouse');
        }
    });
    
    $('.edge').on('contextmenu', function(){return false;}).mousedown(function(event) {
        
        switch (event.which) {
            case 1:
                //alert('Left mouse button pressed');
                break;
            case 2:
                //alert('Middle mouse button pressed');
                break;
            case 3:
                
                
                var link_title = $(this).find('a')[0].getAttribute('xlink:title')
                var edge_triple = link_title.split(', ');
                if (!(edge_triple in items_for_annotation)){
                    items_for_annotation[edge_triple] = true;
                };
                break;
            default:
                alert('You have a strange mouse');
        }
    });
}

function sendItemsToPy(annotation_graph_name){
    $.ajax({
        url: "chartexCGI.py",
        dataType: 'text',
        data: {'items': JSON.stringify(items_for_annotation), 'gname': '<' + annotation_graph_name + '>'},
        error: function(jqXHR, textStatus, errorThrown) {
            //console.log(jqXHR.response, textStatus, errorThrown);
        },
        success: showModal
    });
    $("#localLoader").hide();
}

function uploadAnnotationTriples(){
    null
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
    if (response.items){
        $("#localLoader").hide();
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
    $("#localLoader").hide();
}

function showLocalLoader(obj){
    ot = obj.position().top
    $("#localLoader").css({left: "8%", top: ot - 6}).show()
}

/******************************************************************************************************************
* some of the following stuff does not have to be in document.ready.
* apparently, naked click handlers do.
********************************************************************************************************************/

$(document).ready(function() {

/*****************************/
/* Baggins Annotation Test
/*****************************/
$("#bagginsTest").click(function(){
    // recap an abbreviated deployData suite here with annotation functions
    $.get("annoData", function(data,status){
        var selected_triples = [];
        var dataIn = data.split('<filedelimiter>'); // use json instead of this
        var svg = $(dataIn[0]).find('svg');
        var rdf = dataIn[1];
        var doc_text = dataIn[2]

        $('#doc_text').empty();
        $('#doc_text_display').hide();
        $("#dotimg").empty();
        $("#dotimg").append(dataIn[0]);
        $("svg")[0].width.baseVal.value = 400;
        $("svg")[0].height.baseVal.value = 400;    
        $("#rdfout").html('<pre>' + rdf + '</pre>');    
        
        
        
        $('.node').on('contextmenu', function(){return false;}).mousedown(function(event) {
            switch (event.which) {
                case 1:
                    var $that = $(this);
                    var offsets = [];
                    $that.find('text').contents().each(function(i) {
                        var regexp = /\((\d+),\s(\d+)\)/g;
                        var match = regexp.exec(this.data);
                        if (match !== null) {
                            offsets.push([match[1], match[2]]);
                        }
                    });
            
                    var fillColor = $(this).find('ellipse').css('fill');
                    $("#doc_text").html(replaceOffset(doc_text, offsets, '<span style="background-color:' + fillColor + '">'));
                    var X = event.pageX - 200;
                    var Y = event.pageY + 16;
                    $('#doc_text_display').hide();
                    $('#doc_text_display').css('overflow-y', 'auto');
                    $('#doc_text_display').css({
                        left: X,
                        top: Y
                    }).toggle('slow');
                    break;
                case 2:
                    //alert('Middle mouse button pressed');
                    break;
                case 3:
                    console.log($(this).find('a')[0].getAttribute('xlink:title'));
                    break;
                default:
                    alert('You have a strange mouse');
            }
        });
        
        $('.edge').on('contextmenu', function(){return false;}).mousedown(function(event) {
            
            switch (event.which) {
                case 1:
                    //alert('Left mouse button pressed');
                    break;
                case 2:
                    //alert('Middle mouse button pressed');
                    break;
                case 3:
                    edge_triple = $(this).find('a')[0].getAttribute('xlink:title').split(', ');
                    selected_triples.push(edge_triple);
                    console.dir(selected_triples);
                    //OK: now pass this to a form for creating an annotation
                    break;
                default:
                    alert('You have a strange mouse');
            }
        });
        
    });
// document.getElementById("edge2").getElementsByTagName('a')[0].getAttribute('xlink:title').split(', ')
// use this instead of click: 

})

$(".send_items").click(function(){

    var sample_annotation_uri = "http://chartex.org/user_name/graph/Target#frodo_annotation1";
    sendItemsToPy(sample_annotation_uri);
    showLocalLoader($(this));
    return false;
});

$("#sendOA").click(function(){
    /// this should be moved into a named function above
    showLocalLoader($(this));
    var annotation_uri = "http://chartex.org/user_name/graph/Annotation#frodo_annotation1"
    var target_uri = "http://chartex.org/user_name/graph/Target#frodo_annotation1"
    var body_uri = "http://chartex.org/user_name/graph/Body#frodo_annotation1"
    var content_text = $("#cnt_chars").val();
    $.ajax({
        type: "get",
        url: "chartexCGI.py",
        data: {
            "annotationURI": annotation_uri,
            "targetURI": target_uri,
            "bodyURI": body_uri,
            "contentText": content_text
        },
        dataType: 'text',
        success: showModal
    });
    return false;
});

$(".show_items").click(function(){
    showModal(keyStrings(items_for_annotation))
});


$(".dump_triples").click(function(){
    $thisform = $(this).parents(".getTriples");
    var serialFormat = $thisform.find(".serFormat option:selected").val();
    showLocalLoader($(this));
    $.ajax({
        type: "get",
        url: "chartexCGI.py",
        data: {"dumpTriples": true, "serialFormat": serialFormat},
        dataType: 'text',
        success: showModal
    });
    
    return false;
});

$(".get_filtered_triples").click(function(){
    showLocalLoader($(this));
    $thisform = $(".get_filtered_triples").parents(".SPOGretrieval")
    var s = $thisform.find("input.subj").val() || undefined;
    var p = $thisform.find("input.pred").val() || undefined;
    var o = $thisform.find("input.obj").val()  || undefined;
    var g = $thisform.find("input.ctxt").val() || undefined;
    var serialFormat = $thisform.find(".serFormat option:selected").val() || undefined;

    $.ajax({
        type: "get",
        url: "chartexCGI.py",
        data: {'SPOGretrieval': true,
            's': s,
            'p': p,
            'o': o,
            'g': g,
            'serialFormat': serialFormat},
        dataType: 'text',
        success: showModal,
        error: function(jqXHR, textStatus, errorThrown) {
            //console.log(jqXHR.response, textStatus, errorThrown);
        }
    });
    return false;    
});

$(".get_contexts").click(function(){
    showLocalLoader($(this));

    $.ajax({
        type: "get",
        url: "chartexCGI.py",
        data: {'get_contexts': true},
        dataType: 'text',
        success: showModal,
        error: function(jqXHR, textStatus, errorThrown) {
            //console.log(jqXHR.response, textStatus, errorThrown);
        }
    });
    return false;    

});
/*****************************/
/* named graph problem
/*****************************/

$("#namedGraph1").click(function(){
        showLocalLoader($(this));
        $.ajax({
            type: "get",
            url: "chartexCGI.py",
            data: {"namedGraph1": true},
            dataType: 'text',
            success: showModal
        });
});

$("#namedGraph2").click(function(){
        showLocalLoader($(this));
        $.ajax({
            type: "get",
            url: "chartexCGI.py",
            data: {"namedGraph2": true},
            dataType: 'text',
            success: showModal
        });
});

$("#namedGraph3").click(function(){
        showLocalLoader($(this));
        $.ajax({
            type: "get",
            url: "chartexCGI.py",
            data: {"namedGraph3": true},
            dataType: 'text',
            success: showModal
        });
});

$("#utilButton").click(function(e){
//         showLocalLoader($(this));

//         $.ajax({
//             type: "get",
//             url: "chartexCGI.py",
//             data: {"utilButton": true},
//             dataType: 'text',
//             success: showModal
//         });
});

$("#deleteStatements").click(function(){
        showLocalLoader($(this));
        $.ajax({
            type: "get",
            url: "chartexCGI.py",
            data: {"ADSdelete": true},
            dataType: 'text',
            success: showModal
        });
});



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
                $(".directoriesList").append('<option value="'+ dirs_with_ann_files[i] +'">' + dirs_with_ann_files[i].split('/').slice(6).join('/') + '</option>');
            }
        }
    });


/*****************************/
/* Stupid UI tricks 
/* this is pretty clumsy: use a jQuery ui widget instead.
/*****************************/

    /* remember that the following depends on classes being in the right order eg .swap .levSearch */    
    $(".swap").click(function(){
        $(".expanded a").first().trigger('click');
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
            beforeSend: function(){
                $("#localLoader").css({position: "fixed", left: "8%", top: "50%"}).show()
            },
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
        var dirToSearch = $("select.directoriesList").val();
        var EntityToSearch = $("select#EntityToSearch").val();
        var editDistance = $("select#editDistance").val();
        var targetString = $("input#searchstring").val();
        showLocalLoader($(this));
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
        if ($(".grepSearch input:text").val() == '') {alert("ya gotta gimme somethin'"); return false;};
        var dirToSearch = $(".grepSearch option:selected").val();
        var filetype = $(".grepSearch input:radio:checked").val();
        var targetString = $(".grepSearch input:text").val();
        showLocalLoader($(this));

        $.ajax({
            type: "get",
            url: "chartexCGI.py",
            data: {'searchstring': targetString, 'filetype': filetype, 'dirToSearch': dirToSearch},
            dataType: 'json',
            success: function(pydata){
                // really should break this out into a named function, and do something more rational
                // with all that stupid templating crap.
                if (pydata.length > 0) {
                    $("#result-div").remove();
                    $("#localLoader").hide();
                    
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
                    $("#localLoader").hide();
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
        showLocalLoader($(this));
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
/* JUST SERIALIZE __ now this is independent of element ids
/* example URL: http://neolography.com/chartex/chartexCGI.py?serialDir=/home/neolog/webapps/brat/brat-v1.3_Crunchy_Frog/data/inter-coding-exercise/Jon&serialFormat=n3
/*****************************/

    $(".serializeButton").click(function(){
        $thisform = $(this).parents(".serializeForm");
        var serialDir = $thisform.find(".directoriesList option:selected").val();
        var serialFormat = $thisform.find(".serFormat option:selected").val();
        
        var ifradio = $thisform.find("input:radio:checked").val();
        var pyfile = (ifradio == undefined)? "chartexCGI.py" : ifradio;
        showLocalLoader($(this));
        

        $.ajax({
            type: "get",
            url: pyfile,
            data: {"serialDir": serialDir, "serialFormat": serialFormat},
            dataType: 'text',
            success: showModal,
            error: function(jqXHR, textStatus, errorThrown) {
                console.log(jqXHR.response, textStatus, errorThrown);
            }
        
        });
        return false;
    });

/*****************************/
/* ADSUpload
/*****************************/

    $("#ADSUpload").click(function(){
        $thisform = $("#ADSUpload").parents(".serializeForm")
        var ADSserialDir = $thisform.find(".directoriesList option:selected").val();
        var serialFormat = $thisform.find(".serFormat option:selected").val();

        var ifradio = $thisform.find("input:radio:checked").val();
        var pyfile = (ifradio == undefined)? "chartexCGI.py" : ifradio;

        showLocalLoader($(this));
                
        $.ajax({
            type: "get",
            url: pyfile,
            data: {"ADSUpload": true, "serialDir": ADSserialDir, "serialFormat": serialFormat},
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
        $thisform = $("#ADSserializeButton").parents(".serializeForm")
        var ADSserialDir = $thisform.find(".directoriesList option:selected").val();
        var serialFormat = "turtle";
        showLocalLoader($(this));
        
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


/**************************/

    $("#ADSaddButton").click(function(){
        $thisform = $("#ADSaddButton").parents(".serializeForm")
        var addDir = $thisform.find(".directoriesList option:selected").val();
        showLocalLoader($(this));
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
        showLocalLoader($(this));
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
        showLocalLoader($(this));
        $.ajax({
            type: "get",
            url: "chartexCGI.py",
            data: {"ADSdelete": "True"},
            dataType: 'text',
            success: showModal
        });
        
        return false;
    });

    $(".sendDelete").click(function(){
        $("#ADSdeleteButton").trigger('click');
        showLocalLoader($(this));
        return false;
    })

/*****************************/
/* SPARQL search
/*****************************/
    $("#sparqlButton").click(function(){
        var query = $("#sparqlQuery").setSelection(0, 10000);
        var text = $("#sparqlQuery").getSelection().text;
        showLocalLoader($(this));
    
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
    
    
/*****************************/
/* ADS SPARQL search
/*****************************/
    $("#ADSsparqlButton").click(function(){
        var query = $("#ADSsparqlQuery").setSelection(0, 10000);
        var text = $("#ADSsparqlQuery").getSelection().text;
        var result_format = $("#ADSsparqlForm select").val();
        
        //console.log(result_format);
        
        showLocalLoader($(this));
    
        $.ajax({
            type: "get",
            url: "chartexCGI.py",
            data: {'ADSsparqlQuery': text, 'ADSresult_format': result_format},
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
    
    $(".wipe").click(function(){
        $("#remove_graphs").trigger('click');
    });
    
    $(".toggle_element").click(function(){
        $("#brat_baggins").toggle();
    });
    
    $(".upload_frodo").click(function(){
        showLocalLoader($(this));
    
        $.ajax({
            type: "get",
            url: "chartexCGI.py",
            data: {'upload_frodo': true},
            dataType: 'text',
            success: showModal,
            error: function(jqXHR, textStatus, errorThrown) {
                //console.log(jqXHR.response, textStatus, errorThrown);
            }
        });
        
        return false;    
    });
    
    $(".viz_arbitrary_triples").click(function(){
        showLocalLoader($(this));
    
        $.ajax({
            type: "get",
            url: "chartexCGI.py",
            data: {'viz_arbitrary_triples': true},
            dataType: 'text',
            success: function(pydata){
                vizTriples(pydata);
                $("#localLoader").hide();
            },
            error: function(jqXHR, textStatus, errorThrown) {
                //console.log(jqXHR.response, textStatus, errorThrown);
            }
        });
        
    });
    

    
    $("#add_statement").click(function(){
        triple = "http://yorkhci.org/chartex-schema/lortext#T4, http://yorkhci.org/chartex-schema#is_son_of, http://yorkhci.org/chartex-schema/lortext#T1"
        
        $.ajax({
            type: "get",
            url: "chartexCGI.py",
            data: {'add_statement': triple},
            dataType: 'text',
            success: showModal,
            error: function(jqXHR, textStatus, errorThrown) {
                //console.log(jqXHR.response, textStatus, errorThrown);
            }
        });
        
        return false;
    });
    
    $(".toggle_full_size").toggle(
            function(){
                $('#doc_text_display').hide();
                $("svg")[0].width.baseVal.value = 800;
                $("svg")[0].height.baseVal.value = 800;
            },
            function(){
                $('#doc_text_display').hide();
                $("svg")[0].width.baseVal.value = 1800;
                $("svg")[0].height.baseVal.value = 1800;
            } 
        );
    
});


    