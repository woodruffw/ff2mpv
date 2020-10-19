function handleMessage(_request) {
    pauseVideo() //we don't care about message contents, pause on any message received
};

function pauseVideo() {
    video = document.getElementsByTagName("video") //get all video elements
    video[0].pause() //pause the first one, there is usually only one anyway
};

browser.runtime.onMessage.addListener(handleMessage);
