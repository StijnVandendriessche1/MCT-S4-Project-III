const production = false,
  ip = "http://localhost:5000";
let socket = io.connect(ip);

let domToggleSwitch;

/* Sockets */

/* socket.on("status_server", function () {
  document.querySelector(".js-loader").style.display = "none";
  document.querySelector(".js-end-text").style.display = "block";
  setTimeout(clearLoadingscreen, 6311);
}); */
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

/* Status dishwasher */
socket.on("status_dishwasher", function (data) {
  changeBoxStatus("dishwasher", data.status);
});

/* Status rooms */
socket.on("status_rooms", function (data) {
  output = ``;
  log(data.status)
  for (const roomData in data.status) {
    check = ""
    if(data.status[roomData]) check = "checked"
    log(roomData + data.status[roomData]);
    status = getStatus(data.status[roomData])
    log(status)
    output += `<div class="c-item js-card js-${status}">
    <div class="c-item__header c-card__top">
        <div class="c-item__icon c-card__icon">
            <svg xmlns="http://www.w3.org/2000/svg"
                xmlns:xlink="http://www.w3.org/1999/xlink" width="40" height="40"
                viewBox="0 0 40 40" class="js-icon js-icon__off">
                <g id="Mask_Group_7" data-name="Mask Group 7"
                    transform="translate(-1496 -248)" clip-path="url(#clip-path)">
                    <g id="video-call" transform="translate(1496 248)">
                        <circle id="Ellipse_1" data-name="Ellipse 1" cx="4" cy="4" r="4"
                            transform="translate(12 9.333)" />
                        <path id="Path_3" data-name="Path 3"
                            d="M39.8,36.189A13.2,13.2,0,0,0,35.521,33.4l-2.512-1.019a4.116,4.116,0,0,1-2.177-2.048,4.315,4.315,0,0,1,.988-.048.667.667,0,0,0,1.071-.756,1.845,1.845,0,0,0,1.623-.387.667.667,0,0,0,0-.955,2.285,2.285,0,0,1-.387-1.635v-.173a1.5,1.5,0,0,1,.333-1.075,5.285,5.285,0,0,0,.843-3.5C35.3,18.48,32.58,12,27.587,12a3.565,3.565,0,0,0-1.981.572h-.367c-3.733,0-6.541,5.6-6.541,9.237a5.285,5.285,0,0,0,.843,3.5,1.5,1.5,0,0,1,.333,1.073v.175a2.285,2.285,0,0,1-.387,1.635.667.667,0,0,0,0,.955,1.862,1.862,0,0,0,1.621.391.684.684,0,0,0,.181.836.623.623,0,0,0,.827-.037,3.106,3.106,0,0,1,1.051,0,4.116,4.116,0,0,1-2.176,2.045L18.479,33.4A13.2,13.2,0,0,0,14.2,36.189a.667.667,0,0,0,.465,1.144H39.333a.667.667,0,0,0,.465-1.144Z" />
                        <path id="Path_4" data-name="Path 4"
                            d="M17.952,28.667a2,2,0,0,1,.273-1,.667.667,0,0,0-.577-1h-.315V25.26a.667.667,0,0,0,.34-.779,6.727,6.727,0,0,1-.168-.8,11.552,11.552,0,0,1-.141-1.876,11.215,11.215,0,0,1,.427-2.883.667.667,0,0,0-.555-.836A9.215,9.215,0,0,0,16,18a12.165,12.165,0,0,0-6.153,1.932A3.98,3.98,0,0,0,8.1,22.667H2.667V5.333H29.333V10.42a.667.667,0,0,0,.449.631,7.418,7.418,0,0,1,1.223.552.667.667,0,0,0,.995-.58V5.333a2.669,2.669,0,0,0-2.667-2.667H2.667A2.669,2.669,0,0,0,0,5.333V22.667a2.669,2.669,0,0,0,2.667,2.667h12v1.333H11.333a.667.667,0,0,0-.667.667v1.333a.667.667,0,0,0,.667.667h5.952a.667.667,0,0,0,.667-.667Z" />
                    </g>
                </g>
            </svg>
        </div>
        <div class="c-item__toggle">
            <input class="o-hide-accessible c-option c-option--hidden" type="checkbox"
                id="${roomData}" ${check}>
            <label
                class="c-label c-label--option c-custom-toggle c-custom-toggle--inverted"
                for="${roomData}">
                <span class="c-custom-toggle__fake-input"></span>
                Empty
            </label>
        </div>
    </div>
    <div class="c-item__title c-card__text">
        ${roomData}
    </div>
</div>`;
  }
  document.querySelector(".js-meeting-rooms").innerHTML = output;
});

/* Functions */
/* const clearLoadingscreen = function () {
  document.querySelector(".js-loadings-screen").style.display = "none";
}; */
const getStatus = function (status) {
  selected = "off";
  if (status) selected = "on";
  return selected;
};
const changeBoxStatus = function (box, status) {
  /* Get all the elements from this box */
  const domBoxAIMeeting = document.querySelector(`.js-box--${box}`);

  /* Check if the element is showed */
  selected = getStatus(status);

  /* Set the classes correct */
  domBoxAIMeeting.classList.remove("js-on");
  domBoxAIMeeting.classList.remove("js-off");
  /* Add the correct class */
  domBoxAIMeeting.classList.add(`js-${selected}`);

  /* Give it the correct word */
  domBoxAIMeeting.querySelector(`.js-word--${box}`).innerHTML = selected;

  /* Put the correct color to the svg */
  icon = domBoxAIMeeting.querySelector(`.js-icon--${box}`);
  icon.classList.remove(`js-icon__off`);
  icon.classList.remove(`js-icon__on`);
  icon.classList.add(`js-icon__${selected}`);
};
const toggleSwitchStatusChange = function (box, status) {
  /* Get all the elements from this box */
  const domBoxAIMeeting = document.querySelector(`.js-box--${box}`);

  /* Check if the element is showed */
  selected = getStatus(status);

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