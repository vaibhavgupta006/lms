$(document).ready(function() {
  let dropdown = $(".dropdown");
  let textareas = $("textarea");
  let fileUpload = $("input:file");
  let formsets = $(".dynamic-formset");

  $.each(dropdown, showContent);
  $.each(textareas, bindAutoIncrement);
  $.each(fileUpload, bindGetFileName);
  $.each(formsets, bindAddForm);
});

let bindAutoIncrement = function(index, textarea) {
  $(textarea).on("input copy cut delete", autoIncrementHeight);
};

let bindGetFileName = function(index, fileInput) {
  $(fileInput).on("change", getFileName);
};

let bindAddForm = function(index, formset) {
  formType = $(formset).attr("form-model");

  $(formset).click(function(e) {
    addQuestion(e, formType);
  });
};

let autoIncrementHeight = function(e) {
  textarea = e.target;
  $(textarea).innerHeight(textarea.scrollHeight);
};

let showContent = function(index, dropdown) {
  btn = $(dropdown).find(".dropdown-btn");
  btn.mouseenter(function() {
    content = $(dropdown).find(".dropdown-content");
    content.css({ display: "flex" });
  });
  $(dropdown).mouseleave(function() {
    content = $(dropdown).find(".dropdown-content");
    content.css({ display: "none" });
  });
};

let getFileName = function(e) {
  filename = e.target.files[0].name;
  id = e.target.id;
  customUploadButton = $(`.file[for="${id}"]`);
  customUploadButton.html(`<p>Choose file</p> ${filename}`);
};

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

  newForm.insertBefore(".dynamic-formset");
  return false;
};

let incrementAttrs = function(element, attrName) {
  attr = $(element).attr(attrName);
  newAttr = attr.split("-");
  newAttr[1] = parseInt(newAttr[1]) + 1;
  newAttr = newAttr.join("-");
  $(element).attr(attrName, newAttr);
};
