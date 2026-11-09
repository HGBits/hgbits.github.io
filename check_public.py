#!/usr/bin/env python3
"""
check_public.py — verifica se _site/ (a única pasta publicada) vaza algo restrito.
Só stdlib. Sai com código 1 se encontrar qualquer problema; o workflow roda
isto depois do build e ANTES do deploy.

Uso:
    python build.py && python check_public.py
"""
import html
import sys
from pathlib import Path

ROOT = Path(__file__).parent
SITE = ROOT / "_site"
POSTS = ROOT / "content" / "posts"

FORBIDDEN_SUFFIXES = {".md", ".py", ".yml", ".yaml", ".sh", ".pem", ".key", ".asc", ".gpg"}
FORBIDDEN_DIRS = {"content", "templates", ".github", ".git", "admin", "private"}
TEXT_SUFFIXES = {".html", ".xml", ".js", ".css", ".json", ".txt", ".svg", ""}
MIN_LINE = 20  # linhas menores que isso geram falso positivo

def parse(text):
    """Separa front matter (chave: valor) do corpo, como o build.py."""
    if text.startswith("---"):
        parts = text.split("\n---", 1)
        if len(parts) == 2:
            head, body = parts
            meta = {}
            for line in head.splitlines()[1:]:
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip()
            return meta, body.lstrip("-").lstrip("\n")
    return {}, text

def is_adult(meta):
    return meta.get("classification", "").strip().strip("\"'").lower() in {"18+", "adult"}

def main():
    if not SITE.is_dir():
        print("ERRO: _site/ não existe. Rode python build.py primeiro.")
        return 1

    errors = []
    files = [p for p in SITE.rglob("*") if p.is_file()]

    bad_dirs = set()
    for p in files:
        rel = p.relative_to(SITE)
        if p.suffix.lower() in FORBIDDEN_SUFFIXES:
            errors.append(f"arquivo proibido publicado: {rel}")
        if rel.parts[0] in FORBIDDEN_DIRS:
            bad_dirs.add(rel.parts[0])
    errors.extend(f"diretório proibido publicado: {d}/" for d in sorted(bad_dirs))

    corpus = {}
    for p in files:
        if p.suffix.lower() in TEXT_SUFFIXES:
            try:
                corpus[p.relative_to(SITE)] = p.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                pass

    adult_posts = 0
    for md in sorted(POSTS.glob("*.md")):
        meta, body = parse(md.read_text(encoding="utf-8"))
        if not is_adult(meta):
            continue
        adult_posts += 1
        lines = {l.strip() for l in body.splitlines()
                 if len(l.strip()) >= MIN_LINE and not l.strip().startswith("![")}
        for rel, text in corpus.items():
            for line in lines:
                if line in text or html.escape(line, quote=False) in text \
                        or html.escape(line, quote=True) in text:
                    errors.append(f"texto de post 18+ ({md.name}) encontrado em {rel}: {line[:50]!r}...")
                    break
        page = SITE / "posts" / f"{md.stem}.html"
        if page.exists() and "data-age-content" in page.read_text(encoding="utf-8"):
            errors.append(f"{page.relative_to(SITE)} ainda contém data-age-content")

    if errors:
        print(f"FALHOU: {len(errors)} problema(s) em _site/")
        for e in errors:
            print("  -", e)
        return 1
    print(f"OK: {len(files)} arquivos em _site/, {adult_posts} posts 18+ verificados, nada vazado.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
