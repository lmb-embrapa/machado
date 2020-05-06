/*
 Copyright 2018 by Embrapa.  All rights reserved.

 This code is part of the machado distribution and governed by its
 license. Please see the LICENSE.txt and README.md files that should
 have been included as part of this package for licensing information.
 */

// toggles the arrow
$(document).on('click', '.fas', function() {
   $(this).toggleClass('fa-caret-up fa-caret-down');
})

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
