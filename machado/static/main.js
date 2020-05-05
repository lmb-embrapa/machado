/*
 Copyright 2018 by Embrapa.  All rights reserved.

 This code is part of the machado distribution and governed by its
 license. Please see the LICENSE.txt and README.md files that should
 have been included as part of this package for licensing information.
 */

// toggles the arrow
function machadoToggleCaret(x) {
  ec = x.getElementsByClassName('fas')[0].classList;
  down = 'fa-caret-down';
  up = 'fa-caret-up';
  if (ec.contains(down)) {
  	ec.remove(down);
  	ec.add(up);
  } else {
  	ec.remove(up);
  	ec.add(down);
  }
}

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

//load autocomplete from API
$( function() {
  $( "#q" ).autocomplete({
    source: function( request, response ) {
      var home_url = $("#home_url").val();
      var url = home_url + "api/autocomplete";
	  $.ajax( {
	    url: url,
        data: { q: request.term	},
        success: function( data ) {	response(data); },
		minLength: 2,
      } );
	},
    select: function( event, ui ) {
		$( "#q" ).val(ui.item.value);
		$('.navbar-form').submit();
	},
  });
} );
