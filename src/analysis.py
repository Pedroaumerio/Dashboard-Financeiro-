"""
analysis.py — Módulo de análise financeira com Pandas e NumPy.

Calcula indicadores-chave, médias móveis, identifica outliers
e projeta despesas futuras com base no histórico.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from src.config import MEDIA_MOVEL_CURTA, MEDIA_MOVEL_LONGA, LIMIAR_OUTLIER_SIGMA


# ── Dataclass para resultados ────────────────────────────────────────────────

@dataclass
class IndicadoresFinanceiros:
    """Agrupa os principais indicadores calculados."""
    receita_total: float
    despesa_total: float
    saldo_total: float
    media_despesa_diaria: float
    projecao_despesa_proximo_mes: float
    total_outliers: int


# ── Funções de análise ───────────────────────────────────────────────────────

def calcular_indicadores(df: pd.DataFrame) -> IndicadoresFinanceiros:
    """
    Calcula os indicadores financeiros globais.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame limpo com colunas: data, categoria, valor, tipo.

    Returns
    -------
    IndicadoresFinanceiros
        Dataclass com receita total, despesa total, saldo, média diária
        de despesas, projeção mensal e quantidade de outliers.
    """
    receitas = df.loc[df["tipo"] == "receita", "valor"]
    despesas = df.loc[df["tipo"] == "despesa", "valor"]

    receita_total = float(np.sum(receitas.values))
    despesa_total = float(np.sum(despesas.values))
    saldo_total = receita_total - despesa_total

    # Média diária de despesas
    dias_cobertos = (df["data"].max() - df["data"].min()).days or 1
    media_diaria = despesa_total / dias_cobertos

    # Projeção para o próximo mês (30 dias) via média diária
    projecao = media_diaria * 30

    # Outliers
    outliers_df = identificar_outliers(df)
    total_outliers = len(outliers_df)

    return IndicadoresFinanceiros(
        receita_total=receita_total,
        despesa_total=despesa_total,
        saldo_total=saldo_total,
        media_despesa_diaria=media_diaria,
        projecao_despesa_proximo_mes=projecao,
        total_outliers=total_outliers,
    )


def calcular_serie_diaria(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cria uma série temporal diária com receitas, despesas e médias móveis.

    Returns
    -------
    pd.DataFrame
        Colunas: data, receita, despesa, mm_7d_despesa, mm_30d_despesa.
    """
    # Agrupa por dia e tipo
    pivot = (
        df
        .groupby([pd.Grouper(key="data", freq="D"), "tipo"])["valor"]
        .sum()
        .unstack(fill_value=0)
        .reset_index()
    )

    # Garante que ambas as colunas existam
    for col in ("receita", "despesa"):
        if col not in pivot.columns:
            pivot[col] = 0.0

    pivot = pivot.rename(columns={"data": "data"})

    # Reindex para preencher dias sem transação
    idx_completo = pd.date_range(pivot["data"].min(), pivot["data"].max(), freq="D")
    pivot = pivot.set_index("data").reindex(idx_completo, fill_value=0).reset_index()
    pivot = pivot.rename(columns={"index": "data"})

    # Médias móveis com NumPy / Pandas
    pivot["mm_7d_despesa"] = (
        pivot["despesa"]
        .rolling(window=MEDIA_MOVEL_CURTA, min_periods=1)
        .mean()
    )
    pivot["mm_30d_despesa"] = (
        pivot["despesa"]
        .rolling(window=MEDIA_MOVEL_LONGA, min_periods=1)
        .mean()
    )

    return pivot


def calcular_gastos_por_categoria(df: pd.DataFrame) -> pd.DataFrame:
    """
    Totaliza despesas por categoria, ordenadas do maior para o menor.

    Returns
    -------
    pd.DataFrame
        Colunas: categoria, total, percentual.
    """
    despesas = df[df["tipo"] == "despesa"]

    por_cat = (
        despesas
        .groupby("categoria")["valor"]
        .sum()
        .sort_values(ascending=True)
        .reset_index()
        .rename(columns={"valor": "total"})
    )

    total_geral = por_cat["total"].sum()
    por_cat["percentual"] = np.round((por_cat["total"] / total_geral) * 100, 1)

    return por_cat


def identificar_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Identifica despesas atípicas usando o critério de 2 desvios padrão
    acima da média (calculados com NumPy).

    Returns
    -------
    pd.DataFrame
        Subconjunto do DataFrame original contendo apenas os outliers.
    """
    despesas = df[df["tipo"] == "despesa"].copy()

    valores = despesas["valor"].values.astype(np.float64)
    media = np.mean(valores)
    desvio = np.std(valores)
    limiar = media + LIMIAR_OUTLIER_SIGMA * desvio

    outliers = despesas[despesas["valor"] > limiar].copy()
    outliers["z_score"] = np.round((outliers["valor"] - media) / desvio, 2)

    return outliers.sort_values("valor", ascending=False)


def projetar_despesa_mensal(df: pd.DataFrame) -> dict:
    """
    Projeta a despesa do próximo mês usando a média ponderada
    exponencial dos últimos meses (mais peso para meses recentes).

    Returns
    -------
    dict
        Chaves: meses (lista), despesas_mensais (lista),
                pesos (lista), projecao (float).
    """
    despesas = df[df["tipo"] == "despesa"].copy()
    despesas["ano_mes"] = despesas["data"].dt.to_period("M")

    mensal = despesas.groupby("ano_mes")["valor"].sum()

    # Pesos exponenciais: meses mais recentes pesam mais
    n = len(mensal)
    pesos = np.exp(np.linspace(0, 1, n))
    pesos = pesos / pesos.sum()  # normaliza

    projecao = float(np.dot(mensal.values, pesos))

    return {
        "meses": [str(m) for m in mensal.index],
        "despesas_mensais": mensal.values.tolist(),
        "pesos": np.round(pesos, 4).tolist(),
        "projecao": round(projecao, 2),
    }


def imprimir_indicadores(indicadores: IndicadoresFinanceiros) -> None:
    """Exibe os indicadores financeiros no terminal de forma formatada."""
    print("\n" + "=" * 60)
    print("💰  INDICADORES FINANCEIROS")
    print("=" * 60)
    print(f"  Receita Total               : R$ {indicadores.receita_total:>12,.2f}")
    print(f"  Despesa Total               : R$ {indicadores.despesa_total:>12,.2f}")
    print(f"  Saldo (Receita - Despesa)   : R$ {indicadores.saldo_total:>12,.2f}")
    print(f"  Média Diária de Despesa     : R$ {indicadores.media_despesa_diaria:>12,.2f}")
    print(f"  Projeção Despesa (próx. mês): R$ {indicadores.projecao_despesa_proximo_mes:>12,.2f}")
    print(f"  Outliers Detectados         :    {indicadores.total_outliers:>9}")
    print("=" * 60 + "\n")
