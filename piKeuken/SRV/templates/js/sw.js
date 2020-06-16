self.addEventListener("fetch", function (event) {
    // Now we can do the service worker magic!
    // This will stand in between the network and the device
    console.log(event);
});
