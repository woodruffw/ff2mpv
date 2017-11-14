function ff2mpv(url) {
    browser.runtime.sendNativeMessage("ff2mpv", { url: url });
}

browser.menus.create({
    id: "ff2mpv",
    title: "Play in MPV",
    contexts: ["link"],
    icons: {
        "16": "icons/icon_16x16.png",
        "32": "icons/icon_32x32.png",
    },
});

browser.menus.onClicked.addListener((info, tab) => {
    switch (info.menuItemId) {
        case "ff2mpv":
            ff2mpv(info.linkUrl);
            break;
    }
});

browser.browserAction.onClicked.addListener((tab) => {
    ff2mpv(tab.url);
});
