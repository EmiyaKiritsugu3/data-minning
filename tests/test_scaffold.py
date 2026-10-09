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
    assert Path(".gitignore").read_text().split().__contains__("data/")
