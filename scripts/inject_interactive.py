"""Injeta o painel interativo + scripts nas páginas exportadas pelo nbconvert.

Idempotente: só injeta o que ainda não está lá (marcadores por página).
Chamado pelo run_all.sh (etapa 4) e documentado no README como fallback.

Uso: python3 scripts/inject_interactive.py
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"

SCRIPTS = """  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js" defer></script>
  <script src="assets/js/tables.js" defer></script>
  <script src="assets/js/charts.js" defer></script>
  <script src="assets/js/simulators.js" defer></script>"""

PANELS = {
    "ecommerce.html": """<section>
<h2>Painel interativo — explore, visualize, simule</h2>
    <p><label>Busca global nas tabelas:
    <input type="search" id="global-table-filter" placeholder="ex: SP, cama_mesa_banho, 5.0…"></label>
    <small>Todas as tabelas da página também ganham busca própria e ordenação por clique no cabeçalho.</small></p>
    <h3>Gráficos vivos (requer internet — CDN Plotly; sem internet, veja as figuras estáticas)</h3>
    <div id="chart-olist-cat" class="interactive-chart"></div>
    <div id="chart-olist-uf" class="interactive-chart"></div>
    <div id="chart-olist-atraso" class="interactive-chart"></div>
    <div class="sim-box" id="sim-atraso">
      <h3>Simulador SAD — tolerância ao atraso</h3>
      <p>E se a operação tolerar no máximo <output id="sim-atraso-val">7</output> dias de atraso?</p>
      <input type="range" min="0" max="30" step="1" value="7"
             oninput="document.getElementById('sim-atraso-val').textContent = this.value"
             aria-label="Atraso máximo tolerado em dias">
      <p class="sim-result">Carregando…</p>
    </div>
</section>
""",
    "saude.html": """<section>
<h2>Painel interativo — explore, visualize, simule</h2>
<p><label>Busca global nas tabelas:
<input type="search" id="global-table-filter" placeholder="ex: 1, 30, faixa…"></label>
<small>Todas as tabelas ganham busca própria e ordenação por clique no cabeçalho.</small></p>
<h3>Gráficos vivos (requer internet — CDN Plotly; sem internet, veja as figuras estáticas)</h3>
<div id="chart-diab-idade" class="interactive-chart"></div>
<div id="chart-diab-fatores" class="interactive-chart"></div>
<div class="sim-box" id="sim-risco">
<h3>Simulador SAD — faixa de risco</h3>
<p>Preencha e veja a faixa pela regra de triagem da análise:</p>
<label>IMC: <input type="number" id="sim-imc" value="27" min="10" max="60" step="0.1"></label>
<label>Idade: <input type="number" id="sim-idade" value="55" min="18" max="100" step="1"></label>
<label>Pressão alta: <select id="sim-pa"><option value="nao">Não</option><option value="sim" selected>Sim</option></select></label>
<label>Colesterol alto: <select id="sim-col"><option value="nao">Não</option><option value="sim" selected>Sim</option></select></label>
<label>Sedentário: <select id="sim-sed"><option value="nao">Não</option><option value="sim" selected>Sim</option></select></label>
<p class="sim-result">Carregando…</p>
</div>
</section>
""",
    "fraude.html": """<section>
<h2>Painel interativo — explore, visualize, simule</h2>
<p><label>Busca global nas tabelas:
<input type="search" id="global-table-filter" placeholder="ex: 0.98, 500, recall…"></label>
<small>Todas as tabelas ganham busca própria e ordenação por clique no cabeçalho.</small></p>
<h3>Gráficos vivos (requer internet — CDN Plotly; sem internet, veja as figuras estáticas)</h3>
<div id="chart-fraude-pr" class="interactive-chart"></div>
<div id="chart-fraude-custo" class="interactive-chart"></div>
<div class="sim-box" id="sim-limiar">
<h3>Simulador SAD — limiar de decisão</h3>
<p>E se o limiar de bloqueio for <output id="sim-limiar-val">0.98</output>?</p>
<input type="range" min="0.05" max="0.99" step="0.01" value="0.98"
       oninput="document.getElementById('sim-limiar-val').textContent = (+this.value).toFixed(2)"
       aria-label="Limiar de decisão do escore de fraude">
<p class="sim-result">Carregando…</p>
</div>
</section>
""",
}

MARKERS = {
    "ecommerce.html": "chart-olist-cat",
    "saude.html": "chart-diab-idade",
    "fraude.html": "chart-fraude-pr",
}


def main():
    for page, panel in PANELS.items():
        p = DOCS / page
        text = p.read_text(encoding="utf-8")
        changed = False
        if MARKERS[page] not in text:
            n = text.count("</main>")
            if n != 1:
                raise SystemExit(
                    f"{page}: esperado 1 </main>, achado {n} — "
                    "rode o export do nbconvert de novo?"
                )
            text = text.replace("</main>", panel + "</main>", 1)
            changed = True
        if "cdn.plot.ly" not in text:
            n = text.count("</body>")
            if n != 1:
                raise SystemExit(
                    f"{page}: esperado 1 </body>, achado {n} — "
                    "rode o export do nbconvert de novo?"
                )
            text = text.replace("</body>", SCRIPTS + "\n</body>", 1)
            changed = True
        if changed:
            p.write_text(text, encoding="utf-8")
        print(f"{'injetado' if changed else 'ok (já tinha)'}: {page}")


if __name__ == "__main__":
    main()
