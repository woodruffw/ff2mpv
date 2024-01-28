const contexts = ["link", "image", "video", "audio", "selection", "frame"];

function onError(error) {
  console.log(`${error}`);
}

const OPEN_VIDEO = 'openVideo';
let TITLE;

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

async function getOptions(id) {
  const profiles = await getProfiles();
  const profile = profiles.find(pf => pf.id === id);

  // If profile, remove empty lines
  return profile
    ? profile.content.filter(line => !!line)
    : [];
}

async function submenuClicked(info) {
  if (info.parentMenuItemId === 'ff2mpv' || info.menuItemId === 'ff2mpv') {
    /* These should be mutually exclusive, but,
       if they aren't, this is a reasonable priority.
    */
    const url = info.linkUrl || info.srcUrl || info.selectionText || info.frameUrl;
    if (url) {
      const options = await getOptions(info.menuItemId);
      ff2mpv(url, options);
    }
  }
}

function changeToMultiEntries() {
  // Remove single entry
  browser.contextMenus.remove('ff2mpv');

  // Add sub context menu
  browser.contextMenus.create({
    id: "ff2mpv",
    title: "Profiles",
    contexts,
    onclick: submenuClicked,
  });

  browser.contextMenus.create({
    parentId: "ff2mpv",
    title: TITLE,
    contexts,
    onclick: submenuClicked,
  });
}

function changeToSingleEntry() {
  // Remove sub context menu
  browser.contextMenus.remove('ff2mpv');

  // Add single entry
  browser.contextMenus.create({
    id: "ff2mpv",
    title: TITLE,
    contexts,
    onclick: submenuClicked,
  });
}

async function createProfile(profile) {
  const profiles = await getProfiles();

  if (profiles.length === 0) {
    changeToMultiEntries();
  }

  browser.contextMenus.create({
    parentId: "ff2mpv",
    id: profile.id,
    title: profile.name,
    contexts,
    onclick: submenuClicked,
  })
}

async function deleteProfile(menuItemId) {
  browser.contextMenus.remove(menuItemId);

  const profiles = (await getProfiles())
    .filter(pf => pf.id !== menuItemId);

  if (profiles.length === 0) {
    changeToSingleEntry();
  }
}

function updateProfile(profile) {
  browser.contextMenus.update(profile.id, {
    title: profile.name,
  });
}

browser.browserAction.onClicked.addListener((tab) => {
  ff2mpv(tab.url);
});

// Messages sent with browser.runtime.sendMessage (https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/API/runtime/sendMessage) from external applications will be handle here.
// ref: https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/API/runtime/onMessageExternal
browser.runtime.onMessageExternal.addListener((request, sender, sendResponse) => {
  if (!request) {
    console.warn('No request in external message');
    return;
  }

  const { type, url } = request;
  console.debug('Request from:', sender);

  switch (type) {
    case OPEN_VIDEO:
      ff2mpv(url);
      return sendResponse('ok');
    default:
      console.warn('No handler for external type:', type);
      return;
  }
});

getOS().then(async (os) => {
  TITLE = os === "win" ? "Play in MP&V" : "Play in MPV (&W)";

  const profiles = await getProfiles();

  if (profiles.length === 0) {
    changeToSingleEntry();
  } else {
    changeToMultiEntries();

    profiles.forEach(profile => {
      browser.contextMenus.create({
        parentId: "ff2mpv",
        id: profile.id,
        title: profile.name,
        contexts,
        onclick: submenuClicked,
      })
    });
  }
});
