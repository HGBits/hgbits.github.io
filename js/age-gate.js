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
    const status = gate.querySelector("[data-age-status]");
    const body = gate.querySelector("[data-age-body]");
    const retryButton = gate.querySelector("[data-age-retry]");
    const contentUrl = gate.dataset.ageContentUrl;

    if (!prompt || !denied || !content || !yesButton || !noButton ||
        !status || !body || !contentUrl) return;

    let request = null;
    let loaded = false;

    const loadComments = () => {
      const comments = gate.parentElement.querySelector("[data-age-comments]");
      if (!comments || comments.dataset.loaded === "true") return;

      const mount = comments.querySelector("[data-giscus]");
      if (!mount) return;

      const script = document.createElement("script");
      script.src = "https://giscus.app/client.js";
      script.setAttribute("data-repo", "HGBits/hgbits.github.io");
      script.setAttribute("data-repo-id", "R_kgDOTQ92dw");
      script.setAttribute("data-category", "Comentários");
      script.setAttribute("data-category-id", "DIC_kwDOTQ92d84DGItE");
      script.setAttribute("data-mapping", "pathname");
      script.setAttribute("data-strict", "0");
      script.setAttribute("data-reactions-enabled", "1");
      script.setAttribute("data-emit-metadata", "0");
      script.setAttribute("data-input-position", "bottom");
      script.setAttribute("data-theme", "noborder_dark");
      script.setAttribute("data-lang", "pt");
      script.setAttribute("crossorigin", "anonymous");
      script.async = true;

      comments.hidden = false;
      comments.dataset.loaded = "true";
      mount.appendChild(script);
    };

    const showDenied = () => {
      prompt.hidden = true;
      content.hidden = true;
      denied.hidden = false;
    };

    const loadContent = () => {
      if (loaded) return Promise.resolve();
      if (request) return request;

      status.textContent = "Carregando publicação...";
      retryButton.hidden = true;
      request = fetch(contentUrl, { credentials: "same-origin" })
        .then((response) => {
          if (!response.ok) throw new Error("HTTP " + response.status);
          return response.text();
        })
        .then((markup) => {
          body.innerHTML = markup;
          loaded = true;
          status.hidden = true;
        })
        .catch(() => {
          status.hidden = false;
          status.textContent = "Não foi possível carregar a publicação. Verifique sua conexão.";
          retryButton.hidden = false;
        })
        .finally(() => {
          request = null;
        });

      return request;
    };

    const showAccepted = () => {
      prompt.hidden = true;
      denied.hidden = true;
      content.hidden = false;
      loadContent();
      loadComments();
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

    retryButton.addEventListener("click", () => loadContent());
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
