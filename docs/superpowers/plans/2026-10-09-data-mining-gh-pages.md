# Data Mining 3 Datasets + GH Pages Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publicar em GH Pages um site estático com 3 análises de Data Mining (Olist, Diabetes, Fraude) + relatório consolidado.

**Architecture:** Notebooks executados localmente via Kaggle API geram PNGs/tabelas; script de export monta HTML estático em `docs/` servido pelo GH Pages sem backend nem CDN.

**Tech Stack:** Python 3.11, pandas, numpy, matplotlib, seaborn, scikit-learn, mlxtend, jupyter/nbconvert

**Spec:** `docs/superpowers/specs/2026-10-09-data-mining-gh-pages-design.md`

## Global Constraints

- Hospedagem GH Pages: branch `main`, pasta `/docs`, sem build, sem backend.
- CSS/JS 100% locais (sem CDN) para funcionar na rede da faculdade.
- CSVs crus nunca commitados (`data/` gitignored); só amostras ≤200KB em `docs/assets/data/`.
- Cada página de análise tem ≥6 figuras, ≥3 tabelas, ≥3 recomendações "se → então".
- `requirements.txt` com versões fixas; `run_all.sh` reproduz tudo headless.

## Review Focus

- Dataset do Kaggle mudou de schema/colunas e quebra o notebook — espera-se erro legível citando coluna ausente, não traceback cru no site.
- `data/` vazio (sem `kaggle.json`) e `run_all.sh` roda — espera-se mensagem instruindo download em vez de falha silenciosa.
- Figura ausente em `docs/assets/img/` mas HTML referencia — espera-se teste que falha antes do push.
- Amostra em `docs/assets/data/` >200KB commitada por acidente — espera-se teste de tamanho que barra.
- Abrir `docs/index.html` via `file://` ou Pages sem CSS — espera-se CSS com caminho relativo funcionando nos dois.

---

### Task 1: Scaffold do repo + base do site

**Files:**
- Create: `README.md`, `.gitignore`, `requirements.txt`, `run_all.sh`
- Create: `src/common.py`, `src/mining.py`
- Create: `docs/index.html`, `docs/assets/css/style.css`
- Test: `tests/test_scaffold.py`

**Interfaces:**
- Consumes: nada (primeira task).
- Produces:
  - `src.common: load_csv(path: str) -> DataFrame`, `save_fig(fig, name: str) -> str`, `df_to_html_table(df: DataFrame, max_rows: int = 20) -> str`
  - `src.mining: run_kmeans(X: DataFrame, k: int, seed: int = 42) -> tuple[labels, model]`, `run_tree(X_train, y_train) -> model`, `confusion_summary(y_true, y_pred) -> dict`

- [ ] **Step 1: Write the failing test**

```python
def test_scaffold_files_exist():
    for p in ["README.md", ".gitignore", "requirements.txt", "run_all.sh",
              "src/common.py", "src/mining.py",
              "docs/index.html", "docs/assets/css/style.css"]:
        assert Path(p).exists(), f"missing {p}"

def test_common_signatures():
    import src.common as c, src.mining as m
    assert callable(c.load_csv) and callable(c.save_fig) and callable(c.df_to_html_table)
    assert callable(m.run_kmeans) and callable(m.run_tree) and callable(m.confusion_summary)

def test_data_gitignored():
    assert Path(".gitignore").read_text().split().__contains__("data/")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_scaffold.py -v`
Expected: FAIL (files not defined)

- [ ] **Step 3: Implement scaffold**

Criar `.gitignore` com `data/`, `__pycache__/`, `.ipynb_checkpoints/`; `requirements.txt` pinado (pandas==2.2.3, numpy==1.26.4, matplotlib==3.8.4, seaborn==0.13.2, scikit-learn==1.5.2, mlxtend==0.23.1, jupyter==1.1.0, nbconvert==7.16.4); `src/common.py` e `src/mining.py` com as assinaturas acima (corpos mínimos); `docs/index.html` esqueleto com nav para as 4 páginas + link CSS relativo `assets/css/style.css`; `run_all.sh` com `set -e` + checagem de `data/` vazio com mensagem de Kaggle.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_scaffold.py -v`
Expected: PASS

- [ ] **Step 5: Verify site base opens locally**

Run: `python -m http.server 8000 --directory docs` e abrir `http://localhost:8000/`
Expected: index renderiza com CSS aplicado, links para ecommerce/saude/fraude/relatorio (podem 404 por enquanto)

- [ ] **Step 6: Commit**

```bash
git add README.md .gitignore requirements.txt run_all.sh src/common.py src/mining.py docs/index.html docs/assets/css/style.css tests/test_scaffold.py
git commit -m "feat: scaffold repo, src base e esqueleto GH Pages"
```

### Task 2: Análise Olist (notebook + página)

**Files:**
- Create: `notebooks/01_ecommerce.ipynb`, `docs/ecommerce.html`, `docs/assets/img/olist_*.png`, `docs/assets/data/sample_olist.csv`
- Test: `tests/test_olist.py`

**Interfaces:**
- Consumes: `src.common.load_csv/save_fig/df_to_html_table`, `src.mining.run_kmeans/run_tree/confusion_summary` da Task 1.
- Produces: `docs/ecommerce.html` + 6–8 PNGs `olist_*` + sample ≤200KB; bloco de decisão com 3–4 recomendações.

- [ ] **Step 1: Write the failing test**

```python
def test_olist_outputs():
    assert Path("docs/ecommerce.html").exists()
    figs = list(Path("docs/assets/img").glob("olist_*.png"))
    assert len(figs) >= 6, f"só {len(figs)} figs olist"
    html = Path("docs/ecommerce.html").read_text()
    assert "KMeans" in html and "confus" in html.lower()
    assert html.count("<table") >= 3
    assert "recomenda" in html.lower()
    assert Path("docs/assets/data/sample_olist.csv").stat().st_size <= 200*1024
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_olist.py -v`
Expected: FAIL (notebook/página ainda não existem)

- [ ] **Step 3: Implement `notebooks/01_ecommerce.ipynb`**

Fonte `olistbr/brazilian-ecommerce` via `kaggle datasets download`. Blocos: entendimento (dicionário 9 CSVs) → preparação (join orders/order_items/customers, trata nulos de `order_delivered_*`, outlier de frete/preço) → EDA (atraso vs review_score, receita por categoria/UF, frete vs distância aprox., 6–8 figs `olist_*` via `save_fig`) → mineração (`run_kmeans` em RFM de clientes k=4, `run_tree` prevendo `review_score>=4` ou atraso binário + `confusion_summary`, co-ocorrência de categorias como associação) → decisão (3–4 "se → então", ex: se atraso>X e UF=Y então reforça CD).

- [ ] **Step 4: Exportar para `docs/ecommerce.html` + amostra**

Run: `jupyter nbconvert --to html notebooks/01_ecommerce.ipynb --output-dir docs --output ecommerce.html` e gerar `sample_olist.csv` com 200 linhas. Injetar link CSS local + nav padrão no topo do HTML (mesmo header do index).
Expected: `docs/ecommerce.html` abre com CSS, figuras visíveis, ≥3 tabelas.

- [ ] **Step 5: Run test to verify it passes**

Run: `python -m pytest tests/test_olist.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add notebooks/01_ecommerce.ipynb docs/ecommerce.html docs/assets/img/olist_*.png docs/assets/data/sample_olist.csv tests/test_olist.py
git commit -m "feat: análise Olist EDA + mineração + página"
```

### Task 3: Análise Diabetes (notebook + página)

**Files:**
- Create: `notebooks/02_saude.ipynb`, `docs/saude.html`, `docs/assets/img/diabetes_*.png`, `docs/assets/data/sample_diabetes.csv`
- Test: `tests/test_diabetes.py`

**Interfaces:**
- Consumes: mesmas funções da Task 1; template de blocos da Task 2.
- Produces: `docs/saude.html` + 6–8 PNGs `diabetes_*`; top-5 fatores + regra de triagem.

- [ ] **Step 1: Write the failing test**

```python
def test_diabetes_outputs():
    assert Path("docs/saude.html").exists()
    figs = list(Path("docs/assets/img").glob("diabetes_*.png"))
    assert len(figs) >= 6
    html = Path("docs/saude.html").read_text()
    assert "KMeans" in html and "confus" in html.lower()
    assert html.count("<table") >= 3
    assert "recomenda" in html.lower()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_diabetes.py -v`
Expected: FAIL

- [ ] **Step 3: Implement `notebooks/02_saude.ipynb`**

Fonte `alexteboul/diabetes-health-indicators-dataset`. Preparação (balanceamento documentado, encoding binário) → EDA (prevalência por idade/pressão/colesterol/atividade, correlações) → mineração (`run_kmeans` k=3 perfis de risco, `run_tree` prevendo `Diabetes_binary` + importância top-5 + `confusion_summary`, discretização + Apriori mlxtend em fatores) → decisão (regra de triagem + 3 prevenções priorizadas).

- [ ] **Step 4: Exportar para `docs/saude.html`**

Run: `jupyter nbconvert --to html notebooks/02_saude.ipynb --output-dir docs --output saude.html` + sample 200 linhas + header/nav/CSS local.
Expected: página renderiza com CSS e figuras.

- [ ] **Step 5: Run test to verify it passes**

Run: `python -m pytest tests/test_diabetes.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add notebooks/02_saude.ipynb docs/saude.html docs/assets/img/diabetes_*.png docs/assets/data/sample_diabetes.csv tests/test_diabetes.py
git commit -m "feat: análise Diabetes EDA + mineração + página"
```

### Task 4: Análise Fraude (notebook + página)

**Files:**
- Create: `notebooks/03_fraude.ipynb`, `docs/fraude.html`, `docs/assets/img/fraud_*.png`, `docs/assets/data/sample_fraud.csv`
- Test: `tests/test_fraude.py`

**Interfaces:**
- Consumes: mesmas funções da Task 1; template das Tasks 2–3.
- Produces: `docs/fraude.html` + 6–8 PNGs `fraud_*`; análise de limiar (precision/recall vs custo).

- [ ] **Step 1: Write the failing test**

```python
def test_fraude_outputs():
    assert Path("docs/fraude.html").exists()
    figs = list(Path("docs/assets/img").glob("fraud_*.png"))
    assert len(figs) >= 6
    html = Path("docs/fraude.html").read_text().lower()
    assert "kmeans" in html and "confus" in html
    assert "recomenda" in html
    assert "limiar" in html or "threshold" in html
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_fraude.py -v`
Expected: FAIL

- [ ] **Step 3: Implement `notebooks/03_fraude.ipynb`**

Fonte `mlg-ulb/creditcardfraud` (284k, 0.17% fraude; se RAM estourar, amostra estratificada 50k documentada). EDA (distribuição Amount/Time, V1–V28, desbalanceamento) → mineração (`run_kmeans` em subamostra para perfis, `run_tree`/logística com `class_weight=balanced` + `confusion_summary` + curva precision/recall por limiar, tabela custo FP vs FN) → decisão (limiar recomendado + regra "se score>X então step-up").

- [ ] **Step 4: Exportar para `docs/fraude.html`**

Run: `jupyter nbconvert --to html notebooks/03_fraude.ipynb --output-dir docs --output fraude.html` + sample + header/nav/CSS.
Expected: página renderiza com análise de limiar visível.

- [ ] **Step 5: Run test to verify it passes**

Run: `python -m pytest tests/test_fraude.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add notebooks/03_fraude.ipynb docs/fraude.html docs/assets/img/fraud_*.png docs/assets/data/sample_fraud.csv tests/test_fraude.py
git commit -m "feat: análise Fraude EDA + mineração + página"
```

### Task 5: Home comparativa + relatório + publish Pages

**Files:**
- Modify: `docs/index.html`
- Create: `docs/relatorio.html`
- Test: `tests/test_site.py`

**Interfaces:**
- Consumes: `docs/{ecommerce,saude,fraude}.html` das Tasks 2–4.
- Produces: `docs/index.html` final + `docs/relatorio.html`; site pronto p/ Settings → Pages → main /docs.

- [ ] **Step 1: Write the failing test**

```python
def test_site_integrity():
    for p in ["docs/index.html", "docs/ecommerce.html", "docs/saude.html",
              "docs/fraude.html", "docs/relatorio.html"]:
        assert Path(p).exists(), p
    # sem CDN obrigatório
    for p in Path("docs").glob("*.html"):
        assert "cdn." not in p.read_text().lower() and "unpkg" not in p.read_text().lower(), p
    # figuras referenciadas existem
    import re
    for p in Path("docs").glob("*.html"):
        for img in re.findall(r'assets/img/[\w.\-]+', p.read_text()):
            assert (Path("docs")/img).exists(), f"{p}: {img}"
    # amostras pequenas
    for s in Path("docs/assets/data").glob("*.csv"):
        assert s.stat().st_size <= 200*1024, s
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_site.py -v`
Expected: FAIL (index/relatório ainda esqueletos)

- [ ] **Step 3: Implement `index.html` final + `relatorio.html`**

`index.html`: cards dos 3 casos (volume, técnica, 1 insight-holofote cada) + tabela comparativa SAD (domínio, decisão-tipo, dado-gargalo, técnica que mais rendeu). `relatorio.html`: o que é comum nos 3 (desbalanceamento, top-correlações, clusters), o que difere, limitações e "com mais tempo". Nav consistente nas 5 páginas, CSS relativo.

- [ ] **Step 4: Run full suite + local serve**

Run: `python -m pytest tests/ -v`
Expected: todos PASS. Depois `python -m http.server 8000 --directory docs` e clicar nas 5 páginas: CSS ok, imagens ok, sem 404.

- [ ] **Step 5: Commit + push + ligar Pages**

```bash
git add docs/index.html docs/relatorio.html tests/test_site.py
git commit -m "feat: home comparativa, relatório e integridade do site"
git push origin main
```

Depois: no GitHub, Settings → Pages → Deploy from branch → `main` + `/docs`. URL esperada `https://emiyakiritsugu3.github.io/data-minning/`.
