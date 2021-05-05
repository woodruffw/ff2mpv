function ff2mpv(url, cookies={}) {
    browser.tabs.executeScript({
        code: "video = document.getElementsByTagName('video');video[0].pause();"
    });
    browser.runtime.sendNativeMessage("ff2mpv", {
        url: url,
        cookies: cookies
    }).catch(onError);
}
  
function onError(error) {
    console.log(`${error}`);
}

browser.contextMenus.create({
    id: "ff2mpv",
    title: "Play in MPV",
    contexts: ["link", "image", "video", "audio", "selection", "frame"]
});

browser.contextMenus.onClicked.addListener((info, tab) => {
    url = info.linkUrl || info.srcUrl || info.selectionText || info.frameUrl;
    if (url) {
        browser.cookies.getAll({url: url}).then((cookies) => {
            ff2mpv(url, cookies);
        });
    }
});

browser.browserAction.onClicked.addListener((tab) => {
    ff2mpv(tab.url);
});
