from pathlib import Path


def test_prose_coverage():
    # cada figura tem uma Leitura: por perto; cada página explica as técnicas
    minima_leitura = {
        "docs/ecommerce.html": 8,
        "docs/saude.html": 9,
        "docs/fraude.html": 7,
    }
    for page, minimo in minima_leitura.items():
        n = Path(page).read_text(encoding="utf-8").count("Leitura:")
        assert n >= minimo, f"{page}: {n} leituras < {minimo}"
    for page in minima_leitura:
        assert Path(page).read_text(encoding="utf-8").count("Como ler") >= 3, page


def test_site_integrity():
    for p in ["docs/index.html", "docs/ecommerce.html", "docs/saude.html",
              "docs/fraude.html", "docs/relatorio.html"]:
        assert Path(p).exists(), p
    # CDN permitido (interatividade via Plotly); CSS local continua obrigatório
    for p in Path("docs").glob("*.html"):
        assert "assets/css/style.css" in p.read_text(), p
    # figuras referenciadas existem
    import re
    for p in Path("docs").glob("*.html"):
        for img in re.findall(r'assets/img/[\w.\-]+', p.read_text()):
            assert (Path("docs")/img).exists(), f"{p}: {img}"
    # amostras pequenas
    for s in Path("docs/assets/data").glob("*.csv"):
        assert s.stat().st_size <= 200*1024, s


def test_pages_resolve_under_docs():
    import re
    from pathlib import Path
    for p in Path("docs").glob("*.html"):
        html = p.read_text(encoding="utf-8")
        assert "../" not in re.findall(r'(?:src|href)="([^"]+)"', html) and '"../' not in html, p
        assert "'../" not in html, p
        for m in re.finditer(r'(?:src|href)="([^"]+)"', html):
            u = m.group(1)
            if u.startswith(("http", "#", "mailto:")):
                continue
            clean = u.split('#')[0].split('?')[0]
            if not clean:
                continue
            assert (p.parent / clean).exists(), f"{p}: {u}"
        for m in re.finditer(r'''(?:src|href)=["']([^"']+)''', html):
            assert '"../' not in m.group(0) and "'../" not in m.group(0), p
            u = m.group(1)
            if u.startswith(("http", "#", "mailto:")):
                continue
            if any(c in u for c in "<>{} \t\n\r"):
                continue  # nbconvert <pre> code listing, not a real attr
            clean = u.split('#')[0].split('?')[0]
            if not clean:
                continue
            assert (p.parent / clean).exists(), f"{p}: {u}"


def test_json_contract():
    import json
    from pathlib import Path
    d = Path("docs/assets/data")
    ol = json.loads((d / "olist_charts.json").read_text())
    bins = [r["faixa_atraso_dias"] for r in ol["atraso_vs_review"]]
    assert bins == ["≤0", "1–7", "8–14", ">14"]
    di = json.loads((d / "diabetes_charts.json").read_text())
    for k, v in di["fatores"].items():
        assert v["com_fator"] is not None and v["sem_fator"] is not None, k
    fr = json.loads((d / "fraud_threshold.json").read_text())
    assert [r["threshold"] for r in fr["sweep"]] == sorted(r["threshold"] for r in fr["sweep"])
    assert all(set(r) == {"threshold", "precision", "recall", "f1", "fp", "fn", "custo"} for r in fr["sweep"])
