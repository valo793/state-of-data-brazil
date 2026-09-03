"""
Tech Challenge Fase 3 — Análise Exploratória Completa
=====================================================
Gera relatório de exploração + gráficos para os 3 datasets.
Trata a diferença de formato de colunas entre edições.

Uso:
    python scripts/analytics/exploracao_completa.py
"""

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import os
import ast
import warnings
warnings.filterwarnings("ignore")

# =========================================================================
# Config
# =========================================================================
DATA_DIR = r"C:\Projects\Tech Challenge 3\data\bronze"
OUTPUT_DIR = r"C:\Projects\Tech Challenge 3\output\graficos"
os.makedirs(OUTPUT_DIR, exist_ok=True)

plt.rcParams.update({
    "figure.figsize": (14, 7),
    "font.size": 12,
    "axes.titlesize": 14,
    "axes.labelsize": 12,
})

COLORS = ["#2196F3", "#FF9800", "#4CAF50", "#E91E63", "#9C27B0",
          "#00BCD4", "#FF5722", "#607D8B", "#795548", "#CDDC39"]

# =========================================================================
# 1. Carregamento + normalização de colunas
# =========================================================================
print("=" * 80)
print("CARREGAMENTO DOS DADOS")
print("=" * 80)

files = sorted([f for f in os.listdir(DATA_DIR) if f.endswith('.csv')])
datasets = {}

# Column mapping: maps P-code (2023-2024) to standardized names
# The 2024-2025 and 2025-2026 editions use descriptive names directly
P_CODE_TO_STANDARD = {
    "P0": "token",
    "P1_a": "idade",
    "P1_a_1": "faixa_idade",
    "P1_b": "genero",
    "P1_c": "cor_raca_etnia",
    "P1_d": "pcd",
    "P1_e": "experiencia_profissional_prejudicada",
    "P1_g": "vive_no_brasil",
    "P1_i": "estado_onde_mora",
    "P1_i_1": "uf_onde_mora",
    "P1_i_2": "regiao_onde_mora",
    "P1_j": "vive_no_estado_de_formacao",
    "P1_k": "regiao_de_origem",
    "P1_l": "nivel_de_ensino",
    "P1_m": "area_de_formacao",
    "P2_a": "situacao_atual",
    "P2_b": "setor",
    "P2_c": "numero_de_funcionarios",
    "P2_d": "gestor",
    "P2_e": "cargo_como_gestor",
    "P2_f": "cargo_atual",
    "P2_g": "nivel",
    "P2_h": "faixa_salarial",
    "P2_i": "tempo_experiencia_dados",
    "P2_j": "tempo_experiencia_ti",
    "P2_k": "satisfeito_atualmente",
    "P2_l": "motivo_insatisfacao",
    "P2_m": "participou_entrevistas",
    "P2_n": "pretende_mudar_emprego",
    "P2_r": "modelo_trabalho_atual",
    "P2_s": "modelo_trabalho_ideal",
    "P2_t": "atitude_retorno_presencial",
    "P4_a": "linguagens_utilizadas",
    "P4_b": "linguagem_mais_frequente",
    "P4_c": "linguagem_preferida",
}

# Descriptive column names (2024-2025 / 2025-2026) to standard
DESC_TO_STANDARD = {
    "0.a_token": "token",
    "1.a_idade": "idade",
    "1.a.1_faixa_idade": "faixa_idade",
    "1.b_genero": "genero",
    "1.c_cor/raca/etnia": "cor_raca_etnia",
    "1.d_pcd": "pcd",
    "1.e_experiencia_profissional_prejudicada": "experiencia_profissional_prejudicada",
    "1.g_vive_no_brasil": "vive_no_brasil",
    "1.i_estado_onde_mora": "estado_onde_mora",
    "1.i.1_uf_onde_mora": "uf_onde_mora",
    "1.i.2_regiao_onde_mora": "regiao_onde_mora",
    "1.j_vive_no_estado_de_formacao": "vive_no_estado_de_formacao",
    "1.k.2_regiao_de_origem": "regiao_de_origem",
    "1.l_nivel_de_ensino": "nivel_de_ensino",
    "1.m_area_de_formacao": "area_de_formacao",
    "2.a_situacao_atual": "situacao_atual",
    "2.b_setor": "setor",
    "2.c_numero_de_funcionarios": "numero_de_funcionarios",
    "2.d_gestor": "gestor",
    "2.e_cargo_como_gestor": "cargo_como_gestor",
    "2.f_cargo_atual": "cargo_atual",
    "2.g_nivel": "nivel",
    "2.h_faixa_salarial": "faixa_salarial",
    "2.i_tempo_de_experiencia_em_dados": "tempo_experiencia_dados",
    "2.j_tempo_de_experiencia_em_ti": "tempo_experiencia_ti",
    "2.k_satisfeito_atualmente": "satisfeito_atualmente",
    "2.l_motivo_insatisfacao": "motivo_insatisfacao",
    "2.m_entrevistas_ultimos_6_meses": "participou_entrevistas",
    "2.n_pretende_mudar_emprego": "pretende_mudar_emprego",
    "2.q_modelo_de_trabalho_atual": "modelo_trabalho_atual",
    "2.r_modelo_de_trabalho_atual": "modelo_trabalho_atual",
    "2.r_modelo_de_trabalho_ideal": "modelo_trabalho_ideal",
    "2.s_modelo_de_trabalho_ideal": "modelo_trabalho_ideal",
    "2.s_atitude_em_caso_de_retorno_presencial": "atitude_retorno_presencial",
    "4.c_linguagem_preferida": "linguagem_preferida",
    "4.f_linguagem_preferida": "linguagem_preferida",
}


def normalize_2023_columns(df):
    """Normalize tuple-string column names from 2023-2024 edition."""
    new_cols = {}
    for col in df.columns:
        col_str = str(col)
        # Column names are like "('P1_a ', 'Idade')"
        try:
            parsed = ast.literal_eval(col_str)
            if isinstance(parsed, tuple) and len(parsed) >= 1:
                p_code = parsed[0].strip()
                if p_code in P_CODE_TO_STANDARD:
                    new_cols[col] = P_CODE_TO_STANDARD[p_code]
                else:
                    # Use the descriptive part
                    desc = parsed[1].strip() if len(parsed) > 1 else p_code
                    new_cols[col] = f"_{p_code}_{desc}"
        except (ValueError, SyntaxError):
            pass
    return df.rename(columns=new_cols)


def normalize_2024_2025_columns(df):
    """Normalize descriptive column names from 2024-2025 / 2025-2026."""
    new_cols = {}
    for col in df.columns:
        if col in DESC_TO_STANDARD:
            new_cols[col] = DESC_TO_STANDARD[col]
    return df.rename(columns=new_cols)


for f in files:
    path = os.path.join(DATA_DIR, f)
    year = f.split("State of Data ")[1].split(" -")[0].strip()

    for enc in ["utf-8", "latin-1", "cp1252"]:
        try:
            df = pd.read_csv(path, encoding=enc, low_memory=False)
            break
        except:
            continue

    # Normalize columns based on edition
    if "2023-2024" in year:
        df = normalize_2023_columns(df)
    else:
        df = normalize_2024_2025_columns(df)

    df["ano_pesquisa"] = year
    datasets[year] = df
    print(f"  ✓ {year}: {df.shape[0]:,} linhas × {df.shape[1]} colunas")

# =========================================================================
# 2. Verificar colunas-chave harmonizadas
# =========================================================================
print("\n" + "=" * 80)
print("COLUNAS-CHAVE HARMONIZADAS")
print("=" * 80)

KEY_COLS = [
    "genero", "faixa_idade", "cor_raca_etnia", "regiao_onde_mora",
    "nivel_de_ensino", "cargo_atual", "nivel", "faixa_salarial",
    "tempo_experiencia_dados", "modelo_trabalho_atual", "setor",
    "satisfeito_atualmente", "linguagem_preferida",
]

for col in KEY_COLS:
    present = []
    for year, df in datasets.items():
        if col in df.columns:
            present.append(year)
    status = "✓" if len(present) == 3 else "⚠" if len(present) > 0 else "✗"
    print(f"  {status} {col:35s} → presente em: {', '.join(present) if present else 'NENHUMA'}")

# =========================================================================
# 3. Análises e Gráficos
# =========================================================================
print("\n" + "=" * 80)
print("GERANDO ANALISES E GRAFICOS")
print("=" * 80)


def save_fig(fig, name):
    path = os.path.join(OUTPUT_DIR, f"{name}.png")
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  ✓ Salvo: {path}")


# --- 3.1 Respondentes por ano ---
fig, ax = plt.subplots()
years = list(datasets.keys())
counts = [len(df) for df in datasets.values()]
bars = ax.bar(years, counts, color=COLORS[:3], edgecolor="white", linewidth=2)
for bar, count in zip(bars, counts):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50,
            f"{count:,}", ha="center", va="bottom", fontweight="bold", fontsize=13)
ax.set_title("Total de Respondentes por Edição", fontsize=16, fontweight="bold")
ax.set_ylabel("Respondentes")
ax.set_ylim(0, max(counts) * 1.15)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
save_fig(fig, "01_respondentes_por_ano")

# --- 3.2 Gênero por ano ---
if all("genero" in df.columns for df in datasets.values()):
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    for ax, (year, df) in zip(axes, datasets.items()):
        vc = df["genero"].value_counts()
        ax.pie(vc.values, labels=vc.index, autopct="%1.1f%%",
               colors=COLORS, startangle=90, textprops={"fontsize": 10})
        ax.set_title(f"{year}", fontsize=14, fontweight="bold")
    fig.suptitle("Diversidade de Gênero por Edição", fontsize=16, fontweight="bold", y=1.02)
    fig.tight_layout()
    save_fig(fig, "02_genero_por_ano")

# --- 3.3 Região ---
if all("regiao_onde_mora" in df.columns for df in datasets.values()):
    fig, ax = plt.subplots(figsize=(14, 7))
    regions_data = {}
    for year, df in datasets.items():
        vc = df["regiao_onde_mora"].value_counts(normalize=True) * 100
        regions_data[year] = vc
    reg_df = pd.DataFrame(regions_data).fillna(0)
    reg_df.plot(kind="bar", ax=ax, color=COLORS[:3], edgecolor="white", linewidth=1.5)
    ax.set_title("Distribuição por Região (%)", fontsize=16, fontweight="bold")
    ax.set_ylabel("Percentual (%)")
    ax.legend(title="Edição")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
    save_fig(fig, "03_regiao_por_ano")

# --- 3.4 Nível de senioridade ---
if all("nivel" in df.columns for df in datasets.values()):
    fig, ax = plt.subplots(figsize=(12, 6))
    nivel_data = {}
    for year, df in datasets.items():
        vc = df["nivel"].dropna().value_counts()
        nivel_data[year] = vc
    nivel_df = pd.DataFrame(nivel_data).fillna(0)
    nivel_df.plot(kind="bar", ax=ax, color=COLORS[:3], edgecolor="white", linewidth=1.5)
    ax.set_title("Distribuição por Nível de Senioridade", fontsize=16, fontweight="bold")
    ax.set_ylabel("Respondentes")
    ax.legend(title="Edição")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
    save_fig(fig, "04_nivel_senioridade")

# --- 3.5 Faixa salarial ---
if all("faixa_salarial" in df.columns for df in datasets.values()):
    fig, axes = plt.subplots(1, 3, figsize=(24, 8))
    for ax, (year, df) in zip(axes, datasets.items()):
        vc = df["faixa_salarial"].dropna().value_counts().head(10)
        bars = ax.barh(range(len(vc)), vc.values, color=COLORS[0])
        ax.set_yticks(range(len(vc)))
        ax.set_yticklabels([str(v)[:35] for v in vc.index], fontsize=9)
        ax.set_title(f"{year}", fontsize=13, fontweight="bold")
        ax.set_xlabel("Respondentes")
        ax.invert_yaxis()
    fig.suptitle("Top 10 Faixas Salariais por Edição", fontsize=16, fontweight="bold", y=1.02)
    fig.tight_layout()
    save_fig(fig, "05_faixa_salarial")

# --- 3.6 Cargo atual ---
if all("cargo_atual" in df.columns for df in datasets.values()):
    fig, axes = plt.subplots(1, 3, figsize=(24, 8))
    for ax, (year, df) in zip(axes, datasets.items()):
        vc = df["cargo_atual"].dropna().value_counts().head(10)
        bars = ax.barh(range(len(vc)), vc.values, color=COLORS[1])
        ax.set_yticks(range(len(vc)))
        ax.set_yticklabels([str(v)[:40] for v in vc.index], fontsize=9)
        ax.set_title(f"{year}", fontsize=13, fontweight="bold")
        ax.set_xlabel("Respondentes")
        ax.invert_yaxis()
    fig.suptitle("Top 10 Cargos por Edição", fontsize=16, fontweight="bold", y=1.02)
    fig.tight_layout()
    save_fig(fig, "06_cargo_atual")

# --- 3.7 Modelo de trabalho ---
if all("modelo_trabalho_atual" in df.columns for df in datasets.values()):
    fig, ax = plt.subplots(figsize=(14, 7))
    mt_data = {}
    for year, df in datasets.items():
        vc = df["modelo_trabalho_atual"].dropna().value_counts(normalize=True) * 100
        mt_data[year] = vc
    mt_df = pd.DataFrame(mt_data).fillna(0)
    mt_df.plot(kind="bar", ax=ax, color=COLORS[:3], edgecolor="white", linewidth=1.5)
    ax.set_title("Modelo de Trabalho Atual (%)", fontsize=16, fontweight="bold")
    ax.set_ylabel("Percentual (%)")
    ax.legend(title="Edição")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
    save_fig(fig, "07_modelo_trabalho")

# --- 3.8 Tempo de experiência em dados ---
if all("tempo_experiencia_dados" in df.columns for df in datasets.values()):
    fig, ax = plt.subplots(figsize=(14, 7))
    exp_data = {}
    for year, df in datasets.items():
        vc = df["tempo_experiencia_dados"].dropna().value_counts()
        exp_data[year] = vc
    exp_df = pd.DataFrame(exp_data).fillna(0)
    exp_df.plot(kind="bar", ax=ax, color=COLORS[:3], edgecolor="white", linewidth=1.5)
    ax.set_title("Tempo de Experiência em Dados", fontsize=16, fontweight="bold")
    ax.set_ylabel("Respondentes")
    ax.legend(title="Edição")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
    save_fig(fig, "08_experiencia_dados")

# --- 3.9 Setor ---
if all("setor" in df.columns for df in datasets.values()):
    fig, axes = plt.subplots(1, 3, figsize=(24, 8))
    for ax, (year, df) in zip(axes, datasets.items()):
        vc = df["setor"].dropna().value_counts().head(10)
        bars = ax.barh(range(len(vc)), vc.values, color=COLORS[2])
        ax.set_yticks(range(len(vc)))
        ax.set_yticklabels([str(v)[:35] for v in vc.index], fontsize=9)
        ax.set_title(f"{year}", fontsize=13, fontweight="bold")
        ax.set_xlabel("Respondentes")
        ax.invert_yaxis()
    fig.suptitle("Top 10 Setores por Edição", fontsize=16, fontweight="bold", y=1.02)
    fig.tight_layout()
    save_fig(fig, "09_setor")

# --- 3.10 Nível de ensino ---
if all("nivel_de_ensino" in df.columns for df in datasets.values()):
    fig, ax = plt.subplots(figsize=(14, 7))
    ens_data = {}
    for year, df in datasets.items():
        vc = df["nivel_de_ensino"].dropna().value_counts()
        ens_data[year] = vc
    ens_df = pd.DataFrame(ens_data).fillna(0)
    ens_df.plot(kind="bar", ax=ax, color=COLORS[:3], edgecolor="white", linewidth=1.5)
    ax.set_title("Nível de Ensino", fontsize=16, fontweight="bold")
    ax.set_ylabel("Respondentes")
    ax.legend(title="Edição")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
    save_fig(fig, "10_nivel_ensino")

# --- 3.11 Faixa etária ---
if all("faixa_idade" in df.columns for df in datasets.values()):
    fig, ax = plt.subplots(figsize=(14, 7))
    fi_data = {}
    for year, df in datasets.items():
        vc = df["faixa_idade"].dropna().value_counts()
        fi_data[year] = vc
    fi_df = pd.DataFrame(fi_data).fillna(0)
    # Sort by age range
    fi_df = fi_df.reindex(sorted(fi_df.index))
    fi_df.plot(kind="bar", ax=ax, color=COLORS[:3], edgecolor="white", linewidth=1.5)
    ax.set_title("Distribuição por Faixa Etária", fontsize=16, fontweight="bold")
    ax.set_ylabel("Respondentes")
    ax.legend(title="Edição")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
    save_fig(fig, "11_faixa_etaria")

# --- 3.12 Satisfação ---
if all("satisfeito_atualmente" in df.columns for df in datasets.values()):
    fig, ax = plt.subplots(figsize=(10, 6))
    sat_data = {}
    for year, df in datasets.items():
        col = df["satisfeito_atualmente"].dropna()
        # Normalize boolean-like values
        col = col.astype(str).str.strip().str.lower()
        satisfeitos = col.isin(["true", "1", "1.0", "sim", "yes"]).sum()
        total = len(col)
        sat_data[year] = satisfeitos / total * 100
    bars = ax.bar(sat_data.keys(), sat_data.values(), color=COLORS[:3],
                  edgecolor="white", linewidth=2)
    for bar, pct in zip(bars, sat_data.values()):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f"{pct:.1f}%", ha="center", va="bottom", fontweight="bold", fontsize=13)
    ax.set_title("Taxa de Satisfação no Emprego Atual (%)", fontsize=16, fontweight="bold")
    ax.set_ylabel("Satisfeitos (%)")
    ax.set_ylim(0, 100)
    save_fig(fig, "12_satisfacao")

# =========================================================================
# 4. Resumo estatístico
# =========================================================================
print("\n" + "=" * 80)
print("RESUMO ESTATISTICO")
print("=" * 80)

for year, df in datasets.items():
    print(f"\n--- {year} ({df.shape[0]:,} respondentes) ---")
    for col in KEY_COLS:
        if col in df.columns:
            top = df[col].value_counts().head(3)
            top_str = " | ".join([f"{v}: {c}" for v, c in top.items()])
            print(f"  {col:35s} → Top 3: {top_str}")

print("\n✅ Análise exploratória concluída!")
print(f"📊 Gráficos salvos em: {OUTPUT_DIR}")
