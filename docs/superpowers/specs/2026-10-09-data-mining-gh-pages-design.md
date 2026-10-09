# Design: Análise Data Mining (3 datasets Kaggle) + Site GH Pages

Data: 2026-10-09
Status: aprovado em conversa (4/4 seções), aguardando revisão do spec escrito
Repo: https://github.com/EmiyaKiritsugu3/data-minning.git

## 1. Objetivo e sucesso

Estudo de Data Mining para disciplina de SAD (Sistemas de Apoio à Decisão).
Analisar ≥3 datasets grandes do Kaggle, encontrar relações, informações valiosas
e curiosidades que gerem recomendações decisórias.

Sucesso = site estático no GH Pages acessível nos PCs da faculdade contendo:
- 3 análises completas (EDA + mineração + decisão SAD),
- 1 relatório consolidado comparando os 3 casos,
- cada página com ≥6 figuras, ≥3 tabelas, ≥3 recomendações acionáveis.

## 2. Datasets fechados (Seção 1/4 — aprovada)

| # | Dataset (Kaggle ID) | Volume aprox. | Perguntas decisórias |
|---|---------------------|---------------|----------------------|
| 1 | Olist E-commerce Brasil (`olistbr/brazilian-ecommerce`, 9 CSVs) | ~100k pedidos | Onde atraso mata avaliação? Qual categoria/UF dá receita vs dor logística? Quanto desconto vale a pena? |
| 2 | Diabetes Health Indicators (`alexteboul/diabetes-health-indicators-dataset`) | ~250k linhas, 21 features | Quais 5 fatores mais separam diabéticos? Que regra simples prioriza triagem? |
| 3 | Credit Card Fraud (`mlg-ulb/creditcardfraud`) | ~284k transações, 0.17% fraude | Qual limiar equilibra recall vs falso-positivo? Quanto custa cada erro? |

Decisão: abordagem A (3 domínios distintos) — evita insights repetidos e mostra
versatilidade de SAD. Alternativas descartadas: mesmo domínio (repetitivo),
clássicos pequenos (sem "grande volume").

## 3. Arquitetura do site (Seção 2/4 — aprovada)

Hospedagem: GH Pages, branch `main`, pasta `/docs` (Settings → Pages → main /docs).
Sem build, sem backend, sem CDN obrigatório (CSS/JS locais) para funcionar
com internet ruim/bloqueada da faculdade.

```
data-minning/
  docs/
    index.html          # capa + comparativo SAD dos 3 casos
    ecommerce.html      # análise Olist
    saude.html          # análise Diabetes
    fraude.html         # análise Fraude
    relatorio.html      # relatório consolidado p/ o professor
    assets/
      css/style.css     # CSS local
      img/*.png         # gráficos gerados em Python
      data/sample_*.csv # amostras ≤200KB p/ tabelas demo
  notebooks/
    01_ecommerce.ipynb
    02_saude.ipynb
    03_fraude.ipynb
  src/
    common.py           # limpeza, helpers de plot/tabela
    mining.py           # kmeans, árvore/logística, regras
  data/                 # gitignored (CSVs crus do Kaggle, não commitados)
  requirements.txt
  run_all.sh            # executa notebooks headless → PNGs em docs/assets/img
  README.md
```

Fluxo de dados: Kaggle API → `data/` → notebooks → PNGs + HTML estático →
commit em `docs/` → GH Pages. Nada calculado no browser.

Alternativa descartada: Vercel + Supabase (overkill, 500MB free estoura com
volumes crus, websocket bloqueado na facul, 70% do tempo em backend em vez
de mineração). Vercel estático puro segue como plano B se GH Pages falhar.

## 4. Pipeline de análise (Seção 3/4 — aprovada)

Template único nos 3 notebooks (CRISP-DM resumido), 5 blocos:

1. Entendimento — dicionário de colunas + pergunta decisória.
2. Preparação — nulos, duplicadas, tipos, outliers, encoding; log do descartado.
3. EDA — distribuições, top-N, correlações, 6–8 gráficos + 2 curiosidades.
4. Mineração — KMeans (3–5 clusters + perfil), classificação
   (Árvore de Decisão + matriz de confusão vs baseline burro),
   regras/associação (discretização + Apriori via mlxtend ou co-ocorrência no Olist).
5. Decisão SAD — tabela "se → então" com 3–4 recomendações + limitações
   + bloco "com mais tempo".

Stack: Python + pandas, numpy, matplotlib, seaborn, scikit-learn, mlxtend,
jupyter, nbconvert.

## 5. Reprodutibilidade e publicação (Seção 4/4 — aprovada)

- Dados crus nunca commitados (`data/` gitignored). README documenta
  `kaggle datasets download` + `kaggle.json`. Amostras pequenas em
  `docs/assets/data/` para demo.
- `requirements.txt` com versões fixas. `run_all.sh` usa
  `jupyter nbconvert --to notebook --execute` e exporta figuras.
- Conferência local: `python -m http.server` em `docs/` antes do push.
- Riscos: Kaggle exige login; facul não roda Python (mitigado por pré-render);
  estouro de RAM → amostra estratificada de 50k documentada.

## 6. Fora de escopo (YAGNI)

- Backend, login, realtime, Supabase, APIs dinâmicas.
- Frameworks JS pesados, CDN obrigatório, gráficos interativos com servidor.
- AutoML, deep learning, tuning exaustivo.

## 7. Próximo passo

Após aprovação deste spec: invocar skill writing-plans para gerar o plano
de implementação (ordem: scaffold repo → src/common → notebooks → export
HTML → docs/ → Pages).
