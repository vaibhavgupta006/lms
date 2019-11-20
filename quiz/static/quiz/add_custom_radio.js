$(document).ready(function() {
  options = $("ul > li > label");
  $.each(options, function(index, option) {
    custom_checkbox = '<span class="checkmark"></span>';
    $(option).append(custom_checkbox);
  });
});
