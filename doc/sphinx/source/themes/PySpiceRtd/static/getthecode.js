// https://github.com/FabriceSalvaire/sphinx-getthecode
// Licensed under GPLv3
// Require http://fontawesome.io
$(document).ready(function() {
    // Add a button on the top-right corner of getthecode div to show the code
    $('.getthecode-header').each(function(index) {
	var div = $(this);
	var button = $('<li class="show-code-button"><i class="fa fa-eye" aria-hidden="true"></i><i class="fa fa-eye-slash" aria-hidden="true"></i></li>');
	button.attr('title', 'Show/Hide the code');
	div.find('ul:first').append(button);
	div_highlight = div.parent().find('.highlight').parent();
	if (div_highlight.hasClass('highlight-hidden')) {
	    button.find('.fa-eye-slash').toggle();
	    div_highlight.toggle();
	} else {
	    button.find('.fa-eye').toggle();
	}
    });

    // define the behavior of the button when it's clicked
    $('.show-code-button').click(function() {
	var button = $(this);
	button.parents().eq(3).find('.highlight').parent().toggle();
	button.find('.fa-eye').toggle();
	button.find('.fa-eye-slash').toggle();
    });

    // Add icon to download link
    $('li.getthecode-filename-link > a').append('<i class="fa fa-download" aria-hidden="true"></i>');
});
