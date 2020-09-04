/*
 Copyright 2018 by Embrapa.  All rights reserved.

 This code is part of the machado distribution and governed by its
 license. Please see the LICENSE.txt and README.md files that should
 have been included as part of this package for licensing information.
 */

//load ontology terms from API
$(document).ready(function(){
  $("#collapseOntology").click(loadOntologyTerms());
});
function loadOntologyTerms(){
    var feature_id = $("#feature_id").val();
    var home_url = $("#home_url").val();
    var url = home_url + "api/feature/ontology/" + feature_id;
    if ($("#collapseOntology .table").is(':empty')) {
      $.ajax({
          url : url,
          beforeSend : function(){
            $("#collapseOntology .table").html("<small>LOADING...</small>");
          }, 
          success: function(data) {
            var text = '<thead><tr>';
            text += '<th scope="col">Ontology</th>';
            text += '<th scope="col">ID</th>';
            text += '<th scope="col">Term</th>';
            text += '</tr></thead>';
            text += '<tbody>';

            for (i=0; i<data.length; i++) {
              text += '<tr>'
              text += '<td>' + data[i]['cv'] + '</td>';
              text += '<td>' + data[i]['db'] + ':' + data[i]['dbxref'] + '</td>';
              text += '<td>' + data[i]['cvterm'] + '</td>';
              text += '</tr>'
            }
            text += "</tbody>" ;
            $("#collapseOntology .table").html(text);
          }
      });    
    }
} 

//load protein matches from API
$(document).ready(function(){
  $("#collapseProteinMatches").click(loadProteinMatches());
});
function loadProteinMatches(){
    var feature_id = $("#feature_id").val();
    var home_url = $("#home_url").val();
    var url = home_url + "api/feature/proteinmatches/" + feature_id;
    if ($("#collapseProteinMatches .table").is(':empty')) {
      $.ajax({
          url : url,
          beforeSend : function(){
            $("#collapseProteinMatches .table").html("<small>LOADING...</small>");
          }, 
          success: function(data) {
            var text = '<thead><tr>';
            text += '<th scope="col">Protein database</th>';
            text += '<th scope="col">Protein domain</th>';
            text += '</tr></thead>';
            text += '<tbody>';

            for (i=0; i<data.length; i++) {
              text += '<tr>'
              text += '<td>' + data[i]['db'] + '</td>';
              text += '<td>' + data[i]['subject_id'] + ' ' + data[i]['subject_desc'] + '</td>';
              text += '</tr>'
            }
            text += "</tbody></table>" ;
            $("#collapseProteinMatches .table").html(text);
          }
      });    
    }
}

//load similarity from API
$(document).ready(function(){
  $("#collapseSimilarity").click(loadSimilarity());
});
function loadSimilarity(){
    var feature_id = $("#feature_id").val();
    var home_url = $("#home_url").val();
    var url = home_url + "api/feature/similarity/" + feature_id;
    if ($("#collapseSimilarity .table").is(':empty')) {
      $.ajax({
          url : url,
          beforeSend : function(){
            $("#collapseOntology .table").html("<small>LOADING...</small>");
          }, 
          success: function(data) {
            var text = '<thead><tr>';
            text += '<th scope="col">Program</th>';
            text += '<th scope="col">Hit</th>';
            text += '<th scope="col">Query start</th>';
            text += '<th scope="col">Query end</th>';
            text += '<th scope="col">Score</th>';
            text += '<th scope="col">Evalue</th>';
            text += '</tr></thead>';
            text += '<tbody>';

            for (i=0; i<data.length; i++) {
              if (!data[i]['uniquename']) {
                  uniquename = ""
              } else {
                  uniquename = data[i]['uniquename']
              }
              if (!data[i]['name']) {
                  name = ""
              } else {
                  name = data[i]['name']
              }

              text += '<tr>'
              text += '<td>' + data[i]['program'] + ' ' + data[i]['programversion'] + '</td>';
              if (data[i]['db_name'] == 'BLAST_SOURCE' && data[i]['sotype'] == 'polypeptide') {
                  text += '<td>' + data[i]['db_name'] + ' ' + uniquename + ' <a href="https://www.ncbi.nlm.nih.gov/protein/' + name + '" target="_blank">' + name + '</a></td>';
              }
              else {
                text += '<td>' + data[i]['db_name'] + ' ' + uniquename + ' ' + name + '</td>';
              }
              text += '<td>' + data[i]['query_start'] + '</td>';
              text += '<td>' + data[i]['query_end'] + '</td>';
              text += '<td>' + data[i]['score'] + '</td>';
              text += '<td>' + data[i]['evalue'] + '</td>';
              text += '</tr>'
            }
            text += "</tbody>" ;
            $("#collapseSimilarity .table").html(text);
          }
      });    
    }
} 

//load orthologs from API
$(document).ready(function(){
  $("#collapseOrthologs").click(loadOrthologs());
});
function loadOrthologs(){
  $('#collapseOrthologs').on('show.bs.collapse', function() {
    var feature_id = $("#feature_id").val();
    var home_url = $("#home_url").val();
    var url = home_url + "api/feature/ortholog/" + feature_id;
    if ($("#collapseOrthologs .card-text").is(':empty')) {
      $.ajax({
          url : url,
          beforeSend : function(){
            $("#collapseOrthologs .card-text").html("<small>LOADING...</small>");
          }, 
          success: function(data) {
            var text = '<ul class="list-group list-group-flush">';
            text += '<li class="list-group-item list-group-item-secondary">Orthologous group: <a href="' + home_url + 'find/?selected_facets=orthologous_group:' + data['ortholog_group'] + '">' + data['ortholog_group'] + '</a></li>';
            var members = data['members'];
            for (i=0; i<members.length; i++) {
              text += '<li class="list-group-item">' ;
              text += '<a href="' + home_url + 'feature/?feature_id=' + members[i].feature_id + '">' + members[i].uniquename + '</a> ';
              text += members[i].display + ' ';
              text += '<i>' +members[i].organism + '</i>';
              text += "</li>" ;
            }
            text += "</ul>" ;
            $("#collapseOrthologs .card-text").html(text);
          }
      });    
    }
  });
} 

//load publication from API
$(document).ready(function(){
  $("#collapsePub").click(loadPublication());
});
function loadPublication(){
  $('#collapsePub').on('show.bs.collapse', function() {
    var feature_id = $("#feature_id").val();
    var home_url = $("#home_url").val();
    var url = home_url + "api/feature/publication/" + feature_id;
    if ($("#collapsePub .card-text").is(':empty')) {
      $.ajax({
          url : url,
          beforeSend : function(){
            $("#collapsePub .card-text").html("<small>LOADING...</small>");
          }, 
          success: function(data) {
            var text = '<ul class="list-group">';
            for (i=0; i<data.length; i++) {
              var text = '<li class="list-group-item"><small>' ;
              text += data[i].authors + ' ';
              text += '<b>' + data[i].title + '</b> ';
              text += '<i>' + data[i].series_name + '</i>.  ';
              text += data[i].pyear + '; ' + data[i].volume + ' ' + data[i].pages + ' ';
              if (data[i].doi) {
                text += 'DOI:<a target="_blank" href="http://dx.doi.org/' + data[i].doi + '">' + data[i].doi + '</a>';
              }
              text += "</smal></li>" ;
            }
            text += "</ul>" ;
            $("#collapsePub .card-text").html(text);
          }
      });    
    }
  });
}

// load sequence from API
$(document).ready(function(){
  $("#collapseSeq").click(loadSequence());
});
function loadSequence(){
  $('#collapseSeq').on('show.bs.collapse', function() {
    var feature_id = $("#feature_id").val();
    var home_url = $("#home_url").val();
    var url = home_url + "api/feature/sequence/" + feature_id;
    if ($("#collapseSeq .card-text small").is(':empty')) {
      $.ajax({
          url : url,
          beforeSend : function(){
            $("#collapseSeq .card-text small").html("<small>LOADING...</small>");
          }, 
          success: function(data) {
            $("#collapseSeq .card-text small").text(data.sequence);
          }
      });    
    }
  });
} 

