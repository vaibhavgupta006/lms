function csrfSafeMethod(method) {
  // these HTTP methods do not require CSRF protection
  return /^(GET|HEAD|OPTIONS|TRACE)$/.test(method);
}

$(document).ready(function() {
  let button = $(".btn-primary");
  button.on("click", course_action);
});

let course_action = function(e) {
  let url = window.location.href;
  let csrftoken = $("[name=csrfmiddlewaretoken]").val();
  let action = null;
  let text = null;
  let target = $(e.target);
  if (target.attr("id") === "enroll") {
    action = "enroll";
    text = "Enrolling";
  } else if (target.attr("id") === "unenroll") {
    action = "unenroll";
    text = "Unenrolling";
  } else if (target.attr("id") === "delete") {
    action = "delete";
    text = "Deleting";
  }
  target.html(text);
  target.addClass("waiting");

  $.ajaxSetup({
    beforeSend: function(xhr, settings) {
      if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
      }
    }
  });

  $.ajax({
    type: "POST",
    url: url + `${action}/`,
    data: "",
    success: function(response) {
      change_dom_elements(response, action, target);
    },
    error: function(response) {
      show_error(response, action, target);
    }
  });
};

let change_dom_elements = function(response, action, button) {
  $(response).replaceAll(".actions");
  let url = document.location.href;
  let new_url = null;
  let new_id = null;
  let new_text = null;
  let new_icon = null;

  if (action == "enroll") {
    new_url = url.replace("/all/", "/enrolled-courses/");
    new_id = "unenroll";
    new_text = "Unenroll";
    new_icon = "clear";
  } else if (action == "unenroll") {
    new_url = url.replace("/enrolled-courses/", "/all/");
    new_id = "enroll";
    new_text = "Enroll";
    new_icon = "add";
  }
  window.history.replaceState({}, document.title, new_url);
  button.html(`<i class='material-icons'>${new_icon}</i> ${new_text}`);
  button.removeClass("waiting");
  button.attr({ id: new_id });
};

let show_error = function(response, action, button) {
  let new_text = null;
  let new_icon = null;

  if (action === "enroll") {
    new_text = "enroll";
    new_icon = "add";
  } else if (action === "unenroll") {
    new_text = "Unenroll";
    new_icon = "clear";
  } else if (action === "delete") {
    new_text = "Delete";
    new_icon = "delete";
  }
  button.removeClass("waiting");
  button.html(`<i class='material-icons'>${new_icon}</i> ${new_text}`);
  alert(`${response.status}: ${response.statusText}`);
};
