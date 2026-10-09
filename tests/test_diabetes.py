from pathlib import Path


def test_diabetes_outputs():
    assert Path("docs/saude.html").exists()
    figs = list(Path("docs/assets/img").glob("diabetes_*.png"))
    assert len(figs) >= 6
    html = Path("docs/saude.html").read_text()
    assert "KMeans" in html and "confus" in html.lower()
    assert html.count("<table") >= 3
    assert "recomenda" in html.lower()
