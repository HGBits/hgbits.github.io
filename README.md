# hgbits :: notas

Blog pessoal estático, gerado a partir de arquivos Markdown por `build.py`.

## Estrutura de conteúdo

As publicações ficam em `content/posts/`. Cada arquivo Markdown representa um post e seu nome, sem a extensão `.md`, é usado como identificador (slug) para gerar a página em `posts/`.

A página sobre o blog é escrita em `content/sobre.md`. O gerador lê dela o campo `title`; o restante do arquivo é convertido para HTML.

Para gerar o site localmente:

```bash
python build.py
```

O gerador usa apenas a biblioteca padrão do Python. Os arquivos HTML e auxiliares são escritos na raiz do projeto.

## Front matter

O front matter é um bloco opcional no início de cada arquivo Markdown, delimitado por duas linhas com três hífens (`---`). Ele contém metadados usados pelo gerador para montar títulos, datas, listagens, tags e restrição etária.

### Campos disponíveis

| Campo | Obrigatório | Descrição |
| --- | --- | --- |
| `title` | Não | Título da publicação. Se omitido, o nome do arquivo (sem `.md`) é usado. |
| `date` | Não | Data da publicação no formato `AAAA-MM-DD`. É exibida no post e nas listagens, ordena as publicações e alimenta o arquivo por ano/mês e o RSS. |
| `excerpt` | Não | Resumo curto exibido na listagem inicial e usado nas descrições de metadados/compartilhamento. Se omitido, fica vazio. |
| `tags` | Não | Lista de tags separadas por vírgulas. Cada tag gera links e uma página própria. |
| `classification` | Não | Classificação de conteúdo. `18+` e `adult` ativam o Age Gate e o selo `+18`; `14+` e `teen` exibem somente o selo `+14`, sem bloqueio. |

Todos os campos são opcionais para o parser. Na prática, recomenda-se informar pelo menos `title`, `date` e `excerpt` para que a publicação apareça corretamente identificada e contextualizada.

### Exemplo completo

```yaml
---
title: Uma publicação de exemplo
date: 2026-10-31
excerpt: Um resumo curto que aparece na página inicial.
tags: Linux, Segurança, Desenvolvimento
classification: public
---

O conteúdo da publicação começa aqui.
```

Para uma publicação destinada a adultos:

```yaml
---
title: Uma publicação adulta
date: 2026-10-31
excerpt: Resumo da publicação.
tags: Pessoal, Reflexões
classification: 18+
---

Conteúdo da publicação.
```

### Regras e limitações do parser

O bloco é inspirado na sintaxe YAML, mas **não é um parser YAML completo**. O `build.py` lê cada linha no formato simples `chave: valor`:

- Use uma propriedade por linha.
- O texto antes do primeiro `:` é o nome do campo; o restante é o valor.
- Não use listas YAML, objetos aninhados, continuações de linha ou estruturas complexas.
- Para `tags`, escreva os nomes na mesma linha, separados por vírgulas. Não use a sintaxe de lista com hífens.
- Valores de texto são mantidos como texto. Em `classification`, espaços externos e aspas simples ou duplas são removidos e o valor é convertido para minúsculas.
- Se não houver front matter delimitado corretamente no início do arquivo, o arquivo inteiro será tratado como corpo Markdown e os metadados ficarão vazios.

A data deve ser escrita como `AAAA-MM-DD`. Datas válidas são organizadas cronologicamente. Uma publicação sem data aparece no grupo **sem data**; uma data que não possa ser interpretada pode aparecer como texto literal e ser agrupada em **sem mês**.

### Classificação e Age Gate

O campo `classification` é opcional. Os valores abaixo, sem distinção entre maiúsculas e minúsculas, ativam a tela de confirmação:

- `18+`
- `adult`

Os valores `14+` e `teen` são classificações exclusivamente visuais e equivalentes: exibem o selo `+14` na listagem inicial, sem confirmação de idade ou bloqueio de leitura.

Qualquer outro valor, inclusive `public` ou a ausência do campo, não ativa o Age Gate nem exibe selo.

Quando ativado:

1. A página apresenta a pergunta **“Você é maior de 18 anos?”**.
2. A opção **Sim** libera o conteúdo e registra a escolha no `localStorage` do navegador.
3. A opção **Não** mantém o conteúdo oculto naquela página.
4. Na listagem de publicações, o post recebe o selo `+18`.

**Limitação de segurança:** o Age Gate é uma confirmação por autodeclaração, não controle de acesso. O site é estático e o HTML continua publicado; portanto, alguém ainda pode acessar diretamente o arquivo ou inspecionar seu conteúdo. Não use esse mecanismo para proteger informações privadas.

## Imagens

As imagens dos posts ficam, por convenção, no diretório `assets/` na raiz do projeto. Por exemplo:

```text
assets/
├── avatar.jpg
├── screenshot.png
└── ilustracao.webp
```

Use a sintaxe de imagem do Markdown no corpo do post:

```markdown
![Descrição alternativa](assets/screenshot.png)
```

O texto alternativo (`alt`) descreve a imagem para leitores de tela e aparece quando ela não pode ser carregada. Sempre que possível, escreva uma descrição útil em vez de deixar o campo vazio.

### Legenda

É possível adicionar uma legenda usando o título opcional da imagem:

```markdown
![Captura da aplicação](assets/screenshot.png "Tela inicial da aplicação")
```

Quando a imagem ocupa uma linha sozinha, o gerador a transforma em um bloco `figure` e exibe o título como legenda (`figcaption`). Se a imagem estiver dentro de um parágrafo, ela é renderizada como imagem em linha; nesse caso, o título não é exibido no corpo do post.

### Caminhos das imagens

Os caminhos relativos são interpretados a partir da raiz do blog, e o gerador ajusta automaticamente o prefixo conforme a página gerada:

- Na página inicial e em páginas na raiz, `assets/imagem.png` permanece `assets/imagem.png`.
- Dentro de uma publicação em `posts/`, o mesmo caminho vira `../assets/imagem.png`.

Assim, use sempre o mesmo caminho relativo à raiz do projeto, sem adicionar `../` apenas porque a imagem está sendo usada em um post.

O resolvedor mantém caminhos absolutos e URLs externas sem alterações, incluindo:

- URLs com protocolo, como `https://exemplo.com/imagem.png`;
- URLs iniciadas por `//`;
- caminhos iniciados por `/`, relativos à raiz do domínio.

Prefira armazenar imagens do próprio blog em `assets/`. Imagens externas dependem da disponibilidade do servidor de terceiros.

### Como as imagens são processadas

O mecanismo de imagens tem três etapas:

1. **Renderização:** o Markdown reconhece imagens no formato `![texto alternativo](caminho "legenda")`. Imagens em uma linha isolada viram `figure`; imagens dentro de texto viram elementos `img`.
2. **Carregamento:** as imagens geradas recebem `loading="lazy"`, permitindo que o navegador adie o carregamento até que elas estejam próximas da área visível.
3. **Galeria Artes:** o gerador coleta as imagens referenciadas no corpo dos posts e cria `artes.html`, reunindo cada imagem com sua legenda (ou texto alternativo, quando não há legenda) e um link para a publicação de origem.

Trechos de código cercados por crases triplas são ignorados pela coleta da galeria. Uma referência de imagem escrita dentro de um bloco de código, portanto, aparece como código e não é adicionada à página Artes.

A galeria não é um repositório separado: ela é montada automaticamente a partir das referências encontradas nos arquivos Markdown durante cada execução de `build.py`.

## Outros recursos gerados

Além das páginas individuais e da página inicial, o gerador cria:

- `sobre.html`: página sobre o autor;
- `artes.html`: galeria das imagens usadas nas publicações;
- páginas em `tags/`: uma página para cada tag;
- `feed.xml`: feed RSS;
- `sitemap.xml`: mapa do site.

A publicação no GitHub Pages é feita pelo workflow em `.github/workflows/build.yml`.
