import json
from html import escape

from pyscript import document, window
from pyscript.fetch import fetch
from pyscript.ffi import create_proxy

OWNER = "Willianjesusdasilva"
REPO = "willianjesusdasilva.github.io"
BRANCH = "master"
IDEAS_DIR = "ideas"

ideas = []
selected_status = "todos"
proxies = []


def qs(selector):
    return document.querySelector(selector)


def parse_document(text):
    source = text.lstrip("\ufeff \t\r\n")
    decoder = json.JSONDecoder()

    try:
        metadata, end = decoder.raw_decode(source)
        if not isinstance(metadata, dict):
            raise ValueError("O JSON inicial precisa ser um objeto.")
        markdown = source[end:].lstrip("\r\n")
    except Exception:
        metadata = {}
        markdown = source

    return metadata, markdown


def normalize(value):
    return str(value or "").casefold().strip()


def idea_slug(file_name):
    return file_name[:-3] if file_name.lower().endswith(".md") else file_name


def get_selected_idea_from_url():
    params = window.URLSearchParams.new(window.location.search)
    value = params.get("idea")
    return str(value) if value else ""


def set_selected_idea_in_url(file_name):
    params = window.URLSearchParams.new(window.location.search)
    params.set("idea", idea_slug(file_name))
    query = params.toString()
    new_url = f"{window.location.pathname}?{query}"
    window.history.replaceState(None, "", new_url)


async def load_profile():
    profile = qs("#profile")

    try:
        response = await fetch(f"https://api.github.com/users/{OWNER}")
        if not response.ok:
            raise RuntimeError(f"GitHub retornou HTTP {response.status}")

        data = await response.json()

        name = escape(str(data.get("name") or OWNER))
        bio = escape(str(data.get("bio") or ""))
        company = escape(str(data.get("company") or ""))
        avatar = escape(str(data.get("avatar_url") or ""), quote=True)
        login = escape(str(data.get("login") or OWNER))

        extra = ""
        if company:
            extra = f'<div class="profile-company">{company}</div>'

        profile.innerHTML = f"""
            <a class="avatar-wrap"
               href="https://github.com/{login}"
               target="_blank"
               rel="noreferrer">
                <img class="profile-avatar"
                     src="{avatar}"
                     alt="Foto de {name}">
                <span class="profile-online"></span>
            </a>
            <div class="profile-copy">
                <h1>{name}</h1>
                <div class="profile-login">@{login}</div>
                <p>{bio}</p>
                {extra}
            </div>
        """

    except Exception as exc:
        profile.innerHTML = f"""
            <div class="profile-copy">
                <h1>Willian Jesus da Silva</h1>
                <div class="profile-login">@{OWNER}</div>
                <p>Perfil indisponível no momento.</p>
            </div>
        """
        window.console.warn("Falha ao carregar perfil:", str(exc))


async def load_ideas():
    global ideas

    api_url = (
        f"https://api.github.com/repos/{OWNER}/{REPO}/contents/"
        f"{IDEAS_DIR}?ref={BRANCH}"
    )

    response = await fetch(api_url)
    if not response.ok:
        raise RuntimeError(
            f"Não foi possível listar /{IDEAS_DIR}. HTTP {response.status}."
        )

    files = await response.json()

    markdown_files = [
        item
        for item in files
        if item.get("type") == "file"
        and item.get("name", "").lower().endswith(".md")
    ]

    loaded = []

    for item in markdown_files:
        try:
            doc_response = await fetch(item["download_url"])
            if not doc_response.ok:
                continue

            text = await doc_response.text()
            metadata, markdown = parse_document(text)

            loaded.append({
                "file": item["name"],
                "slug": idea_slug(item["name"]),
                "path": item["path"],
                "raw_url": item["download_url"],
                "html_url": item["html_url"],
                "nome": str(metadata.get("nome") or idea_slug(item["name"])),
                "tags": [
                    str(tag)
                    for tag in metadata.get("tags", [])
                    if str(tag).strip()
                ],
                "status": str(metadata.get("status") or "sem status"),
                "markdown": markdown,
            })

        except Exception as exc:
            window.console.warn(
                "Falha ao carregar",
                item.get("name"),
                str(exc),
            )

    ideas = sorted(
        loaded,
        key=lambda idea: normalize(idea["nome"]),
    )

    render_status_filters()
    render_list()
    open_from_url()


def status_class(status):
    key = normalize(status)

    if key in {"feito", "concluido", "concluído", "implementado", "pronto"}:
        return "done"

    if key in {
        "fazendo",
        "desenvolvimento",
        "em desenvolvimento",
        "andamento",
    }:
        return "doing"

    if key in {"pausado", "arquivado", "descartado"}:
        return "paused"

    return "idea"


def render_status_filters():
    statuses = sorted(
        {idea["status"] for idea in ideas},
        key=normalize,
    )

    container = qs("#status-filters")
    container.innerHTML = ""

    options = [("todos", "Todos")] + [
        (status, status)
        for status in statuses
    ]

    for value, label in options:
        button = document.createElement("button")
        button.type = "button"
        button.className = (
            "filter-chip active"
            if value == selected_status
            else "filter-chip"
        )
        button.textContent = label
        button.dataset.status = value

        proxy = create_proxy(on_status_click)
        proxies.append(proxy)

        button.addEventListener("click", proxy)
        container.appendChild(button)


def on_status_click(event):
    global selected_status

    selected_status = str(event.currentTarget.dataset.status)

    render_status_filters()
    render_list()


def filtered_ideas():
    query = normalize(qs("#search").value)
    result = []

    for idea in ideas:
        if (
            selected_status != "todos"
            and idea["status"] != selected_status
        ):
            continue

        haystack = " ".join([
            idea["nome"],
            idea["status"],
            idea["file"],
            *idea["tags"],
        ]).casefold()

        if query and query not in haystack:
            continue

        result.append(idea)

    return result


def render_list():
    current = filtered_ideas()

    qs("#idea-count").textContent = str(len(current))

    container = qs("#idea-list")
    container.innerHTML = ""

    if not current:
        container.innerHTML = (
            '<div class="empty-list">'
            'Nenhuma ideia encontrada.'
            '</div>'
        )
        return

    active_slug = get_selected_idea_from_url()

    for idea in current:
        button = document.createElement("button")
        button.type = "button"

        button.className = (
            "idea-card active"
            if idea["slug"] == active_slug
            else "idea-card"
        )

        button.dataset.file = idea["file"]

        tags_preview = " ".join(
            f"#{escape(tag)}"
            for tag in idea["tags"][:4]
        )

        button.innerHTML = f"""
            <div class="idea-card-top">
                <span class="card-status-dot {status_class(idea['status'])}"></span>
                <span class="card-status">{escape(idea['status'])}</span>
            </div>
            <strong>{escape(idea['nome'])}</strong>
            <small>{tags_preview}</small>
        """

        proxy = create_proxy(on_idea_click)
        proxies.append(proxy)

        button.addEventListener("click", proxy)
        container.appendChild(button)


def on_idea_click(event):
    file_name = str(event.currentTarget.dataset.file)

    show_idea_by_file(
        file_name,
        update_url=True,
    )

    close_sidebar()


def show_idea_by_file(file_name, update_url=False):
    idea = next(
        (
            item
            for item in ideas
            if item["file"] == file_name
        ),
        None,
    )

    if not idea:
        return

    qs("#welcome").classList.add("hidden")
    qs("#error-state").classList.add("hidden")
    qs("#article").classList.remove("hidden")

    qs("#article-title").textContent = idea["nome"]

    status = qs("#article-status")
    status.textContent = idea["status"]
    status.className = (
        f"status-badge {status_class(idea['status'])}"
    )

    tags = qs("#article-tags")
    tags.innerHTML = "".join(
        f'<span>#{escape(tag)}</span>'
        for tag in idea["tags"]
    )

    qs("#raw-link").href = idea["html_url"]
    qs("#current-path").textContent = idea["path"]

    html = window.marked.parse(idea["markdown"])
    safe_html = window.DOMPurify.sanitize(html)

    qs("#markdown").innerHTML = safe_html

    if update_url:
        set_selected_idea_in_url(idea["file"])

    render_list()
    window.scrollTo(0, 0)


def open_from_url():
    selected_slug = get_selected_idea_from_url()

    if not selected_slug:
        return

    idea = next(
        (
            item
            for item in ideas
            if item["slug"] == selected_slug
            or item["file"] == selected_slug
        ),
        None,
    )

    if idea:
        show_idea_by_file(
            idea["file"],
            update_url=False,
        )


def show_error(message):
    qs("#welcome").classList.add("hidden")
    qs("#article").classList.add("hidden")
    qs("#error-state").classList.remove("hidden")
    qs("#error-message").textContent = str(message)

    qs("#idea-list").innerHTML = (
        '<div class="empty-list">'
        'Falha ao carregar.'
        '</div>'
    )


def toggle_sidebar(event=None):
    qs("#sidebar").classList.toggle("open")
    qs("#sidebar-backdrop").classList.toggle("visible")


def close_sidebar(event=None):
    qs("#sidebar").classList.remove("open")
    qs("#sidebar-backdrop").classList.remove("visible")


def bind_events():
    search_proxy = create_proxy(
        lambda event: render_list()
    )

    menu_proxy = create_proxy(toggle_sidebar)
    backdrop_proxy = create_proxy(close_sidebar)

    proxies.extend([
        search_proxy,
        menu_proxy,
        backdrop_proxy,
    ])

    qs("#search").addEventListener(
        "input",
        search_proxy,
    )

    qs("#menu-button").addEventListener(
        "click",
        menu_proxy,
    )

    qs("#sidebar-backdrop").addEventListener(
        "click",
        backdrop_proxy,
    )


async def main():
    bind_events()
    await load_profile()

    try:
        await load_ideas()
    except Exception as exc:
        show_error(exc)


await main()