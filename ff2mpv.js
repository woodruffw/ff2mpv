function ff2mpv(url, opt) {
    browser.runtime.sendNativeMessage("ff2mpv", { url: url, opt: opt });
}

browser.contextMenus.create({
    id: "ff2mpv",
    title: "Play in MPV",
    contexts: ["link", "image", "video", "audio", "selection", "frame"]
});
browser.contextMenus.create({
     id: "ff2mpv_novideo",
     title: "Play in MPV (no video)",
     contexts: ["link", "image", "video", "audio", "selection", "frame"]
});

browser.contextMenus.onClicked.addListener((info, tab) => {
    switch (info.menuItemId) {
        case "ff2mpv":
            /* These should be mutually exclusive, but,
               if they aren't, this is a reasonable priority.
            */
            url = info.linkUrl || info.srcUrl || info.selectionText || info.frameUrl;
            if (url) ff2mpv(url, {"video": true});
            break;
        case "ff2mpv_novideo":
            url = info.linkUrl || info.srcUrl || info.selectionText || info.frameUrl;
            if (url) ff2mpv(url, {"video": false});
            break;
    }
});

browser.browserAction.onClicked.addListener((tab) => {
    ff2mpv(tab.url, {"video": true});  //clicking the extension icon plays with video
});
