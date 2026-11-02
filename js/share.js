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
    var copy = root.querySelector("[data-share-copy]");
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
    setLink("[data-share-whatsapp]", "https://wa.me/?text=" + encodedTitle + "%20" + encodedUrl);
    setLink("[data-share-telegram]", "https://t.me/share/url?url=" + encodedUrl + "&text=" + encodedTitle);
    setLink("[data-share-x]", "https://twitter.com/intent/tweet?url=" + encodedUrl + "&text=" + encodedTitle);
    setLink("[data-share-facebook]", "https://www.facebook.com/sharer/sharer.php?u=" + encodedUrl);
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

    copy.addEventListener("click", function () {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(url).then(function () {
          setStatus("Link copiado.");
        }).catch(function () {
          setStatus("Não foi possível copiar automaticamente. Copie o endereço do navegador.");
        });
      } else {
        setStatus("Seu navegador não permite cópia automática. Copie o endereço do navegador.");
      }
    });
  } catch (error) {
    // Compartilhamento é opcional e não deve afetar a leitura.
  }
})();
