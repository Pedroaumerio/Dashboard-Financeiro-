"""
main.py — Ponto de entrada do Dashboard de Performance e Métricas Financeiras.

Orquestra todo o pipeline:
  1. (Opcional) Popular o banco com dados fictícios.
  2. Carregar e limpar os dados do Supabase.
  3. Calcular indicadores financeiros.
  4. Gerar e exibir/salvar o dashboard visual.

Uso:
  python main.py              → Carrega dados, analisa e exibe o dashboard.
  python main.py --seed       → Popula o banco antes de executar.
  python main.py --salvar     → Salva o dashboard como PNG em output/.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.pipeline import carregar_dados, resumo_dados
from src.analysis import (
    calcular_indicadores,
    identificar_outliers,
    projetar_despesa_mensal,
    imprimir_indicadores,
)
from src.visualization import gerar_dashboard


def _parse_args() -> argparse.Namespace:
    """Configura e processa argumentos de linha de comando."""
    parser = argparse.ArgumentParser(
        description="Dashboard de Performance e Métricas Financeiras",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--seed",
        action="store_true",
        help="Popula o banco Supabase com dados fictícios antes de executar.",
    )
    parser.add_argument(
        "--salvar",
        action="store_true",
        help="Salva o dashboard como PNG em output/ ao invés de exibir na tela.",
    )
    return parser.parse_args()


def main() -> None:
    """Pipeline principal de execução."""
    args = _parse_args()

    # ── Etapa 0: Seed (opcional) ─────────────────────────────────────────
    if args.seed:
        print("🌱 Populando o banco de dados com dados fictícios...")
        from src.seed_data import popular_banco
        total = popular_banco()
        print(f"✅ {total} transações inseridas com sucesso.\n")

    # ── Etapa 1: Ingestão e limpeza ──────────────────────────────────────
    print("📥 Carregando dados do Supabase...")
    try:
        df = carregar_dados()
    except RuntimeError as e:
        print(f"\n❌ {e}")
        print("   Dica: execute com --seed para popular o banco primeiro.\n")
        sys.exit(1)

    resumo_dados(df)

    # ── Etapa 2: Análise ─────────────────────────────────────────────────
    print("🔍 Calculando indicadores financeiros...")
    indicadores = calcular_indicadores(df)
    imprimir_indicadores(indicadores)

    # Outliers
    outliers = identificar_outliers(df)
    if not outliers.empty:
        print("⚠️  OUTLIERS DETECTADOS (despesas atípicas):")
        print("-" * 60)
        for _, row in outliers.iterrows():
            print(
                f"  {row['data'].strftime('%d/%m/%Y')}  |  "
                f"{row['categoria']:<15}  |  "
                f"R$ {row['valor']:>10,.2f}  |  "
                f"z-score: {row['z_score']}"
            )
        print("-" * 60 + "\n")

    # Projeção
    projecao = projetar_despesa_mensal(df)
    print("🔮 PROJEÇÃO DE DESPESA PARA O PRÓXIMO MÊS:")
    print(f"   Estimativa (média ponderada exponencial): R$ {projecao['projecao']:,.2f}")
    print(f"   Baseado em {len(projecao['meses'])} meses de histórico.\n")

    # ── Etapa 3: Visualização ────────────────────────────────────────────
    print("📊 Gerando dashboard visual...")
    caminho_saida = Path("output/dashboard_financeiro.png") if args.salvar else None
    gerar_dashboard(df, indicadores, salvar_em=caminho_saida)

    if not args.salvar:
        print("✅ Dashboard exibido com sucesso!")
    print("\n🎉 Pipeline concluído.\n")


if __name__ == "__main__":
    main()
