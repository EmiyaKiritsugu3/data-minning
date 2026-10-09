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
4. Sirva localmente: `python -m http.server 8000 --directory docs`
   e abra `http://localhost:8000/`.
