-- =============================================================================
-- Dashboard de Performance e Métricas Financeiras
-- Script SQL para criação da tabela no Supabase (PostgreSQL)
-- =============================================================================

-- Habilita a extensão uuid-ossp caso ainda não esteja ativa
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Remove a tabela caso já exista (útil durante desenvolvimento)
DROP TABLE IF EXISTS transacoes;

-- Cria a tabela principal de transações financeiras
CREATE TABLE transacoes (
    id          UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    data        DATE NOT NULL,
    categoria   VARCHAR(50) NOT NULL,
    valor       NUMERIC(12, 2) NOT NULL CHECK (valor > 0),
    tipo        VARCHAR(10) NOT NULL CHECK (tipo IN ('receita', 'despesa')),
    descricao   TEXT,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para otimizar consultas frequentes
CREATE INDEX idx_transacoes_data      ON transacoes (data);
CREATE INDEX idx_transacoes_tipo      ON transacoes (tipo);
CREATE INDEX idx_transacoes_categoria ON transacoes (categoria);

-- Comentários na tabela e colunas para documentação
COMMENT ON TABLE  transacoes              IS 'Tabela principal de transações financeiras (receitas e despesas)';
COMMENT ON COLUMN transacoes.id           IS 'Identificador único da transação (UUID v4)';
COMMENT ON COLUMN transacoes.data         IS 'Data em que a transação ocorreu';
COMMENT ON COLUMN transacoes.categoria    IS 'Categoria da transação (ex: Alimentação, Salário, Transporte)';
COMMENT ON COLUMN transacoes.valor        IS 'Valor monetário da transação (sempre positivo)';
COMMENT ON COLUMN transacoes.tipo         IS 'Tipo da transação: receita ou despesa';
COMMENT ON COLUMN transacoes.descricao    IS 'Descrição opcional da transação';
COMMENT ON COLUMN transacoes.created_at   IS 'Timestamp de criação do registro';
