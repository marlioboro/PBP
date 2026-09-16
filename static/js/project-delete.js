document.addEventListener('click', (event) => {
    const trigger = event.target.closest('[data-delete-dialog]');
    if (!trigger) return;

    const dialog = document.getElementById(trigger.dataset.deleteDialog);
    if (dialog) dialog.showModal();
});
