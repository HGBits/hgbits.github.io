# hgbits :: notas

Blog pessoal estático, gerado a partir de arquivos Markdown por `build.py`.

## Estrutura de conteúdo

As publicações ficam em `content/posts/`. Cada arquivo Markdown representa um post e seu nome, sem a extensão `.md`, é usado como identificador (slug) para gerar a página em `posts/`.

A página sobre o blog é escrita em `content/sobre.md`. O gerador lê dela o campo `title`; o restante do arquivo é convertido para HTML.

Para gerar o site localmente:

```bash
python build.py
```

O gerador usa apenas a biblioteca padrão do Python. Todo o site é escrito em `_site/` (ignorada pelo Git) e **somente essa pasta é publicada**. O build copia para lá apenas os itens listados em `PUBLIC_COPY` no `build.py` (`css/`, `js/`, `assets/`, `.well-known/`, `favicon.svg`); `content/`, `templates/`, `build.py` e o restante do repositório nunca chegam ao servidor.

Para testar localmente:

```bash
python build.py
python -m http.server -d _site 8000   # http://localhost:8000
```

## Front matter

O front matter é um bloco opcional no início de cada arquivo Markdown, delimitado por duas linhas com três hífens (`---`). Ele contém metadados usados pelo gerador para montar títulos, datas, listagens, tags e restrição etária.

### Campos disponíveis

| Campo | Obrigatório | Descrição |
| --- | --- | --- |
| `title` | Não | Título da publicação. Se omitido, o nome do arquivo (sem `.md`) é usado. |
| `date` | Não | Data original da publicação no formato `AAAA-MM-DD`. É exibida no post e nas listagens, ordena as publicações e alimenta o arquivo por ano/mês e o RSS. |
| `updated` | Não | Data da última revisão no formato `AAAA-MM-DD`. Quando preenchida, é exibida no cabeçalho do post como “Atualizado em”; não altera a ordenação nem a data original do RSS. |
| `excerpt` | Não | Resumo curto exibido na listagem inicial e usado nas descrições de metadados/compartilhamento. Se omitido, fica vazio. |
| `tags` | Não | Lista de tags separadas por vírgulas. Cada tag gera links e uma página própria. |
| `classification` | Não | Classificação de conteúdo. `18+` e `adult` restringem a publicação (corpo não é publicado) e exibem o selo `+18`; `14+` e `teen` exibem somente o selo `+14`, sem bloqueio. |

Todos os campos são opcionais para o parser. Na prática, recomenda-se informar pelo menos `title`, `date` e `excerpt` para que a publicação apareça corretamente identificada e contextualizada.

### Exemplo completo

```yaml
---
title: Uma publicação de exemplo
date: 2026-10-31
updated: 2026-11-03
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
updated: 2026-11-03
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

Os campos `date` e `updated`, quando informados, devem usar o formato `AAAA-MM-DD`. `date` representa a publicação original; `updated` registra a última revisão e só aparece no cabeçalho quando preenchido. A revisão não altera a ordem cronológica das publicações nem a data original do RSS. Datas válidas em `date` são organizadas cronologicamente. Uma publicação sem data aparece no grupo **sem data**; uma data que não possa ser interpretada pode aparecer como texto literal e ser agrupada em **sem mês**.

### Classificação e posts 18+

O campo `classification` é opcional. Os valores abaixo, sem distinção entre maiúsculas e minúsculas, marcam a publicação como restrita:

- `18+`
- `adult`

Os valores `14+` e `teen` são classificações exclusivamente visuais e equivalentes: exibem o selo `+14` na listagem inicial, sem bloqueio de leitura.

Qualquer outro valor, inclusive `public` ou a ausência do campo, não restringe nada nem exibe selo.

Para posts restritos (`18+`/`adult`), o build:

1. **Não renderiza o corpo.** A página publicada contém só título, data, tags, selo `+18` e um aviso. O texto não aparece no HTML, no feed, na busca nem em metadados.
2. **Mantém o `excerpt` público** (listagem, metadados, feed e busca): é ele que permite ao leitor decidir se quer ler o post.
3. **Não publica imagens do corpo** usadas somente nesse post (a capa, `![Capa do Post](...)`, continua pública) e não as lista na galeria de artes.
4. Remove os comentários (Giscus) e o compartilhamento da página.

O Markdown original nunca é publicado: apenas `_site/` vai ao servidor. **Atenção:** isso vale daqui para frente. O que já esteve publicado antes (site, histórico do Git, caches) deve ser considerado exposto. Ainda não há distribuição do texto restrito a leitores autorizados; a página é um marcador até que essa etapa exista.

## Revisão de publicações

O blog permite registrar a revisão de uma publicação sem substituir sua data original. Para isso, use o campo opcional `updated` no front matter do arquivo Markdown em `content/posts/`.

### Como registrar uma revisão

1. Abra o arquivo Markdown da publicação que foi revisada.
2. Adicione ou atualize o campo `updated` com a data da revisão, no formato `AAAA-MM-DD`.
3. Salve o arquivo e execute `python build.py` para regenerar o site.

Exemplo:

```yaml
---
title: Minha publicação
date: 2026-10-31
updated: 2026-11-03
excerpt: Resumo da publicação.
tags: Linux, Desenvolvimento
---
```

Quando `updated` estiver preenchido, a página da publicação exibirá **“Atualizado em: 03 nov 2026”** ao lado da data original de publicação. Se o campo estiver vazio ou ausente, a indicação de atualização não será exibida.

A revisão é apenas um registro da última atualização editorial: ela não altera a data de publicação, a ordem dos posts, o agrupamento no arquivo cronológico nem a data `pubDate` do RSS. O gerador não mantém um histórico de versões ou de revisões anteriores; o campo armazena somente a data mais recente informada pelo autor.

---

## Sumário automático (TOC)

Cada publicação pode receber um sumário automático com links para suas seções. O gerador monta esse sumário a partir dos títulos Markdown de nível 2 e 3 (`##` e `###`).

### Como funciona

1. O `build.py` converte o corpo Markdown para HTML e, em seguida, identifica os elementos `<h2>` e `<h3>`.
2. Cada título recebe um identificador (`id`) derivado do texto: letras são convertidas para minúsculas, acentos são removidos e sequências de caracteres não alfanuméricos viram hífens.
3. Se dois títulos gerarem o mesmo identificador, o gerador acrescenta um sufixo numérico (`-2`, `-3` etc.) para manter os links únicos.
4. Quando a publicação tem pelo menos **dois títulos** entre `##` e `###`, o sumário é criado automaticamente. Títulos `#` e `####` ou níveis mais profundos não entram nele.

Por padrão, o sumário aparece logo depois do cabeçalho da publicação, antes do corpo do texto.

### Escolher a posição do sumário

Para posicionar o sumário em outro ponto, insira `[[TOC]]` em uma linha isolada no corpo Markdown:

```markdown
## Introdução

Texto introdutório.

[[TOC]]

## Instalação

Conteúdo da seção.
```

O marcador é substituído pelo sumário no local indicado. Apenas a primeira ocorrência é usada. Se a publicação não tiver títulos suficientes para gerar o sumário, o marcador é removido e nenhum sumário é exibido.

### Hierarquia visual

- Seções `##` aparecem no nível principal.
- Subseções `###` aparecem recuadas em relação às seções principais.

O sumário é HTML estático gerado durante a execução de `build.py`. Não depende de JavaScript, bibliotecas externas ou requisições em tempo de leitura. Sua apresentação e o controle de abrir/fechar são definidos pelo CSS do site.

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

Imagens pertencentes a publicações classificadas como `18+` ou `adult` aparecem borradas na galeria Artes, com uma confirmação de maioridade sobre a miniatura. A confirmação usa a mesma escolha armazenada pelo Age Gate das publicações (`localStorage`); ao aceitar, todas as miniaturas adultas da galeria são liberadas. Ao recusar, elas permanecem ocultas.

## Outros recursos gerados

Além das páginas individuais e da página inicial, o gerador cria:

- `sobre.html`: página sobre o autor;
- `artes.html`: galeria das imagens usadas nas publicações;
- páginas em `tags/`: uma página para cada tag;
- `feed.xml`: feed RSS;
- `sitemap.xml`: mapa do site.

A publicação no GitHub Pages é feita pelo workflow em `.github/workflows/build.yml`.
