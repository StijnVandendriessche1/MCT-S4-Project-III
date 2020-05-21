const production = false,
  ip = "http://localhost:5000";
let socket = io.connect(ip);

let domToggleSwitch;

/* Sockets */

socket.on("status_server", function () {
  document.querySelector(".js-loader").style.display = "none";
  document.querySelector(".js-end-text").style.display = "block";
  setTimeout(clearLoadingscreen, 631);
});
/* Sockets for putting the ai's on or off */
socket.on("status_ai_meeting", function (data) {
  toggleSwitchStatusChange("ai-meeting", data.status);
});
socket.on("status_ai_coffee", function (data) {
  toggleSwitchStatusChange("ai_coffee", data.status);
});
socket.on("status_ai_dishwasher", function (data) {
  toggleSwitchStatusChange("ai_dishwasher", data.status);
});

/* Status coffee left */
socket.on("status_coffee_left", function (data) {
  document.querySelector(".js-coffee-left").innerHTML = `${data.status}kg`;
});

/* Functions */
const clearLoadingscreen = function () {
  document.querySelector(".js-loadings-screen").style.display = "none";
};
const toggleSwitchStatusChange = function (box, status) {
  /* Get all the elements from this box */
  const domBoxAIMeeting = document.querySelector(`.js-box--${box}`);

  /* Check if the element is showed */
  selected = "off";
  if (status) selected = "on";

  /* Set the classes correct */
  domBoxAIMeeting.classList.remove("js-on");
  domBoxAIMeeting.classList.remove("js-off");
  /* Add the correct class */
  domBoxAIMeeting.classList.add(`js-${selected}`);

  /* Give it the correct word */
  domBoxAIMeeting.querySelector(`.js-word--${box}`).innerHTML = selected;

  /* Set the toggle to the correct side */
  domBoxAIMeeting.querySelector(`.js-toggleswitch--${box}`).checked = status;

  /* Put the correct color to the svg */
  icon = domBoxAIMeeting.querySelector(`.js-icon--${box}`);
  icon.classList.remove(`js-icon__off`);
  icon.classList.remove(`js-icon__on`);
  icon.classList.add(`js-icon__${selected}`);
};

/* Function for logging while debugging */
const log = function (message) {
  if (!production) console.log(message);
};
const toggleBox = function (domToggleSwitch) {
  toggle = domToggleSwitch.checked;
  /* Get the head_parent of the box */
  parent = domToggleSwitch.parentNode.parentNode.parentNode.parentNode;
  /* Change the classes */
  parent.classList.toggle("js-off");
  parent.classList.toggle("js-on");
  if (toggle) {
  }
};
/* Check wich toggle it is */
const toggleSwitch = function (domToggleSwitch) {
  switch (domToggleSwitch.getAttribute("data-name")) {
    case "ai_meeting":
      socket.emit("ai_meeting");
      break;
    case "ai_coffee":
      socket.emit("ai_coffee");
      break;
    case "ai_dishwasher":
      socket.emit("ai_dishwasher");
      break;

    default:
      break;
  }
};
/* Load toggleSwitches */
const loadDOM = function () {
  domToggleSwitches = document.querySelectorAll(".js-toggleswitch");
  for (const domToggleSwitch of domToggleSwitches) {
    domToggleSwitch.addEventListener("change", function () {
      toggleSwitch(domToggleSwitch);
    });
  }
};
/* init-function --> For starting the script */
const init = function () {
  loadDOM();
  socket.emit("connect");
};

/* When the script starts */
document.addEventListener("DOMContentLoaded", function () {
  log("Js Started");
  init();
});
