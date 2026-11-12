// SPDX-License-Identifier: GPL-3.0-only
// Copyright (C) 2026 hgbits <https://github.com/HGBits>
/* Aviso de primeira visita dos termos de uso. */
(() => {
  "use strict";

  // Versão dos termos: 11/11/2026.
  const TERMS_VERSION = "2026-11-11";
  const STORAGE_KEY = `hgbits-terms-accepted-${TERMS_VERSION}`;
  const dialog = document.querySelector("[data-terms-notice]");
  if (!dialog || typeof dialog.showModal !== "function") return;

  // As páginas de termos e de privacidade devem permanecer legíveis sem
  // outro bloqueio (com ou sem ".html", como o GitHub Pages também serve).
  if (/\/(termos|privacidade)(\.html)?\/?$/.test(window.location.pathname)) return;

  let accepted = false;
  try {
    accepted = window.localStorage.getItem(STORAGE_KEY) === "accepted";
  } catch (_error) {
    // Sem armazenamento disponível, o aviso aparece em cada visita.
  }

  if (accepted) return;

  const acceptButton = dialog.querySelector("[data-terms-accept]");
  if (!acceptButton) return;

  // Impede que Escape feche o diálogo sem uma decisão explícita.
  dialog.addEventListener("cancel", (event) => {
    event.preventDefault();
  });

  acceptButton.addEventListener("click", () => {
    try {
      window.localStorage.setItem(STORAGE_KEY, "accepted");
    } catch (_error) {
      // O aceite vale para a sessão atual mesmo sem armazenamento.
    }
    dialog.close("accepted");
  });

  // A recusa é um link externo no HTML. Ela não grava aceite e leva
  // o visitante para fora do blog, sem liberar a página protegida.
  dialog.showModal();
})();
