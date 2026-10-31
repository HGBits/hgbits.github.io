Coloque aqui as imagens usadas nos posts (ex: assets/screenshot.png).
No Markdown, referencie como caminho relativo à raiz do blog:

    ![legenda opcional aqui](assets/screenshot.png "texto da legenda")

O build.py ajusta o caminho automaticamente para funcionar tanto em
index.html/sobre.html (raiz) quanto em posts/*.html (um nível abaixo).


## Restrição etária (Age Gate)

Para exibir a confirmação de maioridade em uma publicação, adicione ao front matter:

```yaml
---
title: Título da publicação
date: 2026-10-31
classification: 18+
---
```

As classificações `18+`, `adult` e `adulto` ativam o Age Gate. Sem essa propriedade, a publicação permanece pública normalmente. A escolha é lembrada no navegador por meio de `localStorage`.

**Limitação:** este recurso é uma confirmação visual por autodeclaração. Como o site é estático e o conteúdo continua publicado no GitHub Pages, não é uma barreira técnica contra acesso direto aos arquivos ou inspeção do HTML.
