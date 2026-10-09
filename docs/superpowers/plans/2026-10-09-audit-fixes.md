# Audit Fixes (PR #2) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix all CRITICAL audit findings on branch `feat/dados-reais` (PR #2) so the three analyses use real Kaggle data with sound methodology and the site renders correctly on GH Pages.

**Architecture:** Methodology fixes inside the two notebooks (group split, raw totals, null-delay flag, split-before-undersample) with full re-execution; pipeline hardening in `scripts/` + `src/`; Pages-path + stale-number refresh across `docs/`; tests hardened first so every fix has a failing-then-passing gate.

**Tech Stack:** Python 3.14, pandas, scikit-learn (GroupShuffleSplit), mlxtend (apriori, unchanged), Plotly 2.35.2 pinned CDN, vanilla JS

**Spec:** Audit reports (binding evidence):
- `.superpowers/sdd/2026-10-09-data-mining-gh-pages/audit-olist-report.md`
- `.superpowers/sdd/2026-10-09-data-mining-gh-pages/audit-saude-fraude-report.md`
- `.superpowers/sdd/2026-10-09-data-mining-gh-pages/audit-scripts-src-report.md`
- `.superpowers/sdd/2026-10-09-data-mining-gh-pages/audit-site-report.md`

Doc refs (Context7): sklearn `GroupShuffleSplit.split(X, y, groups)` (`/websites/scikit-learn_stable` docs — group-safe splits); Plotly README (`/plotly/plotly.js` — v2+ CDN requires pinned version, ours `plotly-2.35.2.min.js` is conformant); mlxtend `apriori(df, min_support, use_colnames)` (`/rasbt/mlxtend` — semantics confirmed, no change needed).

## Global Constraints

- Branch `feat/dados-reais`, PR #2 open (`feat/dados-reais` → `main`); implementers commit, NEVER push (controller pushes once at the end).
- `data/` (314MB real CSVs) is gitignored — never `git add` it; re-execution requires it present.
- Every published number must come from a committed executed cell output — inventing metrics is forbidden; methodology-fix tasks WILL change acc values (0.75, 0.655), Task 5 reads them from outputs.
- `docs/` is the Pages root: no `..` escapes in `src`/`href`; all refs relative (`assets/...`).
- Full suite green before every commit; `node --check` on touched JS; `bash -n` on touched `run_all.sh`.

## Review Focus

- Re-exported `saude.html`/`fraude.html` silently dropping panel/scripts/title/nav — Task 3/5 verify markers post-export; test: `test_pages_load_plotly_and_local_js`.
- JSON key drift vs `charts.js`/`simulators.js` readers — Task 1 adds key-contract test; Task 4 must keep key names byte-identical.
- `../docs/` refs reintroduced by notebook display strings — Task 1 bans `..` in tests; Task 3 uses `save_fig` return verbatim.
- Fallback-mode (no `data/`) claims real provenance — Task 3 gates sample/prose on an `is_real` flag; test pins it.
- Rebalanced test set presented at real prevalence — Task 3 asserts holdout prevalence ≈ 0.139 ± 0.02.

---

### Task 1: Harden the test gates (RED first)

**Files:**
- Modify: `tests/test_site.py`, `tests/test_interactive.py`

**Interfaces:**
- Consumes: nothing.
- Produces: failing gates that Tasks 2–5 turn green; `test_pages_resolve_under_docs` + `test_json_contract` names reused by later tasks.

- [ ] **Step 1: Write failing tests in `tests/test_site.py`**

```python
def test_pages_resolve_under_docs():
    import re
    from pathlib import Path
    for p in Path("docs").glob("*.html"):
        html = p.read_text(encoding="utf-8")
        assert "../" not in re.findall(r'(?:src|href)="([^"]+)"', html) and '"../' not in html, p
        for m in re.finditer(r'(?:src|href)="([^"]+)"', html):
            u = m.group(1)
            if u.startswith(("http", "#", "mailto:")):
                continue
            assert (p.parent / u).exists(), f"{p}: {u}"
```

```python
def test_json_contract():
    import json
    from pathlib import Path
    d = Path("docs/assets/data")
    ol = json.loads((d / "olist_charts.json").read_text())
    assert [r["faixa_atraso_dias"] for r in ol["atraso_vs_review"] if r["faixa_atraso_dias"] in
            ["≤0", "1–7", "8–14", ">14"]] == ["≤0", "1–7", "8–14", ">14"][:len(
            [r for r in ol["atraso_vs_review"]])]
    di = json.loads((d / "diabetes_charts.json").read_text())
    for k, v in di["fatores"].items():
        assert v["com_fator"] is not None and v["sem_fator"] is not None, k
    fr = json.loads((d / "fraud_threshold.json").read_text())
    assert [r["threshold"] for r in fr["sweep"]] == sorted(r["threshold"] for r in fr["sweep"])
    assert all(set(r) == {"threshold", "precision", "recall", "f1", "fp", "fn", "custo"} for r in fr["sweep"])
```

- [ ] **Step 2: Run to verify they fail**

Run: `python -m pytest tests/test_site.py::test_pages_resolve_under_docs tests/test_site.py::test_json_contract -v`
Expected: FAIL (both — `../docs/` refs exist; fatores null; bins unordered)

- [ ] **Step 3: Commit the tests**

```bash
git add tests/test_site.py
git commit -m "test: harden Pages-path + JSON-contract gates (RED)"
```

### Task 2: Notebook 01 methodology rework + re-execution

**Files:**
- Modify: `notebooks/01_ecommerce.ipynb` (cells 4, 8, §6 markdown), `docs/assets/img/olist_*.png` (regen), `docs/assets/data/sample_olist.csv` (regen from real df)
- Test: `tests/test_olist.py` (unchanged — must stay green)

**Interfaces:**
- Consumes: real CSVs in `data/`; `src.mining.run_tree/confusion_summary/run_kmeans` unchanged.
- Produces: executed notebook with new acc/CM/importances; PNGs; sample; §6 numbers that Task 5 copies into `docs/ecommerce.html` + `index.html` + `relatorio.html`.

- [ ] **Step 1: Replace item-row split with group split (cell 8)**

```python
from sklearn.model_selection import GroupShuffleSplit
gss = GroupShuffleSplit(n_splits=1, test_size=0.3, random_state=42)
tr, te = next(gss.split(Xf, yf, groups=feat["order_id"]))
Xtr, Xte, ytr, yte = Xf.iloc[tr], Xf.iloc[te], yf.iloc[tr], yf.iloc[te]
```

Keep features as-is plus `is_null_delivered` (see Step 2); compute `freight_ratio` median on `Xtr` only, apply to `Xte`.

- [ ] **Step 2: Raw totals + null-delay flag (cell 4) + median-after-split (cell 8)**

Add `df["price_c"] = df["price"].clip(upper=p99)` / `df["freight_c"]` (same p99 values); receita/RFM/monetary/sample keep raw columns; tree uses `_c` columns. Add `feat["is_null_delivered"]` to `Xf`; impute `delay_fill` with median (not 0). Fix §6 `4,15` → value computed by a new cell printing means per band (on-time / 1–7 / >7). Document in markdown that `delay_days` uses `.dt.days` floor (same-day deliveries land on −1; sign preserved so `is_late` unaffected).

- [ ] **Step 3: Re-execute notebook end-to-end, outputs committed**

Run: `jupyter nbconvert --to notebook --execute --inplace notebooks/01_ecommerce.ipynb`
Expected: all cells executed, no errors; new `olist_matriz_confusao.png` + acc/CM/importances in outputs.

- [ ] **Step 4: Verify tests + record numbers**

Run: `python -m pytest tests/test_olist.py tests/test_site.py -v`
Expected: PASS. Append new acc/CM/cluster/RFM numbers to the task report file (Task 5 consumes them).

- [ ] **Step 5: Commit**

```bash
git add notebooks/01_ecommerce.ipynb docs/assets/img/olist_*.png docs/assets/data/sample_olist.csv
git commit -m "fix(olist): group split, raw totals, null-delay flag, re-executed"
```

### Task 3: Notebook 02 split-fix + Pages-path fix + re-execution + re-export

**Files:**
- Modify: `notebooks/02_saude.ipynb` (cells 0, 3, 5, 12, 15–16, display cells), `docs/saude.html` (re-export + conventions), `docs/assets/img/diabetes_*.png`, `docs/assets/data/sample_diabetes.csv`
- Test: `tests/test_diabetes.py` (unchanged)

**Interfaces:**
- Consumes: `data/diabetes_binary_health_indicators_BRFSS2015.csv` (imbalanced first in CANDIDATES — keep).
- Produces: executed notebook with holdout acc at real prevalence; `docs/saude.html` with `assets/img/` refs, CSS/nav/title, panel anchors intact for `inject_interactive.py`.

- [ ] **Step 1: Split first, undersample only train (cells 5 + 12)**

Cell 12 becomes: split `df` (test_size=0.25, stratify, seed 42) → undersample majority in train only → `run_tree` on balanced train → predict on untouched holdout. Add an executed guard cell asserting holdout prevalence: `assert abs(float(yte.mean()) - 0.139) < 0.02` (output proves the metric is measured at real prevalence). Update header §2/§5 prose: test keeps prevalence ≈ 0.14. Set `is_real = <loader hit a data/ candidate>` in cell 3; gate sample/prose claims on it; fix fallback header to 20 cols (no Education/Income).

- [ ] **Step 2: Use `save_fig` return verbatim in all display cells**

Replace every `display(HTML(f'<img src="../docs/assets/img/{fname}" ...'))` with `url = save_fig(fig, fname)` + `f'<img src="{url}" ...>'`.

- [ ] **Step 3: Re-execute + re-export + re-apply conventions**

Run: `jupyter nbconvert --to notebook --execute --inplace notebooks/02_saude.ipynb`
Then: `jupyter nbconvert --to html notebooks/02_saude.ipynb --output-dir docs --output saude.html`
Then re-apply: CSS link, nav header (copy from `docs/ecommerce.html`), `<title>Saúde (Diabetes) — Mineração de Dados</title>`, `lang="pt-BR"`. Do NOT hand-add panel/scripts (Task 5 runs injector).

- [ ] **Step 4: Verify**

Run: `python -m pytest tests/test_diabetes.py tests/test_site.py::test_pages_resolve_under_docs -v`
Expected: PASS. Record new acc/CM/top-5/clusters/rules in report for Task 5.

- [ ] **Step 5: Commit**

```bash
git add notebooks/02_saude.ipynb docs/saude.html docs/assets/img/diabetes_*.png docs/assets/data/sample_diabetes.csv
git commit -m "fix(saude): split-first eval, Pages img paths, re-executed"
```

### Task 4: Pipeline scripts hardening + JSON regen

**Files:**
- Modify: `scripts/build_interactive_data.py`, `scripts/inject_interactive.py`, `src/common.py`, `src/mining.py`, `docs/assets/data/*.json` (regen)
- Test: Task 1's `test_json_contract` + existing suite

**Interfaces:**
- Consumes: real samples (Tasks 2–3 outputs), `docs/fraude.html` sweep table.
- Produces: JSONs with real non-null payloads, ordered bins; hardened scripts. Key names byte-identical.

- [ ] **Step 1: Fix `build_interactive_data.py`**

Float-tolerant factor split (`float(v) == 1.0` helper, ignore empty); explicit `ORDEM = ["≤0", "1–7", "8–14", ">14"]`; scraper: `encoding="utf-8"`, pick candidate table with most parsed rows, digit-strip ints, `raise SystemExit` instead of `assert`.

- [ ] **Step 2: Fix `inject_interactive.py` + `src/` guards**

Asserts → `raise SystemExit` with actionable message; wrap ecommerce panel in `<section><h2>` parity. `load_csv`: wrap missing-file error naming the Kaggle path. `mining.py`: `k < 1`/length guards + `confusion_summary` label-order docstring. `save_fig` contract test asserting return `assets/img/<name>` + file exists (add to `tests/test_scaffold.py`).

- [ ] **Step 3: Regenerate JSONs + verify**

Run: `python3 scripts/build_interactive_data.py && python -m pytest tests/ -v`
Expected: all PASS including `test_json_contract`.

- [ ] **Step 4: Commit**

```bash
git add scripts/ src/ docs/assets/data/*.json tests/test_scaffold.py
git commit -m "fix(pipeline): float compare, bin order, scraper, guards"
```

### Task 5: Site refresh — real numbers, charts.js, simulators, consistency

**Files:**
- Modify: `docs/index.html`, `docs/relatorio.html`, `docs/ecommerce.html`, `docs/assets/js/charts.js`, `docs/assets/js/simulators.js`, `docs/fraude.html` (H1/lang only), `docs/saude.html` (injector run only)
- Test: full suite + serve check

**Interfaces:**
- Consumes: executed outputs from Tasks 2–3 (read acc/CM/clusters/RFM/rules from committed cells — never invent); injector script from Task 4.
- Produces: consistent site, working charts/simulators, PR-ready tree.

- [ ] **Step 1: Rewrite `docs/ecommerce.html` numbers + recs from Task 2 outputs**

Replace synthetic-era figures (6000/7337/0.80/295/973) with executed real results; keep structure, ≥3 SE→ENTÃO recs, panel + script tags byte-intact.

- [ ] **Step 2: Rewrite `docs/index.html` + `docs/relatorio.html`**

Cards/intro/table (index) and §§1–4 + Limitações/Com-mais-tempo (relatorio) with real numbers: Olist 99,441/112,650/95,420; Diabetes 253,680/0.139/15/22 + new acc; Fraude unchanged (284,807/492/0.98/0.562/0.831). Cross-check every number against page/notebook outputs. Add script tags to index/relatorio (copy from ecommerce) so `tables.js` enhances their tables; add sample-CSV links in saude/fraude panels; fix `lang="pt-BR"`, fraude H1 accents.

- [ ] **Step 3: Fix `charts.js` + `simulators.js`**

`render(url, id, draw)` explicit id + `fail(id)` in catch; `else fail(...)` on the two bare Plotly guards; null-guard slider/out in atraso/limiar + out in risco; caption `196 com atraso calculado; 4 sem data`.

- [ ] **Step 4: Run injector + full verification**

Run: `python3 scripts/inject_interactive.py && python -m pytest tests/ -v`
Expected: all PASS. Serve `docs/` and curl 200 on 5 pages + 3 JS + 3 JSON; assert no `../docs/` remains: `grep -rn '"\.\./' docs/*.html` empty.

- [ ] **Step 5: Commit**

```bash
git add docs/
git commit -m "fix(site): real numbers, Pages paths, chart/sim hardening"
```

### Task 6: README parity + final gate

**Files:**
- Modify: `README.md` (only if pipeline steps changed)

**Interfaces:**
- Consumes: final tree. Produces: merge-ready branch.

- [ ] **Step 1: Verify `run_all.sh` + README reproduce the tree**

Run: `bash -n run_all.sh && python -m pytest tests/ -v`
Expected: PASS. If any step's commands drifted from implementation, update README only.

- [ ] **Step 2: Final status check**

Run: `git status --short` (expect only intended files; `data/` absent) + `git log --oneline -8`
Expected: clean story for PR #2 update. Commit README if touched. Do NOT push.
