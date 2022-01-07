function onError(error) {
    console.log(`${error}`);
    // Response to user tried to open when json file and config isn't there
    var msg = "alert(`Seems integration is failed : "+error+"`)";
    browser.tabs.executeScript({
        code: msg
    }); 
}

function ff2mpv(url) {
    browser.tabs.executeScript({
        code: "video = document.getElementsByTagName('video');video[0].pause();"
    });
    browser.runtime.sendNativeMessage("ff2mpv", { url: url }, function(r) {
        console.log(r);
        if (r != "ok") {
            // If failed, print terminal failure message
            var msg = "alert(`"+r+"`)";
            browser.tabs.executeScript({
                code: msg
            }); 
        }
    }).catch(onError);
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
