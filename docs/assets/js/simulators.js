/* simulators.js — mini-SAD no navegador (zero dependências).
 * 3 simuladores, um por página; cada bloco só ativa se o seu <section>
 * existir. Todos leem os mesmos JSONs dos gráficos (ver fonte em cada um).
 */
(function () {
  function get(url) {
    return fetch(url).then(function (r) {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.json();
    });
  }

  // E-commerce: "e se eu tolerar no máximo X dias de atraso?"
  function initAtraso() {
    var root = document.getElementById("sim-atraso");
    if (!root) return;
    var slider = root.querySelector('input[type="range"]');
    var out = root.querySelector(".sim-result");
    if (!slider || !out) return;
    get("assets/data/olist_charts.json").then(function (d) {
      function update() {
        var max = parseFloat(slider.value);
        var afet = d.delays.filter(function (x) { return x > max; });
        var pct = d.delays.length ? (100 * afet.length / d.delays.length) : 0;
        out.innerHTML = "Pedidos com atraso &gt; <b>" + max + " dias</b>: <b>" +
          afet.length + "</b> de " + d.delays.length + " (" + pct.toFixed(1) +
          "%) — <i>SE o atraso &gt; " + max + " dias derruba a nota, ENTÃO " +
          "esses pedidos pedem estoque regional ou frete prioritário.</i> " +
          "<br><small>Base: amostra de 200 pedidos reais (Olist) — 196 com atraso calculado; 4 sem data.</small>";
      }
      slider.addEventListener("input", update);
      update();
    }).catch(function () {
      out.textContent = "Simulador indisponível offline (precisa do JSON local via http/https).";
    });
  }

  // Saúde: calculadora de faixa de risco pela regra de triagem da página.
  function initRisco() {
    var root = document.getElementById("sim-risco");
    if (!root) return;
    var out = root.querySelector(".sim-result");
    if (!out) return;
    function update() {
      var v = function (id) {
        var el = root.querySelector("#" + id);
        return el ? el.value : "";
      };
      var imc = parseFloat(v("sim-imc")) || 0;
      var idade = parseInt(v("sim-idade"), 10) || 0;
      var pa = v("sim-pa") === "sim";
      var col = v("sim-col") === "sim";
      var sed = v("sim-sed") === "sim";
      var pontos = 0;
      if (pa && col && idade >= 55) pontos += 2;
      if (imc >= 30 && sed) pontos += 2;
      if (imc >= 30 || sed || pa || col) pontos += 1;
      var faixa = pontos >= 3 ? "PRIORITÁRIO — encaminhar ao rastreio" :
        pontos >= 1 ? "ATENÇÃO — reavaliar em 6–12 meses" : "RISCO BAIXO — rotina";
      out.innerHTML = "Faixa: <b>" + faixa + "</b> (" + pontos + " pts). " +
        "<i>Regra da análise: SE pressão+colesterol+idade avançada OU (IMC ≥ 30 + sedentarismo), " +
        "ENTÃO priorizar.</i><br><small>Educacional, sobre amostra real — não é diagnóstico.</small>";
    }
    root.querySelectorAll("input, select").forEach(function (el) {
      el.addEventListener("input", update);
    });
    update();
  }

  // Fraude: "e se o limiar for X?" — usa o sweep real (FP=10, FN=500).
  function initLimiar() {
    var root = document.getElementById("sim-limiar");
    if (!root) return;
    var slider = root.querySelector('input[type="range"]');
    var out = root.querySelector(".sim-result");
    if (!slider || !out) return;
    get("assets/data/fraud_threshold.json").then(function (d) {
      function nearest(x) {
        return d.sweep.reduce(function (a, b) {
          return Math.abs(b.threshold - x) < Math.abs(a.threshold - x) ? b : a;
        });
      }
      function update() {
        var x = parseFloat(slider.value);
        var r = nearest(x);
        var tag = r.threshold === d.recomendado ? " ★ mínimo" : "";
        out.innerHTML = "Limiar <b>" + r.threshold.toFixed(2) + "</b>" + tag +
          ": precision <b>" + r.precision + "</b>, recall <b>" + r.recall +
          "</b>, FP " + r.fp + ", FN " + r.fn + ", custo <b>" + r.custo + "</b>. " +
          "<i>SE escore &gt; limiar ENTÃO step-up (revisão), SENÃO aprovar.</i>" +
          "<br><small>Sweep com dados reais; custos FP=10, FN=500.</small>";
      }
      slider.addEventListener("input", update);
      update();
    }).catch(function () {
      out.textContent = "Simulador indisponível offline (precisa do JSON local via http/https).";
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    initAtraso(); initRisco(); initLimiar();
  });
})();
