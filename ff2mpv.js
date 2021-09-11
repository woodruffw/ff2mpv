function onError(error) {
    console.log(`${error}`);
}

async function ff2mpv(url, direct) {
    let time;
    if (direct) {
        time = await browser.tabs.executeScript({
            code: "video = document.getElementsByTagName('video');video[0].pause();video[0].currentTime"
        });
    }
    browser.runtime.sendNativeMessage("ff2mpv", time ? { url, time } : { url }).catch(onError);
}

browser.contextMenus.create({
    id: "ff2mpv",
    title: "Play in MPV"  + ( !!browser.contextMenus.getTargetElement ? " (&W)" : "" ),
    contexts: ["link", "image", "video", "audio", "selection", "frame"]
});

browser.contextMenus.onClicked.addListener((info, tab) => {
    switch (info.menuItemId) {
        case "ff2mpv":
            /* These should be mutually exclusive, but,
               if they aren't, this is a reasonable priority.
            */
            url = info.linkUrl || info.srcUrl || info.selectionText || info.frameUrl;
            if (url) ff2mpv(url, false);
            break;
    }
});

browser.browserAction.onClicked.addListener((tab) => {
    ff2mpv(tab.url, true);
});
