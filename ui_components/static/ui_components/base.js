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
  // formType = $(formset).attr("form-model");

  $(formset).click(function(e) {
    addNewForm(e, null);
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
  if (customUploadButton.hasClass("preview-image")) {
    var reader = new FileReader();
    reader.onload = function(e) {
      customUploadButton.html(`<img src='${e.target.result}'></img>`);
      customUploadButton.addClass("image-selected");
    };

    reader.readAsDataURL(e.target.files[0]);
    oldForm = customUploadButton.parents()[0];
    addNewForm(e, $(oldForm));

    return;
  }
  customUploadButton.html(`<p>Choose file</p> ${filename}`);
};

let change_nested_form = function(nested_formset) {
  nested_form = $(nested_formset).find(".form-nested");
  let prefix = $(nested_formset).attr("prefix");

  let prefix_list = prefix.split("-");
  prefix_list[1] = parseInt(prefix_list[1]) + 1;
  let new_prefix = prefix_list.join("-");

  let management_form = $(nested_formset).children(
    ".form-nested-management-form"
  );
  prefix_list.pop();
  let new_management_prefix = prefix_list.join("-");
  prefix_list[1] -= 1;
  let management_prefix = prefix_list.join("-");

  $.each(management_form.children("input"), function(index, input) {
    replaceAttrs(input, "id", management_prefix, new_management_prefix);
    replaceAttrs(input, "name", management_prefix, new_management_prefix);
  });

  let total_forms = `id_${new_management_prefix}-TOTAL_FORMS`;
  let initial_forms = `id_${new_management_prefix}-INITIAL_FORMS`;

  management_form.children(`#${total_forms}`).attr("value", 1);
  management_form.children(`#${initial_forms}`).attr("value", 0);

  $.each(nested_form.children("label"), function(index, label) {
    replaceAttrs(label, "for", prefix, new_prefix);
  });

  $.each(nested_form.children("input"), function(index, input) {
    $(input).val("");
    replaceAttrs(input, "name", prefix, new_prefix);
    replaceAttrs(input, "id", prefix, new_prefix);
  });

  nested_form.attr("prefix", `${new_prefix}-0`);
};

let addNewForm = function(e, oldForm) {
  if (oldForm == undefined || oldForm == null) {
    e.preventDefault();
    oldForm = $(".form").last();
    newForm = oldForm.clone(true);
  } else {
    newForm = oldForm.clone(true);
  }

  let prefix = newForm.attr("prefix");

  let prefix_list = prefix.split("-");
  let lastElementIndex = prefix_list.length - 1;

  prefix_list[lastElementIndex] = parseInt(prefix_list[lastElementIndex]) + 1;
  let newPrefix = prefix_list.join("-");

  newForm.attr("prefix", newPrefix);

  // id starts from 0 => form number = last id + 1
  let managementFormValue = prefix_list.pop() + 1;
  let managementFormName = prefix_list.join("-");

  nested_formsets = newForm.children(".nested-formset");
  $.each(nested_formsets, function(index, nested_formset) {
    change_nested_form(nested_formset);
  });

  $.each(newForm.children("label"), function(index, label) {
    replaceAttrs(label, "for", prefix, newPrefix);
  });

  $.each(newForm.children("textarea"), function(index, textarea) {
    $(textarea).val("");
    replaceAttrs(textarea, "name", prefix, newPrefix);
    replaceAttrs(textarea, "id", prefix, newPrefix);
  });

  $.each(newForm.children("input"), function(index, input) {
    $(input).val("");
    replaceAttrs(input, "name", prefix, newPrefix);
    replaceAttrs(input, "id", prefix, newPrefix);
  });

  formCount = $(`#id_${managementFormName}-TOTAL_FORMS`);
  formCount.attr("value", managementFormValue);

  newForm.insertAfter(oldForm);
  return false;
};

let replaceAttrs = function(element, attrName, prefix, newPrefix) {
  attr = $(element).attr(attrName);
  newAttr = attr.replace(prefix, newPrefix);
  $(element).attr(attrName, newAttr);
};
