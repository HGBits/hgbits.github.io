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


def tag_pills(tags):
    return " · ".join(f'<span class="tag">{html.escape(t.strip())}</span>' for t in tags)


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


def build_sitemap(posts):
    today = datetime.now().strftime("%Y-%m-%d")
    urls = [(f"{SITE_URL}/", today), (f"{SITE_URL}/sobre.html", today)]
    urls += [(f'{SITE_URL}/posts/{p["slug"]}.html', p["date"] or today) for p in posts]
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
        posts.append({
            "slug": md_file.stem,
            "title": meta.get("title", md_file.stem),
            "date": meta.get("date", ""),
            "excerpt": meta.get("excerpt", ""),
            "tags": tags,
            "body_html": markdown_to_html(body, root="../"),
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

        body = f'''    <article class="article-wrap">
      <header class="post-header">
        <h1>{html.escape(post["title"])}</h1>
        <p class="byline">{format_date(post["date"])} &middot; {post["reading"]} min de leitura</p>
        <p class="tags">{tag_pills(post["tags"])}</p>
      </header>

{post["body_html"]}

      <nav class="post-nav" aria-label="navegação entre posts">
        {prev_link}
        {next_link}
      </nav>
    </article>'''

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

    posts_items = "\n".join(f'''      <li data-search="{html.escape((p["title"] + " " + p["excerpt"] + " " + " ".join(p["tags"])).lower(), quote=True)}">
        <div><a href="posts/{p["slug"]}.html">{html.escape(p["title"])}</a></div>
        <p class="meta">{format_date(p["date"])} &middot; {p["reading"]} min de leitura {tag_pills(p["tags"])}</p>
        <p class="excerpt">{html.escape(p["excerpt"])}</p>
      </li>''' for p in posts)

    tags_items = "\n".join(f'''      <li>
        <span class="tag">{html.escape(tag)}</span>
        <ul class="taglist-posts">
{chr(10).join(f'          <li><a href="posts/{p["slug"]}.html">{html.escape(p["title"])}</a></li>' for p in plist)}
        </ul>
      </li>''' for tag, plist in tag_map.items())

    tag_cloud = " ".join(f'<span class="tag">{html.escape(t)}</span>' for t in sorted(tag_map.keys()))

    index_body = f'''    <div class="layout-grid">
      <div class="layout-main">
        <section class="hero">
          <h1>notas de hgbits</h1>
          <p class="tagline">Linux User, Libertário e Gamedev.</p>
        </section>

        <div class="tabs">
          <input type="radio" name="tabs" id="tab-posts" checked>
          <input type="radio" name="tabs" id="tab-tags">
          <div class="tab-labels">
            <label for="tab-posts">Posts</label>
            <label for="tab-tags">Tags</label>
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

    # ---------- feed.xml + sitemap.xml ----------
    (ROOT_DIR / "feed.xml").write_text(build_rss(posts), encoding="utf-8")
    (ROOT_DIR / "sitemap.xml").write_text(build_sitemap(posts), encoding="utf-8")

    print(f"OK: {len(posts)} posts, {len(tag_map)} tags, index.html, sobre.html, feed.xml e sitemap.xml gerados.")


if __name__ == "__main__":
    main()
