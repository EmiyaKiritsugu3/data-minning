"""Gera os JSONs que alimentam gráficos e simuladores do site.

Fontes honestas, sem dependências além da stdlib:
- olist/diabetes: agregações sobre docs/assets/data/sample_*.csv
  (amostras de 200 linhas; o JSON carrega o aviso "amostra").
- fraude: sweep threshold extraído de docs/fraude.html
  (tabela gerada com os dados reais do Kaggle).

Uso: python3 scripts/build_interactive_data.py
"""

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "docs" / "assets" / "data"

ORDEM = ["≤0", "1–7", "8–14", ">14"]


def _is1(v):
    try:
        return float(v) == 1.0
    except (TypeError, ValueError):
        return False


def write(name, payload):
    p = DATA / name
    p.write_text(json.dumps(payload, ensure_ascii=False, indent=1))
    print(f"{name}: {p.stat().st_size} bytes")


def build_olist():
    rows = list(csv.DictReader(open(DATA / "sample_olist.csv")))
    rec_cat, rec_uf = {}, {}
    for r in rows:
        try:
            price = float(r["price"])
        except (ValueError, KeyError):
            continue
        rec_cat[r.get("product_category_name", "?")] = (
            rec_cat.get(r.get("product_category_name", "?"), 0) + price
        )
        rec_uf[r.get("customer_state", "?")] = (
            rec_uf.get(r.get("customer_state", "?"), 0) + price
        )
    bins = {}
    for r in rows:
        try:
            d = float(r["delay_days"])
            s = float(r["review_score"])
        except (ValueError, KeyError):
            continue
        b = "≤0" if d <= 0 else ("1–7" if d <= 7 else "8–14" if d <= 14 else ">14")
        bins.setdefault(b, {"soma": 0.0, "n": 0})
        bins[b]["soma"] += s
        bins[b]["n"] += 1
    write(
        "olist_charts.json",
        {
            "fonte": "amostra sample_olist.csv (200 linhas, dados reais Olist)",
            "receita_por_categoria": [
                {"categoria": k, "receita": round(v, 2)}
                for k, v in sorted(rec_cat.items(), key=lambda kv: -kv[1])[:8]
            ],
            "receita_por_uf": [
                {"uf": k, "receita": round(v, 2)}
                for k, v in sorted(rec_uf.items(), key=lambda kv: -kv[1])[:8]
            ],
            "atraso_vs_review": [
                {
                    "faixa_atraso_dias": b,
                    "review_medio": round(bins[b]["soma"] / bins[b]["n"], 2),
                    "pedidos": bins[b]["n"],
                }
                for b in [k for k in ORDEM if k in bins]
            ],
            "delays": sorted(
                float(r["delay_days"])
                for r in rows
                if r.get("delay_days") not in (None, "")
            ),
        },
    )


def build_diabetes():
    rows = list(csv.DictReader(open(DATA / "sample_diabetes.csv")))
    faixas = {}
    for r in rows:
        try:
            age = int(float(r["Age"]))
            d = int(float(r["Diabetes_binary"]))
        except (ValueError, KeyError):
            continue
        faixas.setdefault(age, {"casos": 0, "n": 0})
        faixas[age]["casos"] += d
        faixas[age]["n"] += 1
    fatores = {}
    for col in ["HighBP", "HighChol", "Smoker", "PhysActivity"]:
        a = [float(r["Diabetes_binary"]) for r in rows if _is1(r.get(col))]
        b = [
            float(r["Diabetes_binary"])
            for r in rows
            if not _is1(r.get(col)) and r.get(col) not in (None, "")
        ]
        fatores[col] = {
            "com_fator": round(sum(a) / len(a), 3) if a else None,
            "sem_fator": round(sum(b) / len(b), 3) if b else None,
        }
    write(
        "diabetes_charts.json",
        {
            "fonte": "amostra sample_diabetes.csv (200 linhas, dados reais BRFSS 2015)",
            "prevalencia_por_idade": [
                {
                    "faixa_etaria": k,
                    "prevalencia": round(v["casos"] / v["n"], 3),
                    "n": v["n"],
                }
                for k, v in sorted(faixas.items())
            ],
            "fatores": fatores,
        },
    )


def _to_int(s: str) -> int:
    digits = re.sub(r"[^\d]", "", s)
    if not digits:
        raise ValueError(f"sem dígitos em {s!r}")
    return int(digits)


def build_fraude():
    html = (ROOT / "docs" / "fraude.html").read_text(encoding="utf-8")
    sweep = None
    best = 0
    for m in re.finditer(r"<table[^>]*>.*?</table>", html, re.S):
        t = m.group(0)
        if "threshold" in t.lower() and "custo" in t.lower():
            cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", t, re.S)
            cells = [re.sub(r"<[^>]+>", "", c).strip() for c in cells]
            # cabeçalho: ['', threshold, precision, recall, f1, FP, FN, custo]
            rows = []
            for i in range(0, len(cells), 8):
                chunk = cells[i : i + 8]
                if len(chunk) < 8:
                    break
                if chunk[1] == "threshold":
                    continue
                try:
                    rows.append(
                        {
                            "threshold": float(chunk[1].replace(",", ".")),
                            "precision": float(chunk[2].replace(",", ".")),
                            "recall": float(chunk[3].replace(",", ".")),
                            "f1": float(chunk[4].replace(",", ".")),
                            "fp": _to_int(chunk[5]),
                            "fn": _to_int(chunk[6]),
                            "custo": _to_int(chunk[7]),
                        }
                    )
                except ValueError:
                    continue
            if rows and len(rows) > best:
                sweep = rows
                best = len(rows)
    if not sweep:
        raise SystemExit(
            "tabela sweep não encontrada em docs/fraude.html — "
            "re-exporte docs/fraude.html pelo nbconvert e rode de novo"
        )
    write(
        "fraud_threshold.json",
        {
            "fonte": "sweep gerado com dados reais (mlg-ulb/creditcardfraud); FP=10, FN=500",
            "recomendado": 0.98,
            "sweep": sweep,
        },
    )


if __name__ == "__main__":
    build_olist()
    build_diabetes()
    build_fraude()
