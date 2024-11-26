const contexts = ["link", "image", "video", "audio", "selection", "frame"];
const CREATE_PROFILE = "createProfile";
const UPDATE_PROFILE = "updateProfile";
const DELETE_PROFILE = "deleteProfile";
const PROFILES = "profiles";
const OPEN_VIDEO = "openVideo";
const TITLE = "Play in MPV";

function onError(error) {
  console.log(`${error}`);
}

function ff2mpv(url, tabId, options) {
  if (tabId != null) {
    chrome.scripting.executeScript({
      target: { tabId: tabId, allFrames: true },
      func: () => {
        document.querySelectorAll("video").forEach((video) => video.pause());
      },
    });
  }
  options = options ? options : [];
  chrome.runtime.sendNativeMessage("ff2mpv", { url, options }).catch(onError);
}

async function getProfiles() {
  try {
    return (await chrome.storage.sync.get(PROFILES))[PROFILES] || [];
  } catch (error) {
    console.debug("Unable to get profiles:", error);
    return [];
  }
}

async function getOptions(id) {
  try {
    const profiles = await getProfiles();
    const profile = profiles.find((pf) => pf.id === id);

    // If profile, remove empty lines
    return profile ? profile.content.filter((line) => !!line) : [];
  } catch (error) {
    console.debug("Unable to get options for profile:", id, error);
    return [];
  }
}

async function submenuClicked(info, tab) {
  if (info.parentMenuItemId === "ff2mpv" || info.menuItemId === "ff2mpv") {
    /* These should be mutually exclusive, but,
       if they aren't, this is a reasonable priority.
    */
    const url =
      info.linkUrl || info.srcUrl || info.selectionText || info.frameUrl;
    if (url) {
      const tabId = tab ? tab.tabId : null;
      const options = await getOptions(info.menuItemId);
      ff2mpv(url, tabId, options);
    }
  }
}

async function changeToMultiEntries() {
  // Remove single entry
  await chrome.contextMenus.removeAll();

  // Add sub context menu
  await chrome.contextMenus.create({
    id: "ff2mpv",
    title: "Profiles",
    contexts,
  });

  await chrome.contextMenus.create({
    parentId: "ff2mpv",
    id: "22941114-4db3-4296-8fc2-49f178843f52",
    title: TITLE,
    contexts,
  });
}

async function changeToSingleEntry() {
  // Remove sub context menu
  await chrome.contextMenus.removeAll();

  await chrome.contextMenus.create({
    id: "ff2mpv",
    title: TITLE,
    contexts,
  });
}

async function createProfile(profile) {
  const profiles = await getProfiles();

  if (profiles.length === 0) {
    await changeToMultiEntries();
  }

  await chrome.contextMenus.create({
    parentId: "ff2mpv",
    id: profile.id,
    title: profile.name,
    contexts,
  });
}

async function deleteProfile(menuItemId) {
  await chrome.contextMenus.remove(menuItemId);

  const profiles = (await getProfiles()).filter((pf) => pf.id !== menuItemId);

  if (profiles.length === 0) {
    await changeToSingleEntry();
  }
}

async function updateProfile(profile) {
  await chrome.contextMenus.update(profile.id, {
    title: profile.name,
  });
}

chrome.action.onClicked.addListener((tab) => {
  ff2mpv(tab.url, tab.id);
});

// Messages sent with chrome.runtime.sendMessage (https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/API/runtime/sendMessage) from external applications will be handle here.
// ref: https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/API/runtime/onMessageExternal
chrome.runtime.onMessageExternal.addListener((request, sender, sendResponse) => {
  if (!request) {
    console.warn("No request in external message");
    return;
  }

  const { type, url } = request;
  console.debug("Request from:", sender);

  switch (type) {
    case OPEN_VIDEO:
      ff2mpv(url);
      return sendResponse("ok");
    default:
      console.warn("No handler for external type:", type);
      return sendResponse("failure");
  }
});

chrome.runtime.onInstalled.addListener(async (_) => {
  const profiles = await getProfiles();

  if (profiles.length === 0) {
    await changeToSingleEntry();
  } else {
    await changeToMultiEntries();

    await profiles.reduce(async (promise, profile) => {
      await promise;
      await chrome.contextMenus.create({
        parentId: "ff2mpv",
        id: profile.id,
        title: profile.name,
        contexts,
      });
    }, Promise.resolve());
  }
});

chrome.contextMenus.onClicked.addListener(submenuClicked);

chrome.runtime.onMessage.addListener(async (request, _sender, sendResponse) => {
  if (!request) {
    console.warn("No request in message");
    return;
  }

  const { type, profile } = request;

  switch (type) {
    case CREATE_PROFILE:
      await createProfile(profile);
      return sendResponse("ok");
    case UPDATE_PROFILE:
      await updateProfile(profile);
      return sendResponse("ok");
    case DELETE_PROFILE:
      await deleteProfile(profile.id);
      return sendResponse("ok");
    default:
      console.warn("No handler for type:", type);
      return sendResponse("failure");
  }
});
