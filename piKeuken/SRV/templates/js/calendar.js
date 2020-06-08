const production = false,
  ip = "https://localhost:5000";
  
/* init-function --> For starting the script */
const init = function () {
    console.log("script stared");
  };
  
  const registeredServiceWorker = function () {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker
        .register("./sw.js", {scope: '/'})
        .then(registration => {
          console.log("ServiceWorker running");
        })
        .catch(err => {
           console.log(err);
        })
    }
  };
  
  /* When the script starts */
  document.addEventListener("DOMContentLoaded", function () {
    console.log("Js Started");
    registeredServiceWorker();
    init();
  });