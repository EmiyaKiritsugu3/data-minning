"""Rotinas de mineracao: clustering (k-means), arvore de decisao e sumario de confusao."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pandas import DataFrame


def run_kmeans(X: DataFrame, k: int, seed: int = 42) -> tuple:
    """Ajusta KMeans com k clusters e retorna (labels, model)."""
    from sklearn.cluster import KMeans

    if k < 1:
        raise ValueError(f"k deve ser >= 1, recebido {k}")
    if len(X) == 0:
        raise ValueError("X vazio — sem amostras para clusterizar")
    model = KMeans(n_clusters=k, random_state=seed, n_init=10)
    labels = model.fit_predict(X)
    return labels, model


def run_tree(X_train, y_train):
    """Treina uma DecisionTreeClassifier e retorna o modelo ajustado."""
    from sklearn.tree import DecisionTreeClassifier

    if len(X_train) == 0:
        raise ValueError("treino vazio — sem amostras para ajustar a árvore")
    if len(X_train) != len(y_train):
        raise ValueError(
            f"X/y com tamanhos diferentes: {len(X_train)} != {len(y_train)}"
        )
    model = DecisionTreeClassifier(random_state=42)
    model.fit(X_train, y_train)
    return model


def confusion_summary(y_true, y_pred) -> dict:
    """Retorna dict com acuracia e matriz de confusao (como lista).

    Ordem das linhas/colunas: rótulos ordenados (sklearn `confusion_matrix`
    sem `labels=`, i.e. unique labels em ordem crescente); para o caso
    binário 0/1, linha/coluna 0 = classe 0 e 1 = classe 1.
    """
    from sklearn.metrics import accuracy_score, confusion_matrix

    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
    }
