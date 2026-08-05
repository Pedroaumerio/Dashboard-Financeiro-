"""
seed_data.py — Gera e insere dados fictícios realistas na tabela 'transacoes'.

Produz transações dos últimos 6 meses cobrindo categorias variadas de
receita e despesa, com valores e frequências plausíveis para simular
a vida financeira de uma pessoa física.
"""

from __future__ import annotations

import random
from datetime import date, timedelta
from typing import Any

from src.config import get_supabase_client, TABELA_TRANSACOES, MESES_HISTORICO


# ── Categorias e faixas de valores ───────────────────────────────────────────

CATEGORIAS_DESPESA: dict[str, dict[str, Any]] = {
    "Alimentação":   {"min": 15,   "max": 120,  "freq_mensal": (20, 30)},
    "Transporte":    {"min": 5,    "max": 60,   "freq_mensal": (15, 25)},
    "Moradia":       {"min": 1200, "max": 2500, "freq_mensal": (1, 1)},
    "Saúde":         {"min": 50,   "max": 800,  "freq_mensal": (0, 3)},
    "Educação":      {"min": 80,   "max": 600,  "freq_mensal": (1, 3)},
    "Lazer":         {"min": 20,   "max": 350,  "freq_mensal": (3, 8)},
    "Assinaturas":   {"min": 15,   "max": 80,   "freq_mensal": (2, 5)},
    "Vestuário":     {"min": 40,   "max": 500,  "freq_mensal": (0, 4)},
    "Supermercado":  {"min": 80,   "max": 650,  "freq_mensal": (4, 8)},
    "Outros":        {"min": 10,   "max": 300,  "freq_mensal": (1, 5)},
}

CATEGORIAS_RECEITA: dict[str, dict[str, Any]] = {
    "Salário":       {"min": 5000, "max": 8500, "freq_mensal": (1, 1)},
    "Freelance":     {"min": 500,  "max": 4000, "freq_mensal": (0, 2)},
    "Investimentos": {"min": 50,   "max": 1200, "freq_mensal": (1, 2)},
    "Cashback":      {"min": 5,    "max": 80,   "freq_mensal": (1, 4)},
}

DESCRICOES_DESPESA: dict[str, list[str]] = {
    "Alimentação":  ["Almoço restaurante", "iFood delivery", "Café padaria", "Jantar fora", "Lanche tarde"],
    "Transporte":   ["Uber trajeto", "Gasolina posto", "Estacionamento", "Recarga Bilhete Único", "99 corrida"],
    "Moradia":      ["Aluguel mensal", "Condomínio", "IPTU parcela"],
    "Saúde":        ["Farmácia", "Consulta médica", "Plano de saúde", "Exame laboratorial"],
    "Educação":     ["Mensalidade curso", "Livro técnico", "Curso online Udemy", "Assinatura Alura"],
    "Lazer":        ["Cinema ingresso", "Streaming Netflix", "Bar com amigos", "Show/evento", "Jogo Steam"],
    "Assinaturas":  ["Spotify Premium", "iCloud 200GB", "ChatGPT Plus", "Amazon Prime", "Adobe CC"],
    "Vestuário":    ["Camiseta loja", "Tênis novo", "Calça jeans", "Roupa esportiva"],
    "Supermercado": ["Compra semanal", "Feira hortifrúti", "Produtos de limpeza", "Compra mensal grande"],
    "Outros":       ["Presente aniversário", "Conserto celular", "Material escritório", "Doação"],
}

DESCRICOES_RECEITA: dict[str, list[str]] = {
    "Salário":       ["Salário CLT", "Salário depósito"],
    "Freelance":     ["Projeto web cliente", "Consultoria dados", "Freelance design"],
    "Investimentos": ["Dividendos FII", "Rendimento CDB", "Juros Tesouro Direto"],
    "Cashback":      ["Cashback Nubank", "Cashback cartão", "Desconto programa fidelidade"],
}


# ── Funções de geração ───────────────────────────────────────────────────────

def _gerar_datas_mes(ano: int, mes: int) -> list[date]:
    """Retorna todas as datas válidas de um mês."""
    inicio = date(ano, mes, 1)
    if mes == 12:
        fim = date(ano + 1, 1, 1)
    else:
        fim = date(ano, mes + 1, 1)
    return [inicio + timedelta(days=d) for d in range((fim - inicio).days)]


def _gerar_transacoes_mes(ano: int, mes: int) -> list[dict]:
    """Gera transações fictícias para um mês específico."""
    datas_do_mes = _gerar_datas_mes(ano, mes)
    registros: list[dict] = []

    # ── Despesas ──
    for categoria, config in CATEGORIAS_DESPESA.items():
        qtd = random.randint(*config["freq_mensal"])
        for _ in range(qtd):
            valor = round(random.uniform(config["min"], config["max"]), 2)
            registros.append({
                "data":      random.choice(datas_do_mes).isoformat(),
                "categoria": categoria,
                "valor":     valor,
                "tipo":      "despesa",
                "descricao": random.choice(DESCRICOES_DESPESA[categoria]),
            })

    # ── Receitas ──
    for categoria, config in CATEGORIAS_RECEITA.items():
        qtd = random.randint(*config["freq_mensal"])
        for _ in range(qtd):
            valor = round(random.uniform(config["min"], config["max"]), 2)
            # Salário sempre no dia 5 (ou próximo dia útil)
            if categoria == "Salário":
                dia_pgto = date(ano, mes, min(5, len(datas_do_mes)))
                data_trans = dia_pgto.isoformat()
            else:
                data_trans = random.choice(datas_do_mes).isoformat()
            registros.append({
                "data":      data_trans,
                "categoria": categoria,
                "valor":     valor,
                "tipo":      "receita",
                "descricao": random.choice(DESCRICOES_RECEITA[categoria]),
            })

    return registros


def gerar_dados_ficticios() -> list[dict]:
    """
    Gera dados fictícios dos últimos MESES_HISTORICO meses.

    Returns
    -------
    list[dict]
        Lista de dicionários prontos para inserção no Supabase.
    """
    hoje = date.today()
    registros: list[dict] = []

    for offset in range(MESES_HISTORICO, 0, -1):
        # Calcula ano/mês retroativo
        mes_alvo = hoje.month - offset
        ano_alvo = hoje.year
        while mes_alvo <= 0:
            mes_alvo += 12
            ano_alvo -= 1
        registros.extend(_gerar_transacoes_mes(ano_alvo, mes_alvo))

    # Ordena cronologicamente
    registros.sort(key=lambda r: r["data"])

    # Injeta alguns outliers propositais para enriquecer a análise
    registros.extend(_gerar_outliers(hoje))

    return registros


def _gerar_outliers(referencia: date) -> list[dict]:
    """Insere gastos atípicos (outliers) para a análise estatística."""
    outliers = [
        {
            "data":      (referencia - timedelta(days=random.randint(10, 60))).isoformat(),
            "categoria": "Saúde",
            "valor":     round(random.uniform(2500, 5000), 2),
            "tipo":      "despesa",
            "descricao": "Procedimento odontológico emergencial",
        },
        {
            "data":      (referencia - timedelta(days=random.randint(30, 90))).isoformat(),
            "categoria": "Lazer",
            "valor":     round(random.uniform(1800, 3500), 2),
            "tipo":      "despesa",
            "descricao": "Viagem fim de semana (hotel + passagem)",
        },
        {
            "data":      (referencia - timedelta(days=random.randint(15, 75))).isoformat(),
            "categoria": "Outros",
            "valor":     round(random.uniform(2000, 4000), 2),
            "tipo":      "despesa",
            "descricao": "Compra de notebook novo",
        },
    ]
    return outliers


def popular_banco() -> int:
    """
    Gera dados fictícios e insere na tabela 'transacoes' do Supabase.

    Returns
    -------
    int
        Quantidade de registros inseridos.
    """
    client = get_supabase_client()

    # Limpa registros antigos (idempotente para re-execuções)
    client.table(TABELA_TRANSACOES).delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()

    registros = gerar_dados_ficticios()

    # Insere em lotes de 100 para respeitar limites da API
    BATCH_SIZE = 100
    for i in range(0, len(registros), BATCH_SIZE):
        lote = registros[i : i + BATCH_SIZE]
        client.table(TABELA_TRANSACOES).insert(lote).execute()

    return len(registros)


# ── Execução direta ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    total = popular_banco()
    print(f"✅ {total} transações inseridas com sucesso na tabela '{TABELA_TRANSACOES}'.")
