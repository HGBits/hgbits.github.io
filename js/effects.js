/*
 * effects.js — hgbits
 * Único efeito visual do site: scanline/CRT sutil de fundo.
 * Regras que este arquivo segue à risca:
 *   1. Nunca carrega/altera conteúdo. Só desenha por cima, decorativo.
 *   2. Sem CDN, sem fetch de rede, sem tracking. 100% local.
 *   3. Se falhar por qualquer motivo, falha em silêncio — a página
 *      já é 100% funcional sem isto (é assim que ela chega pra quem
 *      usa lynx/w3m ou navega com JS desligado).
 *   4. Respeita prefers-reduced-motion: sem isso, desenha o efeito
 *      estático, sem animação.
 */
(function () {
  "use strict";
  try {
    var reduceMotion =
      window.matchMedia &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    var canvas = document.createElement("canvas");
    canvas.id = "crt-overlay";
    canvas.setAttribute("aria-hidden", "true");
    document.body.appendChild(canvas);

    var ctx = canvas.getContext("2d");
    if (!ctx) return;

    function resize() {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    }

    function drawScanlines() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = "rgba(0, 0, 0, 0.12)";
      for (var y = 0; y < canvas.height; y += 3) {
        ctx.fillRect(0, y, canvas.width, 1);
      }
    }

    var sweepY = 0;
    function drawSweep() {
      var grad = ctx.createLinearGradient(0, sweepY - 50, 0, sweepY + 50);
      grad.addColorStop(0, "rgba(46, 125, 214, 0)");
      grad.addColorStop(0.5, "rgba(46, 125, 214, 0.05)");
      grad.addColorStop(1, "rgba(46, 125, 214, 0)");
      ctx.fillStyle = grad;
      ctx.fillRect(0, sweepY - 50, canvas.width, 100);
      sweepY += 1.2;
      if (sweepY > canvas.height + 50) sweepY = -50;
    }

    resize();
    window.addEventListener("resize", resize);

    if (reduceMotion) {
      drawScanlines(); // desenha uma vez, estático, sem loop de animação
      return;
    }

    function frame() {
      drawScanlines();
      drawSweep();
      requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  } catch (e) {
    // efeito cosmético — nunca deve travar a página por causa disto
  }
})();
