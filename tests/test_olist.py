from pathlib import Path


def test_olist_outputs():
    assert Path("docs/ecommerce.html").exists()
    figs = list(Path("docs/assets/img").glob("olist_*.png"))
    assert len(figs) >= 6, f"só {len(figs)} figs olist"
    html = Path("docs/ecommerce.html").read_text()
    assert "KMeans" in html and "confus" in html.lower()
    assert html.count("<table") >= 3
    assert "recomenda" in html.lower()
    assert Path("docs/assets/data/sample_olist.csv").stat().st_size <= 200 * 1024
