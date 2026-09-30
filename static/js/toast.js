(() => {
    const toast = document.getElementById('site-toast');
    const title = document.getElementById('toast-title');
    const message = document.getElementById('toast-message');
    let timer;

    window.showToast = (heading, body, type = 'normal', duration = 3000) => {
        clearTimeout(timer);
        title.textContent = heading;
        message.textContent = body;
        toast.dataset.type = type;
        toast.showPopover();
        toast.classList.add('is-visible');
        timer = setTimeout(() => {
            toast.classList.remove('is-visible');
            setTimeout(() => {
                if (!toast.classList.contains('is-visible')) toast.hidePopover();
            }, 250);
        }, duration);
    };
})();
