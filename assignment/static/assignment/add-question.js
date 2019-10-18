$(document).ready(function() {
  formType = $(".add-more").attr("form-model");
  $(".add-more").click(function(e) {
    addQuestion(e, formType);
  });
});

let addQuestion = function(e, formType) {
  e.preventDefault();
  newForm = $(".form")
    .last()
    .clone(true);

  $.each(newForm.find("label"), function(index, label) {
    incrementAttrs(label, "for");
  });

  $.each(newForm.find("input"), function(index, input) {
    $(input).val("");
    incrementAttrs(input, "name");
    incrementAttrs(input, "id");
  });

  $.each(newForm.find("textarea"), function(index, textarea) {
    $(textarea).val("");
    incrementAttrs(textarea, "name");
    incrementAttrs(textarea, "id");
  });

  formCount = $(`#id_${formType}-TOTAL_FORMS`);
  newCount = parseInt(formCount.attr("value")) + 1;
  formCount.attr("value", newCount);

  newForm.insertBefore(".add-more");
  return false;
};

let incrementAttrs = function(element, attrName) {
  attr = $(element).attr(attrName);
  newAttr = attr.split("-");
  newAttr[1] = parseInt(newAttr[1]) + 1;
  newAttr = newAttr.join("-");
  $(element).attr(attrName, newAttr);
};
