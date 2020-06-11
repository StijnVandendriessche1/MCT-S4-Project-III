const production = false,
  ip = "https://localhost:5000";

let isclicked = false;

/* init-function --> For starting the script */
const init = function () {
  console.log("script stared");
  domBell = document.querySelector(".js-bell");
  domBell.addEventListener("click", function () {
    showNotifications();
  });
};

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

/* When the script starts */
document.addEventListener("DOMContentLoaded", function () {
  console.log("Js Started");
  registeredServiceWorker();
  init();
});
