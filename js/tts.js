/*
 * tts.js — hgbits
 * Botão "Ouvir post", usando a Web Speech API nativa do navegador.
 * Regras que este arquivo segue à risca:
 *   1. Progressive enhancement: só existe se JS rodar E o navegador
 *      suportar speechSynthesis. Sem isso, nada aparece.
 *   2. Zero rede, zero CDN — speechSynthesis é 100% local.
 *   3. Falha em silêncio: nunca quebra a página.
 */
(function () {
  "use strict";
  try {
    if (!("speechSynthesis" in window)) return;

    var content = document.getElementById("post-content");
    if (!content) return; // só existe em posts

    var text = content.textContent.replace(/\s+/g, " ").trim();
    if (!text) return;

    var wrap = document.createElement("div");
    wrap.className = "tts-wrap";

    var button = document.createElement("button");
    button.type = "button";
    button.className = "tts-button";
    button.textContent = "🔊 Ouvir post";

    wrap.appendChild(button);
    content.parentNode.insertBefore(wrap, content);

    var speaking = false;

    function stop() {
      window.speechSynthesis.cancel();
      speaking = false;
      button.textContent = "🔊 Ouvir post";
      button.classList.remove("tts-active");
    }

    button.addEventListener("click", function () {
      if (speaking) { stop(); return; }
      var utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = "pt-BR";
      utterance.onend = stop;
      utterance.onerror = stop;
      window.speechSynthesis.speak(utterance);
      speaking = true;
      button.textContent = "⏹ Parar leitura";
      button.classList.add("tts-active");
    });

    window.addEventListener("beforeunload", function () {
      window.speechSynthesis.cancel();
    });
  } catch (e) {
    // TTS é extra — nunca deve quebrar a página por causa disto
  }
})();
