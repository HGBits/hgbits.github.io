/* share.js — hgbits
 * Compartilhamento progressivo: links sociais, cópia e Web Share API.
 */
(function () {
  "use strict";
  try {
    var root = document.querySelector("[data-share]");
    if (!root) return;

    var toggle = root.querySelector(".share-toggle");
    var options = root.querySelector(".share-options");
    var nativeButton = root.querySelector("[data-share-native]");
    var status = root.querySelector("[data-share-status]");
    var url = window.location.href.split("#")[0];
    var title = document.title.replace(/\s*::\s*hgbits\s*$/, "");

    function setStatus(message) {
      status.textContent = message;
    }

    function setLink(selector, href) {
      var link = root.querySelector(selector);
      if (link) link.href = href;
    }

    var encodedUrl = encodeURIComponent(url);
    var encodedTitle = encodeURIComponent(title);
    setLink("[data-share-mastodon]", "https://share.joinmastodon.org/#text=" + encodeURIComponent(title + " " + url));
    setLink("[data-share-telegram]", "https://t.me/share/url?url=" + encodedUrl + "&text=" + encodedTitle);
    setLink("[data-share-x]", "https://twitter.com/intent/tweet?url=" + encodedUrl + "&text=" + encodedTitle);
    setLink("[data-share-email]", "mailto:?subject=" + encodedTitle + "&body=" + encodedUrl);

    toggle.addEventListener("click", function () {
      var expanded = toggle.getAttribute("aria-expanded") === "true";
      toggle.setAttribute("aria-expanded", String(!expanded));
      options.hidden = expanded;
      if (!expanded) setStatus("");
    });

    if (navigator.share) {
      nativeButton.hidden = false;
      nativeButton.addEventListener("click", function () {
        navigator.share({ title: title, text: title, url: url }).catch(function (error) {
          if (error && error.name !== "AbortError") setStatus("Não foi possível abrir o compartilhamento.");
        });
      });
    }

;
  } catch (error) {
    // Compartilhamento é opcional e não deve afetar a leitura.
  }
})();
