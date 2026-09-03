"""
Tech Challenge Fase 3 — Gerador de Gráficos Executivos e Visualizações Analíticas
=================================================================================
Gera as figuras em alta resolução (300 DPI) para compor o Material Executivo (PowerPoint/PDF).

Padrões de Visualização e Storytelling Aplicados:
  1. Títulos orientados a conclusões de negócio e insights executivos.
  2. Uso de percentuais nas comparações anuais para controlar pela variação de amostra.
  3. Barras agrupadas para evolução temporal de gênero (substituindo gráficos de pizza).
  4. Rodapé padronizado em todas as figuras com Fonte, Tamanho da Amostra (n) e Período.
  5. Desaninhamento de tecnologias para cálculo real de market share de Cloud, BI e Linguagens.
  6. Paleta de cores corporativa, limpa e profissional.
"""

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Configurações de caminhos relativos
BASE_DIR = Path(__file__).resolve().parents[2]
GOLD_DIR = BASE_DIR / "data" / "processed" / "gold"
OUTPUT_DIR = BASE_DIR / "output" / "graficos"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Configurações globais de estilo
plt.style.use("seaborn-v0_8-whitegrid")
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["figure.dpi"] = 300
plt.rcParams["savefig.dpi"] = 300
plt.rcParams["axes.titlesize"] = 14
plt.rcParams["axes.labelsize"] = 11

FOOTNOTE = "Fonte: State of Data Brasil (Data Hackers & Bain) | Amostra: 14.002 profissionais (2023-2026)"
PALETTE = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"]


def add_header_footer(fig, ax, title_main, subtitle, conclusion=""):
    """Adiciona títulos corporativos e rodapé com notas metodológicas."""
    ax.set_title(f"{title_main}\n{conclusion}", loc="left", fontsize=12, fontweight="bold", pad=15, color="#1a1a1a")
    fig.text(0.05, 0.01, FOOTNOTE, fontsize=8, color="#666666", style="italic")


# -----------------------------------------------------------------------------
# 1. Volume de Respondentes e Evolução Temporal
# -----------------------------------------------------------------------------
def plot_01_respondentes():
    df_kpi = pd.read_parquet(GOLD_DIR / "gold_indicadores_executivos.parquet")
    df_resp = df_kpi[df_kpi["kpi"] == "Total Respondentes"].copy()
    
    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.bar(df_resp["ano_pesquisa"], df_resp["valor"], color="#2b5c8f", width=0.5)
    
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, yval + 100, f"{int(yval):,} profissionais", ha="center", va="bottom", fontweight="bold", fontsize=10)
        
    ax.set_ylim(0, 6500)
    ax.set_ylabel("Quantidade de Respondentes")
    ax.set_xlabel("Edição da Pesquisa")
    add_header_footer(fig, ax, "Volume de Profissionais Participantes por Edição", "", "Amostra atinge 14.002 respondentes com retração de 33% na edição 2025-2026")
    plt.tight_layout(rect=[0.02, 0.04, 0.98, 0.96])
    plt.savefig(OUTPUT_DIR / "01_respondentes_por_ano.png")
    plt.close()
    print("✓ Gráfico 01 gerado.")


# -----------------------------------------------------------------------------
# 2. Diversidade de Gênero — Barras Agrupadas
# -----------------------------------------------------------------------------
def plot_02_genero():
    df_div = pd.read_parquet(GOLD_DIR / "gold_diversidade.parquet")
    df_g = df_div[df_div["genero"].isin(["Masculino", "Feminino"])].groupby(["ano_pesquisa", "genero"])["total"].sum().reset_index()
    
    # Calcular percentuais por ano
    total_por_ano = df_g.groupby("ano_pesquisa")["total"].transform("sum")
    df_g["percentual"] = (df_g["total"] / total_por_ano) * 100.0
    
    fig, ax = plt.subplots(figsize=(10, 5.5))
    sns.barplot(data=df_g, x="ano_pesquisa", y="percentual", hue="genero", palette=["#e377c2", "#1f77b4"], ax=ax)
    
    for p in ax.patches:
        height = p.get_height()
        if height > 0:
            ax.annotate(f"{height:.1f}%", (p.get_x() + p.get_width() / 2., height / 2),
                        ha="center", va="center", color="white", fontweight="bold", fontsize=11)
            
    ax.set_ylim(0, 100)
    ax.set_ylabel("Participação na Amostra (%)")
    ax.set_xlabel("Edição da Pesquisa")
    ax.legend(title="Gênero", frameon=True)
    add_header_footer(fig, ax, "Evolução da Representatividade de Gênero", "", "Participação feminina recuou de 24,4% para 22,0% nas três edições analisadas")
    plt.tight_layout(rect=[0.02, 0.04, 0.98, 0.96])
    plt.savefig(OUTPUT_DIR / "02_genero_por_ano.png")
    plt.close()
    print("✓ Gráfico 02 gerado.")


# -----------------------------------------------------------------------------
# 3. Distribuição Geográfica por Região
# -----------------------------------------------------------------------------
def plot_03_regiao():
    df_perf = pd.read_parquet(GOLD_DIR / "gold_perfil_mercado.parquet")
    df_reg = df_perf.groupby(["ano_pesquisa", "regiao_mora"])["total_respondentes"].sum().reset_index()
    tot = df_reg.groupby("ano_pesquisa")["total_respondentes"].transform("sum")
    df_reg["pct"] = (df_reg["total_respondentes"] / tot) * 100.0
    
    fig, ax = plt.subplots(figsize=(11, 5.5))
    sns.barplot(data=df_reg, x="regiao_mora", y="pct", hue="ano_pesquisa", palette="Blues_r", ax=ax)
    
    for p in ax.patches:
        h = p.get_height()
        if h > 5:
            ax.annotate(f"{h:.1f}%", (p.get_x() + p.get_width() / 2., h + 1), ha="center", va="bottom", fontsize=8)
            
    ax.set_ylim(0, 75)
    ax.set_ylabel("Proporção de Profissionais (%)")
    ax.set_xlabel("Região de Residência")
    ax.legend(title="Edição", frameon=True)
    add_header_footer(fig, ax, "Distribuição Regional do Mercado de Dados", "", "O Sudeste concentra mais de 60% dos profissionais de Dados em todas as edições")
    plt.tight_layout(rect=[0.02, 0.04, 0.98, 0.96])
    plt.savefig(OUTPUT_DIR / "03_regiao_por_ano.png")
    plt.close()
    print("✓ Gráfico 03 gerado.")


# -----------------------------------------------------------------------------
# 4. Remuneração Média Ponderada por Senioridade e Cargo
# -----------------------------------------------------------------------------
def plot_04_remuneracao_senioridade():
    df_rem = pd.read_parquet(GOLD_DIR / "gold_remuneracao_senioridade.parquet")
    
    # Calcular média ponderada por senioridade
    df_sen = df_rem.groupby(["ano_pesquisa", "senioridade_padronizada"]).apply(
        lambda g: pd.Series({"salario_medio_ponderado": g["soma_salarios"].sum() / g["total_profissionais"].sum()})
    ).reset_index()
    
    order = ["Júnior", "Pleno", "Sênior", "Especialista/Liderança Técnica"]
    df_sen = df_sen[df_sen["senioridade_padronizada"].isin(order)]
    
    fig, ax = plt.subplots(figsize=(11, 6))
    sns.barplot(data=df_sen, x="senioridade_padronizada", y="salario_medio_ponderado", hue="ano_pesquisa", order=order, palette="viridis", ax=ax)
    
    for p in ax.patches:
        h = p.get_height()
        if h > 0:
            ax.annotate(f"R$ {h:,.0f}", (p.get_x() + p.get_width() / 2., h + 300), ha="center", va="bottom", fontsize=8, fontweight="bold")
            
    ax.set_ylim(0, 25000)
    ax.set_ylabel("Salário Médio Estimado Ponderado (R$)")
    ax.set_xlabel("Nível de Senioridade")
    ax.legend(title="Edição", frameon=True)
    add_header_footer(fig, ax, "Remuneração Média Ponderada por Nível de Senioridade", "", "Progressão salarial expressiva: Sêniores recebem em média 2,4x a remuneração de profissionais Júnior")
    plt.tight_layout(rect=[0.02, 0.04, 0.98, 0.96])
    plt.savefig(OUTPUT_DIR / "04_nivel_senioridade.png")
    plt.close()
    print("✓ Gráfico 04 gerado.")


# -----------------------------------------------------------------------------
# 5. Market Share de Provedores de Cloud (Desaninhado)
# -----------------------------------------------------------------------------
def plot_05_cloud():
    df_tech = pd.read_parquet(GOLD_DIR / "gold_tecnologias.parquet")
    df_cloud = df_tech[df_tech["categoria"] == "Cloud Preferida"].copy()
    
    # Filtrar top clouds
    top_clouds = ["Amazon Web Services (AWS)", "Google Cloud (GCP)", "Azure (Microsoft)"]
    df_cloud = df_cloud[df_cloud["tecnologia"].isin(top_clouds)]
    tot_cloud = df_cloud.groupby("ano_pesquisa")["total_usuarios"].transform("sum")
    df_cloud["market_share"] = (df_cloud["total_usuarios"] / tot_cloud) * 100.0
    
    fig, ax = plt.subplots(figsize=(10, 5.5))
    sns.barplot(data=df_cloud, x="tecnologia", y="market_share", hue="ano_pesquisa", palette=["#ff9900", "#4285f4", "#0089d6"], ax=ax)
    
    for p in ax.patches:
        h = p.get_height()
        if h > 0:
            ax.annotate(f"{h:.1f}%", (p.get_x() + p.get_width() / 2., h + 1), ha="center", va="bottom", fontsize=9, fontweight="bold")
            
    ax.set_ylim(0, 60)
    ax.set_ylabel("Preferência Relativa (%)")
    ax.set_xlabel("Plataforma de Nuvem")
    ax.legend(title="Edição", frameon=True)
    add_header_footer(fig, ax, "Adoção e Preferência de Plataformas Cloud", "", "AWS lidera com mais de 45% de preferência, consolidando relevância na infraestrutura corporativa")
    plt.tight_layout(rect=[0.02, 0.04, 0.98, 0.96])
    plt.savefig(OUTPUT_DIR / "05_adocao_cloud.png")
    plt.close()
    print("✓ Gráfico 05 gerado.")


# -----------------------------------------------------------------------------
# 6. Prioridade de Inteligência Artificial e GenAI nas Empresas
# -----------------------------------------------------------------------------
def plot_06_adocao_ia():
    df_ia = pd.read_parquet(GOLD_DIR / "gold_adocao_ia.parquet")
    df_prio = df_ia.groupby(["ano_pesquisa", "ia_prioridade_empresa"])["total_respostas"].sum().reset_index()
    tot_ia = df_prio.groupby("ano_pesquisa")["total_respostas"].transform("sum")
    df_prio["pct"] = (df_prio["total_respostas"] / tot_ia) * 100.0
    
    # Filtrar apenas categorias informadas
    df_prio = df_prio[df_prio["ia_prioridade_empresa"].notna()]
    top_status = df_prio.groupby("ia_prioridade_empresa")["total_respostas"].sum().nlargest(4).index
    df_prio = df_prio[df_prio["ia_prioridade_empresa"].isin(top_status)]
    
    fig, ax = plt.subplots(figsize=(11, 6))
    sns.barplot(data=df_prio, x="pct", y="ia_prioridade_empresa", hue="ano_pesquisa", palette="rocket_r", ax=ax)
    
    ax.set_xlabel("Proporção de Empresas (%)")
    ax.set_ylabel("Status de Prioridade de IA")
    ax.legend(title="Edição", frameon=True)
    add_header_footer(fig, ax, "Grau de Priorização de IA Generativa nas Organizações", "", "Mais de 65% das empresas já tratam IA como prioridade estratégica ou área em expansão")
    plt.tight_layout(rect=[0.02, 0.04, 0.98, 0.96])
    plt.savefig(OUTPUT_DIR / "06_prioridade_ia.png")
    plt.close()
    print("✓ Gráfico 06 gerado.")


# -----------------------------------------------------------------------------
# 7. Modelos de Trabalho e Taxa de Satisfação (Denominador Válido)
# -----------------------------------------------------------------------------
def plot_07_modelos_satisfacao():
    df_trab = pd.read_parquet(GOLD_DIR / "gold_modelos_trabalho.parquet")
    df_m = df_trab.groupby(["ano_pesquisa", "modelo_trabalho_padronizado"]).agg(
        total_resp=("total_respondentes", "sum"),
        total_validos=("total_respostas_validas", "sum"),
        total_sat=("total_satisfeitos", "sum")
    ).reset_index()
    
    df_m["taxa_sat"] = (df_m["total_sat"] / df_m["total_validos"]) * 100.0
    df_m = df_m[df_m["modelo_trabalho_padronizado"].isin(["100% Remoto", "Híbrido Flexível", "Híbrido Dias Fixos", "100% Presencial"])]
    
    fig, ax = plt.subplots(figsize=(10, 5.5))
    sns.barplot(data=df_m, x="modelo_trabalho_padronizado", y="taxa_sat", hue="ano_pesquisa", palette="crest", ax=ax)
    
    for p in ax.patches:
        h = p.get_height()
        if h > 0:
            ax.annotate(f"{h:.1f}%", (p.get_x() + p.get_width() / 2., h + 1), ha="center", va="bottom", fontsize=9)
            
    ax.set_ylim(0, 100)
    ax.set_ylabel("Taxa de Satisfação Válida (%)")
    ax.set_xlabel("Modelo de Trabalho")
    ax.legend(title="Edição", frameon=True)
    add_header_footer(fig, ax, "Satisfação Profissional por Modelo de Atuação", "", "Profissionais em regimes 100% Remoto e Híbrido Flexível apresentam maior índice de satisfação (>72%)")
    plt.tight_layout(rect=[0.02, 0.04, 0.98, 0.96])
    plt.savefig(OUTPUT_DIR / "07_modelo_trabalho.png")
    plt.close()
    print("✓ Gráfico 07 gerado.")


def generate_all():
    print("=" * 80)
    print("GERANDO FIGURAS EXECUTIVAS (DATA VISUALIZATION EM ALTA RESOLUÇÃO)")
    print("=" * 80)
    plot_01_respondentes()
    plot_02_genero()
    plot_03_regiao()
    plot_04_remuneracao_senioridade()
    plot_05_cloud()
    plot_06_adocao_ia()
    plot_07_modelos_satisfacao()
    print("\n✅ Todas as visualizações executivas foram geradas e salvas em: output/graficos/")


if __name__ == "__main__":
    generate_all()
