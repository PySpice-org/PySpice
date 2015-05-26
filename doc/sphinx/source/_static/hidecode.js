$(document).ready(function() {
  /* Add a [>>>] button on the top-right corner of getthecode div to show the code */
  var div = $('.getthecode-header')
  
  var button_text = 'Show/Hide the code';

  var button_styles = {
    'cursor':'pointer',
    'float': 'right',
    'text-size': '75%',
    'font-family': 'monospace'
  }
  
  div.each(function(index) {
    var jthis = $(this);
    var button = $('<span class="show-code-button">&gt;&gt;&gt;</span><div style="clear:both;"></div>');
    button.css(button_styles)
    button.attr('title', button_text);
    jthis.append(button);
    jthis.parent().find('.highlight-python').toggle();
  });
  
  // define the behavior of the button when it's clicked
  $('.show-code-button').click(function() {
    var button = $(this);
    button.parent().parent().find('.highlight-python').toggle();
  });
});
