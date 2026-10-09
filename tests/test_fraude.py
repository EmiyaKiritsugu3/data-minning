from pathlib import Path


def test_fraude_outputs():
    assert Path("docs/fraude.html").exists()
    figs = list(Path("docs/assets/img").glob("fraud_*.png"))
    assert len(figs) >= 6
    html = Path("docs/fraude.html").read_text().lower()
    assert "kmeans" in html and "confus" in html
    assert "recomenda" in html
    assert "limiar" in html or "threshold" in html


def test_fraude_sample():
    p = Path("docs/assets/data/sample_fraud.csv")
    assert p.exists(), "sample_fraud.csv ausente"
    assert p.stat().st_size <= 200 * 1024, "sample > 200KB"


def test_fraude_no_cdn():
    html = Path("docs/fraude.html").read_text()
    for token in ["cdnjs", "jsdelivr", "unpkg", "googleapis"]:
        assert token not in html, f"CDN encontrado no HTML: {token}"
