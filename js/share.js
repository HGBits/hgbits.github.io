// SPDX-License-Identifier: GPL-3.0-only
// Copyright (C) 2026 hgbits <https://github.com/HGBits>
/* share.js — hgbits
 * Compartilhamento progressivo com destinos externos e Web Share API.
 */
(function () {
  "use strict";

  var root = document.querySelector("[data-share]");
  if (!root) return;

  var toggle = root.querySelector(".share-toggle");
  var options = root.querySelector(".share-options");
  var nativeButton = root.querySelector("[data-share-native]");
  var status = root.querySelector("[data-share-status]");
  var pageUrl = window.location.href.split("#")[0];
  var title = document.title.replace(/\s*::\s*hgbits\s*$/, "");

  function setStatus(message) {
    if (status) status.textContent = message;
  }

  function setLink(selector, href) {
    var link = root.querySelector(selector);
    if (link) {
      link.href = href;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
    }
  }

  var encodedUrl = encodeURIComponent(pageUrl);
  var encodedTitle = encodeURIComponent(title);
  setLink("[data-share-telegram]", "https://t.me/share/url?url=" + encodedUrl + "&text=" + encodedTitle);

  var mastodonText = encodeURIComponent(title + " " + pageUrl);
  setLink("[data-share-mastodon]", "https://share.joinmastodon.org/#text=" + mastodonText);

  var xUrl = new URL("https://twitter.com/intent/tweet");
  xUrl.searchParams.set("url", pageUrl);
  xUrl.searchParams.set("text", title);
  setLink("[data-share-x]", xUrl.toString());

  var emailUrl = "mailto:?subject=" + encodeURIComponent(title) +
    "&body=" + encodeURIComponent(pageUrl);
  setLink("[data-share-email]", emailUrl);

  if (toggle && options) {
    toggle.addEventListener("click", function () {
      var expanded = toggle.getAttribute("aria-expanded") === "true";
      toggle.setAttribute("aria-expanded", String(!expanded));
      options.hidden = expanded;
      if (!expanded) setStatus("");
    });
  }

  if (nativeButton && navigator.share) {
    nativeButton.hidden = false;
    nativeButton.addEventListener("click", function () {
      navigator.share({ title: title, text: title, url: pageUrl }).catch(function (error) {
        if (error && error.name !== "AbortError") {
          setStatus("Não foi possível abrir o compartilhamento.");
        }
      });
    });
  }
})();
