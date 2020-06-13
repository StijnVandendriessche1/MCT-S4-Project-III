const production = false,
    ip = "https://localhost:5000";

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

let today = new Date();
let day = new Date();
let currentMonth = today.getMonth();
let currentYear = today.getFullYear();
let firstDayOfWeek = today.getDate() - today.getDay() + 1;

const showNotifications = function () {
    box = document.getElementById("js-box");
    if (isclicked == false) {
        box.style.display = "block";
        isclicked = true;
        console.log("showed");
    } else {
        box.style.display = "none";
        isclicked = false;
        console.log("hidden");
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
    day.setDate(day.getDate() + 7);
    console.log(day);
    calendarheader(day);
};

const previousTitle = function () {
    day.setDate(day.getDate() - 7);
    console.log(day);
    calendarheader(day);
};

const calendarheader = function (date) {
    let firstfullday = new Date();
    firstfullday.setDate(
        day.getDate() - day.getDay() + (day.getDay() == 1 ? -6 : 1)
    );
    let firstday = firstfullday.getDate();
    let lastfullday = new Date();
    lastfullday.setDate(firstfullday.getDate() + 6);
    let lastday = lastfullday.getDate();

    titlename = document.querySelector(".js-title");
    titlename.innerHTML =
        months[firstfullday.getMonth()] +
        " " +
        firstday +
        " - " +
        months[lastfullday.getMonth()] +
        " " +
        lastday +
        ", " +
        date.getFullYear();
};

/* 
const calendartitle = function (firstDayOfWeek, month, year) {
    MonthDays = daysInMonth(currentMonth, currentYear);
    let lastDay =
        (firstDayOfWeek + 7) / MonthDays > 1
            ? (lastday = ((firstDayOfWeek + 6) % MonthDays) - MonthDays)
            : (lastday = firstDayOfWeek + 6);
    titlename = document.querySelector(".js-title");
    titlename.innerHTML =
        months[currentMonth] +
        " " +
        firstDayOfWeek +
        " - " +
        lastDay +
        ", " +
        year;
}; */

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
                    date === today.getDate() &&
                    year === today.getFullYear() &&
                    month === today.getMonth()
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

/* init-function --> For starting the script */
const init = function () {
    console.log("script stared");
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

    domBell = document.querySelector(".js-bell");
    domBell.addEventListener("click", function () {
        showNotifications();
    });
};

/* When the script starts */
document.addEventListener("DOMContentLoaded", function () {
    console.log("Js Started");
    registeredServiceWorker();
    init();
});
