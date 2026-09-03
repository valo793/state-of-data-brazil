# %% [markdown]
# # Tech Challenge Fase 3 — Análise Exploratória Inicial
#
# Este notebook realiza a análise exploratória dos dados brutos da pesquisa
# **State of Data Brasil** (Data Hackers + Bain) para as edições 2021, 2022 e 2023.
#
# ## Objetivos
# - Entender a estrutura de cada dataset (colunas, tipos, dimensões)
# - Identificar valores nulos e inconsistências
# - Mapear diferenças entre edições (colunas renomeadas, adicionadas ou removidas)
# - Gerar estatísticas descritivas básicas
# - Produzir um dicionário de dados preliminar

# %% [markdown]
# ## 1. Setup e Carregamento dos Dados

# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings

warnings.filterwarnings("ignore")
sns.set_theme(style="whitegrid", palette="husl")
plt.rcParams["figure.figsize"] = (14, 6)
plt.rcParams["font.size"] = 12

# Diretório dos dados da camada Bronze — ajuste conforme necessário
DATA_DIR = Path("../data/bronze")

# %% [markdown]
# ### 1.1 Descoberta automática dos arquivos CSV

# %%
csv_files = sorted(DATA_DIR.rglob("*.csv"))
print(f"📁 Arquivos CSV encontrados: {len(csv_files)}\n")
for f in csv_files:
    size_mb = f.stat().st_size / (1024 * 1024)
    print(f"  {f.relative_to(DATA_DIR)}  ({size_mb:.2f} MB)")

# %% [markdown]
# ### 1.2 Carregamento dos datasets
#
# Carregamos cada CSV em um dicionário indexado pelo nome do arquivo.

# %%
datasets = {}
for f in csv_files:
    name = f.stem
    try:
        df = pd.read_csv(f, encoding="utf-8", low_memory=False)
    except UnicodeDecodeError:
        df = pd.read_csv(f, encoding="latin-1", low_memory=False)
    datasets[name] = df
    print(f"✓ {name}: {df.shape[0]:,} linhas × {df.shape[1]} colunas")

print(f"\n📊 Total de datasets carregados: {len(datasets)}")

# %% [markdown]
# ## 2. Visão Geral de Cada Dataset

# %%
for name, df in datasets.items():
    print("=" * 80)
    print(f"📋 DATASET: {name}")
    print("=" * 80)
    print(f"\n  Dimensões: {df.shape[0]:,} linhas × {df.shape[1]} colunas")
    print(f"  Memória:   {df.memory_usage(deep=True).sum() / (1024**2):.2f} MB")
    
    # Tipos de dados
    print(f"\n  Tipos de dados:")
    for dtype, count in df.dtypes.value_counts().items():
        print(f"    {dtype}: {count} colunas")
    
    # Valores nulos
    null_cols = df.isnull().sum()
    null_cols = null_cols[null_cols > 0].sort_values(ascending=False)
    print(f"\n  Colunas com valores nulos: {len(null_cols)} de {df.shape[1]}")
    if len(null_cols) > 0:
        print(f"  Top 10 colunas com mais nulos:")
        for col, nulls in null_cols.head(10).items():
            pct = nulls / len(df) * 100
            print(f"    {col}: {nulls:,} ({pct:.1f}%)")
    
    # Primeiras linhas
    print(f"\n  Primeiras 3 colunas (amostra):")
    print(df.iloc[:3, :5].to_string(index=False))
    print()

# %% [markdown]
# ## 3. Análise de Colunas — Comparação Entre Edições

# %%
print("📊 Comparação de colunas entre edições\n")
all_columns = {}
for name, df in datasets.items():
    all_columns[name] = set(df.columns)

dataset_names = list(all_columns.keys())

# Colunas em comum entre todos os datasets
if len(dataset_names) >= 2:
    common_cols = set.intersection(*all_columns.values())
    all_unique = set.union(*all_columns.values())
    
    print(f"  Colunas em TODOS os datasets: {len(common_cols)}")
    print(f"  Total de colunas únicas:      {len(all_unique)}")
    print()
    
    # Colunas exclusivas de cada dataset
    for name in dataset_names:
        exclusive = all_columns[name] - set.union(*(
            all_columns[n] for n in dataset_names if n != name
        ))
        if exclusive:
            print(f"  Colunas EXCLUSIVAS de [{name}]: {len(exclusive)}")
            for col in sorted(exclusive)[:10]:
                print(f"    - {col}")
            if len(exclusive) > 10:
                print(f"    ... e mais {len(exclusive) - 10}")
            print()

# %% [markdown]
# ## 4. Estatísticas Descritivas

# %%
for name, df in datasets.items():
    print("=" * 80)
    print(f"📈 ESTATÍSTICAS: {name}")
    print("=" * 80)
    
    # Colunas numéricas
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        print(f"\n  Colunas numéricas ({len(numeric_cols)}):")
        print(df[numeric_cols].describe().round(2).to_string())
    
    # Colunas categóricas — top valores
    cat_cols = df.select_dtypes(include=["object"]).columns
    if len(cat_cols) > 0:
        print(f"\n  Colunas categóricas ({len(cat_cols)}) — Top 5 valores:")
        for col in cat_cols[:15]:  # Limitar a 15 colunas para não poluir
            top_vals = df[col].value_counts().head(5)
            print(f"\n    [{col}] ({df[col].nunique()} valores únicos)")
            for val, count in top_vals.items():
                pct = count / len(df) * 100
                print(f"      {val}: {count:,} ({pct:.1f}%)")
    print()

# %% [markdown]
# ## 5. Visualizações Iniciais

# %%
for name, df in datasets.items():
    # Gráfico de completude dos dados
    fig, ax = plt.subplots(figsize=(16, max(6, len(df.columns) * 0.25)))
    
    completude = (1 - df.isnull().mean()) * 100
    completude = completude.sort_values(ascending=True)
    
    colors = ["#e74c3c" if v < 50 else "#f39c12" if v < 80 else "#2ecc71" for v in completude]
    
    ax.barh(range(len(completude)), completude.values, color=colors)
    ax.set_yticks(range(len(completude)))
    ax.set_yticklabels(completude.index, fontsize=8)
    ax.set_xlabel("Completude (%)")
    ax.set_title(f"Completude dos Dados — {name}")
    ax.axvline(x=80, color="gray", linestyle="--", alpha=0.5, label="80%")
    ax.legend()
    
    plt.tight_layout()
    plt.savefig(f"../output/graficos/completude_{name}.png", dpi=150, bbox_inches="tight")
    plt.show()
    print(f"  ✓ Gráfico salvo: output/graficos/completude_{name}.png")

# %% [markdown]
# ## 6. Dicionário de Dados Preliminar

# %%
print("📖 DICIONÁRIO DE DADOS PRELIMINAR\n")
for name, df in datasets.items():
    print(f"\n{'='*80}")
    print(f"Dataset: {name}")
    print(f"{'='*80}")
    
    dict_data = []
    for col in df.columns:
        dict_data.append({
            "Coluna": col,
            "Tipo": str(df[col].dtype),
            "Não-Nulos": f"{df[col].notna().sum():,}",
            "Nulos (%)": f"{df[col].isna().mean()*100:.1f}%",
            "Únicos": df[col].nunique(),
            "Exemplo": str(df[col].dropna().iloc[0]) if df[col].notna().any() else "N/A",
        })
    
    dict_df = pd.DataFrame(dict_data)
    print(dict_df.to_string(index=False))

# %% [markdown]
# ## 7. Próximos Passos
#
# Com base nesta análise exploratória:
#
# 1. **Harmonização**: Mapear colunas equivalentes entre edições com nomes diferentes
# 2. **Limpeza**: Definir estratégia para tratamento de nulos
# 3. **Tipagem**: Converter colunas para tipos apropriados
# 4. **ETL Bronze→Silver**: Implementar as transformações no Glue Job PySpark
