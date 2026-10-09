/* charts.js — gráficos Plotly (CDN) com fallback nos PNGs estáticos.
 * Cada gráfico mora numa <div id="chart-..."> com data-json + data-kind.
 * Se o Plotly ou o JSON falharem (ex: sem internet), a div mostra um aviso
 * e os PNGs da página continuam sendo o conteúdo principal.
 */
(function () {
  function fail(id, msg) {
    var el = document.getElementById(id);
    if (el) el.innerHTML = '<p class="chart-offline">' + msg +
      ' Veja as figuras estáticas da página.</p>';
  }

  function bar(id, x, y, title) {
    if (!window.Plotly) return fail(id, "Gráficos interativos exigem internet (CDN Plotly).");
    Plotly.newPlot(id, [{ x: x, y: y, type: "bar" }],
      { title: title, margin: { t: 40, b: 100 }, xaxis: { tickangle: -30 } },
      { responsive: true, displaylogo: false });
  }

  function render(url, draw) {
    fetch(url).then(function (r) {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.json();
    }).then(draw).catch(function () {
      fail(draw._id || "", "Não foi possível carregar os dados do gráfico.");
    });
  }

  function initOlist() {
    if (!document.getElementById("chart-olist-cat")) return;
    render("assets/data/olist_charts.json", function (d) {
      bar("chart-olist-cat",
        d.receita_por_categoria.map(function (r) { return r.categoria; }),
        d.receita_por_categoria.map(function (r) { return r.receita; }),
        "Receita por categoria (amostra)");
      bar("chart-olist-uf",
        d.receita_por_uf.map(function (r) { return r.uf; }),
        d.receita_por_uf.map(function (r) { return r.receita; }),
        "Receita por UF (amostra)");
      if (window.Plotly) {
        Plotly.newPlot("chart-olist-atraso",
          [{ x: d.atraso_vs_review.map(function (r) { return r.faixa_atraso_dias; }),
             y: d.atraso_vs_review.map(function (r) { return r.review_medio; }),
             type: "bar", marker: { color: "#1a5fb4" } }],
          { title: "Review médio por faixa de atraso (amostra)", margin: { t: 40 } },
          { responsive: true, displaylogo: false });
      }
    });
  }

  function initSaude() {
    if (!document.getElementById("chart-diab-idade")) return;
    render("assets/data/diabetes_charts.json", function (d) {
      bar("chart-diab-idade",
        d.prevalencia_por_idade.map(function (r) { return "faixa " + r.faixa_etaria; }),
        d.prevalencia_por_idade.map(function (r) { return r.prevalencia; }),
        "Prevalência de diabetes por faixa etária (amostra)");
      if (window.Plotly) {
        var ks = Object.keys(d.fatores);
        Plotly.newPlot("chart-diab-fatores", [
          { x: ks, y: ks.map(function (k) { return d.fatores[k].com_fator; }),
            name: "com fator", type: "bar" },
          { x: ks, y: ks.map(function (k) { return d.fatores[k].sem_fator; }),
            name: "sem fator", type: "bar" }
        ], { title: "Prevalência com/sem cada fator (amostra)", barmode: "group", margin: { t: 40, b: 100 } },
        { responsive: true, displaylogo: false });
      }
    });
  }

  function initFraude() {
    if (!document.getElementById("chart-fraude-pr")) return;
    render("assets/data/fraud_threshold.json", function (d) {
      if (!window.Plotly) return fail("chart-fraude-pr", "Gráficos interativos exigem internet (CDN Plotly).");
      var s = d.sweep;
      Plotly.newPlot("chart-fraude-pr", [
        { x: s.map(function (r) { return r.threshold; }),
          y: s.map(function (r) { return r.precision; }), name: "precision", mode: "lines+markers" },
        { x: s.map(function (r) { return r.threshold; }),
          y: s.map(function (r) { return r.recall; }), name: "recall", mode: "lines+markers" }
      ], { title: "Precision/recall vs limiar (dados reais)", margin: { t: 40 } },
      { responsive: true, displaylogo: false });
      Plotly.newPlot("chart-fraude-custo",
        [{ x: s.map(function (r) { return r.threshold; }),
           y: s.map(function (r) { return r.custo; }), mode: "lines+markers",
           marker: { color: "#c01c28" } }],
        { title: "Custo esperado vs limiar (FP=10, FN=500)", margin: { t: 40 } },
        { responsive: true, displaylogo: false });
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    initOlist(); initSaude(); initFraude();
  });
})();
