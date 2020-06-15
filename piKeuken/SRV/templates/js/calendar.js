var moment;

const production = false,
    ip = "https://localhost:5000";
let socket = io.connect(ip);

let isclicked = false;

let months = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
];

let today = moment();
let day = moment();
let now = new Date();
let currentMonth = now.getMonth();
let currentYear = now.getFullYear();

socket.on("welcome", function (data) {
    log(data);
});

socket.on("new_notification", function (data) {
    getNotifications(data);
});

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
    domBoxNotifications.innerHTML = output;
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

const registeredServiceWorker = function () {
    if ("serviceWorker" in navigator) {
        navigator.serviceWorker
            .register("./sw.js", { scope: "/" })
            .then((registration) => {
                console.log("ServiceWorker running");
            })
            .catch((err) => {
                console.log(err);
            });
    }
};

const next = function () {
    currentYear = currentMonth === 11 ? currentYear + 1 : currentYear;
    currentMonth = (currentMonth + 1) % 12;
    MiniCalendar(currentMonth, currentYear);
};

const previous = function () {
    currentYear = currentMonth === 0 ? currentYear - 1 : currentYear;
    currentMonth = currentMonth === 0 ? 11 : currentMonth - 1;
    MiniCalendar(currentMonth, currentYear);
};

const daysInMonth = function (iMonth, iYear) {
    return 32 - new Date(iYear, iMonth, 32).getDate();
};

const nextTitle = function () {
    day.day(7);
    console.log(day);
    calendarheader(day);
};

const previousTitle = function () {
    day.day(-7);
    console.log(day);
    calendarheader(day);
};

const calendarheader = function (date) {
    let firstday = date.clone().weekday(1);
    let lastday = date.clone().weekday(7);

    console.log(firstday);
    console.log(lastday);

    titlename = document.querySelector(".js-title");
    titlename.innerHTML =
        months[firstday.month()] +
        " " +
        firstday.date() +
        " - " +
        months[lastday.month()] +
        " " +
        lastday.date() +
        ", " +
        firstday.year();

    monday = document.querySelector(".js-monday");
    monday.innerHTML = date.clone().weekday(1).date();

    tuesday = document.querySelector(".js-tuesday");
    tuesday.innerHTML = date.clone().weekday(2).date();

    wednesday = document.querySelector(".js-wednesday");
    wednesday.innerHTML = date.clone().weekday(3).date();

    thursday = document.querySelector(".js-thursday");
    thursday.innerHTML = date.clone().weekday(4).date();

    friday = document.querySelector(".js-friday");
    friday.innerHTML = date.clone().weekday(5).date();

    saturday = document.querySelector(".js-saturday");
    saturday.innerHTML = date.clone().weekday(6).date();

    sunday = document.querySelector(".js-sunday");
    sunday.innerHTML = date.clone().weekday(7).date();
};

const MiniCalendar = function (month, year) {
    let firstDay = new Date(year, month).getDay();
    body = document.querySelector(".js-mini-body");
    body.innerHTML = "";

    title = document.querySelector(".js-mini-month");
    title.innerHTML = months[currentMonth] + " " + currentYear;

    let date = 1;

    for (let i = 0; i < 6; i++) {
        // creates a table row
        let row = document.createElement("tr");

        //creating individual cells, filing them up with data.
        for (let j = 0; j < 7; j++) {
            if (i === 0 && j < firstDay - 1) {
                cell = document.createElement("td");
                cellText = document.createTextNode("");
                cell.appendChild(cellText);
                row.appendChild(cell);
            } else if (date > daysInMonth(month, year)) {
                break;
            } else {
                cell = document.createElement("td");
                cell.className += "c-calendar__item";
                cellText = document.createTextNode(date);
                if (
                    date === now.getDate() &&
                    year === now.getFullYear() &&
                    month === now.getMonth()
                ) {
                    cell.classList.add("c-calendar__mini--current");
                    row.classList.add("c-calendar__mini--week");
                } // color today's date
                cell.appendChild(cellText);
                row.appendChild(cell);
                date++;
            }
        }

        body.appendChild(row); // appending each row into calendar body.
    }
};

const loadDOM = function () {
    domBoxNotifications = document.querySelector(".js-box-notification");
    domNotificationCount = document.querySelector(".js-notification--count");

    domBell = document.querySelector(".js-bell");
    domBell.addEventListener("click", function () {
        showNotifications();
    });
};

/* init-function --> For starting the script */
const init = function () {
    console.log("script stared");

    loadDOM();
    getAPI("notifications", getNotifications);

    MiniCalendar(currentMonth, currentYear);
    calendarheader(day);

    miniLeft = document.querySelector(".js-mini-left");
    miniRight = document.querySelector(".js-mini-right");
    left = document.querySelector(".js-left");
    right = document.querySelector(".js-right");

    miniLeft.addEventListener("click", function () {
        previous();
    });

    miniRight.addEventListener("click", function () {
        next();
    });

    left.addEventListener("click", function () {
        previousTitle();
    });

    right.addEventListener("click", function () {
        nextTitle();
    });
};

/* When the script starts */
document.addEventListener("DOMContentLoaded", function () {
    console.log("Js Started");
    moment().format();
    registeredServiceWorker();
    init();
});
