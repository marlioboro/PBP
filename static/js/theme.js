const themeToggle = document.querySelector('[data-theme-toggle]');
const themeMedia = window.matchMedia('(prefers-color-scheme: dark)');
const themeOptions = ['system', 'light', 'dark'];

const themeLabels = {
    system: { label: 'System', icon: 'SYS' },
    light: { label: 'Light', icon: 'SUN' },
    dark: { label: 'Dark', icon: 'NGT' },
};

function resolveTheme(preference) {
    if (preference === 'system') {
        return themeMedia.matches ? 'dark' : 'light';
    }
    return preference;
}

function applyTheme(preference, savePreference = true) {
    const safePreference = themeOptions.includes(preference) ? preference : 'system';
    const theme = resolveTheme(safePreference);

    document.documentElement.dataset.theme = theme;
    document.documentElement.dataset.themePreference = safePreference;

    if (savePreference) {
        localStorage.setItem('portfolio-theme', safePreference);
    }

    if (themeToggle) {
        const copy = themeLabels[safePreference];
        themeToggle.querySelector('.theme-toggle-icon').textContent = copy.icon;
        themeToggle.querySelector('.theme-toggle-label').textContent = copy.label;
        themeToggle.setAttribute('aria-label', `Theme: ${copy.label}`);
        themeToggle.setAttribute('title', `Theme: ${copy.label}. Click to change.`);
    }
}

function transitionToTheme(preference, savePreference = true) {
    document.documentElement.classList.add('is-theme-transitioning');

    // Force the browser to register the transition styles before the theme
    // variables change, so the colors interpolate instead of flashing.
    void document.documentElement.offsetWidth;
    applyTheme(preference, savePreference);

    window.setTimeout(() => {
        document.documentElement.classList.remove('is-theme-transitioning');
    }, 420);
}

if (themeToggle) {
    themeToggle.addEventListener('click', () => {
        const current = document.documentElement.dataset.themePreference || 'system';
        const nextIndex = (themeOptions.indexOf(current) + 1) % themeOptions.length;
        transitionToTheme(themeOptions[nextIndex]);
    });
}

themeMedia.addEventListener('change', () => {
    if (document.documentElement.dataset.themePreference === 'system') {
        transitionToTheme('system', false);
    }
});

applyTheme(document.documentElement.dataset.themePreference || 'system', false);
