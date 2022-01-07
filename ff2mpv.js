function onError(error) {
    console.log(`${error}`);
}

function ff2mpv(url) {
    browser.tabs.executeScript({
        code: "video = document.getElementsByTagName('video');video[0].pause();"
    });
    browser.runtime.sendNativeMessage("ff2mpv", { url: url }).catch(onError);
}

async function getOS() {
  return browser.runtime.getPlatformInfo().then((i) => i.os);
}

getOS().then((os) => {
  var title = os == "win" ? "Play in MP&V" : "Play in MPV (&W)";

  browser.contextMenus.create({
      id: "ff2mpv",
      title: title,
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
});
