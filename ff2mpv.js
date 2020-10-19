function ff2mpv(url) {
    notifyContentScript();
    browser.runtime.sendNativeMessage("ff2mpv", { url: url });
}

function notifyContentScript() {
    browser.tabs.query({active: true, currentWindow: true}, function(tabs){
        browser.tabs.sendMessage(tabs[0].id, {launch: true});
    });
}

browser.contentScripts.register({
    matches: ["<all_urls>"],
    js: [{file: "/content_script.js"}]
});

browser.contextMenus.create({
    id: "ff2mpv",
    title: "Play in MPV",
    contexts: ["link", "image", "video", "audio", "selection", "frame"]
});

browser.contextMenus.onClicked.addListener((info, tab) => {
    switch (info.menuItemId) {
        case "ff2mpv":
            /* These should be mutually exclusive, but,
               if they aren't, this is a reasonable priority.
            */
            url = info.linkUrl || info.srcUrl || info.selectionText || info.frameUrl;
            if (url) ff2mpv(url);
            break;
    }
});

browser.browserAction.onClicked.addListener((tab) => {
    ff2mpv(tab.url);
});
