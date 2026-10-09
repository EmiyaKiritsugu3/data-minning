#!/usr/bin/env bash
set -e

if [ ! -d "data" ] || [ -z "$(ls -A data 2>/dev/null)" ]; then
  echo "ERRO: pasta data/ vazia ou inexistente." >&2
  echo "Baixe os CSVs do Kaggle (Olist, Diabetes, Credit Card Fraud) e coloque-os em data/." >&2
  echo "A pasta data/ e propositalmente gitignored: os dados brutos nunca sao commitados." >&2
  exit 1
fi

echo "data/ OK. (Execucao dos notebooks entra nas tasks seguintes.)"
