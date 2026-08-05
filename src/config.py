"""
config.py — Configuração centralizada e conexão com o Supabase.

Carrega credenciais de variáveis de ambiente via python-dotenv
e fornece um client singleton do Supabase para todo o projeto.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client, Client


# Carrega o .env da raiz do projeto
_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=_ENV_PATH)


def _get_env(name: str) -> str:
    """Retorna uma variável de ambiente obrigatória ou encerra com erro claro."""
    value = os.getenv(name)
    if not value:
        sys.exit(
            f"[ERRO] Variável de ambiente '{name}' não encontrada.\n"
            f"       Crie um arquivo .env na raiz do projeto com base no .env.example."
        )
    return value


# ── Credenciais ──────────────────────────────────────────────────────────────
SUPABASE_URL: str = _get_env("SUPABASE_URL")
SUPABASE_KEY: str = _get_env("SUPABASE_KEY")

# ── Constantes do projeto ────────────────────────────────────────────────────
TABELA_TRANSACOES: str = "transacoes"
MESES_HISTORICO: int = 6          # janela de dados fictícios
MEDIA_MOVEL_CURTA: int = 7        # dias
MEDIA_MOVEL_LONGA: int = 30       # dias
LIMIAR_OUTLIER_SIGMA: float = 2.0 # desvios padrão para outliers


def get_supabase_client() -> Client:
    """Cria e retorna o client do Supabase."""
    return create_client(SUPABASE_URL, SUPABASE_KEY)
