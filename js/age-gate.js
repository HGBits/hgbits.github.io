/* HGBits Age Gate: confirmação simples de maioridade por navegador. */
(() => {
  "use strict";

  const STORAGE_KEY = "hgbits-age-gate";
  const acceptedValue = "accepted";
  const deniedValue = "denied";

  const readChoice = () => {
    try {
      return window.localStorage.getItem(STORAGE_KEY);
    } catch (_error) {
      return null;
    }
  };

  const saveChoice = (value) => {
    try {
      window.localStorage.setItem(STORAGE_KEY, value);
    } catch (_error) {
      // A escolha ainda vale para os elementos da página atual.
    }
  };

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

    const savedChoice = readChoice();
    if (savedChoice === acceptedValue) showAccepted();
    else if (savedChoice === deniedValue) showDenied();

    yesButton.addEventListener("click", () => {
      saveChoice(acceptedValue);
      showAccepted();
    });

    noButton.addEventListener("click", () => {
      saveChoice(deniedValue);
      showDenied();
    });
  });

  document.querySelectorAll("[data-age-gallery]").forEach((gallery) => {
    const prompt = gallery.querySelector("[data-art-prompt]");
    const denied = gallery.querySelector("[data-art-denied]");
    const yesButton = gallery.querySelector("[data-art-yes]");
    const noButton = gallery.querySelector("[data-art-no]");

    if (!prompt || !denied || !yesButton || !noButton) return;

    const unlock = () => {
      gallery.classList.add("is-unlocked");
      prompt.hidden = true;
      denied.hidden = true;
    };

    const refuse = () => {
      prompt.hidden = true;
      denied.hidden = false;
    };

    const savedChoice = readChoice();
    if (savedChoice === acceptedValue) unlock();
    else if (savedChoice === deniedValue) refuse();

    yesButton.addEventListener("click", () => {
      saveChoice(acceptedValue);
      document.querySelectorAll("[data-age-gallery]").forEach((item) => {
        item.classList.add("is-unlocked");
        const itemPrompt = item.querySelector("[data-art-prompt]");
        const itemDenied = item.querySelector("[data-art-denied]");
        if (itemPrompt) itemPrompt.hidden = true;
        if (itemDenied) itemDenied.hidden = true;
      });
    });

    noButton.addEventListener("click", () => {
      saveChoice(deniedValue);
      document.querySelectorAll("[data-age-gallery]").forEach((item) => {
        const itemPrompt = item.querySelector("[data-art-prompt]");
        const itemDenied = item.querySelector("[data-art-denied]");
        if (itemPrompt) itemPrompt.hidden = true;
        if (itemDenied) itemDenied.hidden = false;
      });
    });
  });
})();
