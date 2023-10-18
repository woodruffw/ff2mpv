const contexts = ["link", "image", "video", "audio", "selection", "frame"];

function onError(error) {
  console.log(`${error}`);
}

function ff2mpv(url, options = []) {
  browser.tabs.executeScript({
    code: "video = document.getElementsByTagName('video');video[0].pause();"
  });
  browser.runtime.sendNativeMessage("ff2mpv", { url, options }).catch(onError);
}

async function getOS() {
  return browser.runtime.getPlatformInfo().then((i) => i.os);
}

async function getProfiles() {
  return (await browser.storage.sync.get('profiles'))['profiles'] || [];
};

function submenuClicked(content) {
  return (info) => {
    switch (info.parentMenuItemId) {
      case "ff2mpv":
        /* These should be mutually exclusive, but,
           if they aren't, this is a reasonable priority.
        */
        url = info.linkUrl || info.srcUrl || info.selectionText || info.frameUrl;
        if (url) ff2mpv(url, content);
      break;
    }
  }
}

function createProfile(profile) {
  browser.contextMenus.create({
    parentId: "ff2mpv",
    id: profile.id,
    title: profile.name,
    contexts,
    onclick: submenuClicked(profile.content),
  })
}

function deleteProfile(menuItemId) {
  browser.contextMenus.remove(menuItemId);
}

function updateProfile(profile) {
  browser.contextMenus.update(profile.id, {
    title: profile.name,
    onclick: submenuClicked(profile.content),
  });
}

getOS().then(async (os) => {
  var title = os == "win" ? "Play in MP&V" : "Play in MPV (&W)";

  browser.contextMenus.create({
    id: "ff2mpv",
    title: "Profiles",
    contexts,
  });

  // Default entry
  browser.contextMenus.create({
    parentId: "ff2mpv",
    title,
    contexts,
    onclick: submenuClicked(),
  });

  const profiles = await getProfiles();

  profiles.forEach(profile => {
    browser.contextMenus.create({
      parentId: "ff2mpv",
      id: profile.id,
      title: profile.name,
      contexts,
      onclick: submenuClicked(profile.content),
    })
  });

  browser.browserAction.onClicked.addListener((tab) => {
    ff2mpv(tab.url);
  });
});
