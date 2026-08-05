"""
visualization.py — Geração do painel visual com Matplotlib e Seaborn.

Produz uma figura com 3 subplots:
  1. Linha  — Evolução diária de Receitas vs. Despesas + médias móveis.
  2. Barras — Total de gastos por Categoria.
  3. Boxplot + Histograma — Distribuição de despesas com destaque a outliers.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
import seaborn as sns

from src.analysis import (
    IndicadoresFinanceiros,
    calcular_serie_diaria,
    calcular_gastos_por_categoria,
    identificar_outliers,
    projetar_despesa_mensal,
)
from src.config import LIMIAR_OUTLIER_SIGMA


# ── Configuração visual global ───────────────────────────────────────────────

def _configurar_estilo() -> None:
    """Aplica tema escuro premium com Seaborn + Matplotlib."""
    sns.set_theme(
        style="darkgrid",
        palette="muted",
        font="sans-serif",
        rc={
            "figure.facecolor": "#0e1117",
            "axes.facecolor": "#161b22",
            "axes.edgecolor": "#30363d",
            "axes.labelcolor": "#c9d1d9",
            "text.color": "#c9d1d9",
            "xtick.color": "#8b949e",
            "ytick.color": "#8b949e",
            "grid.color": "#21262d",
            "grid.linewidth": 0.5,
            "font.size": 11,
            "axes.titlesize": 14,
            "axes.titleweight": "bold",
        },
    )


def _formatar_brl(valor: float, _pos=None) -> str:
    """Formata um valor numérico como moeda brasileira."""
    if abs(valor) >= 1_000:
        return f"R$ {valor:,.0f}"
    return f"R$ {valor:,.2f}"


# ── Função principal ─────────────────────────────────────────────────────────

def gerar_dashboard(
    df: pd.DataFrame,
    indicadores: IndicadoresFinanceiros,
    salvar_em: str | Path | None = None,
) -> None:
    """
    Gera o painel visual completo com 3 gráficos em uma única figura.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame limpo com as transações.
    indicadores : IndicadoresFinanceiros
        Indicadores pré-calculados para anotações nos gráficos.
    salvar_em : str | Path | None
        Caminho para salvar a imagem. Se None, exibe interativamente.
    """
    _configurar_estilo()

    fig, axes = plt.subplots(
        nrows=2, ncols=2,
        figsize=(20, 12),
        gridspec_kw={"height_ratios": [1, 1], "width_ratios": [1.3, 1]},
    )

    # Reorganiza: gráfico de linha ocupa a linha inteira de cima
    ax_linha = plt.subplot2grid((2, 2), (0, 0), colspan=2, fig=fig)
    ax_barras = axes[1, 0]
    ax_dist = axes[1, 1]

    # Remove os axes originais da primeira linha (já substituídos)
    axes[0, 0].remove()
    axes[0, 1].remove()

    # ── 1. Gráfico de Linha ──────────────────────────────────────────────
    _plotar_evolucao_diaria(df, ax_linha)

    # ── 2. Gráfico de Barras ─────────────────────────────────────────────
    _plotar_gastos_categoria(df, ax_barras)

    # ── 3. Distribuição / Boxplot ────────────────────────────────────────
    _plotar_distribuicao_despesas(df, ax_dist)

    # ── Título geral e KPIs ──────────────────────────────────────────────
    projecao = projetar_despesa_mensal(df)

    fig.suptitle(
        "DASHBOARD DE PERFORMANCE E MÉTRICAS FINANCEIRAS",
        fontsize=18,
        fontweight="bold",
        color="#58a6ff",
        y=0.98,
    )

    # Faixa de KPIs no rodapé
    kpi_text = (
        f"  💰 Receita: R$ {indicadores.receita_total:,.2f}"
        f"    |    📉 Despesa: R$ {indicadores.despesa_total:,.2f}"
        f"    |    📊 Saldo: R$ {indicadores.saldo_total:,.2f}"
        f"    |    🔮 Projeção próx. mês: R$ {projecao['projecao']:,.2f}"
        f"    |    ⚠️ Outliers: {indicadores.total_outliers}"
    )
    fig.text(
        0.5, 0.01, kpi_text,
        ha="center", fontsize=11,
        color="#f0f6fc",
        bbox=dict(boxstyle="round,pad=0.6", facecolor="#1f2937", edgecolor="#30363d", alpha=0.95),
    )

    plt.tight_layout(rect=[0, 0.04, 1, 0.95])

    if salvar_em:
        caminho = Path(salvar_em)
        caminho.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(caminho, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
        print(f"📸 Dashboard salvo em: {caminho.resolve()}")
    else:
        plt.show()

    plt.close(fig)


# ── Subplot 1: Evolução Diária ───────────────────────────────────────────────

def _plotar_evolucao_diaria(df: pd.DataFrame, ax: plt.Axes) -> None:
    """Gráfico de linha — receitas vs. despesas diárias + médias móveis."""
    serie = calcular_serie_diaria(df)

    # Áreas preenchidas (receita e despesa)
    ax.fill_between(
        serie["data"], serie["receita"], alpha=0.15, color="#3fb950", label="_nolegend_"
    )
    ax.fill_between(
        serie["data"], serie["despesa"], alpha=0.15, color="#f85149", label="_nolegend_"
    )

    # Linhas de receita e despesa
    ax.plot(
        serie["data"], serie["receita"],
        color="#3fb950", linewidth=1.2, alpha=0.7, label="Receita diária",
    )
    ax.plot(
        serie["data"], serie["despesa"],
        color="#f85149", linewidth=1.2, alpha=0.7, label="Despesa diária",
    )

    # Médias móveis
    ax.plot(
        serie["data"], serie["mm_7d_despesa"],
        color="#f0883e", linewidth=2, linestyle="--", label="Média Móvel 7d (despesa)",
    )
    ax.plot(
        serie["data"], serie["mm_30d_despesa"],
        color="#a371f7", linewidth=2.5, linestyle="-", label="Média Móvel 30d (despesa)",
    )

    ax.set_title("Evolução Diária — Receitas vs. Despesas", pad=12)
    ax.set_xlabel("Data")
    ax.set_ylabel("Valor (R$)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(_formatar_brl))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b/%Y"))
    ax.legend(loc="upper left", framealpha=0.7, fontsize=9)
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")


# ── Subplot 2: Gastos por Categoria ──────────────────────────────────────────

def _plotar_gastos_categoria(df: pd.DataFrame, ax: plt.Axes) -> None:
    """Gráfico de barras horizontal — total de gastos por categoria."""
    cat_df = calcular_gastos_por_categoria(df)

    # Paleta de cores gradiente
    cores = sns.color_palette("rocket_r", n_colors=len(cat_df))

    barras = ax.barh(
        cat_df["categoria"], cat_df["total"],
        color=cores, edgecolor="#30363d", linewidth=0.5,
    )

    # Anotações com valor e percentual
    for barra, (_, row) in zip(barras, cat_df.iterrows()):
        largura = barra.get_width()
        ax.text(
            largura + cat_df["total"].max() * 0.02,
            barra.get_y() + barra.get_height() / 2,
            f"R$ {row['total']:,.0f} ({row['percentual']}%)",
            va="center", fontsize=9, color="#c9d1d9",
        )

    ax.set_title("Gastos por Categoria", pad=12)
    ax.set_xlabel("Total (R$)")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(_formatar_brl))
    ax.set_xlim(0, cat_df["total"].max() * 1.35)


# ── Subplot 3: Distribuição de Despesas ──────────────────────────────────────

def _plotar_distribuicao_despesas(df: pd.DataFrame, ax: plt.Axes) -> None:
    """Histograma + destaque de outliers — distribuição dos valores de despesas."""
    despesas = df.loc[df["tipo"] == "despesa", "valor"].values.astype(np.float64)

    # Limiar de outlier
    media = np.mean(despesas)
    desvio = np.std(despesas)
    limiar = media + LIMIAR_OUTLIER_SIGMA * desvio

    # Histograma
    ax.hist(
        despesas, bins=40, color="#58a6ff", alpha=0.6,
        edgecolor="#30363d", linewidth=0.5, label="Despesas",
    )

    # Linha do limiar de outlier
    ax.axvline(
        limiar, color="#f85149", linewidth=2, linestyle="--",
        label=f"Limiar outlier ({LIMIAR_OUTLIER_SIGMA}σ = R$ {limiar:,.0f})",
    )

    # Linha da média
    ax.axvline(
        media, color="#3fb950", linewidth=1.5, linestyle=":",
        label=f"Média = R$ {media:,.0f}",
    )

    # Destaca os outliers
    outliers_vals = despesas[despesas > limiar]
    if len(outliers_vals) > 0:
        ax.hist(
            outliers_vals, bins=20, color="#f85149", alpha=0.8,
            edgecolor="#da3633", linewidth=0.8, label=f"Outliers ({len(outliers_vals)})",
        )

    ax.set_title("Distribuição de Despesas", pad=12)
    ax.set_xlabel("Valor (R$)")
    ax.set_ylabel("Frequência")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(_formatar_brl))
    ax.legend(loc="upper right", framealpha=0.7, fontsize=8)
