const production = false,
  ip = "http://localhost:5000";
let socket = io.connect(ip);

/* Sockets */

/* Sockets for putting the ai's on or off */
socket.on('status_ai_meeting', function(data) {
	log(data);
});


/* Functions */

/* Function for putting the ai's on or off */
const ai_meeting_status = function(){
  socket.emit("ai_meeting")
};

/* Function for logging while debugging */
const log = function (message) {
  if (!production) console.log(message);
};
/* init-function --> For starting the script */
const init = function () {
    socket.emit("connect")
};

/* When the script starts */
document.addEventListener("DOMContentLoaded", function () {
  log("Js Started");
  init();
});
