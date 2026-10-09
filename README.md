# SAD — Mineração de Dados (GH Pages)

Site estático com 3 análises de mineração de dados em datasets do Kaggle,
para a disciplina de Sistemas de Apoio à Decisão (SAD):

- **E-commerce (Olist):** segmentação de clientes e padrões de compra.
- **Saúde (Diabetes):** classificação e fatores de risco.
- **Fraude (cartão de crédito):** detecção de transações anômalas.

## Estrutura

- `src/common.py` — utilidades (`load_csv`, `save_fig`, `df_to_html_table`).
- `src/mining.py` — mineração (`run_kmeans`, `run_tree`, `confusion_summary`).
- `notebooks/` — análises por dataset (geram as páginas em `docs/`).
- `docs/` — site publicado via GitHub Pages (branch `main`, pasta `/docs`).
- `data/` — **não versionado** (CSV brutos do Kaggle; ver `.gitignore`).

## Como reproduzir

1. Baixe os CSVs do Kaggle e coloque-os em `data/` (a pasta é gitignored).
2. `pip install -r requirements.txt`
3. `./run_all.sh` — executa os notebooks e regenera as páginas em `docs/`.
4. `python3 scripts/build_interactive_data.py` — regenera os JSONs dos
   painéis interativos (`docs/assets/data/*_charts.json`, `fraud_threshold.json`).
   O `run_all.sh` já executa este passo + `scripts/inject_interactive.py`
   (reaplica painel interativo e scripts após o export cru do nbconvert);
   rode-os manualmente se pular o `run_all.sh`. A sweep de fraude é
   extraída de `docs/fraude.html`.
5. Sirva localmente: `python -m http.server 8000 --directory docs`
   e abra `http://localhost:8000/`.

## Export manual (fallback sem `./run_all.sh`)

Se preferir rodar passo a passo, estes são os comandos exatos que o
`run_all.sh` executa:

```bash
# 1. Executa os notebooks in-place (regenera as figuras em docs/assets/img)
jupyter nbconvert --to notebook --execute --inplace notebooks/01_ecommerce.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/02_saude.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/03_fraude.ipynb

# 2. Exporta cada notebook para a sua página em docs/
jupyter nbconvert --to html --output-dir docs --output ecommerce.html notebooks/01_ecommerce.ipynb
jupyter nbconvert --to html --output-dir docs --output saude.html notebooks/02_saude.ipynb
jupyter nbconvert --to html --output-dir docs --output fraude.html notebooks/03_fraude.ipynb
```

```bash
# 3. Injeta o CSS do site + cabeçalho de navegação padrão nas páginas
# exportadas (o export cru do nbconvert não os inclui).
python3 - <<'EOF'
import re
from pathlib import Path

HEADER = """  <header>
    <h1>Sistemas de Apoio à Decisão — Mineração de Dados</h1>
    <nav>
      <ul>
        <li><a href="index.html">Início</a></li>
        <li><a href="ecommerce.html">E-commerce (Olist)</a></li>
        <li><a href="saude.html">Saúde (Diabetes)</a></li>
        <li><a href="fraude.html">Fraude (Cartão de Crédito)</a></li>
        <li><a href="relatorio.html">Relatório</a></li>
      </ul>
    </nav>
  </header>"""

for page in ["docs/ecommerce.html", "docs/saude.html", "docs/fraude.html"]:
    p = Path(page)
    text = p.read_text(encoding="utf-8")
    if "assets/css/style.css" not in text:
        text = text.replace(
            "</head>",
            '  <link rel="stylesheet" href="assets/css/style.css">\n</head>',
            1,
        )
    if "<header>" not in text:
        text, n = re.subn(r"(<body[^>]*>)", r"\1\n" + HEADER, text, count=1)
        assert n == 1, f"sem tag <body> em {page}"
    p.write_text(text, encoding="utf-8")
    print(f"injetado: {page}")
EOF
```
