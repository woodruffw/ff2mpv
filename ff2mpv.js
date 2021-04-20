function ff2mpv(url, cookies={}) {
    browser.runtime.sendNativeMessage("ff2mpv", {
        url: url,
        cookies: cookies
    });
}

browser.contextMenus.create({
    id: "ff2mpv",
    title: "Play in MPV",
    contexts: ["link", "image", "video", "audio", "selection", "frame"]
});

browser.contextMenus.onClicked.addListener((info, tab) => {
    switch (info.menuItemId) {
        case "ff2mpv":
            url = info.linkUrl || info.srcUrl || info.selectionText || info.frameUrl;
            if (url) {
                browser.cookies.getAll({url: url}).then((cookies) => {
                    ff2mpv(url, cookies);
                });
            }
            break;
    }
});

browser.browserAction.onClicked.addListener((tab) => {
    ff2mpv(tab.url);
});
