$(document).ready(function() {
  dropdown = $(".dropdown");
  textareas = $("textarea");
  fileUpload = $("input:file");

  $.each(dropdown, showContent);
  $.each(textareas, bindAutoIncrement);
  $.each(fileUpload, bindGetFileName);
});

let bindAutoIncrement = function(index, textarea) {
  $(textarea).on("input copy cut delete", autoIncrementHeight);
};

let bindGetFileName = function(index, fileInput) {
  $(fileInput).on("change", getFileName);
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
