#!/usr/bin/env python3
"""
build.py — gerador estático do blog de hgbits.
Zero dependências externas (só stdlib). Lê Markdown em content/,
escreve HTML final na raiz do blog usando templates/page.html.

Uso:
    python build.py
"""
import re
import html
import unicodedata
from pathlib import Path
from datetime import datetime, timezone
from email.utils import format_datetime

ROOT_DIR = Path(__file__).parent
CONTENT = ROOT_DIR / "content"
TEMPLATE = (ROOT_DIR / "templates" / "page.html").read_text(encoding="utf-8")

# Ajuste aqui se o domínio real do blog for diferente.
SITE_URL = "https://hgbits.github.io"
SITE_NAME = "hgbits :: notas"
SITE_DESCRIPTION = "Blog pessoal de hgbits — Linux User, Libertário e Gamedev."

MESES = ["", "jan", "fev", "mar", "abr", "mai", "jun",
         "jul", "ago", "set", "out", "nov", "dez"]

IMG_INLINE_RE = re.compile(r'!\[([^\]]*)\]\(([^)\s]+)(?:\s+"([^"]*)")?\)')
IMG_BLOCK_RE = re.compile(r'^!\[([^\]]*)\]\(([^)\s]+)(?:\s+"([^"]*)")?\)\s*$')
TABLE_SEP_RE = re.compile(r'^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$')

def resolve_src(src, root):
    """Caminhos absolutos (http, //, /, #) ficam intactos; relativos ganham o
    prefixo ROOT (\"\" na raiz, \"../\" dentro de posts/) para resolver certo
    não importa de onde a página é servida."""
    if re.match(r'^([a-zA-Z][a-zA-Z0-9+.\-]*:)?//', src) or src.startswith(("/", "#")):
        return src
    return root + src

def slugify(text):
    text = unicodedata.normalize("NFD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text).strip('-')
    return text or "tag"

def extract_images(md):
    """Extrai todas as imagens referenciadas no corpo do post (alt/src/legenda)
    para a galeria de artes. NÃO toca no parser de markdown — usa os mesmos
    regexes já compilados só pra coleta de metadado, sem alterar renderização."""
    md_no_code = re.sub(r'```.*?```', '', md, flags=re.DOTALL)
    out = []
    for m in IMG_INLINE_RE.finditer(md_no_code):
        alt, src, caption = m.group(1), m.group(2), m.group(3)
        out.append({"alt": alt, "src": src, "caption": caption or ""})
    return out

HEADING_RE = re.compile(r'<(h2|h3)>(.*?)</\1>', re.DOTALL)

def add_heading_ids(body_html):
    """Pós-processa o HTML já renderizado: dá id a cada h2/h3 e monta o
    sumário (TOC). NÃO mexe no parser de markdown — só decora a saída
    depois de pronta, igual extract_images faz para a galeria de artes."""
    toc = []
    used_slugs = set()

    def repl(m):
        level, inner = m.group(1), m.group(2)
        plain = html.unescape(re.sub(r'<[^>]+>', '', inner)).strip()
        slug = slugify(plain) or "secao"
        base, n = slug, 2
        while slug in used_slugs:
            slug = f"{base}-{n}"
            n += 1
        used_slugs.add(slug)
        toc.append((level, inner, slug))
        return f'<{level} id="{slug}">{inner}</{level}>'

    return HEADING_RE.sub(repl, body_html), toc

# ---------- front matter ----------
def parse_frontmatter(text):
    """Front matter simples 'chave: valor' entre linhas '---'. Sem libs de YAML."""
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.DOTALL)
    if not m:
        return {}, text
    raw, body = m.group(1), m.group(2)
    meta = {}
    for line in raw.splitlines():
        if ":" in line:
            key, val = line.split(":", 1)
            meta[key.strip()] = val.strip()
    return meta, body

# ---------- markdown -> html (subconjunto deliberadamente pequeno e auditável) ----------
# NADA nesta seção foi alterado.
def inline_md(text, root=""):
    text = html.escape(text, quote=False)

    def render_inline_img(m):
        alt, src, _caption = m.group(1), m.group(2), m.group(3)
        alt_safe = alt.replace('"', "&quot;")
        src_safe = resolve_src(src, root).replace('"', "&quot;")
        return f'<img src="{src_safe}" alt="{alt_safe}" loading="lazy">'

    text = IMG_INLINE_RE.sub(render_inline_img, text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    return text


def markdown_to_html(md, root=""):
    lines = md.strip("\n").split("\n")
    out = []
    i = 0
    in_list = False
    while i < len(lines):
        line = lines[i]

        # bloco de código ```
        if line.strip().startswith("```"):
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1
            out.append("<pre><code>" + html.escape("\n".join(code_lines)) + "</code></pre>")
            continue

        # imagem em bloco (sozinha na linha), com legenda opcional
        img_m = IMG_BLOCK_RE.match(line.strip())
        if img_m:
            alt, src, caption = img_m.groups()
            src_r = resolve_src(src, root).replace('"', "&quot;")
            alt_safe = html.escape(alt or "", quote=True)
            fig = f'<figure><img src="{src_r}" alt="{alt_safe}" loading="lazy">'
            if caption:
                fig += f"<figcaption>{inline_md(caption, root)}</figcaption>"
            fig += "</figure>"
            out.append(fig)
            i += 1
            continue

        # tabela em pipe: linha de cabeçalho seguida de linha separadora ---|---
        if "|" in line and i + 1 < len(lines) and TABLE_SEP_RE.match(lines[i + 1]):
            header_cells = [c.strip() for c in line.strip().strip("|").split("|")]
            sep_cells = [c.strip() for c in lines[i + 1].strip().strip("|").split("|")]
            aligns = []
            for c in sep_cells:
                left, right = c.startswith(":"), c.endswith(":")
                aligns.append("center" if left and right else "right" if right else "left" if left else "")
            i += 2
            rows = []
            while i < len(lines) and lines[i].strip() and "|" in lines[i]:
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1

            def cell(tag, value, align):
                style = f' style="text-align:{align}"' if align else ""
                return f"<{tag}{style}>{inline_md(value, root)}</{tag}>"

            thead = "<tr>" + "".join(
                cell("th", c, aligns[j] if j < len(aligns) else "")
                for j, c in enumerate(header_cells)
            ) + "</tr>"
            tbody = "".join(
                "<tr>" + "".join(
                    cell("td", c, aligns[j] if j < len(aligns) else "")
                    for j, c in enumerate(row)
                ) + "</tr>"
                for row in rows
            )
            out.append(f'<div class="table-wrap"><table><thead>{thead}</thead><tbody>{tbody}</tbody></table></div>')
            continue

        # cabeçalhos
        if line.startswith("## "):
            out.append(f"<h2>{inline_md(line[3:], root)}</h2>")
            i += 1
            continue
        if line.startswith("### "):
            out.append(f"<h3>{inline_md(line[4:], root)}</h3>")
            i += 1
            continue

        # citação
        if line.startswith("> "):
            quote_lines = []
            while i < len(lines) and lines[i].startswith("> "):
                quote_lines.append(lines[i][2:])
                i += 1
            out.append(f"<blockquote><p>{inline_md(' '.join(quote_lines), root)}</p></blockquote>")
            continue

        # lista
        if line.startswith("- "):
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{inline_md(line[2:], root)}</li>")
            i += 1
            continue
        else:
            if in_list:
                out.append("</ul>")
                in_list = False

        # linha em branco
        if not line.strip():
            i += 1
            continue

        # parágrafo (junta linhas seguidas até linha em branco)
        para_lines = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not lines[i].startswith(
            ("## ", "### ", "> ", "- ", "```")
        ):
            para_lines.append(lines[i])
            i += 1
        out.append(f"<p>{inline_md(' '.join(para_lines), root)}</p>")

    if in_list:
        out.append("</ul>")
    return "\n".join(out)


def format_date(iso):
    try:
        d = datetime.strptime(iso, "%Y-%m-%d")
        return f"{d.day:02d} {MESES[d.month]} {d.year}"
    except Exception:
        return iso


def reading_time(text):
    words = len(text.split())
    return max(1, round(words / 200))


def render(template, **kwargs):
    out = template
    for key, val in kwargs.items():
        out = out.replace("{{" + key + "}}", val)
    return out

def tag_link(tag, root=""):
    slug = slugify(tag)
    return f'<a class="tag" href="{root}tags/{slug}.html">{html.escape(tag.strip())}</a>'

def tag_pills(tags, root=""):
    return " · ".join(tag_link(t, root) for t in tags)

def render_post_list(posts_list, root=""):
    items = []
    for post in posts_list:
        adult_badge = (
            '<span class="adult-badge" aria-label="Conteúdo para maiores de 18 anos">+18</span>'
            if post["classification"] in {"18+", "adult", "adulto"} else ""
        )
        items.append(f'''      <li data-search="{html.escape((post["title"] + " " + post["excerpt"] + " " + " ".join(post["tags"])).lower(), quote=True)}">
        <div><a href="{root}posts/{post["slug"]}.html">{html.escape(post["title"])}</a> {adult_badge}</div>
        <p class="meta">{format_date(post["date"])} &middot; {post["reading"]} min de leitura {tag_pills(post["tags"], root)}</p>
        <p class="excerpt">{html.escape(post["excerpt"])}</p>
      </li>''')
    return "\n".join(items)

def head_extra(canonical, og_type, og_title, og_description):
    """Bloco de <head> com canonical + Open Graph + Twitter Card.
    Tudo escapado — mesmo tratamento que TITLE/DESCRIPTION já recebiam."""
    c = html.escape(canonical, quote=True)
    t = html.escape(og_title, quote=True)
    d = html.escape(og_description, quote=True)
    ty = html.escape(og_type, quote=True)
    return f'''<link rel="canonical" href="{c}">
<link rel="alternate" type="application/rss+xml" title="{html.escape(SITE_NAME, quote=True)}" href="{{{{ROOT}}}}feed.xml">
<meta property="og:type" content="{ty}">
<meta property="og:site_name" content="{html.escape(SITE_NAME, quote=True)}">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:url" content="{c}">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{t}">
<meta name="twitter:description" content="{d}">'''


def build_rss(posts):
    items = []
    for p in posts:
        try:
            dt = datetime.strptime(p["date"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except Exception:
            dt = datetime.now(timezone.utc)
        link = f'{SITE_URL}/posts/{p["slug"]}.html'
        items.append(f'''    <item>
      <title>{html.escape(p["title"], quote=True)}</title>
      <link>{link}</link>
      <guid>{link}</guid>
      <pubDate>{format_datetime(dt)}</pubDate>
      <description>{html.escape(p["excerpt"], quote=True)}</description>
    </item>''')
    now = format_datetime(datetime.now(timezone.utc))
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>{html.escape(SITE_NAME, quote=True)}</title>
    <link>{SITE_URL}/</link>
    <description>{html.escape(SITE_DESCRIPTION, quote=True)}</description>
    <lastBuildDate>{now}</lastBuildDate>
{chr(10).join(items)}
  </channel>
</rss>
'''

def build_sitemap(posts, tag_map):
    today = datetime.now().strftime("%Y-%m-%d")
    urls = [(f"{SITE_URL}/", today), (f"{SITE_URL}/sobre.html", today), (f"{SITE_URL}/artes.html", today)]
    urls += [(f'{SITE_URL}/posts/{p["slug"]}.html', p["date"] or today) for p in posts]
    urls += [(f'{SITE_URL}/tags/{slugify(t)}.html', today) for t in tag_map]
    entries = "\n".join(f'''  <url>
    <loc>{u}</loc>
    <lastmod>{lastmod}</lastmod>
  </url>''' for u, lastmod in urls)
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{entries}
</urlset>
'''

def main():
    posts = []
    (CONTENT / "posts").mkdir(parents=True, exist_ok=True)
    (ROOT_DIR / "posts").mkdir(parents=True, exist_ok=True)
    for md_file in sorted((CONTENT / "posts").glob("*.md")):
        raw = md_file.read_text(encoding="utf-8")
        meta, body = parse_frontmatter(raw)
        tags = [t.strip() for t in meta.get("tags", "").split(",") if t.strip()]
        raw_body_html = markdown_to_html(body, root="../")
        body_html, toc = add_heading_ids(raw_body_html)
        posts.append({
            "slug": md_file.stem,
            "title": meta.get("title", md_file.stem),
            "date": meta.get("date", ""),
            "excerpt": meta.get("excerpt", ""),
            "classification": meta.get("classification", "").strip().strip('"\'').lower(),
            "tags": tags,
            "images": extract_images(body),
            "body_html": body_html,
            "toc": toc,
            "reading": reading_time(body),
        })
    posts.sort(key=lambda p: p["date"], reverse=True)

    # ---------- gera cada post ----------
    for idx, post in enumerate(posts):
        prev_p = posts[idx + 1] if idx + 1 < len(posts) else None
        next_p = posts[idx - 1] if idx > 0 else None
        prev_link = (f'<a href="{prev_p["slug"]}.html" rel="prev">&larr; {html.escape(prev_p["title"])}</a>'
                     if prev_p else '<span></span>')
        next_link = (f'<a href="{next_p["slug"]}.html" rel="next">{html.escape(next_p["title"])} &rarr;</a>'
                     if next_p else '<span></span>')

        toc_html = ""
        if len(post["toc"]) >= 2:
            toc_items = "\n".join(
                f'          <li class="toc-{level}"><a href="#{slug}">{text}</a></li>'
                for level, text, slug in post["toc"]
            )
            toc_html = f'''
      <div class="toc">
        <input type="checkbox" id="toc-toggle" class="toc-checkbox">
        <label for="toc-toggle" class="toc-button">Sumário</label>
        <nav class="toc-panel" aria-label="sumário do post">
          <ul>
{toc_items}
          </ul>
        </nav>
      </div>'''

        body = f'''    <article class="article-wrap">
      <header class="post-header">
        <h1>{html.escape(post["title"])}</h1>
        <p class="byline">{format_date(post["date"])} &middot; {post["reading"]} min de leitura</p>
        <p class="tags">{tag_pills(post["tags"], root="../")}</p>
      </header>
{toc_html}
      <div id="post-content">
{post["body_html"]}
      </div>

      <section class="giscus-wrap" aria-label="comentários">
        <script src="https://giscus.app/client.js"
                data-repo="HGBits/hgbits.github.io"
                data-repo-id="R_kgDOTQ92dw"
                data-category="Comentários"
                data-category-id="DIC_kwDOTQ92d84DGItE"
                data-mapping="pathname"
                data-strict="0"
                data-reactions-enabled="1"
                data-emit-metadata="0"
                data-input-position="bottom"
                data-theme="noborder_dark"
                data-lang="pt"
                crossorigin="anonymous"
                async>
        </script>
      </section>

      <nav class="post-nav" aria-label="navegação entre posts">
        {prev_link}
        {next_link}
      </nav>
    </article>'''

        if post["classification"] in {"18+", "adult", "adulto"}:
            body = f'''<section class="age-gate" data-age-gate>
      <div class="age-gate-prompt" data-age-prompt role="region" aria-labelledby="age-gate-title">
        <p class="age-gate-label">conteúdo restrito</p>
        <h1 id="age-gate-title">Você é maior de 18 anos?</h1>
        <p>Esta publicação contém conteúdo destinado a adultos. Confirme sua idade para continuar.</p>
        <div class="age-gate-actions">
          <button class="age-gate-button age-gate-yes" type="button" data-age-yes>Sim, sou maior de 18 anos</button>
          <button class="age-gate-button age-gate-no" type="button" data-age-no>Não</button>
        </div>
      </div>
      <div class="age-gate-denied" data-age-denied role="status" hidden>
        <h1>Acesso não autorizado</h1>
        <p>O conteúdo permanece oculto porque você informou que não é maior de 18 anos.</p>
        <a href="../index.html">Voltar ao início</a>
      </div>
      <div class="age-gate-content" data-age-content hidden>
${body}
      </div>
    </section>'''

        canonical = f'{SITE_URL}/posts/{post["slug"]}.html'
        html_out = render(
            TEMPLATE,
            TITLE=html.escape(f'{post["title"]} :: hgbits', quote=True),
            DESCRIPTION=html.escape(post["excerpt"], quote=True),
            HEAD_EXTRA=head_extra(canonical, "article", post["title"], post["excerpt"]),
            YEAR=str(datetime.now().year),
            ROOT="../",
            BODY=body,
        )
        (ROOT_DIR / "posts" / f'{post["slug"]}.html').write_text(html_out, encoding="utf-8")

    # ---------- gera lista de tags ----------
    tag_map = {}
    for post in posts:
        for t in post["tags"]:
            tag_map.setdefault(t, []).append(post)

    # ---------- arquivo por ano e mês ----------
    year_map = {}
    for post in posts:
        date = post["date"]
        year = date[:4] if date[:4].isdigit() else "sem data"
        try:
            month = datetime.strptime(date, "%Y-%m-%d").month
        except ValueError:
            month = 0
        year_map.setdefault(year, {}).setdefault(month, []).append(post)

    posts_items = render_post_list(posts, root="")

    tags_items = "\n".join(f'''      <li>
        {tag_link(tag)}
        <ul class="taglist-posts">
{chr(10).join(f'          <li><a href="posts/{p["slug"]}.html">{html.escape(p["title"])}</a></li>' for p in plist)}
        </ul>
      </li>''' for tag, plist in tag_map.items())

    tag_cloud = " ".join(tag_link(t) for t in sorted(tag_map.keys()))

    month_names = {
        1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril",
        5: "maio", 6: "junho", 7: "julho", 8: "agosto",
        9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro",
        0: "sem mês",
    }
    years_sorted = sorted((y for y in year_map if y != "sem data"), reverse=True)
    if "sem data" in year_map:
        years_sorted.append("sem data")

    archive_years = []
    for year in years_sorted:
        month_groups = []
        for month in sorted(year_map[year], reverse=True):
            month_posts = year_map[year][month]
            links = "\n".join(
                f'              <li><a href="posts/{post["slug"]}.html">{html.escape(post["title"])}</a></li>'
                for post in month_posts
            )
            month_groups.append(f'''          <section class="archive-month">
            <h3 class="archive-month-title">{month_names[month]}</h3>
            <ul class="taglist-posts">
{links}
            </ul>
          </section>''')
        archive_years.append(f'''      <li class="archive-year">
        <span class="tag">{html.escape(year)}</span>
        <div class="archive-months">
{chr(10).join(month_groups)}
        </div>
      </li>''')

    anos_items = "\n".join(archive_years)

    index_body = f'''    <div class="layout-grid">
      <div class="layout-main">
        <section class="hero">
          <h1>notas de hgbits</h1>
          <p class="tagline">Linux User, Libertário e Gamedev.</p>
        </section>

        <div class="tabs">
          <input type="radio" name="tabs" id="tab-posts" checked>
          <input type="radio" name="tabs" id="tab-tags">
          <input type="radio" name="tabs" id="tab-anos">
          <div class="tab-labels">
            <label for="tab-posts">Posts</label>
            <label for="tab-tags">Tags</label>
            <label for="tab-anos">Anos</label>
          </div>
          <div class="tab-panels">
            <section class="tab-panel panel-posts">
              <ul class="postlist">
{posts_items}
              </ul>
            </section>
            <section class="tab-panel panel-tags">
              <ul class="taglist">
{tags_items}
              </ul>
            </section>
            <section class="tab-panel panel-anos">
              <ul class="taglist">
{anos_items}
              </ul>
            </section>
          </div>
        </div>

        <p class="colophon">{len(posts)} posts &middot; gerado por build.py a partir de Markdown, sem CDN</p>
      </div>

      <aside class="sidebar">
        <div class="sidebar-card">
          <div class="sidebar-avatar">
            <img src="assets/avatar.jpg" alt="Foto de hgbits" width="44" height="44" loading="lazy">
          </div>
          <p class="sidebar-mark">hgbits</p>
          <p>{html.escape(SITE_DESCRIPTION)}</p>
          <a href="sobre.html">saiba mais &rarr;</a>
        </div>
        <div class="sidebar-card">
          <h2>tags</h2>
          <div class="tag-cloud">{tag_cloud}</div>
        </div>
      </aside>
    </div>'''

    index_html = render(
        TEMPLATE,
        TITLE=SITE_NAME,
        DESCRIPTION=html.escape(SITE_DESCRIPTION, quote=True),
        HEAD_EXTRA=head_extra(f"{SITE_URL}/", "website", SITE_NAME, SITE_DESCRIPTION),
        YEAR=str(datetime.now().year),
        ROOT="",
        BODY=index_body,
    )
    (ROOT_DIR / "index.html").write_text(index_html, encoding="utf-8")

    # ---------- sobre.html ----------
    sobre_raw = (CONTENT / "sobre.md").read_text(encoding="utf-8")
    meta, body = parse_frontmatter(sobre_raw)
    sobre_title = meta.get("title", "sobre")
    sobre_body = f'''    <article class="article-wrap">
      <h1>{html.escape(sobre_title)}</h1>

{markdown_to_html(body)}
    </article>'''
    sobre_html = render(
        TEMPLATE,
        TITLE="sobre :: hgbits",
        DESCRIPTION="Sobre hgbits.",
        HEAD_EXTRA=head_extra(f"{SITE_URL}/sobre.html", "website", sobre_title, "Sobre hgbits."),
        YEAR=str(datetime.now().year),
        ROOT="",
        BODY=sobre_body,
    )
    (ROOT_DIR / "sobre.html").write_text(sobre_html, encoding="utf-8")

    # ---------- galeria de artes ----------
    arte_items = []
    for post in posts:
        for img in post["images"]:
            src_r = resolve_src(img["src"], "").replace('"', "&quot;")
            alt_safe = html.escape(img["alt"] or "", quote=True)
            cap = img["caption"] or img["alt"] or ""
            arte_items.append(f'''      <figure class="art-card">
        <a href="posts/{post["slug"]}.html">
          <img src="{src_r}" alt="{alt_safe}" loading="lazy">
        </a>
        <figcaption>
          {html.escape(cap)}<br>
          <a href="posts/{post["slug"]}.html">{html.escape(post["title"])}</a>
        </figcaption>
      </figure>''')

    artes_body = f'''    <article class="article-wrap">
      <h1>artes</h1>
      <p class="tagline">Todas as imagens usadas nos posts, num só lugar.</p>
      <div class="art-grid">
{chr(10).join(arte_items) if arte_items else "        <p>Nenhuma imagem publicada ainda.</p>"}
      </div>
    </article>'''

    artes_html = render(
        TEMPLATE,
        TITLE="artes :: hgbits",
        DESCRIPTION="Galeria de imagens usadas nos posts de hgbits.",
        HEAD_EXTRA=head_extra(f"{SITE_URL}/artes.html", "website", "artes", "Galeria de imagens dos posts."),
        YEAR=str(datetime.now().year),
        ROOT="",
        BODY=artes_body,
    )
    (ROOT_DIR / "artes.html").write_text(artes_html, encoding="utf-8")

    # ---------- páginas por tag ----------
    (ROOT_DIR / "tags").mkdir(parents=True, exist_ok=True)
    for tag, plist in tag_map.items():
        slug = slugify(tag)
        n = len(plist)
        tag_body = f'''    <article class="article-wrap">
      <h1>tag: {html.escape(tag)}</h1>
      <p class="tagline">{n} post{"s" if n != 1 else ""} com essa tag.</p>
      <ul class="postlist">
{render_post_list(plist, root="../")}
      </ul>
      <p class="colophon"><a href="../index.html">&larr; voltar pra todos os posts</a></p>
    </article>'''
        tag_html_out = render(
            TEMPLATE,
            TITLE=html.escape(f'tag: {tag} :: hgbits', quote=True),
            DESCRIPTION=html.escape(f'Posts marcados com a tag {tag}.', quote=True),
            HEAD_EXTRA=head_extra(f"{SITE_URL}/tags/{slug}.html", "website", f"tag: {tag}", f"Posts marcados com a tag {tag}."),
            YEAR=str(datetime.now().year),
            ROOT="../",
            BODY=tag_body,
        )
        (ROOT_DIR / "tags" / f"{slug}.html").write_text(tag_html_out, encoding="utf-8")

    # ---------- feed.xml + sitemap.xml ----------
    (ROOT_DIR / "feed.xml").write_text(build_rss(posts), encoding="utf-8")
    (ROOT_DIR / "sitemap.xml").write_text(build_sitemap(posts, tag_map), encoding="utf-8")

    print(f"OK: {len(posts)} posts, {len(tag_map)} tags, index.html, sobre.html, "
          f"artes.html, {len(tag_map)} páginas de tag, feed.xml e sitemap.xml gerados.")

if __name__ == "__main__":
    main()
