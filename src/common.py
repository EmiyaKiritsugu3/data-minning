"""Funcoes compartilhadas: leitura de CSV, salvamento de figuras e tabelas HTML."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pandas import DataFrame

IMG_DIR = Path(__file__).resolve().parent.parent / "docs" / "assets" / "img"


def load_csv(path: str) -> DataFrame:
    """Le um CSV e retorna um DataFrame."""
    import pandas as pd

    return pd.read_csv(path)


def save_fig(fig, name: str) -> str:
    """Salva a figura em docs/assets/img/<name> e retorna o caminho como str."""
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    dest = IMG_DIR / name
    fig.savefig(dest, bbox_inches="tight")
    return str(dest)


def df_to_html_table(df: DataFrame, max_rows: int = 20) -> str:
    """Converte as primeiras max_rows linhas do DataFrame em tabela HTML."""
    return df.head(max_rows).to_html(index=False, classes="data-table", border=0)
