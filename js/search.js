/*
 * search.js — hgbits
 * Busca client-side dos posts, só na index.
 * Regras que este arquivo segue à risca:
 *   1. Progressive enhancement de verdade: o campo de busca é criado
 *      via JS. Se o JS não rodar (lynx/w3m ou JS desligado), o campo
 *      simplesmente não existe — nunca fica uma caixa morta na tela.
 *   2. Sem rede, sem CDN, sem dependências. Filtra o que já está no DOM.
 *   3. Falha em silêncio: um erro aqui nunca deve quebrar a página.
 */
(function () {
  "use strict";
  try {
    var list = document.querySelector("ul.postlist");
    var tabs = document.querySelector(".tabs");
    if (!list || !tabs) return; // só existe na index

    var items = Array.prototype.slice.call(list.querySelectorAll("li"));
    if (!items.length) return;

    var wrap = document.createElement("div");
    wrap.className = "search-wrap";

    var input = document.createElement("input");
    input.type = "search";
    input.className = "search-input";
    input.placeholder = "buscar posts…";
    input.setAttribute("aria-label", "Buscar posts");

    wrap.appendChild(input);
    tabs.parentNode.insertBefore(wrap, tabs);

    var empty = document.createElement("p");
    empty.className = "search-empty";
    empty.textContent = "Nenhum post encontrado.";
    empty.hidden = true;
    list.parentNode.insertBefore(empty, list.nextSibling);

    input.addEventListener("input", function () {
      var q = input.value.trim().toLowerCase();
      var anyVisible = false;
      items.forEach(function (li) {
        var hit = !q || (li.getAttribute("data-search") || "").indexOf(q) !== -1;
        li.hidden = !hit;
        if (hit) anyVisible = true;
      });
      empty.hidden = anyVisible || !q;
    });
  } catch (e) {
    // busca é extra — nunca deve quebrar a página por causa disto
  }
})();
