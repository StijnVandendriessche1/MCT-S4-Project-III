const production = false;
//ip = "https://192.168.238.2.xip.io:5000";
const ip = "https://localhost:5000";
let socket = io.connect(ip);

let domReady = false;

let isclicked = false;
let isSettingsClicked = false;
let isSettingsClickedDishwasher = false;
let graphLabel;

let notificationsNotViewed = [],
    apiCoffeeSettingsSend = false;

let domToggleSwitch,
    domToggleSwitchRoomBoxes,
    domBtnStats,
    domMapMeetingBoxes,
    domMapCardBody,
    domMapCardTitle,
    domBoxNotifications,
    domListNotification,
    domNotificationCount;

let graphAlreadyCreated = false,
    myChart;
const classStatsSelected = "c-stats--selected";

/* Sockets */

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

/* Status MeetingBoxes */
socket.on("status_rooms", function (data) {
    if (domReady) {
        for (const box in data.status) {
            roomDataId = box.replace(/ /g, "");
            changeBoxStatus(roomDataId, data.status[box]);
            selected = "Empty";
            if (data.status[box]) selected = "Busy";
            document.querySelector(
                `.js-word--${roomDataId}`
            ).innerHTML = selected;
        }
    }
});

socket.on("welcome", function (data) {
    log(data);
});

socket.on("new_notification", function (data) {
    log(data)
    getAPI("notifications", getNotifications);
});

socket.on("coffee_settings", function (data) {
    log(data);
    /* Change the settings in the inputfields from the coffee */
    for (const setting in data) {
        if (data.hasOwnProperty(setting)) {
            const settingValue = data[setting];
            log(settingValue);
            log(setting);
            document.querySelector(
                `.js-coffee-settings__input--${setting}`
            ).value = settingValue;
        }
    }
});

socket.on("dishwasher_settings", function (data){
    log(data);
    for (const setting in data) {
        if (data.hasOwnProperty(setting)) {
            const settingValue = data[setting];
            log(`${setting} - ${settingValue}`);
            document.querySelector(
                `.js-dishwasher-settings__input--${setting}`
            ).value = settingValue;
        }
    }
})

/* Functions */
const changeNotificationCount = function () {
    log(notificationsNotViewed);
    if (notificationsNotViewed.length == 0) {
        domNotificationCount.style.display = "none";
    } else {
        domNotificationCount.style.display = "block";
        domNotificationCount.querySelector(
            ".js-notification-count__count"
        ).innerHTML = notificationsNotViewed.length;
    }
};
const notificationViewed = function (data) {
    log(data);
    /* Delete the notification from the viewed list */
    notificationsNotViewed.splice(notificationsNotViewed.indexOf(data.nid), 1);
    changeNotificationCount();
};
const checkNotificationViewed = function () {
    /* Check if there are notifications that are not viewed */
    if (notificationsNotViewed.length > 0) {
        /* Set the notifications as viewed */
        for (const notification of notificationsNotViewed) {
            /* Send it to the API */
            getAPI(`notifications/${notification}`, notificationViewed, "POST");
        }
    }
};
/* Function for getting the notifications */
const getNotifications = function (data) {
    let output = "";
    for (const notification of data) {
        /* Check if the notification already viewed */
        if (!notification["viewed"])
            notificationsNotViewed.push(notification["nid"]);
        output += `<div class="c-notification__item" data-notificationId="${notification["nid"]}" data-viewed="${notification["viewed"]}">${notification["title"]}${notification["msg"]}</div>`;
    }
    changeNotificationCount();
    domListNotification.innerHTML = output;
};

/* Reset status_Meetingboxes */
const resetMeetingBoxes = function (data) {
    log(data);
    output = ``;
    for (const roomData in data.status) {
        let check = "";
        let busy = "Empty";
        roomDataId = roomData.replace(/ /g, "");
        if (data.status[roomData]) {
            check = "checked";
            busy = "Busy";
        }
        status = getStatus(data.status[roomData]);
        output += `<div class="c-item js-card js-${status} js-box--${roomDataId}">
    <div class="c-item__header c-card__top">
        <div class="c-item__icon c-card__icon">
            <svg xmlns="http://www.w3.org/2000/svg"
                xmlns:xlink="http://www.w3.org/1999/xlink" width="40" height="40"
                viewBox="0 0 40 40" class="js-icon js-icon__${status} js-icon--${roomDataId}">
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
            <input class="o-hide-accessible c-option c-option--hidden js-toggleswicht--roomBox" type="checkbox"
                id="${roomDataId}" data-room="${roomData}" data-name="RoomStatus" ${check}>
            <label
                class="c-label c-label--option c-custom-toggle c-custom-toggle--inverted"
                for="${roomDataId}">
                <span class="c-custom-toggle__fake-input"></span>
                <span class="js-word--${roomDataId}">${busy}</span>
            </label>
        </div>
    </div>
    <div class="c-item__title c-card__text">
        ${roomData}
    </div>
</div>`;
    }
    document.querySelector(".js-meeting-rooms").innerHTML = output;
    getDOMMeetingBoxes();
    domReady = true;
};

/* Add addEventListener to Roomboxes */
const getDOMMeetingBoxes = function () {
    /* Check if their are elements in the var */
    if (domToggleSwitchRoomBoxes != null) {
        /* Remove all the eventlisteners */
        for (const toggleSwitchRoomBox of domToggleSwitchRoomBoxes) {
            toggleSwitchRoomBox.removeEventListener("change", function () {
                toggleSwitch(toggleSwitchRoomBox);
            });
        }
    }
    /* Add eventlisteners to the elements */
    domToggleSwitchRoomBoxes = document.querySelectorAll(
        ".js-toggleswicht--roomBox"
    );
    for (const toggleSwitchRoomBox of domToggleSwitchRoomBoxes) {
        toggleSwitchRoomBox.addEventListener("change", function () {
            toggleSwitch(
                toggleSwitchRoomBox,
                toggleSwitchRoomBox.getAttribute("data-room")
            );
        });
    }
};

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
const toggleSwitch = function (domToggleSwitch, box = null) {
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
        case "RoomStatus":
            socket.emit("status_room_change", { room: box });
            break;

        default:
            break;
    }
};
/* Function that clear the stat-btns */
const resetBtnStats = function () {
    for (const domBtnStat of domBtnStats) {
        domBtnStat.classList.remove(classStatsSelected);
    }
};
const changeDishwasherSettingsResponse = function (data) {
    document.querySelector(".js-dishwasher-settings--msg").style.display = "block";
    if (data["status"]) {
        document.querySelector(".js-dishwasher-settings--msg").innerHTML =
            "Changed!";
    } else {
        document.querySelector(".js-dishwasher-settings--msg").innerHTML =
            "Changes failed!";
    }
    apiCoffeeSettingsSend = false;
};
const changeDishwasherSettings = function () {
    if (!apiCoffeeSettingsSend) {
        /* Get all the data from the fields */
        const domInputFields = document.querySelectorAll(
            ".js-dishwasher-settings__input"
        );
        newSettings = {};
        for (const domInputField of domInputFields) {
            newSettings[domInputField.getAttribute("data-setting")] =
                domInputField.value;
        }
        log(newSettings);
        /* Send it to the API */
        getAPI(
            `settings/dishwasher`,
            changeDishwasherSettingsResponse,
            "POST",
            JSON.stringify(newSettings)
        );
        apiCoffeeSettingsSend = true;
    }
};
const changeCoffeeSettingsResponse = function (data) {
    document.querySelector(".js-coffee-settings--msg").style.display = "block";
    if (data["status"]) {
        document.querySelector(".js-coffee-settings--msg").innerHTML =
            "Changed!";
    } else {
        document.querySelector(".js-coffee-settings--msg").innerHTML =
            "Changes failed!";
    }
    apiCoffeeSettingsSend = false;
};
const changeCoffeeSettings = function () {
    if (!apiCoffeeSettingsSend) {
        /* Get all the data from the fields */
        const domInputFields = document.querySelectorAll(
            ".js-coffee-settings__input"
        );
        newSettings = {};
        for (const domInputField of domInputFields) {
            newSettings[domInputField.getAttribute("data-setting")] =
                domInputField.value;
        }
        log(newSettings);
        /* Send it to the API */
        getAPI(
            `settings/coffee`,
            changeCoffeeSettingsResponse,
            "POST",
            JSON.stringify(newSettings)
        );
        apiCoffeeSettingsSend = true;
    }
};
const showSettingsDishwasher = function () {
    box = document.querySelector(".js-settings__dishwasher");
    console.log(box);
    if (isSettingsClickedDishwasher == false) {
        box.style.display = "block";
        isSettingsClickedDishwasher = true;
        console.log("showed");
    } else {
        box.style.display = "none";
        isSettingsClickedDishwasher = false;
        console.log("hidden");
    }
};
/* Load toggleSwitches */
const loadDOM = function () {
    domMapCardBody = document.querySelector(".js-map-card__body");
    domMapCardTitle = document.querySelector(".js-map-card__title");
    domBoxNotifications = document.querySelector(".js-box-notification");
    domListNotification = document.querySelector(".js-notification-list");
    domNotificationCount = document.querySelector(".js-notification--count");
    /* Load the toggleswitches */
    domToggleSwitches = document.querySelectorAll(".js-toggleswitch");
    for (const domToggleSwitch of domToggleSwitches) {
        log(domToggleSwitch);
        domToggleSwitch.addEventListener("change", function () {
            toggleSwitch(domToggleSwitch);
        });
        const domBtnCoffeeSettings = document.querySelector(
            ".js-coffee-settings__btn"
        );
        const domBtnDishwasherSettings = document.querySelector(".js-dishwasher-settings__btn");
        /* Btn for coffee_settings */
        domBtnCoffeeSettings.addEventListener("submit", function (e) {
            e.preventDefault();
            changeCoffeeSettings();
        });
        /* Btn for dishwasher_settings */
        domBtnDishwasherSettings.addEventListener("submit", function (e) {
            e.preventDefault();
            changeDishwasherSettings();
        });
    }
    /* Load the btns for the stats */
    domBtnStats = document.querySelectorAll(".js-btn--stats");
    const graphPath = {
        CoffeeWeek: ["coffee/week", "WeekDay"],
        temperatureRoom: ["temperature/room", "host"],
        humidityRoom: ["humidity/room", "host"],
    };
    for (const domBtnStat of domBtnStats) {
        domBtnStat.addEventListener("click", function () {
            resetBtnStats();
            domBtnStat.classList.add(classStatsSelected);
            graphLabel = graphPath[domBtnStat.getAttribute("data-name")][1];
            getAPI(
                `graph/${graphPath[domBtnStat.getAttribute("data-name")][0]}`,
                setDataForGraph
            );
        });
    }

    let domBell = document.querySelector(".js-bell");
    domBell.addEventListener("click", function () {
        showNotifications();
    });

    let domSettings = document.querySelector(".c-settings__icon");
    domSettings.addEventListener("click", function () {
        showSettings();
    });

    let domDishwasher = document.querySelector(".js-settings__dishwasher-icon");
    domDishwasher.addEventListener("click", function () {
        showSettingsDishwasher();
    });
};

const showNotifications = function () {
    if (isclicked == false) {
        domBoxNotifications.style.display = "block";
        isclicked = true;
        log("showed");
        /* Check if the notifications are viewed */
        checkNotificationViewed();
    } else {
        domBoxNotifications.style.display = "none";
        isclicked = false;
        log("hidden");
    }
};

const showSettings = function () {
    box = document.querySelector(".c-settings__box");
    console.log(box);
    if (isSettingsClicked == false) {
        box.style.display = "block";
        isSettingsClicked = true;
        console.log("showed");
    } else {
        box.style.display = "none";
        isSettingsClicked = false;
        console.log("hidden");
    }
};

const isFloat = function (n) {
    return Number(n) === n && n % 1 !== 0;
};
const sensorNotation = function (sensor, data) {
    output = "";
    if (isFloat(data)) data = data.toFixed(2);
    switch (sensor) {
        case "temperature":
            output = `${data}°C`;
            break;

        default:
            output = `${data}`;
            break;
    }
    return output;
};
const cleanDict = function (data) {
    const delItems = [
        "result",
        "table",
        "_measurement",
        "_start",
        "_stop",
        "_time",
        "host",
    ];
    for (const delItem of delItems) {
        if (data.hasOwnProperty(delItem)) {
            delete data[delItem];
        }
    }
    return data;
};
const resetInfoMapBoxes = function(){
    /* Reset all roomBoxes */
    const domRoomBoxes = document.querySelectorAll(".js-map-room");
    for (const domRoomBox of domRoomBoxes) {
        //domroombox.style.stroke = "rgb(0, 0, 0)"
        domRoomBox.style.stroke = ""
        domRoomBox.style.strokeWidth = "3px";
    }
    /* Reset all icons */
    const domIcons = document.querySelectorAll(".js-map-icon");
    for (const domIcon of domIcons) {
        domIcon.style.fill = ""
    }
};
const changeInfoMapBoxes = function (data) {
    resetInfoMapBoxes()
    let output = "";
    let box = data[0]["host"];
    box = box.replace(/ /g, "");
    const domMapBox = document.querySelector(`.js-map-room${box}`);
    domMapBox.style.stroke = "var(--global-accent)";
    domMapBox.style.strokeWidth = "5px";
    document.querySelector(`.js-map-icon${box}`).style.fill =
        "var(--global-accent)";
    /* Clean the dict */
    data = cleanDict(data[0]);
    document.querySelector(".js-card__temp").innerHTML = data[
        "temperature"
    ].toFixed(2);
    document.querySelector(".js-card__humidity").innerHTML = data["humidity"];
    document.querySelector(".js-card__light").innerHTML = data["light"].toFixed(
        2
    );
    domMapCardBody.innerHTML = output;
};
const getMapBoxes = function () {
    domMapMeetingBoxes = document.querySelectorAll(".js-map");
    for (const meetingBox of domMapMeetingBoxes) {
        meetingBox.addEventListener("click", function () {
            /* Get the box-name from the dom */
            box = meetingBox.getAttribute("data-room");
            /* Change the title */
            domMapCardTitle.innerHTML = box;
            /* Send the boxname to the api */
            getAPI(`meetingbox/${box}/info`, changeInfoMapBoxes);
        });
    }
};
/* init-function --> For starting the script */
const init = function () {
    loadDOM();
    getAPI("meetingbox/status", resetMeetingBoxes);
    getAPI("notifications", getNotifications);
    socket.emit("connect");
    log("Socket emitted");
    getMapBoxes();
    /* Send the boxname to the api */
    getAPI(`meetingbox/Kitchen/info`, changeInfoMapBoxes);
    graphLabel = "WeekDay";
    getAPI(`graph/coffee/week`, setDataForGraph);
};

const setDataForGraph = function (data) {
    //data = JSON.parse(data)
    /* Create 2 vars with the data */
    data_labels = [];
    data_values = [];
    for (const row of data) {
        data_labels.push(row[graphLabel]);
        data_values.push(row["_value"]);
    }
    Graph(data_labels, data_values);
};

const Graph = function (data_labels, data_values) {
    document.getElementById("Stats").innerHTML = "";
    var ctx = document.getElementById("Stats").getContext("2d");
    /* Check if there is already a chart*/
    if (graphAlreadyCreated) myChart.destroy();
    else graphAlreadyCreated = true;
    myChart = new Chart(ctx, {
        type: "bar",
        data: {
            labels: data_labels,
            datasets: [
                {
                    label: "Mean",
                    data: data_values,
                    backgroundColor: ["rgba(255, 99, 132, 0.2)"],
                    borderColor: ["rgba(255, 99, 132, 1)"],
                    borderWidth: 1,
                },
            ],
        },
        options: {
            scales: {
                yAxes: [
                    {
                        ticks: {
                            beginAtZero: true,
                        },
                    },
                ],
            },
        },
    });
};

const registeredServiceWorker = function () {
    if ("serviceWorker" in navigator) {
        navigator.serviceWorker
            .register("/static/sw.js")
            .then((registration) => {
                console.log("ServiceWorker running");
            })
            .catch((err) => {
                console.log(err);
            });
    }
};

const handleFloatingLabel = function () {
    let input = document.querySelectorAll(".js-floating-input"),
        label = document.querySelectorAll(".js-floating-label");

    for (const [index, inputfield] of input.entries()) {
        inputfield.addEventListener("blur", function () {
            console.log(event);
            if (inputfield.value) {
                label[index].classList.add("is-floating");
            } else {
                label[index].classList.remove("is-floating");
            }
        });
    }
};

/* When the script starts */
document.addEventListener("DOMContentLoaded", function () {
    log("Js Started");
    registeredServiceWorker();
    init();
    handleFloatingLabel();
});
