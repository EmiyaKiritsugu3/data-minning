import json
from pathlib import Path

PAGES = ["docs/ecommerce.html", "docs/saude.html", "docs/fraude.html"]
JS_FILES = [
    "docs/assets/js/tables.js",
    "docs/assets/js/charts.js",
    "docs/assets/js/simulators.js",
]
JSON_FILES = [
    "docs/assets/data/olist_charts.json",
    "docs/assets/data/diabetes_charts.json",
    "docs/assets/data/fraud_threshold.json",
]


def test_interactive_assets_exist():
    for js in JS_FILES:
        assert Path(js).exists(), f"missing {js}"
    for data in JSON_FILES:
        p = Path(data)
        assert p.exists(), f"missing {data}"
        json.loads(p.read_text())  # JSON válido
        assert p.stat().st_size <= 200 * 1024, f"{data} > 200KB"


def test_pages_load_plotly_and_local_js():
    for page in PAGES:
        html = Path(page).read_text()
        assert "plotly" in html.lower(), f"{page}: sem Plotly CDN"
        assert "assets/js/" in html, f"{page}: sem JS local"


def test_pages_have_search_and_simulator():
    for page in PAGES:
        low = Path(page).read_text().lower()
        assert 'type="search"' in low or "data-table-filter" in low, (
            f"{page}: sem busca em tabelas"
        )
        assert "simulador" in low, f"{page}: sem simulador"


def test_png_fallback_kept():
    import re

    for page in PAGES:
        html = Path(page).read_text()
        assert re.search(r"assets/img/[\w.\-]+\.png", html), (
            f"{page}: fallback PNG removido"
        )
