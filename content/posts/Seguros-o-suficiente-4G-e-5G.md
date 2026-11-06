---
title: 4G e 5G são seguros o suficiente?
date: 2026-11-06
tags: Notícias
excerpt: Pesquisadores identificaram 84 vulnerabilidades em implementações de redes 4G e 5G. Algumas podem permitir ataques de negação de serviço e até sequestro de sessões de usuários.
---

![Capa do Post](assets/Segurança-4G-e-5G.png)

# 4G e 5G são seguros o suficiente?

A evolução das redes móveis trouxe velocidades maiores, menor latência e novas possibilidades de conectividade. Mas será que também trouxe segurança suficiente?

Pesquisadores da Universidade Tecnológica Nanyang, em Singapura, identificaram **84 vulnerabilidades inéditas em implementações de núcleos de redes 4G e 5G**.

As falhas foram encontradas em sete implementações de código aberto utilizadas na infraestrutura dessas redes. Das 84 vulnerabilidades identificadas, 83 foram confirmadas e 81 receberam identificadores CVE.

Entre os problemas encontrados estão falhas que podem permitir ataques de negação de serviço (DoS) e até mesmo **sequestro de sessão (Session Hijacking)**.

### Como isso pode afetar os usuários?

Um dos cenários demonstrados pelos pesquisadores envolve uma vulnerabilidade no protocolo PFCP, responsável pela comunicação entre componentes da infraestrutura móvel.

Explorando a ausência de validação adequada de identificadores de regras, um invasor pode fazer com que o tráfego de dados de uma vítima seja redirecionado para uma infraestrutura controlada por ele.

Na prática, isso pode permitir que o atacante intercepte o tráfego de rede da vítima.

O problema não está necessariamente no smartphone ou no chip utilizado, mas na infraestrutura responsável por transportar e encaminhar os dados.

### Isso significa que usar 4G ou 5G é perigoso?

Não necessariamente.

As vulnerabilidades identificadas dependem de condições específicas de exploração, incluindo acesso a interfaces internas da infraestrutura da operadora e configurações inadequadas de segurança.

Portanto, não significa que qualquer pessoa conectada a uma rede 4G ou 5G esteja automaticamente vulnerável.

Ainda assim, a descoberta demonstra que tecnologias mais recentes não são sinônimo de segurança absoluta.

### E quanto às redes antigas?

As redes 2G e 3G também possuem limitações e vulnerabilidades conhecidas há bastante tempo. A existência de mecanismos de compatibilidade com tecnologias antigas continua sendo uma preocupação para a segurança das comunicações móveis.

**A conclusão é simples:** não devemos tratar a infraestrutura de telecomunicações como uma camada de segurança infalível.

Mesmo quando utilizamos tecnologias modernas, a proteção dos nossos dados depende de diversas camadas de segurança, desde o dispositivo até a infraestrutura das operadoras.

**Fonte:** https://caveiratech.com/post/pesquisadores-identificam-84-falhas-nos-nucleos-4g-e-5g-incluindo-brecha-de-session-hijacking-2201038
