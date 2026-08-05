# 📊 Dashboard de Performance e Métricas Financeiras

Dashboard analítico de finanças pessoais construído com **Python**, **Pandas**, **NumPy**, **Matplotlib** e **Supabase** (PostgreSQL).

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.0+-150458?style=flat&logo=pandas&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?style=flat&logo=supabase&logoColor=white)

## 🏗️ Arquitetura

```
dashboard/
├── .env.example          # Template de variáveis de ambiente
├── .gitignore
├── requirements.txt      # Dependências do projeto
├── README.md
├── main.py               # Ponto de entrada (orquestrador)
├── sql/
│   └── create_tables.sql # DDL da tabela no Supabase
├── src/
│   ├── __init__.py
│   ├── config.py         # Configuração e conexão Supabase
│   ├── seed_data.py      # Geração de dados fictícios
│   ├── pipeline.py       # Ingestão e limpeza de dados
│   ├── analysis.py       # Cálculos analíticos (Pandas + NumPy)
│   └── visualization.py  # Dashboard visual (Matplotlib + Seaborn)
└── output/               # Imagens geradas (gitignored)
```

## 🚀 Setup Rápido

### 1. Clonar e instalar dependências

```bash
git clone <repo-url>
cd dashboard
python -m venv .venv
.venv\Scripts\activate       # Windows
pip install -r requirements.txt
```

### 2. Configurar o Supabase

1. Crie um projeto em [supabase.com](https://supabase.com).
2. Execute o SQL de `sql/create_tables.sql` no SQL Editor do Supabase.
3. Copie `.env.example` para `.env` e preencha suas credenciais:

```env
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua-chave-anon-key
```

### 3. Executar

```bash
# Popular o banco + gerar dashboard na tela
python main.py --seed

# Apenas gerar dashboard (dados já no banco)
python main.py

# Salvar dashboard como PNG
python main.py --salvar
```

## 📈 Funcionalidades

| Funcionalidade | Descrição |
|---|---|
| **Pipeline ETL** | Conexão Supabase → DataFrame → Limpeza automatizada |
| **Indicadores** | Saldo, receita/despesa total, média diária |
| **Médias Móveis** | 7 dias e 30 dias sobre despesas |
| **Outliers** | Detecção via z-score (2σ acima da média) |
| **Projeção** | Estimativa de despesa do próximo mês (média ponderada exponencial) |
| **Dashboard** | 3 gráficos profissionais em tema escuro |

## 🛠️ Tecnologias

- **Python 3.10+**
- **Pandas** — manipulação e análise de dados
- **NumPy** — cálculos estatísticos (média, desvio padrão, z-score)
- **Matplotlib + Seaborn** — visualização de dados
- **Supabase (PostgreSQL)** — banco de dados na nuvem
- **python-dotenv** — gerenciamento de credenciais

## 📄 Licença

MIT
