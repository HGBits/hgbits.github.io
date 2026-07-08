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
from datetime import datetime

ROOT_DIR = Path(__file__).parent
CONTENT = ROOT_DIR / "content"
TEMPLATE = (ROOT_DIR / "templates" / "page.html").read_text(encoding="utf-8")

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


def slugify(name):
    return name


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


def main():
    posts = []
    (ROOT_DIR / "posts").mkdir(parents=True, exist_ok=True)  # ← ADICIONAR ESTA LINHA
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
        nav_links = []
        if prev_p:
            nav_links.append(f'<a href="{prev_p["slug"]}.html">← anterior: {html.escape(prev_p["title"])}</a>')
        if next_p:
            nav_links.append(f'<a href="{next_p["slug"]}.html">próximo: {html.escape(next_p["title"])} →</a>')

        body = f'''    <h1 class="prompt">{html.escape(post["title"])}</h1>
    <p class="meta">{format_date(post["date"])} · {post["reading"]} min de leitura · {tag_pills(post["tags"])}</p>

{post["body_html"]}

    <div class="rule" aria-hidden="true"></div>

    <footer class="term-footer">
      <span>{" &nbsp;·&nbsp; ".join(nav_links) if nav_links else "fim da lista de posts"}</span>
      <span class="prompt-end">exit 0</span>
    </footer>'''

        html_out = render(
            TEMPLATE,
            TITLE=f'{post["title"]} :: hgbits',
            DESCRIPTION=post["excerpt"],
            CHROME_PATH=f'hgbits@inlocus:~/blog/posts$ cat {post["slug"]}.md',
            ROOT="../",
            BODY=body,
        )
        (ROOT_DIR / "posts" / f'{post["slug"]}.html').write_text(html_out, encoding="utf-8")

    # ---------- gera lista de tags ----------
    tag_map = {}
    for post in posts:
        for t in post["tags"]:
            tag_map.setdefault(t, []).append(post)

    posts_items = "\n".join(f'''      <li>
        {tag_pills(p["tags"])}
        <div><a href="posts/{p["slug"]}.html">{html.escape(p["title"])}</a></div>
        <p class="excerpt">{html.escape(p["excerpt"])}</p>
        <p class="meta">{format_date(p["date"])} · {p["reading"]} min de leitura</p>
      </li>''' for p in posts)

    tags_items = "\n".join(f'''      <li>
        <span class="tag">{html.escape(tag)}</span>
        <ul class="taglist-posts">
{chr(10).join(f'          <li><a href="posts/{p["slug"]}.html">{html.escape(p["title"])}</a></li>' for p in plist)}
        </ul>
      </li>''' for tag, plist in tag_map.items())

    index_body = f'''    <pre class="banner" aria-hidden="true">
 _           _     _ _
| |__   __ _| |__ (_) |_ ___
| '_ \\ / _` | '_ \\| | __/ __|
| | | | (_| | |_) | | |_\\__ \\
|_| |_|\\__, |_.__/|_|\\__|___/
       |___/
    </pre>

    <h1 class="prompt">notas de hgbits</h1>
    <p class="tagline">
     Linux User, Libertário  e Gamedev.<span class="cursor" aria-hidden="true">_</span>
    </p>

    <div class="tabs">
      <input type="radio" name="tabs" id="tab-posts" checked>
      <input type="radio" name="tabs" id="tab-tags">
      <div class="tab-labels">
        <label for="tab-posts">$ ls posts/</label>
        <label for="tab-tags">$ ls tags/</label>
      </div>
      <div class="tab-panels">
        <section class="tab-panel panel-posts">
          <h2>posts</h2>
          <ul class="postlist">
{posts_items}
          </ul>
        </section>
        <section class="tab-panel panel-tags">
          <h2>por tag</h2>
          <ul class="taglist">
{tags_items}
          </ul>
        </section>
      </div>
    </div>

    <div class="rule" aria-hidden="true"></div>

    <footer class="term-footer">
      <span class="prompt-end">exit 0</span>
      <span>{len(posts)} posts · gerado por build.py a partir de Markdown, sem JS, sem CDN</span>
    </footer>'''

    index_html = render(
        TEMPLATE,
        TITLE="hgbits :: notas",
        DESCRIPTION="Blog pessoal de hgbits — Linux User, Libertário  e Gamedev.",
        CHROME_PATH="hgbits@inlocus:~/blog$",
        ROOT="",
        BODY=index_body,
    )
    (ROOT_DIR / "index.html").write_text(index_html, encoding="utf-8")

    # ---------- sobre.html ----------
    sobre_raw = (CONTENT / "sobre.md").read_text(encoding="utf-8")
    meta, body = parse_frontmatter(sobre_raw)
    sobre_body = f'''    <h1 class="prompt">{meta.get("title", "sobre")}</h1>

{markdown_to_html(body)}

    <div class="rule" aria-hidden="true"></div>

    <footer class="term-footer">
      <span class="prompt-end">exit 0</span>
      <span>hgbits :: 2026</span>
    </footer>'''
    sobre_html = render(
        TEMPLATE,
        TITLE="sobre :: hgbits",
        DESCRIPTION="Sobre hgbits.",
        CHROME_PATH="hgbits@inlocus:~/blog$ cat sobre.md",
        ROOT="",
        BODY=sobre_body,
    )
    (ROOT_DIR / "sobre.html").write_text(sobre_html, encoding="utf-8")

    print(f"OK: {len(posts)} posts, {len(tag_map)} tags, index.html e sobre.html gerados.")


if __name__ == "__main__":
    main()
