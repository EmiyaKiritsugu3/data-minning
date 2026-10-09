from pathlib import Path


def test_scaffold_files_exist():
    for p in ["README.md", ".gitignore", "requirements.txt", "run_all.sh",
              "src/common.py", "src/mining.py",
              "docs/index.html", "docs/assets/css/style.css"]:
        assert Path(p).exists(), f"missing {p}"


def test_common_signatures():
    import src.common as c
    import src.mining as m
    assert callable(c.load_csv) and callable(c.save_fig) and callable(c.df_to_html_table)
    assert callable(m.run_kmeans) and callable(m.run_tree) and callable(m.confusion_summary)


def test_data_gitignored():
    lines = {ln.strip() for ln in Path(".gitignore").read_text().splitlines()}
    assert lines & {"data/", "/data/"}, ".gitignore deve ignorar a pasta data/ da raiz"


def test_save_fig_contract():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    import src.common as c

    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    name = "test_contract_tmp.png"
    url = c.save_fig(fig, name)
    plt.close(fig)
    try:
        assert url == f"assets/img/{name}", url
        assert (Path("docs") / url).exists(), url
    finally:
        (Path("docs") / url).unlink(missing_ok=True)
