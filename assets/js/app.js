const CONFIG = {
    owner: 'Willianjesusdasilva',
    repo: 'willianjesusdasilva.github.io',
    branch: 'master',
    ideasPath: 'ideas'
};

let ideas = [];
let selectedIdea = null;

function escapeHtml(value = '') {
    return String(value)
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#039;');
}

function extractJsonHeader(text) {
    const source = text.replace(/^\uFEFF/, '').trimStart();

    if (!source.startsWith('{')) {
        throw new Error('O arquivo precisa começar com um objeto JSON.');
    }

    let depth = 0;
    let inString = false;
    let escaped = false;
    let end = -1;

    for (let i = 0; i < source.length; i++) {
        const char = source[i];

        if (inString) {
            if (escaped) {
                escaped = false;
            } else if (char === '\\') {
                escaped = true;
            } else if (char === '"') {
                inString = false;
            }
            continue;
        }

        if (char === '"') {
            inString = true;
            continue;
        }

        if (char === '{') depth++;
        if (char === '}') {
            depth--;
            if (depth === 0) {
                end = i;
                break;
            }
        }
    }

    if (end === -1) {
        throw new Error('JSON inicial não foi fechado corretamente.');
    }

    const metadata = JSON.parse(source.slice(0, end + 1));
    const markdown = source.slice(end + 1).trimStart();

    if (!metadata.nome || typeof metadata.nome !== 'string') {
        throw new Error('O JSON precisa conter "nome".');
    }

    if (!Array.isArray(metadata.tags)) {
        metadata.tags = [];
    }

    metadata.status = metadata.status || 'ideia';

    return { metadata, markdown };
}

async function loadProfile() {
    const target = document.getElementById('side-bar');

    try {
        const response = await fetch(`https://api.github.com/users/${CONFIG.owner}`);
        if (!response.ok) throw new Error('Perfil indisponível');

        const profile = await response.json();
        target.innerHTML = `
            <img src="${escapeHtml(profile.avatar_url)}" class="img-circle" id="profile-img" alt="Avatar">
            <h4 id="text-profile-name">${escapeHtml(profile.name || profile.login)}</h4>
            <h6 id="text-profile-bio">${escapeHtml(profile.bio || '')}</h6>
            <h6 id="text-profile-company">${profile.company ? `Desenvolvedor na ${escapeHtml(profile.company)}` : ''}</h6>
        `;
    } catch (error) {
        target.innerHTML = `<h4 id="text-profile-name">${escapeHtml(CONFIG.owner)}</h4>`;
    }
}

async function discoverMarkdownFiles() {
    const url = `https://api.github.com/repos/${CONFIG.owner}/${CONFIG.repo}/contents/${CONFIG.ideasPath}?ref=${CONFIG.branch}`;
    const response = await fetch(url, {
        headers: { Accept: 'application/vnd.github+json' }
    });

    if (response.status === 404) return [];
    if (!response.ok) throw new Error(`GitHub respondeu ${response.status}`);

    const entries = await response.json();
    return entries
        .filter(item => item.type === 'file' && item.name.toLowerCase().endsWith('.md'))
        .sort((a, b) => a.name.localeCompare(b.name));
}

async function loadIdeaFile(file) {
    try {
        // Cache-busting pelo SHA: quando o arquivo muda, a URL muda também.
        const rawUrl = `https://raw.githubusercontent.com/${CONFIG.owner}/${CONFIG.repo}/${CONFIG.branch}/${file.path}?v=${file.sha}`;
        const response = await fetch(rawUrl);
        if (!response.ok) throw new Error(`Não foi possível baixar ${file.name}`);

        const text = await response.text();
        const { metadata, markdown } = extractJsonHeader(text);

        return {
            fileName: file.name,
            path: file.path,
            sha: file.sha,
            nome: metadata.nome,
            tags: metadata.tags.map(String),
            status: String(metadata.status),
            markdown
        };
    } catch (error) {
        console.warn(error);
        return null;
    }
}

function renderIdeaList(items) {
    const list = document.getElementById('list-side-bar');
    list.innerHTML = '';

    if (!items.length) {
        list.innerHTML = '<li class="idea-empty">Nenhuma ideia</li>';
        return;
    }

    for (const idea of items) {
        const li = document.createElement('li');
        li.className = selectedIdea?.path === idea.path ? 'idea-item active' : 'idea-item';
        li.dataset.path = idea.path;
        li.innerHTML = `
            <a href="#${encodeURIComponent(idea.fileName)}">${escapeHtml(idea.nome)}</a>
            <span class="idea-status">${escapeHtml(idea.status)}</span>
            <span class="idea-tags">${idea.tags.map(tag => `#${escapeHtml(tag)}`).join(' ')}</span>
        `;
        li.addEventListener('click', () => selectIdea(idea));
        list.appendChild(li);
    }
}

function renderIdea(idea) {
    const center = document.getElementById('center');
    const tags = idea.tags
        .map(tag => `<span class="tag">#${escapeHtml(tag)}</span>`)
        .join(' ');

    const html = DOMPurify.sanitize(marked.parse(idea.markdown));

    center.innerHTML = `
        <article class="markdown-document">
            <header class="idea-header">
                <h1>${escapeHtml(idea.nome)}</h1>
                <div class="idea-meta">
                    <span class="status">${escapeHtml(idea.status)}</span>
                    <span class="tags">${tags}</span>
                </div>
            </header>
            <div class="markdown-body">${html}</div>
        </article>
    `;
}

function selectIdea(idea, updateHash = true) {
    selectedIdea = idea;
    renderIdea(idea);
    renderIdeaList(filterIdeas(document.getElementById('search').value));

    if (updateHash) {
        history.replaceState(null, '', `#${encodeURIComponent(idea.fileName)}`);
    }
}

function filterIdeas(query) {
    const term = query.trim().toLowerCase();
    if (!term) return ideas;

    return ideas.filter(idea => {
        const haystack = [idea.nome, idea.status, ...idea.tags].join(' ').toLowerCase();
        return haystack.includes(term);
    });
}

function selectFromHash() {
    const fileName = decodeURIComponent(location.hash.slice(1));
    if (!fileName) return false;

    const idea = ideas.find(item => item.fileName === fileName);
    if (!idea) return false;

    selectIdea(idea, false);
    return true;
}

async function loadIdeas() {
    const list = document.getElementById('list-side-bar');
    list.innerHTML = '<li class="idea-empty">Carregando...</li>';

    try {
        const files = await discoverMarkdownFiles();
        const loaded = await Promise.all(files.map(loadIdeaFile));
        ideas = loaded.filter(Boolean);

        renderIdeaList(ideas);

        if (!selectFromHash() && ideas.length) {
            selectIdea(ideas[0], false);
        }
    } catch (error) {
        console.error(error);
        list.innerHTML = '<li class="idea-empty">Erro ao buscar ideias</li>';
        document.getElementById('center').innerHTML = `
            <div id="empty-state">
                <h2>Não foi possível carregar as ideias</h2>
                <p>${escapeHtml(error.message)}</p>
            </div>
        `;
    }
}

document.getElementById('search').addEventListener('input', event => {
    renderIdeaList(filterIdeas(event.target.value));
});

window.addEventListener('hashchange', selectFromHash);

loadProfile();
loadIdeas();
