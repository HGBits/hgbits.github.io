---
title: Nem a NSA está segura.
date: 2026-11-18
excerpt: A queda temporária de uma rede da NSA e uma falha no Bitcoin Core envolvendo conexões Tor levantam uma questão incômoda: em uma era de desenvolvimento acelerado por IA, ainda sabemos o quanto nossos sistemas são seguros?
tags: Segurança, Tecnologia, IA, Privacidade
authorship: ai-assisted
---

![Capa do Post](assets/NEM-A-NSA-ESTÁ-SEGURA.png)

Existe uma certa ingenuidade na forma como as pessoas enxergam segurança digital. Alguns sistemas ganham uma reputação tão grande que passam a ser tratados como se fossem impossíveis de comprometer. Tor, criptografia, redes de inteligência, sistemas operacionais e softwares de código aberto. Basta o nome carregar algum peso técnico para muita gente assumir que está tudo resolvido.

Mas segurança não funciona assim.

Em novembro, uma rede confidencial de comunicações da NSA sofreu uma interrupção durante um procedimento de manutenção. Na mesma semana, o Bitcoin Core revelou uma vulnerabilidade que permitiu que milhares de nós tratassem conexões recebidas pelo Tor como conexões confiáveis.

São acontecimentos diferentes, com causas diferentes. Mas existe uma pergunta que conecta os dois: **se até sistemas construídos para resistir a ameaças sofisticadas estão sujeitos a falhas, por que ainda tratamos determinados softwares como fortalezas impossíveis de invadir?**

E existe outro elemento tornando essa discussão ainda mais importante: a inteligência artificial.

## Nem a NSA está imune a falhas

A rede NSANet é utilizada para comunicações internas e informações sigilosas da Agência de Segurança Nacional dos Estados Unidos. Segundo informações divulgadas pela CNN, a infraestrutura sofreu uma interrupção que afetou parte de seus sistemas internos.

A explicação apresentada posteriormente foi uma degradação temporária durante uma manutenção programada. O diretor de Inteligência Nacional, Jay Clayton, atribuiu o problema à aplicação de uma atualização de software que não permitiu que os sistemas reiniciassem como esperado.

A NSA afirmou que suas capacidades essenciais de missão permaneceram operacionais, graças às camadas de redundância existentes.

Não há evidências de que o episódio tenha sido provocado por um ataque cibernético. E essa distinção importa. Uma falha operacional não é a mesma coisa que uma invasão.

Ainda assim, existe algo bastante interessante nesse episódio: uma infraestrutura construída para lidar com ameaças de inteligência e segurança nacional também depende de atualizações, configurações, manutenção e decisões humanas.

A tecnologia pode ser sofisticada. Os erros continuam sendo humanos.

## Até o Tor pode estar no meio de uma falha

Outro caso recente merece atenção.

Em novembro de 2026, desenvolvedores do Bitcoin Core divulgaram detalhes sobre a vulnerabilidade CVE-2025-62860. O problema permitia que conexões recebidas por meio do Tor herdassem permissões de uma lista de conexões confiáveis, conhecida como `-whitelist`.

Em determinadas configurações, o Bitcoin Core identificava conexões externas como se fossem provenientes do próprio serviço Tor local. Quando o endereço desse serviço estava dentro de uma faixa configurada como confiável, conexões de terceiros acabavam recebendo privilégios que deveriam ser reservados a máquinas conhecidas.

O resultado? Milhares de nós acessíveis da rede principal do Bitcoin concediam permissões de whitelist a conexões recebidas pelo Tor.

Essas permissões removiam algumas proteções contra negação de serviço e mecanismos de mitigação de vazamentos de privacidade.

É importante deixar uma coisa clara: isso não significa que o protocolo Tor foi quebrado, que o anonimato de todos os usuários foi comprometido ou que a rede Bitcoin foi invadida. O problema estava na integração e na configuração do Bitcoin Core com o Tor. Nós que não utilizavam a opção de whitelist não eram afetados.

A vulnerabilidade já havia sido corrigida em versões lançadas em outubro de 2025. Os detalhes técnicos só foram divulgados em novembro de 2026, depois que a última versão afetada perdeu suporte.

Ainda assim, o episódio é um bom lembrete: não basta utilizar ferramentas conhecidas por sua segurança. É necessário entender como elas funcionam, como são configuradas e, principalmente, como interagem com outros componentes.

Uma cadeia de segurança é tão confiável quanto suas partes mais frágeis.

## A inteligência artificial está mudando o jogo

Agora chegamos à parte que considero mais preocupante.

A inteligência artificial está mudando a maneira como software é desenvolvido, auditado e protegido. Modelos conseguem analisar grandes quantidades de código, identificar padrões suspeitos, sugerir correções e encontrar vulnerabilidades que poderiam passar despercebidas durante uma revisão convencional.

Isso é positivo. O problema é que essa capacidade não pertence exclusivamente a quem trabalha com defesa.

As mesmas ferramentas que ajudam um pesquisador a encontrar uma falha também podem ajudar alguém mal-intencionado a localizá-la. O custo técnico para analisar código e procurar vulnerabilidades está diminuindo.

O próprio Bitcoin Core precisou rever sua política de divulgação de vulnerabilidades. Em outubro de 2026, desenvolvedores alteraram o procedimento para falhas que poderiam ser redescobertas facilmente por modelos de IA, inclusive com comandos relativamente simples.

A preocupação é compreensível: manter uma vulnerabilidade em sigilo por meses não oferece muita proteção quando qualquer pessoa com acesso a um modelo pode encontrar o mesmo problema.

Um levantamento citado pela CoinDesk ilustra a dimensão dessa mudança. Um grupo de pesquisadores utilizou modelos de IA para analisar 390 projetos relacionados ao Bitcoin e registrou 4.962 possíveis problemas, incluindo 85 classificados como críticos.

Não estamos falando apenas de ferramentas que escrevem funções ou completam trechos de código. Estamos falando de sistemas que alteram o equilíbrio entre quem procura falhas e quem tenta corrigi-las.

E isso traz uma consequência desconfortável para o desenvolvimento de software.

Produzir código ficou mais rápido. Isso não significa que produzir software seguro também ficou.

Se uma equipe consegue implementar funcionalidades em uma fração do tempo, mas não consegue revisar, testar e auditar tudo na mesma velocidade, o resultado pode ser um acúmulo de complexidade difícil de controlar.

A IA pode acelerar a defesa, mas também acelera a descoberta de vulnerabilidades. Pode ajudar a corrigir um erro e, ao mesmo tempo, tornar mais fácil encontrar outro.

O problema não é utilizar IA no desenvolvimento. É confundir velocidade de implementação com qualidade e segurança.

## Segurança não é uma promessa, é um processo

Existe uma diferença enorme entre um sistema ser seguro e um sistema ainda não ter apresentado uma falha conhecida.

Criptografia forte não impede erros de implementação. Código aberto não significa código perfeitamente auditado. Uma rede distribuída não está automaticamente livre de pontos frágeis. E uma ferramenta voltada à privacidade não é uma garantia absoluta de anonimato.

A segurança depende de uma combinação de fatores: arquitetura, implementação, configuração, atualização, auditoria e capacidade de resposta.

É por isso que projetos sérios precisam de pesquisadores independentes, revisão de código, testes contínuos e processos responsáveis de divulgação de vulnerabilidades.

Também é por isso que confiar cegamente em uma ferramenta é um erro.

A IA não vai tornar todo software inseguro, assim como o código aberto não torna todo software seguro. O que está mudando é a velocidade com que erros podem ser encontrados, explorados e corrigidos.

E talvez seja justamente essa velocidade que deveríamos observar com mais atenção.

Afinal, se uma atualização consegue derrubar parte de uma infraestrutura da NSA e uma configuração consegue transformar conexões anônimas em conexões privilegiadas dentro de milhares de nós, talvez seja hora de abandonar a ideia de que existem sistemas impossíveis de quebrar.

**Não existe software invulnerável. Existe software que ainda não teve sua próxima falha descoberta.**

---

## Fontes

- [Olhar Digital — Rede confidencial de comunicações da NSA sai do ar nos EUA](https://olhardigital.com.br/2026/11/17/seguranca/rede-confidencial-de-comunicacoes-da-nsa-sai-do-ar-nos-eua/)
- [CBS News — NSA network down](https://www.cbsnews.com/news/nsa-network-down-classified-fort-meade/)
- [Bitcoin Core — CVE-2025-62860: conexões Tor recebiam permissões de whitelist](https://bitcoincore.org/en/2026/11/10/disclose-cve-2025-62860/)
- [CoinDesk — Bitcoin Core revela falha que fez milhares de nós confiarem em conexões desconhecidas via Tor](https://www.coindesk.com/tech/2026/11/12/bitcoin-core-reveals-bug-that-made-thousands-of-nodes-trust-any-stranger-on-tor)
- [CoinDesk — Bitcoin Core altera regras de segurança diante da capacidade da IA de encontrar vulnerabilidades](https://www.coindesk.com/tech/2026/10/23/bitcoin-will-now-stop-hiding-bugs-an-ai-can-find-in-one-prompt/)
