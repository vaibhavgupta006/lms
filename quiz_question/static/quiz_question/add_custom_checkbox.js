$(document).ready(function() {
  questions = $(".form-nested");
  $.each(questions, function(index, question) {
    checkbox = $(question).children("input[type='checkbox']");
    checkbox_id = checkbox.attr("id");
    custom_checkbox = `<label for=${checkbox_id} class="checkbox"><i class='material-icons'>check</i></label>`;
    $(question).append(custom_checkbox);
  });
});
