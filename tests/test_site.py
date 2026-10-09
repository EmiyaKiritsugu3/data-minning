from pathlib import Path


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
