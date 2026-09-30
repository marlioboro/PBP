(() => {
    const config = document.getElementById('project-config').dataset;
    const grid = document.getElementById('project-grid');
    const loading = document.getElementById('project-loading');
    const error = document.getElementById('project-error');
    const empty = document.getElementById('project-empty');
    const search = document.getElementById('project-title-search');
    const searchForm = document.getElementById('project-search-form');
    const clear = document.getElementById('clear-project-search');
    const projectForm = document.getElementById('project-form');
    const csrfToken = document.querySelector('[name="csrfmiddlewaretoken"]').value;
    let controller;
    let debounceTimer;

    function element(tag, className, value) {
        const node = document.createElement(tag);
        if (className) node.className = className;
        if (value !== undefined) node.textContent = value;
        return node;
    }

    function urlFor(template, marker, value) {
        return template.replace(marker, encodeURIComponent(value));
    }

    function postForm(action, className) {
        const form = element('form', className);
        form.method = 'post';
        form.action = action;
        const token = document.createElement('input');
        token.type = 'hidden';
        token.name = 'csrfmiddlewaretoken';
        token.value = csrfToken;
        form.append(token);
        return form;
    }

    function buildCard(item) {
        const data = item.fields;
        const detailUrl = urlFor(config.detailUrl, 'project-placeholder', data.slug);
        const card = element('article', `project-card${data.featured ? ' is-featured' : ''}`);
        const cover = element('a', 'project-cover');
        cover.href = detailUrl;
        cover.setAttribute('aria-label', `View ${data.title} details`);
        if (data.thumbnail_url) {
            const image = document.createElement('img');
            image.src = data.thumbnail_url;
            image.alt = `Cover art for ${data.title}`;
            cover.append(image);
        } else {
            const placeholder = element('div', 'project-placeholder');
            placeholder.append(element('span', '', '</>'), element('small', '', 'NO_COVER.PNG'));
            cover.append(placeholder);
        }
        cover.append(element('span', 'project-status', data.status));
        if (data.featured) cover.append(element('span', 'featured-flag', 'Featured'));
        card.append(cover);

        const body = element('div', 'project-card-body');
        body.append(element('p', 'project-category', `${data.category} · ${data.role}`));
        const heading = document.createElement('h3');
        const title = element('a', '', data.title);
        title.href = detailUrl;
        heading.append(title);
        body.append(heading, element('p', '', data.summary));

        const tags = element('ul', 'tag-list');
        tags.setAttribute('aria-label', 'Technologies used');
        data.technologies.forEach((technology) => tags.append(element('li', '', technology)));
        body.append(tags);

        const actions = element('div', 'project-card-actions');
        const detail = element('a', 'project-link', 'Read case file →');
        detail.href = detailUrl;
        actions.append(detail);

        const star = postForm(urlFor(config.starUrl, '00000000-0000-0000-0000-000000000000', item.pk), 'star-form');
        const starButton = element('button', `button button-star${data.is_starred ? ' is-starred' : ''}`, `${data.is_starred ? 'Unstar' : 'Star'} `);
        starButton.type = 'submit';
        starButton.title = data.star_count ? `Starred by ${data.starred_by_names}` : 'Be the first to star this project';
        starButton.prepend(element('span', '', '★ '));
        starButton.append(element('span', 'star-count', String(data.star_count)));
        star.append(starButton);
        actions.append(star);

        if (config.isSuperuser === 'true') {
            const deleteButton = element('button', 'project-delete-trigger', 'Delete');
            deleteButton.type = 'button';
            deleteButton.dataset.deleteDialog = `delete-project-${item.pk}`;
            deleteButton.setAttribute('aria-label', `Delete ${data.title}`);
            actions.append(deleteButton);

            const dialog = element('dialog', 'project-delete-modal');
            dialog.id = deleteButton.dataset.deleteDialog;
            const dialogBody = element('div', 'project-delete-modal-content');
            dialogBody.append(element('p', 'section-label', '// CONFIRM_DELETE'), element('h4', '', 'Delete project?'), element('p', '', `"${data.title}" akan dihapus dari database. Aksi ini tidak bisa dibatalkan.`));
            const dialogActions = element('div', 'project-delete-modal-actions');
            const cancel = postForm('', '');
            cancel.method = 'dialog';
            cancel.querySelector('input').remove();
            const cancelButton = element('button', 'button button-ghost', 'Cancel');
            cancelButton.type = 'submit';
            cancel.append(cancelButton);
            const deletion = postForm(urlFor(config.deleteUrl, '00000000-0000-0000-0000-000000000000', item.pk), '');
            const confirm = element('button', 'button button-danger', 'Yes, delete');
            confirm.type = 'submit';
            deletion.append(confirm);
            dialogActions.append(cancel, deletion);
            dialogBody.append(dialogActions);
            dialog.append(dialogBody);
            card.append(dialog);
        }

        body.append(actions);
        card.append(body);
        return card;
    }

    function showState(state) {
        for (const [name, node] of Object.entries({ loading, error, empty, grid })) {
            node.classList.toggle('hide', name !== state);
        }
    }

    async function fetchProjects() {
        if (controller) controller.abort();
        const requestController = new AbortController();
        controller = requestController;
        showState('loading');
        const query = search.value.trim();
        const url = query ? `${config.apiUrl}?title=${encodeURIComponent(query)}` : config.apiUrl;
        try {
            const response = await fetch(url, { headers: { Accept: 'application/json' }, signal: requestController.signal });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const projects = await response.json();
            if (controller !== requestController) return;
            grid.replaceChildren(...projects.map(buildCard));
            showState(projects.length ? 'grid' : 'empty');
        } catch (failure) {
            if (failure.name !== 'AbortError') {
                console.error('Unable to load projects:', failure);
                showState('error');
            }
        }
    }

    search.addEventListener('input', () => {
        clearTimeout(debounceTimer);
        clear.hidden = !search.value;
        debounceTimer = setTimeout(fetchProjects, 300);
    });
    searchForm.addEventListener('submit', (event) => {
        event.preventDefault();
        clearTimeout(debounceTimer);
        fetchProjects();
    });
    clear.addEventListener('click', () => {
        search.value = '';
        clear.hidden = true;
        fetchProjects();
        search.focus();
    });
    document.getElementById('retry-projects').addEventListener('click', fetchProjects);

    if (projectForm) {
        projectForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const submit = projectForm.querySelector('[type="submit"]');
            submit.disabled = true;
            projectForm.querySelectorAll('[data-error-for]').forEach((node) => { node.textContent = ''; });
            try {
                const response = await fetch(config.createUrl, {
                    method: 'POST',
                    headers: { 'X-CSRFToken': csrfToken, Accept: 'application/json' },
                    body: new FormData(projectForm),
                });
                const result = await response.json().catch(() => ({}));
                if (!response.ok) {
                    if (result.errors) {
                        Object.entries(result.errors).forEach(([field, errors]) => {
                            const target = projectForm.querySelector(`[data-error-for="${field}"]`);
                            if (target) target.textContent = errors.map((error) => error.message).join(' ');
                        });
                    }
                    const message = result.errors
                        ? Object.values(result.errors).flat().map((error) => error.message).join(' ')
                        : result.message || `HTTP ${response.status}`;
                    showToast('Gagal menambahkan proyek', message, 'error');
                    return;
                }
                projectForm.reset();
                document.getElementById('add-project-modal').hidePopover();
                showToast('Berhasil', 'Proyek baru berhasil ditambahkan!', 'success');
                for (const [key, id] of Object.entries({ total: 'project-count', released: 'released-count', featured: 'featured-count' })) {
                    document.getElementById(id).textContent = String(result.counts[key]).padStart(2, '0');
                }
                fetchProjects();
            } catch (failure) {
                console.error('Unable to add project:', failure);
                showToast('Gagal menambahkan proyek', 'Tidak dapat terhubung ke server.', 'error');
            } finally {
                submit.disabled = false;
            }
        });
    }

    fetchProjects();
})();
