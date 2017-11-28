function ff2mpv(url) {
    browser.runtime.sendNativeMessage("ff2mpv", { url: url });
}

browser.contextMenus.create({
    id: "ff2mpv",
    title: "Play in MPV",
    contexts: ["link"]
});

browser.contextMenus.onClicked.addListener((info, tab) => {
    switch (info.menuItemId) {
        case "ff2mpv":
            ff2mpv(info.linkUrl);
            break;
    }
});

browser.browserAction.onClicked.addListener((tab) => {
    ff2mpv(tab.url);
});
