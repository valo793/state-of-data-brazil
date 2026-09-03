"""
Gerador de Notebooks Jupyter (.ipynb) para o projeto Tech Challenge Fase 3
"""

import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
NB_DIR = BASE_DIR / "notebooks"
NB_DIR.mkdir(exist_ok=True)


def make_notebook(cells):
    return {
        "cells": cells,
        "metadata": {
            "language_info": {"name": "python", "version": "3.12"},
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }


def md_cell(text):
    return {"cell_type": "markdown", "metadata": {}, "source": text.splitlines(True)}


def code_cell(code):
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": code.splitlines(True)}


def build_notebooks():
    # 01. Analise Exploratoria
    nb1_cells = [
        md_cell("# 01. Análise Exploratória de Metadados — Camada Bronze\n\nEste notebook realiza a inspeção preliminar dos dados brutos das 3 edições da pesquisa **State of Data Brasil** armazenadas na Camada Bronze (`data/bronze`)."),
        code_cell("""import pandas as pd
from pathlib import Path

bronze_dir = Path("../data/bronze")
files = sorted(list(bronze_dir.glob("*.csv")))
print(f"Total de arquivos encontrados: {len(files)}")
for f in files:
    print(f" - {f.name}")
"""),
        md_cell("## 1. Carregamento e Inspeção de Esquemas"),
        code_cell("""for f in files:
    df = pd.read_csv(f, low_memory=False)
    print(f"Arquivo: {f.name}")
    print(f"  Shape: {df.shape[0]} linhas x {df.shape[1]} colunas\\n")
"""),
        md_cell("## 2. Diagnóstico de Qualidade e Estrutura dos Cabeçalhos\n\nObservação da diferença entre as tuplas de 2023-2024 e os nomes descritivos de 2024+."),
        code_cell("""df23 = pd.read_csv(files[0], nrows=3)
print("Amostra de colunas 2023-2024:")
print(list(df23.columns[:5]))

df24 = pd.read_csv(files[1], nrows=3)
print("\\nAmostra de colunas 2024-2025:")
print(list(df24.columns[:5]))
""")
    ]
    with open(NB_DIR / "01_analise_exploratoria.ipynb", "w", encoding="utf-8") as f:
        json.dump(make_notebook(nb1_cells), f, indent=2, ensure_ascii=False)

    # 02. Validacao Silver
    nb2_cells = [
        md_cell("# 02. Validação e Qualidade da Camada Silver\n\nAuditoria dos dados limpos, harmonizados e tipados na Camada Silver (`state_of_data_silver.parquet`)."),
        code_cell("""import pandas as pd
from pathlib import Path

silver_path = Path("../data/processed/silver/state_of_data_silver.parquet")
df_silver = pd.read_parquet(silver_path)
print(f"Total de registros na Camada Silver: {len(df_silver)}")
print(f"Total de colunas estruturadas: {len(df_silver.columns)}")
df_silver.head(3)
"""),
        md_cell("## 1. Verificação de Chaves Primárias e Deduplicação"),
        code_cell("""print("Contagem por edição:")
print(df_silver["ano_pesquisa"].value_counts())

null_ids = df_silver["id_respondente"].isna().sum()
dups = df_silver.duplicated(subset=["ano_pesquisa", "id_respondente"]).sum()
print(f"\\nIDs nulos: {null_ids}")
print(f"Duplicidades exatas: {dups}")
"""),
        md_cell("## 2. Validação dos Campos Calculados e Tipados"),
        code_cell("""print("Resumo estatístico do salário médio estimado (R$):")
print(df_silver["salario_medio_estimado"].describe())
""")
    ]
    with open(NB_DIR / "02_validacao_silver.ipynb", "w", encoding="utf-8") as f:
        json.dump(make_notebook(nb2_cells), f, indent=2, ensure_ascii=False)

    # 03. Analises de Negocio
    nb3_cells = [
        md_cell("# 03. Análises Estratégicas de Negócio — Camada Gold\n\nConsultas e DataViz orientadas à expansão da área de Dados, Analytics e IA da Instituição Financeira."),
        code_cell("""import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns

gold_dir = Path("../data/processed/gold")
kpis = pd.read_parquet(gold_dir / "gold_indicadores_executivos.parquet")
kpis
"""),
        md_cell("## 1. Remuneração Média Ponderada por Senioridade"),
        code_cell("""rem = pd.read_parquet(gold_dir / "gold_remuneracao_senioridade.parquet")
sal_sen = rem.groupby(["ano_pesquisa", "senioridade_padronizada"]).apply(
    lambda g: g["soma_salarios"].sum() / g["total_profissionais"].sum()
).unstack()
print(sal_sen)
"""),
        md_cell("## 2. Market Share de Plataformas Cloud"),
        code_cell("""tech = pd.read_parquet(gold_dir / "gold_tecnologias.parquet")
clouds = tech[tech["categoria"] == "Cloud Preferida"]
print(clouds.sort_values(by=["ano_pesquisa", "total_usuarios"], ascending=[True, False]))
""")
    ]
    with open(NB_DIR / "03_analises_negocio.ipynb", "w", encoding="utf-8") as f:
        json.dump(make_notebook(nb3_cells), f, indent=2, ensure_ascii=False)

    print("✅ Todos os 3 notebooks Jupyter (.ipynb) foram criados com sucesso em: notebooks/")


if __name__ == "__main__":
    build_notebooks()
