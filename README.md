# State of Data Brazil — Data Lake & Analytics Platform (Tech Challenge Fase 3)

## Contexto do Projeto
Este projeto é o **Tech Challenge da Pós-Tech em Data Analytics / Big Data (Fase 3)**. O desafio simula uma atuação como **Especialista em Big Data & Analytics** em uma consultoria estratégica de dados, prestando suporte a uma **Instituição Financeira de grande porte** que busca expandir sua área de Dados, Analytics e Inteligência Artificial no mercado brasileiro.

Para orientar as decisões de contratação, remuneração, capacitação de equipes e investimento tecnológico, estruturamos um pipeline analítico robusto e moderno em ambiente de nuvem (**AWS**), processando os microdados históricos das 3 últimas edições da pesquisa **State of Data Brasil** (realizada pela comunidade Data Hackers em parceria com a Bain & Company).

A solução contempla desde a ingestão dos dados na camada **Bronze** em Data Lake até o processamento distribuído com **PySpark**, organização nas camadas **Silver** e **Gold**, catalogação no **AWS Glue Data Catalog**, consultas interativas no **Amazon Athena** e preparação de insights executivos com foco em Storytelling.

---

## Arquitetura da Solução AWS

A arquitetura foi concebida seguindo rigorosamente o padrão de **Data Lakehouse em 3 Camadas (Medallion Architecture)** na AWS:

```
                  ┌────────────────────────────────────────────────────────┐
                  │                   Amazon S3 Data Lake                  │
                  │                                                        │
┌──────────────┐  │  ┌──────────────┐    ┌──────────────┐    ┌───────────┐ │  ┌───────────────┐
│ Kaggle CSV   │──┼─▶│    Bronze    │───▶│    Silver    │───▶│   Gold    │─┼─┼▶ Amazon Athena│
│  (Datasets   │  │  │(Dados Brutos)│    │(Limpo/Tipado)│    │(Agregado) │ │  │ Consultas SQL │
│  Históricos) │  │  └──────┬───────┘    └──────┬───────┘    └─────┬─────┘ │  └───────┬───────┘
└──────────────┘  │         │                   │                  │       │          │
                  └─────────┼───────────────────┼──────────────────┼───────┘          │
                            │                   │                  │                  │
                            ▼                   ▼                  ▼                  ▼
                  ┌──────────────────┐ ┌──────────────────┐ ┌─────────────┐ ┌─────────────────┐
                  │ AWS Glue Crawler │ │AWS Glue Job (ETL)│ │  AWS Glue   │ │ Visualização &  │
                  │  & Data Catalog  │ │  Bronze ➔ Silver │ │  Job (ETL)  │ │   Storytelling  │
                  │  (Metadados)     │ │  (PySpark Glue)  │ │Silver ➔ Gold│ │   Executivo     │
                  └──────────────────┘ └──────────────────┘ └─────────────┘ └─────────────────┘
```

### Detalhamento das 3 Camadas de Dados
* **🥉 Camada Bronze (`s3://<bucket>/bronze/`)**: Ingestão e catalogação dos dados brutos exatamente como disponibilizados nas pesquisas do Data Hackers (2023-2024, 2024-2025 e 2025-2026), preservando a fidelidade da fonte original.
* **🥈 Camada Silver (`s3://<bucket>/silver/`)**: Dados limpos, estruturados e harmonizados. Nesta etapa, corrigimos heterogeneidades nos cabeçalhos das pesquisas, convertemos tipos primitivos, padronizamos nomenclaturas de cargos, modelos de trabalho e senioridades, calculamos métricas contínuas de salário médio estimado e removemos registros duplicados. Armazenado em formato colunar **Parquet** particionado por `ano_pesquisa`.
* **🥇 Camada Gold (`s3://<bucket>/gold/`)**: Data Marts agregados e otimizados para consumo analítico. Cada tabela responde a um eixo estratégico de negócio (perfil demográfico, remuneração, diversidade, stack tecnológica, adoção de IA e modelos de trabalho).

> O diagrama editável oficial encontra-se em [`diagrams/arquitetura_aws.drawio`](diagrams/arquitetura_aws.drawio).

---

## Perguntas Estratégicas de Negócio

O pipeline foi projetado para responder às perguntas centrais do case da Instituição Financeira:

1. **Estrutura do Mercado**: Como está distribuído o ecossistema brasileiro de dados em termos de geografia, senioridade e formação acadêmica?
2. **Valorização Profissional**: Quais cargos, especialidades e níveis de senioridade recebem as maiores remunerações médias?
3. **Diversidade de Gênero & Inclusão**: Qual é a representatividade feminina e de grupos minorizados, e como ela varia entre cargos técnicos e posições de liderança?
4. **Adoção Tecnológica**: Quais linguagens de programação, plataformas de nuvem (AWS/GCP/Azure) e ferramentas de BI dominam o mercado?
5. **Inteligência Artificial & GenAI**: Qual é o grau de priorização de IA Generativa nas empresas e como os profissionais utilizam Copilots/LLMs no cotidiano?
6. **Modelos de Trabalho**: Como se distribui a preferência entre remoto, híbrido e presencial, e qual seu impacto na satisfação dos colaboradores?
7. **Recomendações Estratégicas**: Quais diretrizes práticas a Instituição Financeira deve adotar para atração, retenção e capacitação de talentos?

---

## Estrutura do Repositório

O projeto segue uma arquitetura modular, separando a infraestrutura como código, jobs distribuídos de ETL, validações locais e scripts analíticos:

```text
state-of-data-brazil/
│
├── data/
│   ├── bronze/                 # Datasets da camada Bronze (CSVs originais, ignorados no Git)
│   │   └── .gitkeep
│   └── processed/              # Datasets processados nas camadas Silver e Gold (ignorados no Git)
│       └── .gitkeep
│
├── diagrams/
│   └── arquitetura_aws.drawio  # Diagrama completo da arquitetura AWS (Draw.io / diagrams.net)
│
├── notebooks/
│   └── 01_analise_exploratoria.py # Script/Notebook de inspeção inicial dos metadados e qualidade
│
├── output/
│   ├── graficos/               # Visualizações executivas geradas a partir dos dados consolidados
│   │   ├── 01_respondentes_por_ano.png
│   │   ├── 02_genero_por_ano.png
│   │   ├── 03_regiao_por_ano.png
│   │   ├── 04_nivel_senioridade.png
│   │   ├── 05_faixa_salarial.png
│   │   ├── 06_cargo_atual.png
│   │   ├── 07_modelo_trabalho.png
│   │   ├── 08_experiencia_dados.png
│   │   ├── 09_setor.png
│   │   ├── 10_nivel_ensino.png
│   │   ├── 11_faixa_etaria.png
│   │   └── 12_satisfacao.png
│   └── apresentacao/           # Diretório reservado para o material executivo final (PDF/PPTX)
│       └── .gitkeep
│
├── scripts/
│   ├── aws/
│   │   ├── setup_infrastructure.sh # Provisionamento de S3, Glue Database e Crawlers via AWS CLI
│   │   └── upload_to_s3.py         # Script Python (Boto3) para upload dos dados brutos para a camada Bronze do S3
│   ├── etl/
│   │   ├── glue_job_bronze_to_silver.py # AWS Glue Job PySpark: Ingestão, harmonização e limpeza (Silver)
│   │   ├── glue_job_silver_to_gold.py   # AWS Glue Job PySpark: Agregações analíticas e Data Marts (Gold)
│   │   └── pipeline_silver_gold.py      # Pipeline local para validação e testes das transformações
│   └── analytics/
│       ├── exploracao_completa.py  # Pipeline de geração dos gráficos analíticos consolidados
│       └── queries_athena.sql      # Consultas SQL no Amazon Athena sobre as tabelas Gold
│
├── .gitignore                  # Regras de exclusão do Git (ignora dados pesados e credenciais)
├── requirements.txt            # Dependências e bibliotecas Python do projeto
└── README.md                   # Documentação técnica e executiva do projeto (este arquivo)
```

---

## Como Executar o Projeto

### 1. Pré-requisitos
* Python 3.10+ instalado.
* Acesso ao **AWS Academy Lab** (ou conta AWS com permissões para S3, Glue e Athena).
* AWS CLI configurado localmente (`aws configure`).

### 2. Instalação de Dependências Locais
```bash
pip install -r requirements.txt
```

### 3. Provisionamento da Infraestrutura AWS
Execute o script de automação para criar o bucket S3 particionado nas 3 camadas e o catálogo de dados no AWS Glue:
```bash
chmod +x scripts/aws/setup_infrastructure.sh
./scripts/aws/setup_infrastructure.sh
```

### 4. Ingestão dos Dados na Camada Bronze do S3
Faça o upload dos datasets brutos (baixados do [Kaggle Data Hackers](https://www.kaggle.com/datahackers/datasets)) diretamente para a camada Bronze:
```bash
python scripts/aws/upload_to_s3.py --bucket seu-bucket-datalake --data-dir ./data/bronze
```

### 5. Execução dos Glue Jobs (ETL Distribuído)
No console do **AWS Glue** (ou via AWS CLI):
1. Execute o job [`glue_job_bronze_to_silver.py`](scripts/etl/glue_job_bronze_to_silver.py) com os parâmetros `--BUCKET_NAME` e `--DATABASE_NAME`.
2. Em seguida, execute o job [`glue_job_silver_to_gold.py`](scripts/etl/glue_job_silver_to_gold.py) para gerar as tabelas analíticas.

### 6. Consultas Analíticas no Amazon Athena
No editor de consultas do **Amazon Athena**, selecione o database `tech_challenge_3_db` e execute as queries de [`scripts/analytics/queries_athena.sql`](scripts/analytics/queries_athena.sql) para extrair os indicadores de cada dimensão de negócio.

---

## Entregáveis do Tech Challenge
1. **Material Executivo com DataViz e Storytelling**: Relatório estruturado com diagnóstico de mercado e plano de ação estratégico para a expansão da área de dados do banco.
2. **Diagrama da Arquitetura AWS**: Arquitetura visual documentada em Draw.io detalhando todo o fluxo de ingestão, processamento e catálogo nas 3 camadas.
3. **Scripts e Pipelines de Dados**: Códigos PySpark para Glue Jobs, scripts de automação de infraestrutura em nuvem e consultas SQL documentadas.
