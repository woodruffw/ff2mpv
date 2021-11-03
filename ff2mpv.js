function onError(error) {
    console.log(`${error}`);
}

function ff2mpv(url) {
    browser.tabs.executeScript({
        code: "video = document.getElementsByTagName('video');video[0].pause();"
    });
    browser.runtime.sendNativeMessage("ff2mpv", { url: url }).catch(onError);
}

// define the platform variable to check the platform Info
var platform = browser.runtime.getPlatformInfo();

// Make check on platform
platform.then(function(i) {
  var os = i.os;
  // if it's windows then use mnemonics V, if not use W as default
  var contextMenu = os == "win" ? "&V" : "V (&W)";
  browser.contextMenus.create({
      id: "ff2mpv",
      title: "Play in MP"  + ( !!browser.contextMenus.getTargetElement ? contextMenu : "" ),
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
