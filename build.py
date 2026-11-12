#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 hgbits <https://github.com/HGBits>
"""
build.py — gerador estático do blog de hgbits.
Zero dependências externas (só stdlib). Lê Markdown em content/,
escreve o site final em _site/ usando templates/page.html.

Uso:
    python build.py
"""
import re
import html
import posixpath
import shutil
import unicodedata
from urllib.parse import unquote
from pathlib import Path
from datetime import datetime, timezone
from email.utils import format_datetime

ROOT_DIR = Path(__file__).parent
CONTENT = ROOT_DIR / "content"

# Tudo que o build gera vai para OUT_DIR, e SÓ OUT_DIR é publicado (ver
# .github/workflows/build.yml). Arquivos do repositório que não estiverem em
# PUBLIC_COPY nunca chegam ao servidor (content/, build.py, templates/, etc.).
OUT_DIR = ROOT_DIR / "_site"
PUBLIC_COPY = ["css", "js", "assets", "favicon.svg"]
TEMPLATE = (ROOT_DIR / "templates" / "page.html").read_text(encoding="utf-8")

# Ajuste aqui se o domínio real do blog for diferente.
SITE_URL = "https://hgbits.github.io"
SITE_NAME = "hgbits :: notas"
SITE_DESCRIPTION = "Blog pessoal de hgbits — Linux User, Libertário e Gamedev."

MESES = ["", "jan", "fev", "mar", "abr", "mai", "jun",
         "jul", "ago", "set", "out", "nov", "dez"]

IMG_INLINE_RE = re.compile(r'!\[([^\]]*)\]\(([^)\s]+)(?:\s+"([^"]*)")?\)')
IMG_BLOCK_RE = re.compile(r'^!\[([^\]]*)\]\(([^)\s]+)(?:\s+"([^"]*)")?\)\s*$')
# Capa de post: SOMENTE a imagem com alt exatamente "Capa do Post", sozinha na linha.
# Qualquer outra imagem do corpo não é capa.
COVER_RE = re.compile(r'^!\[Capa do Post\]\(([^)\s]+)(?:\s+"[^"]*")?\)\s*$', re.MULTILINE)
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
        # Uma pasta (ex.: "assets/") é um marcador de posição, não uma imagem.
        if not src.strip() or src.rstrip().endswith("/"):
            continue
        out.append({"alt": alt, "src": src, "caption": caption or ""})
    return out

def extract_cover(md):
    """Retorna o src da capa do post (![Capa do Post](...)) ou \"\" se não houver.
    Ignora blocos de código e só considera a primeira ocorrência."""
    md_no_code = re.sub(r'```.*?```', '', md, flags=re.DOTALL)
    m = COVER_RE.search(md_no_code)
    if not m:
        return ""
    src = m.group(1).strip()
    # Permite manter a marcação preparada sem criar uma imagem quebrada.
    return "" if not src or src.endswith("/") else src

def is_adult_post(post):
    return post["classification"] in {"18+", "adult"}


def is_teen_post(post):
    """Aceita as grafias +14 (preferida), 14+ e o alias teen."""
    return post["classification"] in {"+14", "14+", "teen"}

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
# Renderização de imagens e identificação de licenças.
IMAGE_LICENSES = {
    "cc by 4.0": ("CC BY 4.0", "https://creativecommons.org/licenses/by/4.0/"),
    "cc-by-4.0": ("CC BY 4.0", "https://creativecommons.org/licenses/by/4.0/"),
    "cc by-sa 4.0": ("CC BY-SA 4.0", "https://creativecommons.org/licenses/by-sa/4.0/"),
    "cc-by-sa-4.0": ("CC BY-SA 4.0", "https://creativecommons.org/licenses/by-sa/4.0/"),
    "cc by-nc 4.0": ("CC BY-NC 4.0", "https://creativecommons.org/licenses/by-nc/4.0/"),
    "cc-by-nc-4.0": ("CC BY-NC 4.0", "https://creativecommons.org/licenses/by-nc/4.0/"),
    "cc0 1.0": ("CC0 1.0", "https://creativecommons.org/publicdomain/zero/1.0/"),
    "cc0-1.0": ("CC0 1.0", "https://creativecommons.org/publicdomain/zero/1.0/"),
    "gpl-3.0": ("GPL-3.0", "https://www.gnu.org/licenses/gpl-3.0.html"),
}

def image_license_html(title, root=""):
    """Converte títulos reconhecidos em identificação visível e link da licença."""
    if not title:
        return ""
    key = re.sub(r"\s+", " ", title.strip()).lower()
    license_info = IMAGE_LICENSES.get(key)
    if not license_info:
        return ""
    label, url = license_info
    return (f'<span class="image-license">Licença: '
            f'<a href="{url}" rel="license noopener" target="_blank">{label}</a></span>')


def inline_md(text, root=""):
    text = html.escape(text, quote=False)

    def render_inline_img(m):
        alt, src, title = m.group(1), m.group(2), m.group(3)
        alt_safe = alt.replace('"', "&quot;")
        src_safe = resolve_src(src, root).replace('"', "&quot;")
        license_html = image_license_html(title, root)
        image = f'<img src="{src_safe}" alt="{alt_safe}" loading="lazy">'
        return f'<span class="inline-image">{image}{license_html}</span>' if license_html else image

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
            # Ignora marcadores de capa ainda sem arquivo associado.
            if not src.strip() or src.rstrip().endswith("/"):
                i += 1
                continue
            src_r = resolve_src(src, root).replace('"', "&quot;")
            alt_safe = html.escape(alt or "", quote=True)
            fig = f'<figure><img src="{src_r}" alt="{alt_safe}" loading="lazy">'
            license_html = image_license_html(caption, root)
            if license_html:
                fig += f"<figcaption>{license_html}</figcaption>"
            elif caption:
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
        if post["classification"] in {"18+", "adult"}:
            classification_badge = '<span class="adult-badge" aria-label="Classificação indicativa: 18 anos ou mais">+18</span>'
        elif is_teen_post(post):
            classification_badge = '<span class="teen-badge" aria-label="Classificação indicativa: 14 anos ou mais">+14</span>'
        else:
            classification_badge = ""
        # Capas são prévias visuais independentes da classificação do conteúdo.
        cover_html = ""
        if post["cover"]:
            cover_src = html.escape(resolve_src(post["cover"], root), quote=True)
            cover_alt = html.escape(f'Capa de {post["title"]}', quote=True)
            cover_html = (f'<a class="post-cover" href="{root}posts/{post["slug"]}.html" tabindex="-1" aria-hidden="true">'
                          f'<img src="{cover_src}" alt="{cover_alt}" loading="lazy"></a>\n        ')
        items.append(f'''      <li data-search="{html.escape((post["title"] + " " + post["excerpt"] + " " + " ".join(post["tags"])).lower(), quote=True)}">
        {cover_html}<div><a href="{root}posts/{post["slug"]}.html">{html.escape(post["title"])}</a> {classification_badge}</div>
        <p class="meta">{format_date(post["date"])} &middot; {post["reading"]} min de leitura {tag_pills(post["tags"], root)}</p>
        <p class="excerpt">{html.escape(post["excerpt"])}</p>
      </li>''')
    return "\n".join(items)

def head_extra(canonical, og_type, og_title, og_description, og_image=""):
    """Bloco de <head> com canonical + Open Graph + Twitter Card.
    Tudo escapado — mesmo tratamento que TITLE/DESCRIPTION já recebiam."""
    c = html.escape(canonical, quote=True)
    t = html.escape(og_title, quote=True)
    d = html.escape(og_description, quote=True)
    ty = html.escape(og_type, quote=True)
    img_meta = ""
    card = "summary"
    if og_image:
        img = html.escape(og_image, quote=True)
        img_meta = (f'\n<meta property="og:image" content="{img}">'
                    f'\n<meta name="twitter:image" content="{img}">')
        card = "summary_large_image"
    return f'''<link rel="canonical" href="{c}">
<link rel="alternate" type="application/rss+xml" title="{html.escape(SITE_NAME, quote=True)}" href="{{{{ROOT}}}}feed.xml">
<meta property="og:type" content="{ty}">
<meta property="og:site_name" content="{html.escape(SITE_NAME, quote=True)}">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:url" content="{c}">{img_meta}
<meta name="twitter:card" content="{card}">
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
    urls = [(f"{SITE_URL}/", today), (f"{SITE_URL}/sobre.html", today), (f"{SITE_URL}/termos.html", today), (f"{SITE_URL}/privacidade.html", today), (f"{SITE_URL}/artes.html", today)]
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

def asset_key(src):
    """Caminho relativo normalizado de uma imagem local; None se for URL/absoluto."""
    src = unquote(src.strip())
    if not src or src.startswith(("/", "#")) or re.match(r"^[a-zA-Z][a-zA-Z0-9+.\-]*:", src):
        return None
    return posixpath.normpath(src)

def find_restricted_assets(posts):
    """Imagens usadas SOMENTE no corpo de posts 18+ (não-capa). Não são publicadas."""
    restricted, public = set(), set()
    for post in posts:
        for img in post["images"]:
            key = asset_key(img["src"])
            if key is None:
                continue
            if is_adult_post(post) and img["alt"] != "Capa do Post":
                restricted.add(key)
            else:
                public.add(key)
    return restricted - public

def copy_public_files():
    """Copia para OUT_DIR somente a lista explícita PUBLIC_COPY."""
    for name in PUBLIC_COPY:
        src = ROOT_DIR / name
        dst = OUT_DIR / name
        if src.is_dir():
            shutil.copytree(src, dst)
        elif src.is_file():
            shutil.copy2(src, dst)
        else:
            print(f"AVISO: {name} está em PUBLIC_COPY mas não existe.")
    (OUT_DIR / ".nojekyll").touch()

def main():
    posts = []
    (CONTENT / "posts").mkdir(parents=True, exist_ok=True)
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir()
    (OUT_DIR / "posts").mkdir()
    for md_file in sorted((CONTENT / "posts").glob("*.md")):
        raw = md_file.read_text(encoding="utf-8")
        meta, body = parse_frontmatter(raw)
        tags = [t.strip() for t in meta.get("tags", "").split(",") if t.strip()]
        classification = meta.get("classification", "").strip().strip('"\'').lower()
        adult = classification in {"18+", "adult"}
        raw_body_html = markdown_to_html(body, root="../")
        body_html, toc = add_heading_ids(raw_body_html)
        posts.append({
            "slug": md_file.stem,
            "title": meta.get("title", md_file.stem),
            "date": meta.get("date", ""),
            "updated": meta.get("updated", "").strip().strip('"\''),
            "excerpt": meta.get("excerpt", ""),
            "classification": classification,
            "tags": tags,
            "images": extract_images(body),
            "cover": extract_cover(body),
            "body_html": body_html,
            "toc": toc,
            "reading": reading_time(body),
        })
    posts.sort(key=lambda p: p["date"], reverse=True)

    # ---------- gera cada post ----------
    for idx, post in enumerate(posts):
        prev_p = posts[idx + 1] if idx + 1 < len(posts) else None
        next_p = posts[idx - 1] if idx > 0 else None
        def nav_card(target, direction):
            if not target:
                return '<span class="post-nav-empty" aria-hidden="true"></span>'
            cover_html = ""
            if target["cover"]:
                cover_src = html.escape(resolve_src(target["cover"], "../"), quote=True)
                cover_alt = html.escape(f'Capa de {target["title"]}', quote=True)
                cover_html = f'<img src="{cover_src}" alt="{cover_alt}" loading="lazy">'
            label = "Post anterior" if direction == "prev" else "Próximo post"
            arrow = "&larr;" if direction == "prev" else "&rarr;"
            return (f'<a class="post-nav-card post-nav-{direction}" href="{target["slug"]}.html" rel="{direction}">'
                    f'{cover_html}<span class="post-nav-label">{label} {arrow}</span>'
                    f'<span class="post-nav-title">{html.escape(target["title"])}</span></a>')

        prev_link = nav_card(prev_p, "prev")
        next_link = nav_card(next_p, "next")

        toc_html = ""
        if len(post["toc"]) >= 2:
            toc_items = "\\n".join(
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

        # [[TOC]] posiciona o sumário no ponto escolhido pelo autor.
        # Sem marcador, mantém o comportamento atual: sumário após o cabeçalho.
        toc_marker = re.compile(r'<p>\s*\[\[TOC\]\]\s*</p>')
        if toc_html and toc_marker.search(post["body_html"]):
            post["body_html"] = toc_marker.sub(toc_html, post["body_html"], count=1)
            toc_html = ""
        elif not toc_html:
            post["body_html"] = toc_marker.sub("", post["body_html"])

        teen_badge = (
            ' <span class="teen-badge" aria-label="Classificação indicativa: 14 anos ou mais">+14</span>'
            if is_teen_post(post) else ""
        )
        body = f'''    <article class="article-wrap">
      <header class="post-header">
        <h1>{html.escape(post["title"])}{teen_badge}</h1>
        <p class="byline">Publicado em: {format_date(post["date"])}{f' &middot; Atualizado em: {format_date(post["updated"])}' if post["updated"] else ''} &middot; {post["reading"]} min de leitura</p>
        <p class="tags">{tag_pills(post["tags"], root="../")}</p>
      </header>
{toc_html}
      <div id="post-content">
{post["body_html"]}
      </div>

      <section class="share-wrap" data-share aria-label="compartilhar publicação">
        <button class="share-toggle" type="button" aria-expanded="false" aria-controls="share-options">
          ↗ Compartilhar publicação
        </button>
        <div class="share-options" id="share-options" hidden>
          <button type="button" data-share-native hidden>Compartilhar...</button>
          <a data-share-mastodon target="_blank" rel="noopener noreferrer">Mastodon</a>
          <a data-share-telegram target="_blank" rel="noopener noreferrer">Telegram</a>
          <a data-share-x target="_blank" rel="noopener noreferrer">X</a>
          <a data-share-email>E-mail</a>
        </div>
        <p class="share-status" data-share-status role="status" aria-live="polite"></p>
      </section>

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

        if is_adult_post(post):
            restricted_dir = OUT_DIR / "restricted"
            restricted_dir.mkdir(exist_ok=True)
            (restricted_dir / f'{post["slug"]}.html').write_text(
                post["body_html"], encoding="utf-8"
            )
            body = f'''    <article class="article-wrap">
      <header class="post-header">
        <h1>{html.escape(post["title"])} <span class="adult-badge" aria-label="Classificação indicativa: 18 anos ou mais">+18</span></h1>
        <p class="byline">Publicado em: {format_date(post["date"])}</p>
        <p class="tags">{tag_pills(post["tags"], root="../")}</p>
      </header>
      <section class="age-gate" id="post-content" data-age-gate
               data-age-content-url="../restricted/{html.escape(post["slug"], quote=True)}.html">
        <div class="age-gate-prompt" data-age-prompt>
          <p class="age-gate-label">conteúdo restrito</p>
          <h2>Esta publicação é destinada a adultos</h2>
          <p>Confirme que você tem 18 anos ou mais para carregar o conteúdo.</p>
          <div class="age-gate-actions">
            <button class="age-gate-button age-gate-yes" type="button" data-age-yes>Tenho 18 anos ou mais</button>
            <button class="age-gate-button" type="button" data-age-no>Não tenho 18 anos</button>
          </div>
        </div>
        <div class="age-gate-denied" data-age-denied hidden>
          <p class="age-gate-label">acesso recusado</p>
          <h2>O conteúdo não foi carregado</h2>
          <p>Você recusou a confirmação de maioridade.</p>
          <a href="../index.html">Voltar ao início</a>
        </div>
        <div class="age-gate-content" data-age-content hidden aria-live="polite">
          <p data-age-status role="status">Carregando publicação...</p>
          <div data-age-body></div>
          <button type="button" data-age-retry hidden>Tentar carregar novamente</button>
        </div>
      </section>

      <section class="giscus-wrap" data-age-comments hidden aria-label="comentários">
        <div data-giscus></div>
      </section>

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
            HEAD_EXTRA=head_extra(
                canonical, "article", post["title"], post["excerpt"],
                og_image=(f'{SITE_URL}/{post["cover"]}' if post["cover"]
                          and not post["cover"].startswith(("http", "/")) else "")),
            YEAR=str(datetime.now().year),
            ROOT="../",
            BODY=body,
        )
        (OUT_DIR / "posts" / f'{post["slug"]}.html').write_text(html_out, encoding="utf-8")

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
          <div class="sidebar-profile">
            <div class="sidebar-avatar">
              <img src="assets/avatar.jpg" alt="Foto de hgbits" width="44" height="44" loading="lazy">
            </div>
            <p class="sidebar-mark">hgbits</p>
          </div>
          <p>{html.escape(SITE_DESCRIPTION)}</p>
          <a href="sobre.html">saiba mais &rarr;</a>
        </div>
        <div class="sidebar-card">
          <h2>tags</h2>
          <div class="tag-cloud">{tag_cloud}</div>
        </div>
        <section class="sidebar-card classification-card" aria-labelledby="classification-title">
          <h2 id="classification-title">classificação indicativa</h2>
          <div class="classification-entry">
            <span class="adult-badge">+18</span>
            <p>Publicações com conteúdo mais pesado, que pode abordar sexo, ansiedade, coação sexual, prostituição, depressão ou violência.</p>
          </div>
          <div class="classification-entry">
            <span class="teen-badge">+14</span>
            <p>Publicações que podem conter xingamentos, bullying, medo, preconceito e insinuações sexuais leves, sem conteúdo explícito.</p>
          </div>
        </section>
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
    (OUT_DIR / "index.html").write_text(index_html, encoding="utf-8")

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
    (OUT_DIR / "sobre.html").write_text(sobre_html, encoding="utf-8")

    # ---------- termos de uso ----------
    termos_raw = (CONTENT / "termos.md").read_text(encoding="utf-8")
    termos_meta, termos_content = parse_frontmatter(termos_raw)
    termos_title = termos_meta.get("title", "termos de uso")
    termos_body = f'''    <article class="article-wrap">
      <h1>{html.escape(termos_title)}</h1>
      <p class="tagline">Condições de acesso e utilização do site.</p>

{markdown_to_html(termos_content)}
    </article>'''
    termos_html = render(
        TEMPLATE,
        TITLE="termos de uso :: hgbits",
        DESCRIPTION="Termos de uso do site hgbits.",
        HEAD_EXTRA=head_extra(f"{SITE_URL}/termos.html", "website", termos_title, "Termos de uso do site hgbits."),
        YEAR=str(datetime.now().year),
        ROOT="",
        BODY=termos_body,
    )
    (OUT_DIR / "termos.html").write_text(termos_html, encoding="utf-8")

    # ---------- política de privacidade ----------
    privacidade_raw = (CONTENT / "privacidade.md").read_text(encoding="utf-8")
    privacidade_meta, privacidade_content = parse_frontmatter(privacidade_raw)
    privacidade_title = privacidade_meta.get("title", "política de privacidade")
    privacidade_body = f'''    <article class="article-wrap">
      <h1>{html.escape(privacidade_title)}</h1>
      <p class="tagline">Como o site trata dados pessoais e informações técnicas.</p>

{markdown_to_html(privacidade_content)}
    </article>'''
    privacidade_html = render(
        TEMPLATE,
        TITLE="política de privacidade :: hgbits",
        DESCRIPTION="Política de Privacidade do site hgbits.",
        HEAD_EXTRA=head_extra(f"{SITE_URL}/privacidade.html", "website", privacidade_title, "Política de Privacidade do site hgbits."),
        YEAR=str(datetime.now().year),
        ROOT="",
        BODY=privacidade_body,
    )
    (OUT_DIR / "privacidade.html").write_text(privacidade_html, encoding="utf-8")

    # ---------- galeria de artes ----------
    arte_items = []
    for post in posts:
        is_adult = post["classification"] in {"18+", "adult"}
        for img in post["images"]:
            src_r = resolve_src(img["src"], "").replace('"', "&quot;")
            alt_safe = html.escape(img["alt"] or "", quote=True)
            cap = img["caption"] or img["alt"] or ""
            gallery_caption = image_license_html(img["caption"]) or html.escape(cap)
            # A capa identificada pelo alt exato "Capa do Post" é uma prévia pública.
            # As demais imagens de posts +18 não são publicadas (ver restricted_assets).
            if is_adult and img["alt"] != "Capa do Post":
                continue
            image_html = f'''        <a href="posts/{post["slug"]}.html">
          <img src="{src_r}" alt="{alt_safe}" loading="lazy">
        </a>'''
            card_class = "art-card"
            arte_items.append(f'''      <figure class="{card_class}">
{image_html}
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
    (OUT_DIR / "artes.html").write_text(artes_html, encoding="utf-8")

    # ---------- páginas por tag ----------
    (OUT_DIR / "tags").mkdir(parents=True, exist_ok=True)
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
        (OUT_DIR / "tags" / f"{slug}.html").write_text(tag_html_out, encoding="utf-8")

    # ---------- feed.xml + sitemap.xml ----------
    (OUT_DIR / "feed.xml").write_text(build_rss(posts), encoding="utf-8")
    (OUT_DIR / "sitemap.xml").write_text(build_sitemap(posts, tag_map), encoding="utf-8")

    copy_public_files()

    print(f"OK: {len(posts)} posts, {len(tag_map)} tags, index.html, sobre.html, termos.html, privacidade.html, "
          f"artes.html, {len(tag_map)} páginas de tag, feed.xml e sitemap.xml gerados.")

if __name__ == "__main__":
    main()
