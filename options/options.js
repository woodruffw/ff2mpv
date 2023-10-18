(() => {
  const profilesWrapper = document.getElementById('profiles-wrapper');
  const addButton = document.getElementById('add');
  const PROFILES = 'profiles';

  const uuid = () => {
    return crypto.randomUUID();
  }

  const getProfiles = async () => {
    return (await browser.storage.sync.get(PROFILES))[PROFILES] || [];
  };

  const saveProfile = async (profile) => {
    const storedProfiles = await getProfiles();
    const existingProfile = storedProfiles.find(sp => sp.id === profile.id);
    let updatedProfiles;

    if (existingProfile) {
      existingProfile.content = profile.content;
      existingProfile.name = profile.name;

      updatedProfiles = {
        [PROFILES]: storedProfiles,
      };
    } else {
      updatedProfiles = {
        [PROFILES]: [
          ...storedProfiles,
          profile,
        ]
      };
    }

    return browser.storage.sync.set(updatedProfiles);
  };

  const deleteProfile = async (id) => {
    const storedProfiles = await getProfiles();
    const updatedProfiles = storedProfiles.filter(sp => sp.id !== id);

    return browser.storage.sync.set({ [PROFILES]: updatedProfiles });
  };

  const onSaveProfile = (event) => {
    const targetProfile = event.target.parentElement.parentElement;
    const name = targetProfile.children[0].value;
    const content = targetProfile.children[1].value.trim().split('\n');

    if (!name) {
      return;
    }

    const backgroundPage = browser.extension.getBackgroundPage();
    let profileFunction = 'updateProfile';

    // Save new profile
    if (!targetProfile.dataset.id) {
      targetProfile.dataset.id = uuid();
      targetProfile.classList.remove('new-profile');
      profileFunction = 'createProfile';
    }

    const id = targetProfile.dataset.id || uuid();
    const profile = { id, name, content };

    backgroundPage[profileFunction](profile);

    return saveProfile(profile);
  };

  const onDeleteProfile = (event) => {
    const targetProfile = event.target.parentElement.parentElement;
    const buttonsWrapper = targetProfile.children[2];
    const id = targetProfile.dataset.id;

    buttonsWrapper.children[0].removeEventListener('click', onSaveProfile);
    buttonsWrapper.children[1].removeEventListener('click', onDeleteProfile);
    profilesWrapper.removeChild(targetProfile);

    if (id) {
      const backgroundPage = browser.extension.getBackgroundPage();

      backgroundPage.deleteProfile(id);
    }

    return deleteProfile(id);
  };

  const createProfile = ({ name = '', content = [], id }) => {
    const profileDiv = document.createElement('div');
    const profileName = document.createElement('input');
    const profileContent = document.createElement('textArea');
    const buttonsWrapper = document.createElement('div');
    const saveButton = document.createElement('button');
    const deleteButton = document.createElement('button');

    if (id) {
      profileDiv.dataset.id = id;
    }

    profileDiv.classList.add('profile');
    buttonsWrapper.classList.add('buttons-wrapper');
    saveButton.classList.add('button');
    deleteButton.classList.add('button');
    deleteButton.classList.add('delete-button');

    profileName.placeholder = 'Profile Name';
    profileContent.placeholder = 'mpv args (1 per line)';

    saveButton.addEventListener('click', onSaveProfile);
    deleteButton.addEventListener('click', onDeleteProfile);

    profileContent.value = content.length ? content.join('\n') + '\n' : '';
    profileName.value = name;

    saveButton.textContent = 'save';
    deleteButton.textContent = 'delete';

    buttonsWrapper.appendChild(saveButton);
    buttonsWrapper.appendChild(deleteButton);

    profileDiv.appendChild(profileName);
    profileDiv.appendChild(profileContent);
    profileDiv.appendChild(buttonsWrapper);

    return profileDiv;
  }

  const load = async () => {
    addButton.addEventListener('click', () => {
      const emptyProfile = createProfile({});

      emptyProfile.classList.add('new-profile');
      profilesWrapper.appendChild(emptyProfile);
    });

    const profiles = await getProfiles();
    const profileElements = profiles.map(pf => createProfile(pf));
    profilesWrapper.replaceChildren(...profileElements);
  };

  window.addEventListener('load', load);
})();
