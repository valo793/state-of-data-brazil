"""
Tech Challenge Fase 3 — Análise Exploratória Inicial da Camada Bronze
====================================================================
Script de perfilamento inicial dos dados brutos com caminhos relativos portáteis.
"""

from pathlib import Path
import os
import ast
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data" / "bronze"
OUTPUT_DIR = BASE_DIR / "output" / "graficos"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

plt.style.use("seaborn-v0_8-whitegrid")
plt.rcParams["figure.figsize"] = (10, 6)
plt.rcParams["font.size"] = 11

P_CODE_TO_STANDARD = {
    "P0": "id",
    "P1_a": "idade",
    "P1_a_1": "faixa_idade",
    "P1_b": "genero",
    "P1_c": "cor_raca_etnia",
    "P1_d": "pcd",
    "P1_i_1": "uf_onde_mora",
    "P1_i_2": "regiao_onde_mora",
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
    "P4_c": "linguagem_preferida",
    "P4_d": "linguagem_mais_usada",
    "P4_f": "linguagem_preferida",
}

DESC_TO_STANDARD = {
    "0.a_token": "id",
    "1.a_idade": "idade",
    "1.a.1_faixa_idade": "faixa_idade",
    "1.b_genero": "genero",
    "1.c_cor/raca/etnia": "cor_raca_etnia",
    "1.d_pcd": "pcd",
    "1.i.1_uf_onde_mora": "uf_onde_mora",
    "1.i.2_regiao_onde_mora": "regiao_onde_mora",
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
    "4.b_linguagem_mais_utilizada": "linguagem_mais_usada",
    "4.e_linguagem_mais_utilizada": "linguagem_mais_usada",
}


def normalize_columns(df, is_2023_2024=False):
    new_cols = {}
    for col in df.columns:
        col_str = str(col)
        if is_2023_2024:
            try:
                parsed = ast.literal_eval(col_str)
                if isinstance(parsed, tuple):
                    p_code = parsed[0].strip()
                    if p_code in P_CODE_TO_STANDARD:
                        new_cols[col] = P_CODE_TO_STANDARD[p_code]
                        continue
                    new_cols[col] = f"{p_code}_{parsed[1].strip()}"
                    continue
            except:
                pass
        col_clean = col_str.strip()
        if col_clean in DESC_TO_STANDARD:
            new_cols[col] = DESC_TO_STANDARD[col_clean]
        else:
            new_cols[col] = col_clean
    return df.rename(columns=new_cols)


def run():
    print("=" * 80)
    print("CARREGAMENTO E PERFILAMENTO DA CAMADA BRONZE")
    print("=" * 80)
    
    files = sorted(list(DATA_DIR.glob("*.csv")))
    datasets = {}
    for f in files:
        df = pd.read_csv(f, encoding="utf-8", low_memory=False)
        year = f.name.split("State of Data ")[1].split(" -")[0].strip()
        is_23 = "2023-2024" in year
        df = normalize_columns(df, is_2023_2024=is_23)
        df["ano_pesquisa"] = year
        datasets[year] = df
        print(f"  ✓ {year}: {df.shape[0]:,} linhas × {df.shape[1]} colunas")
    
    print("\n✅ Perfilamento inicial concluído com sucesso!")


if __name__ == "__main__":
    run()
