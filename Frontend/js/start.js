const production = false,
  ip = "http://localhost:5000";
let socket = io.connect(ip);

/* Sockets */

socket.on('welcome', function(data) {
	log(data);
});


/* Functions */

const log = function (message) {
  if (!production) console.log(message);
};
const init = function () {
    socket.emit("connect")
};
document.addEventListener("DOMContentLoaded", function () {
  log("Js Started");
  init();
});
