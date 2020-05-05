/*
 Copyright 2018 by Embrapa.  All rights reserved.

 This code is part of the machado distribution and governed by its
 license. Please see the LICENSE.txt and README.md files that should
 have been included as part of this package for licensing information.
 */

function machadoToggleText(x) {
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

$(document).ready(function(){
  $('#collapseSeq').on('show.bs.collapse', function() {
    var feature_id = $("#feature_id").val();
    var home_url = $("#home_url").val();
    var url = home_url + "api/feature/sequence/" + feature_id;
    if ($("#collapseSeq .card-text small").is(':empty')) {
      $.ajax({
          url : url,
          beforeSend : function(){
            $("#resultado").html("LOADING...");
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
