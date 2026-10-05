(() => {
    const config = document.getElementById('experience-config').dataset;
    const list = document.getElementById('experience-list');
    const loading = document.getElementById('experience-loading');
    const error = document.getElementById('experience-error');
    const empty = document.getElementById('experience-empty');
    const search = document.getElementById('experience-title-search');
    const category = document.getElementById('experience-category-search');
    const clear = document.getElementById('clear-experience-search');
    const form = document.getElementById('experience-form');
    const csrfToken = document.querySelector('[name="csrfmiddlewaretoken"]').value;
    const uuidMarker = '00000000-0000-0000-0000-000000000000';
    let controller;
    let debounceTimer;

    function element(tag, className, value) {
        const node = document.createElement(tag);
        if (className) node.className = className;
        if (value !== undefined) node.textContent = value;
        return node;
    }

    function actionUrl(template, id) {
        return template.replace(uuidMarker, encodeURIComponent(id));
    }

    function postForm(action, className) {
        const node = element('form', className);
        node.method = 'post';
        node.action = action;
        const token = document.createElement('input');
        token.type = 'hidden';
        token.name = 'csrfmiddlewaretoken';
        token.value = csrfToken;
        node.append(token);
        return node;
    }

    function buildExperience(item) {
        const data = item.fields;
        const row = element('li', 'timeline-item');
        const article = document.createElement('article');
        const marker = element('div', 'timeline-marker');
        marker.setAttribute('aria-hidden', 'true');
        marker.append(document.createElement('span'));

        const meta = element('div', 'timeline-meta');
        meta.append(element('p', '', data.category));
        const status = element('span', `status-chip${data.is_ongoing ? ' status-live' : ''}`, data.is_ongoing ? 'Sedang berlangsung' : 'Selesai');
        if (data.is_ongoing) status.prepend(document.createElement('i'));
        meta.append(status);

        const content = element('div', 'timeline-content');
        content.append(element('h3', '', data.title), element('p', '', data.description));
        const actions = element('div', 'timeline-actions');

        const star = postForm(actionUrl(config.starUrl, item.pk), 'star-form');
        const starButton = element('button', `button button-star${data.is_starred ? ' is-starred' : ''}`);
        starButton.type = 'submit';
        starButton.title = data.star_count ? `Starred by ${data.starred_by_names}` : 'Be the first to star this experience';
        const icon = element('span', '', '★ ');
        icon.setAttribute('aria-hidden', 'true');
        starButton.append(icon, element('span', 'star-label', data.is_starred ? 'Unstar' : 'Star'), element('span', 'star-count', String(data.star_count)));
        star.append(starButton);
        actions.append(star);

        if (config.canEdit === 'true') {
            const edit = element('a', 'button button-ghost', 'Edit');
            edit.href = actionUrl(config.editUrl, item.pk);
            actions.append(edit);
        }

        if (config.isSuperuser === 'true') {
            const deleteButton = element('button', 'button button-danger', 'Delete');
            deleteButton.type = 'button';
            deleteButton.dataset.deleteDialog = `delete-experience-${item.pk}`;
            actions.append(deleteButton);

            const dialog = element('dialog', 'project-delete-modal');
            dialog.id = deleteButton.dataset.deleteDialog;
            const dialogContent = element('div', 'project-delete-modal-content');
            dialogContent.append(element('p', 'section-label', '// CONFIRM_DELETE'), element('h4', '', 'Delete experience?'), element('p', '', `"${data.title}" akan dihapus dari database. Aksi ini tidak bisa dibatalkan.`));
            const dialogActions = element('div', 'project-delete-modal-actions');
            const cancel = element('form', '');
            cancel.method = 'dialog';
            const cancelButton = element('button', 'button button-ghost', 'Cancel');
            cancelButton.type = 'submit';
            cancel.append(cancelButton);
            const deletion = postForm(actionUrl(config.deleteUrl, item.pk), '');
            const confirm = element('button', 'button button-danger', 'Yes, delete');
            confirm.type = 'submit';
            deletion.append(confirm);
            dialogActions.append(cancel, deletion);
            dialogContent.append(dialogActions);
            dialog.append(dialogContent);
            row.append(dialog);
        }

        content.append(actions);
        article.append(marker, meta, content);
        row.prepend(article);
        return row;
    }

    function showState(current) {
        for (const [name, node] of Object.entries({ loading, error, empty, list })) {
            node.classList.toggle('hide', name !== current);
        }
    }

    async function fetchExperiences() {
        if (controller) controller.abort();
        const requestController = new AbortController();
        controller = requestController;
        showState('loading');
        const params = new URLSearchParams();
        if (search.value.trim()) params.set('title', search.value.trim());
        if (category.value) params.set('category', category.value);
        clear.hidden = !params.size;
        const url = params.size ? `${config.apiUrl}?${params}` : config.apiUrl;
        try {
            const response = await fetch(url, { headers: { Accept: 'application/json' }, signal: requestController.signal });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const records = await response.json();
            if (controller !== requestController) return;
            list.replaceChildren(...records.map(buildExperience));
            showState(records.length ? 'list' : 'empty');
        } catch (failure) {
            if (failure.name !== 'AbortError') {
                console.error('Unable to load experiences:', failure);
                showState('error');
            }
        }
    }

    search.addEventListener('input', () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(fetchExperiences, 300);
    });
    category.addEventListener('change', () => {
        clearTimeout(debounceTimer);
        fetchExperiences();
    });
    document.getElementById('experience-search-form').addEventListener('submit', (event) => {
        event.preventDefault();
        clearTimeout(debounceTimer);
        fetchExperiences();
    });
    clear.addEventListener('click', () => {
        search.value = '';
        category.value = '';
        fetchExperiences();
        search.focus();
    });
    document.getElementById('retry-experiences').addEventListener('click', fetchExperiences);

    list.addEventListener('submit', async (event) => {
        const starForm = event.target;
        if (!starForm.matches('.star-form') || config.isAuthenticated !== 'true') return;
        event.preventDefault();
        const button = starForm.querySelector('button');
        button.disabled = true;
        try {
            const response = await fetch(starForm.action, {
                method: 'POST',
                headers: { 'X-CSRFToken': csrfToken, Accept: 'application/json' },
                body: new FormData(starForm),
            });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const result = await response.json();
            button.classList.toggle('is-starred', result.is_starred);
            button.querySelector('.star-label').textContent = result.is_starred ? 'Unstar' : 'Star';
            button.querySelector('.star-count').textContent = result.star_count;
            button.title = result.star_count ? `Starred by ${result.starred_by_names}` : 'Be the first to star this experience';
        } catch (failure) {
            console.error('Unable to update star:', failure);
            showToast('Gagal memberi star', 'Silakan coba lagi.', 'error');
        } finally {
            button.disabled = false;
        }
    });

    if (form) {
        form.addEventListener('submit', async (event) => {
            event.preventDefault();
            const submit = form.querySelector('[type="submit"]');
            submit.disabled = true;
            form.querySelectorAll('[data-error-for]').forEach((node) => { node.textContent = ''; });
            try {
                const response = await fetch(config.createUrl, {
                    method: 'POST',
                    headers: { 'X-CSRFToken': csrfToken, Accept: 'application/json' },
                    body: new FormData(form),
                });
                const result = await response.json().catch(() => ({}));
                if (!response.ok) {
                    if (result.errors) {
                        form.querySelectorAll('[data-error-for]').forEach((node) => {
                            const fieldErrors = result.errors[node.dataset.errorFor] || [];
                            node.textContent = fieldErrors.map((item) => item.message).join(' ');
                        });
                    }
                    const message = result.errors
                        ? Object.values(result.errors).flat().map((item) => item.message).join(' ')
                        : result.message || `HTTP ${response.status}`;
                    showToast('Gagal menambah pengalaman', message, 'error');
                    return;
                }
                form.reset();
                document.getElementById('add-experience-modal').hidePopover();
                showToast('Berhasil', 'Pengalaman baru berhasil ditambahkan!', 'success');
                fetchExperiences();
            } catch (failure) {
                console.error('Unable to add experience:', failure);
                showToast('Gagal menambah pengalaman', 'Tidak dapat terhubung ke server.', 'error');
            } finally {
                submit.disabled = false;
            }
        });
    }

    fetchExperiences();
})();
