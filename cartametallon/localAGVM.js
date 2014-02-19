// tmplist = {"names":["g"],"values":[["<http://chartex.org/graphid/vicars-choral-416>"],["<http://chartex.org/graphid/vicars-choral-415>"],["<http://chartex.org/graphid/vicars-choral-413>"],["<http://chartex.org/graphid/vicars-choral-english-390>"],["<http://chartex.org/graphid/vicars-choral-428>"],["<http://chartex.org/graphid/vicars-choral-429>"],["<http://chartex.org/graphid/vicars-choral-422>"],["<http://chartex.org/graphid/vicars-choral-423>"],["<http://chartex.org/graphid/vicars-choral-400>"],["<http://chartex.org/graphid/vicars-choral-401>"],["<http://chartex.org/graphid/vicars-choral-402>"],["<http://chartex.org/graphid/vicars-choral-403>"],["<http://chartex.org/graphid/vicars-choral-399>"]]}

//tmpglobal = null
//tmpglobal1 = null
docpath = "/Users/jjc/Sites/Ann2DotRdf/chartex/vicars-choral/"
DEEDS_DIR = "/Users/jjc/Sites/Ann2DotRdf/chartex/deeds/"

function showModal(response){
    response = response.replace(/</g, "&lt;");
    response = response.replace(/>/g, "&gt;");
    $("#modalsink").html('<pre>' + response + '</pre>');
    $("#modalsink").modal({
        minWidth: 800,
        maxWidth: 1000,
        maxHeight: 650,
        overlayClose:true,
        opacity:80
    });
    $("#localLoader").hide();
}

function showModalHTML(response){
    $("#modalsink").html(response);
    $("#modalsink").modal({
        minWidth: 800,
        maxWidth: 1000,
        maxHeight: 650,
        overlayClose:true,
        opacity:80
    });
    $("#localLoader").hide();
}

function showLocalLoader(){
    $("#localLoader").show()
}

function hideLocalLoader(){
    $("#localLoader").hide();
}

function hideme() {
    $('#entity_data_display, #databox-wrap').hide('fast');
    $('#entity_data, #databox').empty();
}

function closeThis(box) {
    box.parent().children().eq(1).empty();
    box.parent().hide();
}

function getFrag(uri){
    frag = uri.split('#')[1].replace('>','');
    return frag;
}

function swapBrackets(str){
    str = str.replace(/</, '&lt;').replace(/>/, '&gt;');
    return str;
}

String.prototype.format = function () {
  // Using it as a crude templating mechanism, thus:
  // string = "<div><p class='{0}'>I want a {0} of spam eggs and ham {1}<p></div>"
  // string.format("breakfast-order", "right away")
  // -> "<div><p class='breakfast-order'>I want a breakfast-order of spam eggs and ham right away<p></div>"
  var args = arguments;
  return this.replace(/\{(\d+)\}/g, function (m, n) { return args[n]; });
};


function getDocumentTable(data){
    $("#tabledisplay").empty();
    $("#tabledisplay").append('<div class="result-div"><table id="result-table" class="tablesorter"><thead><tr><th>Charter</th></tr></thead><tbody id="result"></tbody></table></div>');
    data.values.forEach(function(item){
        var adoc = item[0].split('/').pop().replace('>', '');
        $("#result").append('<tr><td>' + '<a class="charterID" href="#" name="' + adoc + '" onClick="graphMe(\'' + adoc + '\');showLocalLoader();">' + adoc + '</a></td></tr>');
    });
    $("#result-table").tablesorter();
    
    setTimeout(hideLocalLoader, 500);
    $(".block-toggle").find('img')[0].src = "http://localhost/Sites/images/icons/down13.gif";
}

function getDeedsDocumentTable(data){
    $("#deedsList").empty();
    $("#deedsList").append('<div class="result-div"><table id="document-table" class="tablesorter"><thead><tr><th>Charter</th></tr></thead><tbody id="result"></tbody></table></div>');
    data.forEach(function(item){
        
        var doc = item.split('.');
        
        if (doc[1] == 'ann'){
        
            $("#document-table").append('<tr><td>' + '<a class="charterID" href="#" name="' + doc + '" onClick="generateDocumentGraph(\'' + item + '\');showLocalLoader();">' + item + '</a></td></tr>');
        }
    });
    $("#document-table").tablesorter();
    
    //setTimeout(hideLocalLoader, 500);
    $(".block-toggle").find('img')[0].src = "http://localhost/Sites/images/icons/down13.gif";
}


function inContext(txtin, offsets){
    offsets.forEach(function(i){
        var start = i[0];
        var end = i[1];
        txtin[start] = "<span class=\"highlight\">" + txtin[start];
        txtin[end] = txtin[end] + "</span>";
    });
    
    return txtin.join('');
}

function annotateGraph(target, username, confidence, comment){
    $.ajax({
        type: "get",
        url: "localAGVM.py",
        data: {"target": target, "username": username, "confidence": confidence, "comment": comment},
        dataType: 'text',
        success: function(data){
            showModal(data);
            hideLocalLoader();
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log(jqXHR.response, textStatus, errorThrown);
        }
    });
}

function annotateTarget(annbutton){
    // handle cases where aotarget is graph uriRef, triple, or Node uriRef.
    // this only handles case where aotarget is a graph uri.
    var confidence_value = annbutton.parent().text().slice(0,6);
    var aotarget = annbutton.context.value;
    var s = aotarget.split('/').slice(-1)[0].replace('>','');
    var statement = s.match(/(.*\d+)(.*)([A-Z].*)/);
    var dmstatement = swapBrackets(statement[1] + " " + statement[2] + " " + statement[3]);
        
    $.get('./annote.html', function(template){
        // see above for String.prototype.format use here //
        showModalHTML(template.format(dmstatement, confidence_value));

        $("#dothis").on('click', function(e){
            var target = aotarget;
            var username = $('#confidence-annotation-input input[name=user]').val();
            var confidence = $('#confidence-annotation-input input[name=cvalue]:checked').val();
            var comment = $('#confidence-annotation-input textarea').val();
            showLocalLoader();
            annotateGraph(target, username, confidence, comment);
        });
    });  
}

function retrieveConfidenceAnnotations(){
    $.ajax({
        type: "get",
        url: "localAGVM.py",
        data: {'getConfidenceAnnotations': true, 'format':'text/rdf+n3'},
        dataType: 'text',
        success: function(data){
            showModal(data);
            hideLocalLoader();
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log(jqXHR.response, textStatus, errorThrown);
        }
    });
    
}

function exDoc(entID, filename, event){
    $.ajax({
        type: "get",
        url: "localAGVM.py",
        data: {"exDoc": filename, "entID": entID},
        dataType: 'json',
        success: function(json){
            exdoc = $(document.createElement('div'));
            exdoc.addClass('exdoc')
                .css({'top': '500px',
                    'left': '16px',
                    'position':'absolute'
                }).draggable();
            
            var color = json.color;
            var offin = json.offsets.toString().replace(/"/g, '');
            var offout = eval('[' + offin.replace(/\s/g, ',').replace(/\(/g, '[').replace(/\)/g, ']') + ']');
            var txt = json.text.split('');
            var html = inContext(txt, offout);

            exdoc.html(html).find("span").css('background-color', color);
            exdoc.prepend("<img class=\"close\" style=\"cursor: pointer;\" src=\"../images/close.png\"><h1>" + filename + "</h1><br />");
            exdoc.click(function(e){
                $('.exdoc').css({'z-index': '0'});
                $(this).css({'z-index': '1'});    
            });
            
            exdoc.find(".close").click(function(){
                $(this).parent().remove();
            });
            
            $("body").append(exdoc);
            
            hideLocalLoader();
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log(jqXHR.response, textStatus, errorThrown);
        }
        
    });
}

function getEntityData(entID, json, $that){
    // make entity attributes table
    $("#entity_data").empty();
    $("#entity_data").append('<table id="pvtable" class="tablesorter"><thead><tr><th>Property</th><th>Value</th></tr></thead><tbody id="pvresult"></tbody></table>');
    
    $("#pvresult").append("<tr><td>Entity ID</td><td>" + entID + "</td></tr>");
    for (a in json.entityAttributes[entID]){
        $("#pvresult").append("<tr><td>" + a + "</td><td>" + json.entityAttributes[entID][a] + "</td></tr>")        
    }
    for (r in json.entityRelations[entID]){
        $("#pvresult").append("<tr><td>" + r + "</td><td>" + json.entityRelations[entID][r] + "</td></tr>")        
    }
    $("#pvtable").tablesorter();


    // make entity goodness table
    gid = "<http://chartex.org/graphid/"
//     gt = document.createElement('div');
//     gt.id = "goodness-table";
//    $("#entity_data").append(gt);
    if (json.confidence['<' + entID + '>'] == undefined){
//        $("#goodness-table").empty();
        $("#entity_data").append("<p class=\"msg\">Entities in other documents that this Entity 'might_be': None</p>");
    } else { //<http://chartex.org/graphid/Person_10434might_bePerson_10622>//
        $("#entity_data").append("<p class=\"msg\">Entities in other documents that this Entity 'might_be':</p>");
        $("#entity_data").append('<table id="goodness" class="tablesorter"><thead><tr><th>Entity</th><th>String value</th><th>in File</th><th>Confidence</th></tr></thead><tbody id="goodness-result"></tbody></table>');
        json.confidence['<' + entID + '>'].forEach(function(item){
            var fn = item.file.replace(/\"/g,'');
            $("#goodness-result").append('<tr><td>' + getFrag(item.obj) + '</td><td>' + item.text + '</td><td><a href=\"#\" name=\"' + fn + '.txt\">' + fn + '</a></td><td>' + item.confidence.slice(1,7) + '<button class="conf-ann" value="' + gid + getFrag(entID) + "might_be" + getFrag(item.obj) + ">" + '">ann.</button></td></tr>');
        });

        $(".conf-ann").click(function(){
            var $that = $(this);
            annotateTarget($that);
        });
        
        $("#goodness").tablesorter();
    }

    // highlight entity in context
    var color = $that.find('ellipse').attr('fill')
    var offin = json.entityAttributes[entID].TextRange;
    var offout = eval('[' + offin.replace(/\s/g, ',').replace(/\(/g, '[').replace(/\)/g, ']') + ']');
    var txt = json.charterText.split('');
    var html = inContext(txt, offout);
    
    $("#graphed-charter-text").html(html);
    $(".highlight").css('backgroundColor', color);
    var firstkey = Object.keys(json.entityAttributes)[0];
    var filename = json.entityAttributes[firstkey].File
    $("#graphed-charter-text").prepend("<h1>"+ filename +".txt</h1>");
    

}

function deploySVG(json){ //called by graphMe(charterid)
    _json = json;
    var svg = json.svg;
    $(".exdoc").remove();
    $("#graphed-charter-text").text(json.charterText);
    var firstkey = Object.keys(json.entityAttributes)[0];
    var filename = json.entityAttributes[firstkey].File
    $("#graphed-charter-text").prepend("<h1>"+ filename +".txt</h1>");
    $("#graphed-charter-text").show();
    $("#dotimg").empty();
    $("#dotimg").append(svg);
    $("svg").draggable();
    
    $('.node').click(function(e) {
        $(".exdoc").remove();
        var $that = $(this);
        var entID = $that.context.id;
        getEntityData(entID, json, $that);
        
    // now show it:
        var X = e.pageX - 200;
        var Y = e.pageY + 16;
        $('#entity_data_display').hide();
        $('#entity_data_display').css('overflow-y', 'auto');
        $('#entity_data_display').css({
            left: X,
            top: Y
        }).toggle('slow');
    });
    
    // make node ellipse an outline if the entity has 'might_be' relations
    for (node in json.confidence){
        var nodeid = node.replace(/[<>]/g, '');
        var bubble = $(document.getElementById(nodeid)).find('ellipse');
        var fillColor = bubble.attr('fill');
        bubble.css({'stroke':fillColor, 'stroke-width': '6px', 'fill':'#fff'});
    }
    

    var gwidth = $("svg")[0].width.baseVal.value;
    var gheight = $("svg")[0].height.baseVal.value;
    $("svg")[0].width.baseVal.value = 800;
    $("svg")[0].height.baseVal.value = 800;
    hideLocalLoader();
}

function deployBratCharterSVG(json){ //called by generateDocumentGraph(charterid)\
    // TODO modify this to display brat charter graph, no bmg data.
    
    _json = json;
    var svg = json.svg;
    var filename = json.charterText.split('\n')[0];
    chartertext = json.charterText;
    
    $("#graphed-charter-text").append('div class="content"').text(json.charterText);
    $("#graphed-charter-text").prepend("<h1>"+ filename +".txt</h1>");
    $("#graphed-charter-text").show();
    $("#dotimg").empty();
    $("#dotimg").append(svg);
    $("svg").draggable();
    
    $('.node').click(function(e) {
        var fill = $(this).find('ellipse').attr('fill');
        var nodeID = $(this).attr('id');
        var offsets = json.entityAttributes[nodeID].offsets;
        var html = inContext(chartertext.split(''), offsets);
        
        $("#graphed-charter-text").html(html).find("span").css('background-color', fill);
        $("#graphed-charter-text").prepend("<h1>" + filename + "</h1>");
        
        //$("g[id='http://chartex.org/document/deeds-00880041#T3']").find('ellipse').attr('fill')
        
    });
    
    var gwidth = $("svg")[0].width.baseVal.value;
    var gheight = $("svg")[0].height.baseVal.value;
    $("svg")[0].width.baseVal.value = 800;
    $("svg")[0].height.baseVal.value = 800;
    hideLocalLoader();
}

function bmgTest(){
    $.ajax({
        url: "localAGVM.py",
        dataType: 'text',
        error: function(jqXHR, textStatus, errorThrown) {
            //console.log(jqXHR.response, textStatus, errorThrown);
        },
        success: showModal
    });
    $("#localLoader").hide();
}

function getDocs(){
//     getDocumentTable(tmplist);

    $.ajax({
        type: "get",
        url: "localAGVM.py",
        data: {'getDocumentContexts': true},
        dataType: 'json',
        success: getDocumentTable,
        error: function(jqXHR, textStatus, errorThrown) {
            console.log(jqXHR.response, textStatus, errorThrown);
        }
    });
}

function getDeedsDocs(){
//     getDocumentTable(tmplist);

    $.ajax({
        type: "get",
        url: "localAGVM.py",
        data: {'getDeedsDocuments': true},
        dataType: 'json',
        success: getDeedsDocumentTable,
        error: function(jqXHR, textStatus, errorThrown) {
            console.log(jqXHR.response, textStatus, errorThrown);
        }
    });
}

function deployGraphSize(sizetext){
    // use this callback so we can use getGraphSize for subgraphs and do something different with the result
    $("#graph-size").text("current number of statements: " + sizetext);

}

function getGraphSize(uri){
    var uri = (!uri) ? true : '<' + uri + '>';
    
    $.ajax({
        type: "get",
        url: "localAGVM.py",
        data: {'getGraphSize': uri},
        dataType: 'text',
        success: deployGraphSize,
        error: function(jqXHR, textStatus, errorThrown) {
            console.log(jqXHR.response, textStatus, errorThrown);
        }
    });
}

function graphMe(charter){
    hideme();
    $.ajax({
        type: "get",
        url: "localAGVM.py",
        data: {"graphMe": charter},
        dataType: 'json',
        success: deploySVG,
        error: function(jqXHR, textStatus, errorThrown) {
            console.log(jqXHR.response, textStatus, errorThrown);
        }
    });
}

function generateDocumentGraph(charter){
    hideme();
    $.ajax({
        type: "get",
        url: "localAGVM.py",
        data: {"generateDocumentGraph": charter},
        dataType: 'json',
        success: deployBratCharterSVG,
        error: function(jqXHR, textStatus, errorThrown) {
            console.log(jqXHR.response, textStatus, errorThrown);
        }
    });

}

function howto(){ // use instead: $.get with a local template as above in annotateTarget
    $.ajax({
        type: "get",
        url: "localAGVM.py",
        data: {"howto": true},
        dataType: 'html',
        success: showModalHTML,
        error: function(jqXHR, textStatus, errorThrown) {
            console.log(jqXHR.response, textStatus, errorThrown);
        }
    });
}



$(document).ready(function() {
    showLocalLoader();
    getDocs();
    getGraphSize();
    getDeedsDocs();
    
    $( "#entity_data_display" ).draggable().resizable();

    $("#getAnnot").click(function(){
        showLocalLoader();
        retrieveConfidenceAnnotations();
    });

    $("#howtobutton").click(function(){
        showLocalLoader();
        howto();
    });
	
    $(".closeThis").click(function(){
        closeThis($(this));
    });

    $('#entity_data').on('click', 'a', function(event) {
    //  using .on() gets also dynamically created elements.
        showLocalLoader();
        entID = $(this).parent().siblings()[0].textContent;
        console.log(this.name);
        exDoc(entID, this.name, event);
        event.preventDefault();
        return false;
    });
    
    $(".block-toggle").click(function(){
        $that = this;
        $timg = $($that).find('img');
        var right = "http://localhost/Sites/images/icons/right13.gif"
        var down = "http://localhost/Sites/images/icons/down13.gif"
        
        if ($timg[0].src == down){
            $timg[0].src = right;
        } else {$timg[0].src = down}
        
        $($that).next().toggle(500);
    });

});


// s = "(93,108) (358,364) (526,541)"
// out = eval('[' + s.replace(/\s/g, ',').replace(/\(/g, '[').replace(/\)/g, ']') + ']')
// 
// 
// txt = $("#myText").text().split('');
// ofst = [[42,47], [59,70]];
// nodeColor = "#ff9500";
// 
// function inContext(txtin, offsets, color, starttag, endtag){
//     offsets.forEach(function(i){
//         var start = i[0];
//         var end = i[1];
//         txtin[start] = "<span class=\"highlight\">" + txtin[start];
//         txtin[end] = txtin[end] + "</span>";
//     });
//     txtout = txtin.join('');
//     
//     $("#myText").html(txtout);
//     $(".highlight").css('backgroundColor', color);
// }
