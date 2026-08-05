"""
pipeline.py — Pipeline de ingestão e limpeza de dados do Supabase.

Conecta ao Supabase, carrega os dados brutos da tabela 'transacoes'
em um DataFrame Pandas e aplica transformações de limpeza.
"""

from __future__ import annotations

import pandas as pd

from src.config import get_supabase_client, TABELA_TRANSACOES


def carregar_dados() -> pd.DataFrame:
    """
    Carrega todos os registros da tabela 'transacoes' do Supabase
    e retorna um DataFrame limpo e tipado.

    Returns
    -------
    pd.DataFrame
        DataFrame com colunas: id, data, categoria, valor, tipo, descricao.
    """
    client = get_supabase_client()

    # Busca todos os registros ordenados por data
    response = (
        client
        .table(TABELA_TRANSACOES)
        .select("*")
        .order("data", desc=False)
        .execute()
    )

    df = pd.DataFrame(response.data)

    if df.empty:
        raise RuntimeError(
            f"Nenhum dado encontrado na tabela '{TABELA_TRANSACOES}'. "
            "Execute primeiro o seed_data.py para popular o banco."
        )

    df = _limpar_dados(df)
    return df


def _limpar_dados(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica tratamento e limpeza nos dados brutos.

    Etapas
    ------
    1. Conversão da coluna 'data' para datetime.
    2. Conversão da coluna 'valor' para float64.
    3. Padronização de strings (categoria, tipo, descricao).
    4. Tratamento de valores nulos.
    5. Remoção de duplicatas exatas.
    6. Ordenação cronológica.
    """
    # 1. Conversão de datas
    df["data"] = pd.to_datetime(df["data"], errors="coerce")

    # Remove registros com data inválida (NaT após coerce)
    antes = len(df)
    df = df.dropna(subset=["data"])
    removidos = antes - len(df)
    if removidos > 0:
        print(f"⚠️  {removidos} registro(s) com data inválida removido(s).")

    # 2. Conversão de valor para numérico
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
    df["valor"] = df["valor"].fillna(0.0).astype("float64")

    # 3. Padronização de strings
    df["categoria"] = df["categoria"].str.strip().str.title()
    df["tipo"] = df["tipo"].str.strip().str.lower()
    df["descricao"] = df["descricao"].fillna("Sem descrição").str.strip()

    # 4. Tratamento de nulos restantes
    df["categoria"] = df["categoria"].fillna("Sem Categoria")

    # 5. Remove duplicatas exatas (ignora id e created_at)
    colunas_dedup = ["data", "categoria", "valor", "tipo", "descricao"]
    antes = len(df)
    df = df.drop_duplicates(subset=colunas_dedup, keep="first")
    removidos = antes - len(df)
    if removidos > 0:
        print(f"ℹ️  {removidos} duplicata(s) removida(s).")

    # 6. Ordena cronologicamente e reseta o índice
    df = df.sort_values("data").reset_index(drop=True)

    return df


def resumo_dados(df: pd.DataFrame) -> None:
    """Imprime um resumo rápido do DataFrame carregado."""
    print("\n" + "=" * 60)
    print("📊  RESUMO DOS DADOS CARREGADOS")
    print("=" * 60)
    print(f"  Total de registros : {len(df):>6}")
    print(f"  Período            : {df['data'].min().date()} → {df['data'].max().date()}")
    print(f"  Categorias únicas  : {df['categoria'].nunique()}")
    print(f"  Tipos              : {', '.join(df['tipo'].unique())}")
    print(f"  Valor mín / máx    : R$ {df['valor'].min():,.2f}  /  R$ {df['valor'].max():,.2f}")
    print("=" * 60 + "\n")
