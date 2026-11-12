---
title: Política de Privacidade
---

**Última atualização: 11 de novembro de 2026**

Esta Política de Privacidade explica como o site **hgbits :: notas**, disponível em [https://hgbits.github.io](https://hgbits.github.io), funciona em relação a dados pessoais e informações técnicas. O site é um blog pessoal estático: não possui sistema próprio de contas, banco de dados de visitantes, formulário de cadastro ou servidor de aplicação administrado pelo mantenedor.

## 1. Responsável pelo tratamento

O controlador dos dados tratados por decisão própria do blog é **Henrique Gabriel**, pessoa natural que mantém o projeto sob o pseudônimo **hgbits** e o perfil [github.com/HGBits](https://github.com/HGBits). Ele responde pelas decisões editoriais e pelos recursos próprios do site.

**Contato do controlador** para questões de privacidade, exercício de direitos de titular (LGPD, art. 18) e demais comunicações sobre proteção de dados: [HG_Bits@protonmail.com](mailto:HG_Bits@protonmail.com). Não foi designado um encarregado separado: esse mesmo canal atende essas comunicações. O [perfil do GitHub](https://github.com/HGBits) e o [repositório do projeto](https://github.com/HGBits/hgbits.github.io) também podem ser usados para contato não sensível.

Esta política não publica endereço residencial, telefone pessoal ou documentos do mantenedor. Não publique dados pessoais ou documentos em áreas públicas, como issues e comentários; use o e-mail acima.

## 2. Dados que podem ser tratados

Dependendo da forma de acesso e dos recursos utilizados, podem estar envolvidos:

- **Dados técnicos de acesso:** endereço IP, data e horário da requisição, endereço solicitado, informações do navegador e do dispositivo, sistema operacional, idioma e dados técnicos semelhantes. Esses dados podem ser registrados pela infraestrutura de hospedagem e entrega do site.
- **Preferências armazenadas no navegador:** escolhas de aceite dos termos e de confirmação ou recusa do aviso de maioridade, mantidas no `localStorage` do próprio navegador.
- **Dados relacionados a comentários:** nome de usuário, imagem de perfil, conteúdo publicado, reações e demais informações associadas à conta GitHub utilizada para participar das discussões.
- **Dados de navegação enviados a serviços externos:** informações técnicas necessárias para solicitar e carregar recursos hospedados por terceiros, como o script e a interface de comentários do Giscus/GitHub.

O blog não solicita diretamente nome civil, endereço, telefone, documentos, dados de pagamento ou informações sensíveis para permitir a leitura de suas páginas.

## 3. Finalidades e bases de funcionamento

As informações técnicas de acesso são tratadas pela infraestrutura de hospedagem para entregar páginas e arquivos, manter a disponibilidade, prevenir abuso e diagnosticar falhas ou incidentes.

As preferências locais são utilizadas para lembrar escolhas feitas pelo visitante e evitar a repetição desnecessária de avisos. A confirmação de maioridade é uma declaração feita pelo próprio visitante e não constitui verificação documental ou identificação da pessoa.

Os dados de comentários são tratados para exibir e permitir a participação nas discussões vinculadas às publicações. A participação é opcional e depende dos serviços externos envolvidos.

Quando aplicável, o tratamento realizado pelo mantenedor se apoia nas hipóteses legais pertinentes da Lei nº 13.709/2018 (LGPD), consideradas a finalidade concreta, a necessidade e o contexto de cada operação. O tratamento independente realizado por provedores externos também está sujeito às respectivas políticas e responsabilidades.

## 4. Serviços externos e compartilhamento

### GitHub Pages

O site é hospedado pelo GitHub Pages. Ao acessar uma página, o navegador faz requisições à infraestrutura do GitHub para receber o conteúdo. O provedor pode tratar dados técnicos de conexão e acesso conforme suas próprias políticas e condições de serviço. O mantenedor do blog não administra essa infraestrutura nem tem acesso garantido a todos os registros internos de hospedagem.

Consulte a [Declaração de Privacidade do GitHub](https://docs.github.com/pt/site-policy/privacy-policies/github-privacy-statement).

### Giscus e GitHub Discussions

As páginas de publicações comuns incorporam o Giscus para exibir comentários associados ao GitHub Discussions. **Por decisão de funcionamento do site, o script do Giscus é carregado diretamente pelo HTML da publicação**, sem aguardar o aceite do aviso de primeira visita dos termos. Assim, ao abrir uma publicação comum, o navegador pode se conectar ao Giscus e aos serviços do GitHub antes de qualquer interação com esse aviso.

O Giscus utiliza discussões do repositório GitHub e pode receber informações técnicas da conexão. Se o visitante interagir, autenticar-se ou publicar um comentário, dados vinculados à sua conta GitHub e à contribuição também serão tratados pelo GitHub. Nas publicações classificadas como 18+, os comentários são carregados somente depois da confirmação de maioridade na interface.

Consulte a [Política de Privacidade do GitHub](https://docs.github.com/pt/site-policy/privacy-policies/github-privacy-statement) e a [documentação do Giscus](https://giscus.app/).

### Leitura em voz alta

O botão "Ouvir post" usa a Web Speech API, ou seja, a síntese de voz do navegador ou do sistema operacional. O script do blog não faz requisições de rede para isso e não envia o texto a nenhum serviço próprio. No entanto, o navegador ou o sistema pode usar vozes processadas online, caso em que o texto da publicação lida é enviado ao serviço do respectivo fornecedor, sujeito às políticas dele. O blog não controla essa escolha. Para evitar esse envio, use uma voz local (offline) nas configurações do navegador ou do sistema, ou não utilize o recurso.

### Outros links e recursos

O botão "compartilhar publicação" apenas monta links para Telegram, X (Twitter), Mastodon (share.joinmastodon.org) e e-mail, além do compartilhamento nativo do navegador ou do sistema, quando existir. Carregar a página não faz nenhuma requisição a esses serviços: a conexão só acontece se você clicar em uma das opções, e passa a ser regida pela política do serviço escolhido. O título e o endereço da publicação são incluídos no link de compartilhamento.

Links para sites externos podem aparecer nas publicações. Ao seguir esses links, o visitante passa a interagir diretamente com os respectivos serviços, que possuem suas próprias políticas. O blog não controla o tratamento realizado por esses terceiros.

O site não utiliza, por iniciativa própria, uma plataforma de publicidade comportamental ou um serviço próprio de analytics para rastrear visitantes.

## 5. Armazenamento local no navegador

O site utiliza `localStorage`, recurso do navegador, para guardar preferências no dispositivo do visitante:

- `hgbits-terms-accepted-2026-11-11`: registra o aceite da versão dos termos identificada pela data. Uma nova versão pode utilizar uma chave diferente e apresentar novamente o aviso.
- `hgbits-age-gate`: registra a escolha `accepted` ou `denied` feita no aviso de maioridade.

Esses valores ficam no navegador utilizado e não são enviados ao mantenedor por uma funcionalidade própria do blog. Não há prazo automático de expiração definido pelo site: os registros permanecem até serem substituídos, removidos pelo próprio site ou apagados pelo visitante nas configurações do navegador. Limpar os dados do site ou utilizar outro navegador/dispositivo pode fazer com que os avisos apareçam novamente.

A busca das publicações é executada no próprio navegador. A leitura em voz alta usa a síntese de voz do navegador ou do sistema, que pode ser local ou online conforme a voz selecionada (veja a seção 4). O comportamento de recursos nativos do navegador pode variar conforme o software e suas configurações.

## 6. Retenção e eliminação

O site não mantém uma base própria de dados de visitantes. As preferências em `localStorage` permanecem no dispositivo até serem removidas conforme descrito acima.

Registros técnicos eventualmente mantidos pelo GitHub Pages e dados tratados pelo GitHub/Giscus seguem os prazos, critérios e procedimentos definidos por esses provedores. O mantenedor não define nem consegue confirmar um prazo único de retenção para esses registros internos. Comentários publicados podem permanecer visíveis no GitHub Discussions enquanto não forem removidos segundo as ferramentas e regras da plataforma.

Quando uma solicitação estiver sob controle do mantenedor, ele poderá avaliar a correção, remoção ou despublicação de conteúdo sob sua responsabilidade. Isso não implica apagar registros que estejam sob controle independente de um provedor externo.

## 7. Direitos do titular

Nos termos da LGPD, o titular pode, conforme aplicável ao caso, solicitar confirmação da existência de tratamento, acesso aos dados, correção de dados incompletos ou inexatos, anonimização, bloqueio ou eliminação de dados desnecessários ou tratados em desconformidade, informação sobre compartilhamentos e demais direitos previstos na legislação.

Para exercer esses direitos em relação a operações sob responsabilidade do mantenedor, entre em contato pelos canais indicados na seção 1. Para dados tratados diretamente pelo GitHub ou por outro provedor, pode ser necessário encaminhar a solicitação ao próprio serviço, por meio de seus canais e ferramentas de privacidade.

Para localizar uma solicitação, informe o contexto e a página ou recurso envolvido. Não envie senhas, documentos ou dados sensíveis em comentários ou espaços públicos. O atendimento poderá exigir informações razoáveis para confirmar o contexto da solicitação, sem coletar dados excessivos.

## 8. Segurança

A arquitetura estática reduz a quantidade de dados e de componentes administrados diretamente pelo mantenedor, mas não elimina riscos inerentes à internet, ao navegador ou aos provedores externos. O visitante deve manter seu navegador atualizado e evitar publicar informações privadas em comentários públicos.

## 9. Alterações desta política

Esta política pode ser atualizada para refletir mudanças no site, nos serviços utilizados ou na legislação. A data da última atualização será indicada no início do documento. Alterações relevantes serão descritas nesta página.

## 10. Contato

Dúvidas e solicitações relacionadas a esta política devem ser enviadas para [HG_Bits@protonmail.com](mailto:HG_Bits@protonmail.com). Também é possível usar o [perfil público do projeto no GitHub](https://github.com/HGBits) ou o [repositório hgbits.github.io](https://github.com/HGBits/hgbits.github.io) para contato não sensível. Para proteger sua privacidade, não inclua dados pessoais em mensagens públicas.

---

Este documento descreve o funcionamento conhecido do site e não substitui orientação ou revisão jurídica. As políticas dos provedores externos podem mudar independentemente desta página.
