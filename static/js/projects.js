(() => {
    const config = document.getElementById('project-config').dataset;
    const grid = document.getElementById('project-grid');
    const states = {
        loading: document.getElementById('project-loading'),
        error: document.getElementById('project-error'),
        empty: document.getElementById('project-empty'),
        grid,
    };
    const search = document.getElementById('project-title-search');
    const clear = document.getElementById('clear-project-search');
    const projectForm = document.getElementById('project-form');
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

    function itemUrl(template, marker, value) {
        return template.replace(marker, encodeURIComponent(value));
    }

    function actionForm(action, type) {
        const form = element('form', type === 'star' ? 'star-form' : '');
        form.method = 'post';
        form.action = action;
        form.dataset.apiAction = type;
        return form;
    }

    function buildCard(project) {
        const detailUrl = itemUrl(config.detailUrl, 'project-placeholder', project.slug);
        const card = element('article', `project-card${project.featured ? ' is-featured' : ''}`);
        const cover = element('a', 'project-cover');
        cover.href = detailUrl;
        cover.setAttribute('aria-label', `View ${project.title} details`);
        if (project.thumbnail_url) {
            const image = document.createElement('img');
            image.src = project.thumbnail_url;
            image.alt = `Cover art for ${project.title}`;
            cover.append(image);
        } else {
            const placeholder = element('div', 'project-placeholder');
            placeholder.append(element('span', '', '</>'), element('small', '', 'NO_COVER.PNG'));
            cover.append(placeholder);
        }
        cover.append(element('span', 'project-status', project.status_display));
        if (project.featured) cover.append(element('span', 'featured-flag', 'Featured'));
        card.append(cover);

        const body = element('div', 'project-card-body');
        body.append(element('p', 'project-category', `${project.category_display} · ${project.role}`));
        const heading = document.createElement('h3');
        const title = element('a', '', project.title);
        title.href = detailUrl;
        heading.append(title);
        body.append(heading, element('p', '', project.summary));
        const tags = element('ul', 'tag-list');
        tags.setAttribute('aria-label', 'Technologies used');
        (project.technology_list || []).forEach((technology) => tags.append(element('li', '', technology)));
        body.append(tags);

        const actions = element('div', 'project-card-actions');
        const detail = element('a', 'project-link', 'Read case file →');
        detail.href = detailUrl;
        actions.append(detail);
        if (config.isAuthenticated === 'true') {
            const star = actionForm(itemUrl(config.starUrl, uuidMarker, project.id), 'star');
            const button = element('button', `button button-star${project.is_starred ? ' is-starred' : ''}`);
            button.type = 'submit';
            button.title = project.star_count ? `Starred by ${project.starred_by_names}` : 'Be the first to star this project';
            const icon = element('span', '', '★ ');
            icon.setAttribute('aria-hidden', 'true');
            button.append(icon, element('span', 'star-label', project.is_starred ? 'Unstar' : 'Star'), element('span', 'star-count', String(project.star_count)));
            star.append(button);
            actions.append(star);
        } else {
            const login = element('a', 'button button-star', `★ Star ${project.star_count}`);
            login.href = `${config.loginUrl}?next=${encodeURIComponent(window.location.pathname)}`;
            login.title = 'Log in to star this project';
            actions.append(login);
        }
        if (config.isSuperuser === 'true') {
            const trigger = element('button', 'project-delete-trigger', 'Delete');
            trigger.type = 'button';
            trigger.dataset.deleteDialog = `delete-project-${project.id}`;
            actions.append(trigger);
            const dialog = element('dialog', 'project-delete-modal');
            dialog.id = trigger.dataset.deleteDialog;
            const content = element('div', 'project-delete-modal-content');
            content.append(element('p', 'section-label', '// CONFIRM_DELETE'), element('h4', '', 'Delete project?'), element('p', '', `"${project.title}" akan dihapus dari database. Aksi ini tidak bisa dibatalkan.`));
            const dialogActions = element('div', 'project-delete-modal-actions');
            const cancel = element('form', '');
            cancel.method = 'dialog';
            const cancelButton = element('button', 'button button-ghost', 'Cancel');
            cancelButton.type = 'submit';
            cancel.append(cancelButton);
            const deletion = actionForm(itemUrl(config.deleteUrl, uuidMarker, project.id), 'delete');
            const confirm = element('button', 'button button-danger', 'Yes, delete');
            confirm.type = 'submit';
            deletion.append(confirm);
            dialogActions.append(cancel, deletion);
            content.append(dialogActions);
            dialog.append(content);
            card.append(dialog);
        }
        body.append(actions);
        card.append(body);
        return card;
    }

    function showState(current) {
        for (const [name, node] of Object.entries(states)) node.classList.toggle('hide', name !== current);
    }

    async function fetchProjects() {
        controller?.abort();
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

    async function refreshStats() {
        try {
            const response = await fetch(config.apiUrl, { headers: { Accept: 'application/json' } });
            if (!response.ok) return;
            const projects = await response.json();
            const counts = {
                'project-count': projects.length,
                'released-count': projects.filter((item) => item.status === 'released').length,
                'featured-count': projects.filter((item) => item.featured).length,
            };
            for (const [id, count] of Object.entries(counts)) {
                document.getElementById(id).textContent = String(count).padStart(2, '0');
            }
        } catch (failure) {
            console.error('Unable to refresh project statistics:', failure);
        }
    }

    function showValidationErrors(result) {
        projectForm.querySelectorAll('[data-error-for]').forEach((target) => {
            target.textContent = (result[target.dataset.errorFor] || []).join(' ');
        });
        return Object.values(result).filter(Array.isArray).flat().join(' ') || result.detail || 'Permintaan gagal.';
    }

    search.addEventListener('input', () => {
        clearTimeout(debounceTimer);
        clear.hidden = !search.value;
        debounceTimer = setTimeout(fetchProjects, 300);
    });
    document.getElementById('project-search-form').addEventListener('submit', (event) => {
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

    grid.addEventListener('submit', async (event) => {
        const form = event.target;
        const action = form.dataset.apiAction;
        if (!action) return;
        event.preventDefault();
        const button = form.querySelector('[type="submit"]');
        button.disabled = true;
        try {
            const response = await fetch(form.action, {
                method: action === 'delete' ? 'DELETE' : 'POST',
                headers: { 'X-CSRFToken': csrfToken, Accept: 'application/json' },
            });
            if (!response.ok) {
                const result = await response.json().catch(() => ({}));
                throw new Error(result.detail || `HTTP ${response.status}`);
            }
            if (action === 'star') {
                const result = await response.json();
                button.classList.toggle('is-starred', result.is_starred);
                button.querySelector('.star-label').textContent = result.is_starred ? 'Unstar' : 'Star';
                button.querySelector('.star-count').textContent = result.star_count;
                button.title = result.star_count ? `Starred by ${result.starred_by_names}` : 'Be the first to star this project';
            } else {
                form.closest('dialog').close();
                showToast('Berhasil', 'Proyek berhasil dihapus.', 'success');
                fetchProjects();
                refreshStats();
            }
        } catch (failure) {
            console.error(`Unable to ${action} project:`, failure);
            showToast('Permintaan gagal', failure.message, 'error');
        } finally {
            button.disabled = false;
        }
    });

    if (projectForm) {
        projectForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const submit = projectForm.querySelector('[type="submit"]');
            submit.disabled = true;
            projectForm.querySelectorAll('[data-error-for]').forEach((node) => { node.textContent = ''; });
            const data = Object.fromEntries(new FormData(projectForm).entries());
            delete data.csrfmiddlewaretoken;
            data.featured = projectForm.elements.featured.checked;
            try {
                const response = await fetch(config.createUrl, {
                    method: 'POST',
                    headers: { 'X-CSRFToken': csrfToken, Accept: 'application/json', 'Content-Type': 'application/json' },
                    body: JSON.stringify(data),
                });
                const result = await response.json().catch(() => ({}));
                if (!response.ok) {
                    showToast('Gagal menambahkan proyek', showValidationErrors(result), 'error');
                    return;
                }
                projectForm.reset();
                document.getElementById('add-project-modal').hidePopover();
                showToast('Berhasil', 'Proyek baru berhasil ditambahkan!', 'success');
                fetchProjects();
                refreshStats();
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
