#!/usr/bin/env bash
set -e

if [ ! -d "data" ] || [ -z "$(ls -A data 2>/dev/null)" ]; then
  echo "ERRO: pasta data/ vazia ou inexistente." >&2
  echo "Baixe os CSVs do Kaggle (Olist, Diabetes, Credit Card Fraud) e coloque-os em data/." >&2
  echo "A pasta data/ e propositalmente gitignored: os dados brutos nunca sao commitados." >&2
  exit 1
fi

# 1. Executa os notebooks in-place (regenera as figuras em docs/assets/img via save_fig).
jupyter nbconvert --to notebook --execute --inplace notebooks/01_ecommerce.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/02_saude.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/03_fraude.ipynb

# 2. Exporta cada notebook para a sua pagina em docs/.
jupyter nbconvert --to html --output-dir docs --output ecommerce.html notebooks/01_ecommerce.ipynb
jupyter nbconvert --to html --output-dir docs --output saude.html notebooks/02_saude.ipynb
jupyter nbconvert --to html --output-dir docs --output fraude.html notebooks/03_fraude.ipynb

# 3. Injeta o CSS do site + cabecalho de navegacao padrao nas paginas exportadas
# (o export cru do nbconvert nao inclui nem o stylesheet nem o <header> do site).
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

echo "OK: notebooks executados e paginas regeneradas em docs/."
