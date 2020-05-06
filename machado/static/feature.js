/*
 Copyright 2018 by Embrapa.  All rights reserved.

 This code is part of the machado distribution and governed by its
 license. Please see the LICENSE.txt and README.md files that should
 have been included as part of this package for licensing information.
 */

//load orthologs from API
$(document).ready(function(){
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
            console.log(data);
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
} );

//load publication from API
$(document).ready(function(){
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
} );

// load sequence from API
$(document).ready(function(){
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
            for (i=0; i<data.length; i++) {
              $("#collapseSeq .card-text small").text(data[i].sequence);
            }
          }
      });    
    }
  });
} );
