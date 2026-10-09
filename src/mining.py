"""Rotinas de mineracao: clustering (k-means), arvore de decisao e sumario de confusao."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pandas import DataFrame


def run_kmeans(X: DataFrame, k: int, seed: int = 42) -> tuple:
    """Ajusta KMeans com k clusters e retorna (labels, model)."""
    from sklearn.cluster import KMeans

    model = KMeans(n_clusters=k, random_state=seed, n_init=10)
    labels = model.fit_predict(X)
    return labels, model


def run_tree(X_train, y_train):
    """Treina uma DecisionTreeClassifier e retorna o modelo ajustado."""
    from sklearn.tree import DecisionTreeClassifier

    model = DecisionTreeClassifier(random_state=42)
    model.fit(X_train, y_train)
    return model


def confusion_summary(y_true, y_pred) -> dict:
    """Retorna dict com acuracia e matriz de confusao (como lista)."""
    from sklearn.metrics import accuracy_score, confusion_matrix

    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
    }
