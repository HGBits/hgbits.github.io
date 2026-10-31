/* HGBits Age Gate: confirmação simples de maioridade por navegador. */
(() => {
  "use strict";

  const STORAGE_KEY = "hgbits-age-gate";
  const acceptedValue = "accepted";
  const deniedValue = "denied";

  document.querySelectorAll("[data-age-gate]").forEach((gate) => {
    const prompt = gate.querySelector("[data-age-prompt]");
    const denied = gate.querySelector("[data-age-denied]");
    const content = gate.querySelector("[data-age-content]");
    const yesButton = gate.querySelector("[data-age-yes]");
    const noButton = gate.querySelector("[data-age-no]");

    if (!prompt || !denied || !content || !yesButton || !noButton) return;

    const showAccepted = () => {
      prompt.hidden = true;
      denied.hidden = true;
      content.hidden = false;
    };

    const showDenied = () => {
      prompt.hidden = true;
      content.hidden = true;
      denied.hidden = false;
    };

    let savedChoice = null;
    try {
      savedChoice = window.localStorage.getItem(STORAGE_KEY);
    } catch (_error) {
      // Se o armazenamento estiver indisponível, a escolha vale apenas nesta página.
    }

    if (savedChoice === acceptedValue) {
      showAccepted();
    } else if (savedChoice === deniedValue) {
      showDenied();
    }

    yesButton.addEventListener("click", () => {
      try {
        window.localStorage.setItem(STORAGE_KEY, acceptedValue);
      } catch (_error) {
        // Continua nesta página mesmo se o navegador bloquear localStorage.
      }
      showAccepted();
    });

    noButton.addEventListener("click", () => {
      try {
        window.localStorage.setItem(STORAGE_KEY, deniedValue);
      } catch (_error) {
        // A recusa continua valendo nesta página.
      }
      showDenied();
    });
  });
})();
