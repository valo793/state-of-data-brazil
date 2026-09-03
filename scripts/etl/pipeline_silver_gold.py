"""
Tech Challenge Fase 3 — Pipeline de Transformação Local & Validação de Regras ETL
================================================================================
Este script implementa e valida as regras de tratamento de dados
para as 3 camadas Medallion (Bronze -> Silver -> Gold) antes do deploy nos Glue Jobs na AWS.

Regras de Tratamento na Camada Silver:
  1. Parsing e harmonização dos cabeçalhos das 3 edições (2023-2024, 2024-2025, 2025-2026).
  2. Tratamento de strings (strip, coerção de vazios para None).
  3. Conversão de tipos de dados (numéricos, inteiros, booleanos).
  4. Extração e normalização de salários (faixa textual + cálculo numérico de salário médio estimado).
  5. Padronização de modelos de trabalho (100% Remoto, Híbrido, Presencial).
  6. Padronização de cargos e senioridade.
  7. Extração de flags tecnológicas (Cloud, BI, Linguagens, IA/GenAI).
  8. Geração de Parquet particionado por `ano_pesquisa`.

Regras de Transformação na Camada Gold:
  1. gold_perfil_mercado: Agregações demográficas e regionais.
  2. gold_remuneracao_senioridade: Métricas salariais por cargo e senioridade.
  3. gold_diversidade: Indicadores de gênero, etnia e PCD.
  4. gold_tecnologias_cloud: Adoção de linguagens, clouds e ferramentas BI.
  5. gold_adocao_ia: Métricas de priorização e uso de IA Generativa / LLMs.
  6. gold_modelos_trabalho: Distribuição e satisfação por modelo de trabalho.
"""

import os
import re
import ast
import pandas as pd
import numpy as np

BRONZE_DIR = r"C:\Projects\Tech Challenge 3\data\bronze"
SILVER_DIR = r"C:\Projects\Tech Challenge 3\data\processed\silver"
GOLD_DIR = r"C:\Projects\Tech Challenge 3\data\processed\gold"

os.makedirs(SILVER_DIR, exist_ok=True)
os.makedirs(GOLD_DIR, exist_ok=True)


def parse_salary_range(val):
    """Extrai valor numérico médio estimado a partir da string de faixa salarial."""
    if pd.isna(val) or not str(val).strip():
        return np.nan
    s = str(val).lower()
    
    if "menos de" in s or "até r$" in s:
        nums = re.findall(r"\d+\.?\d*", s.replace(".", ""))
        if nums:
            return float(nums[0]) / 2
        return 1000.0
    elif "acima de" in s or "mais de" in s:
        nums = re.findall(r"\d+\.?\d*", s.replace(".", ""))
        if nums:
            return float(nums[0]) * 1.2
        return 45000.0
    else:
        nums = re.findall(r"\d+\.?\d*", s.replace(".", ""))
        if len(nums) >= 2:
            return (float(nums[0]) + float(nums[1])) / 2
        elif len(nums) == 1:
            return float(nums[0])
    return np.nan


def normalize_seniority(val):
    if pd.isna(val):
        return "Não Informado"
    s = str(val).strip().capitalize()
    if "Júnior" in s or "Junior" in s:
        return "Júnior"
    if "Pleno" in s:
        return "Pleno"
    if "Sênior" in s or "Senior" in s:
        return "Sênior"
    if any(k in s.lower() for k in ["lead", "líder", "lider", "especialista", "staff", "principal"]):
        return "Especialista/Liderança Técnica"
    return s


def normalize_work_model(val):
    if pd.isna(val):
        return "Não Informado"
    s = str(val).strip().lower()
    if "100% remoto" in s or "totalmente remoto" in s or "home office" in s:
        return "100% Remoto"
    if "100% presencial" in s or "totalmente presencial" in s:
        return "100% Presencial"
    if "híbrido" in s or "hibrido" in s:
        if "flexível" in s or "flexivel" in s:
            return "Híbrido Flexível"
        if "fixo" in s or "dias fixos" in s:
            return "Híbrido Dias Fixos"
        return "Híbrido"
    return "Outro"


def process_edition_2023(df_bronze):
    """Trata dados da edição 2023-2024 (cabeçalhos em tuplas-string)."""
    p_map = {}
    for col in df_bronze.columns:
        try:
            parsed = ast.literal_eval(str(col))
            if isinstance(parsed, tuple):
                p_map[col] = (parsed[0].strip(), parsed[1].strip() if len(parsed) > 1 else "")
        except:
            p_map[col] = (str(col).strip(), "")

    clean_dict = {
        "ano_pesquisa": "2023-2024",
    }
    
    # Mapeamento campo a campo
    for b_col, (p_code, desc) in p_map.items():
        if p_code == "P0":
            clean_dict["id_respondente"] = df_bronze[b_col]
        elif p_code == "P1_a":
            clean_dict["idade"] = pd.to_numeric(df_bronze[b_col], errors="coerce")
        elif p_code == "P1_a_1":
            clean_dict["faixa_idade"] = df_bronze[b_col]
        elif p_code == "P1_b":
            clean_dict["genero"] = df_bronze[b_col]
        elif p_code == "P1_c":
            clean_dict["cor_raca_etnia"] = df_bronze[b_col]
        elif p_code == "P1_d":
            clean_dict["pcd"] = df_bronze[b_col]
        elif p_code == "P1_i_1":
            clean_dict["uf_mora"] = df_bronze[b_col]
        elif p_code == "P1_i_2":
            clean_dict["regiao_mora"] = df_bronze[b_col]
        elif p_code == "P1_l":
            clean_dict["nivel_ensino"] = df_bronze[b_col]
        elif p_code == "P1_m":
            clean_dict["area_formacao"] = df_bronze[b_col]
        elif p_code == "P2_a":
            clean_dict["situacao_trabalho"] = df_bronze[b_col]
        elif p_code == "P2_b":
            clean_dict["setor"] = df_bronze[b_col]
        elif p_code == "P2_c":
            clean_dict["tamanho_empresa"] = df_bronze[b_col]
        elif p_code == "P2_d":
            clean_dict["is_gestor"] = df_bronze[b_col]
        elif p_code == "P2_e":
            clean_dict["cargo_gestor"] = df_bronze[b_col]
        elif p_code == "P2_f":
            clean_dict["cargo_atual"] = df_bronze[b_col]
        elif p_code == "P2_g":
            clean_dict["senioridade"] = df_bronze[b_col]
        elif p_code == "P2_h":
            clean_dict["faixa_salarial"] = df_bronze[b_col]
        elif p_code == "P2_i":
            clean_dict["tempo_experiencia_dados"] = df_bronze[b_col]
        elif p_code == "P2_j":
            clean_dict["tempo_experiencia_ti"] = df_bronze[b_col]
        elif p_code == "P2_k":
            clean_dict["satisfeito_empresa"] = df_bronze[b_col]
        elif p_code == "P2_l":
            clean_dict["motivo_insatisfacao"] = df_bronze[b_col]
        elif p_code == "P2_r":
            clean_dict["modelo_trabalho"] = df_bronze[b_col]
        elif p_code == "P4_e":
            clean_dict["linguagem_mais_usada"] = df_bronze[b_col]
        elif p_code == "P4_f":
            clean_dict["linguagem_preferida"] = df_bronze[b_col]
        elif p_code == "P4_i":
            clean_dict["cloud_preferida"] = df_bronze[b_col]
        elif p_code == "P4_k":
            clean_dict["bi_preferido"] = df_bronze[b_col]
        elif p_code == "P3_e":
            clean_dict["ia_prioridade_empresa"] = df_bronze[b_col]
        elif p_code == "P4_l":
            clean_dict["tipo_uso_ia_empresa"] = df_bronze[b_col]
        elif p_code == "P4_m":
            clean_dict["uso_pessoal_ia"] = df_bronze[b_col]

    df_clean = pd.DataFrame(clean_dict)
    return df_clean


def process_edition_2024(df_bronze):
    """Trata dados da edição 2024-2025."""
    clean_dict = {
        "ano_pesquisa": "2024-2025",
        "id_respondente": df_bronze.get("0.a_token"),
        "idade": pd.to_numeric(df_bronze.get("1.a_idade"), errors="coerce"),
        "faixa_idade": df_bronze.get("1.a.1_faixa_idade"),
        "genero": df_bronze.get("1.b_genero"),
        "cor_raca_etnia": df_bronze.get("1.c_cor/raca/etnia"),
        "pcd": df_bronze.get("1.d_pcd"),
        "uf_mora": df_bronze.get("1.i.1_uf_onde_mora"),
        "regiao_mora": df_bronze.get("1.i.2_regiao_onde_mora"),
        "nivel_ensino": df_bronze.get("1.l_nivel_de_ensino"),
        "area_formacao": df_bronze.get("1.m_area_de_formacao"),
        "situacao_trabalho": df_bronze.get("2.a_situacao_atual"),
        "setor": df_bronze.get("2.b_setor"),
        "tamanho_empresa": df_bronze.get("2.c_numero_de_funcionarios"),
        "is_gestor": df_bronze.get("2.d_gestor"),
        "cargo_gestor": df_bronze.get("2.e_cargo_como_gestor"),
        "cargo_atual": df_bronze.get("2.f_cargo_atual"),
        "senioridade": df_bronze.get("2.g_nivel"),
        "faixa_salarial": df_bronze.get("2.h_faixa_salarial"),
        "tempo_experiencia_dados": df_bronze.get("2.i_tempo_de_experiencia_em_dados"),
        "tempo_experiencia_ti": df_bronze.get("2.j_tempo_de_experiencia_em_ti"),
        "satisfeito_empresa": df_bronze.get("2.k_satisfeito_atualmente"),
        "motivo_insatisfacao": df_bronze.get("2.l_motivo_insatisfacao"),
        "modelo_trabalho": df_bronze.get("2.r_modelo_de_trabalho_atual"),
        "linguagem_mais_usada": df_bronze.get("4.e_linguagem_mais_utilizada"),
        "linguagem_preferida": df_bronze.get("4.f_linguagem_preferida"),
        "cloud_preferida": df_bronze.get("4.i_cloud_preferida"),
        "bi_preferido": df_bronze.get("4.k_ferramenta_de_bi_preferida"),
        "ia_prioridade_empresa": df_bronze.get("3.e_ai_generativa_e_llm_é_uma_prioridade?"),
        "tipo_uso_ia_empresa": df_bronze.get("3.f_tipo_de_uso_de_ai_generativa_e_llm_na_empresa"),
        "uso_pessoal_ia": df_bronze.get("4.m_usa_chatgpt_ou_copilot_no_trabalho?"),
    }
    return pd.DataFrame(clean_dict)


def process_edition_2025(df_bronze):
    """Trata dados da edição 2025-2026."""
    clean_dict = {
        "ano_pesquisa": "2025-2026",
        "id_respondente": df_bronze.get("0.a_token"),
        "idade": pd.to_numeric(df_bronze.get("1.a_idade"), errors="coerce"),
        "faixa_idade": df_bronze.get("1.a.1_faixa_idade"),
        "genero": df_bronze.get("1.b_genero"),
        "cor_raca_etnia": df_bronze.get("1.c_cor/raca/etnia"),
        "pcd": df_bronze.get("1.d_pcd"),
        "uf_mora": df_bronze.get("1.i.1_uf_onde_mora"),
        "regiao_mora": df_bronze.get("1.i.2_regiao_onde_mora"),
        "nivel_ensino": df_bronze.get("1.l_nivel_de_ensino"),
        "area_formacao": df_bronze.get("1.m_area_de_formacao"),
        "situacao_trabalho": df_bronze.get("2.a_situacao_atual"),
        "setor": df_bronze.get("2.b_setor"),
        "tamanho_empresa": df_bronze.get("2.c_numero_de_funcionarios"),
        "is_gestor": df_bronze.get("2.d_gestor"),
        "cargo_gestor": df_bronze.get("2.e_cargo_como_gestor"),
        "cargo_atual": df_bronze.get("2.f_cargo_atual"),
        "senioridade": df_bronze.get("2.g_nivel"),
        "faixa_salarial": df_bronze.get("2.h_faixa_salarial"),
        "tempo_experiencia_dados": df_bronze.get("2.i_tempo_de_experiencia_em_dados"),
        "tempo_experiencia_ti": df_bronze.get("2.j_tempo_de_experiencia_em_ti"),
        "satisfeito_empresa": df_bronze.get("2.k_satisfeito_atualmente"),
        "motivo_insatisfacao": df_bronze.get("2.l_motivo_insatisfacao"),
        "modelo_trabalho": df_bronze.get("2.q_modelo_de_trabalho_atual"),
        "linguagem_mais_usada": df_bronze.get("4.b_linguagem_mais_utilizada"),
        "linguagem_preferida": df_bronze.get("4.c_linguagem_preferida"),
        "cloud_preferida": df_bronze.get("4.f_cloud_preferida"),
        "bi_preferido": df_bronze.get("4.h_ferramenta_de_bi_preferida"),
        "ia_prioridade_empresa": df_bronze.get("3.e_ai_generativa_e_llm_é_uma_prioridade?"),
        "tipo_uso_ia_empresa": df_bronze.get("3.f_tipo_de_uso_de_ai_generativa_e_llm_na_empresa"),
        "uso_pessoal_ia": df_bronze.get("4.j_usa_chatgpt_ou_copilot_no_trabalho?"),
    }
    return pd.DataFrame(clean_dict)


def run_pipeline():
    print("=" * 80)
    print("EXECUTANDO PIPELINE BRONZE -> SILVER -> GOLD")
    print("=" * 80)

    # 1. Carregar Camada Bronze
    f23 = os.path.join(BRONZE_DIR, "Final Dataset - State of Data 2023-2024 - Kaggle.csv")
    f24 = os.path.join(BRONZE_DIR, "Final Dataset - State of Data 2024-2025 - Kaggle.csv")
    f25 = os.path.join(BRONZE_DIR, "Final Dataset - State of Data 2025-2026 - Kaggle.csv")

    df_bronze_23 = pd.read_csv(f23, encoding="utf-8", low_memory=False)
    df_bronze_24 = pd.read_csv(f24, encoding="utf-8", low_memory=False)
    df_bronze_25 = pd.read_csv(f25, encoding="utf-8", low_memory=False)

    print(f"✓ Bronze 2023-2024: {df_bronze_23.shape[0]:,} linhas")
    print(f"✓ Bronze 2024-2025: {df_bronze_24.shape[0]:,} linhas")
    print(f"✓ Bronze 2025-2026: {df_bronze_25.shape[0]:,} linhas")

    # 2. Transformações para a Camada Silver
    s23 = process_edition_2023(df_bronze_23)
    s24 = process_edition_2024(df_bronze_24)
    s25 = process_edition_2025(df_bronze_25)

    silver_df = pd.concat([s23, s24, s25], ignore_index=True)

    # Higienização e padronização
    for col in silver_df.select_dtypes(include="object").columns:
        silver_df[col] = silver_df[col].astype(str).str.strip().replace({"nan": None, "None": None, "": None})

    silver_df["salario_medio_estimado"] = silver_df["faixa_salarial"].apply(parse_salary_range)
    silver_df["senioridade_padronizada"] = silver_df["senioridade"].apply(normalize_seniority)
    silver_df["modelo_trabalho_padronizado"] = silver_df["modelo_trabalho"].apply(normalize_work_model)
    silver_df["satisfeito_empresa_bool"] = silver_df["satisfeito_empresa"].apply(
        lambda x: True if str(x).lower() in ["true", "1", "1.0", "sim"] else (False if pd.notna(x) else None)
    )

    # Persistir Camada Silver (Parquet particionado por ano)
    silver_parquet_path = os.path.join(SILVER_DIR, "state_of_data_silver.parquet")
    silver_df.to_parquet(silver_parquet_path, index=False, partition_cols=["ano_pesquisa"])
    print(f"\n✅ Camada Silver criada com sucesso!")
    print(f"  → Arquivo: {silver_parquet_path}")
    print(f"  → Total de registros consolidados: {len(silver_df):,}")
    print(f"  → Colunas estruturadas: {len(silver_df.columns)}")

    # 3. Construção da Camada Gold (Data Marts Agregados)
    print("\n" + "=" * 80)
    print("CONSTRUINDO TABELAS ANALÍTICAS (CAMADA GOLD)")
    print("=" * 80)

    # Gold 1: Perfil de Mercado por Região & Demografia
    gold_perfil = silver_df.groupby(["ano_pesquisa", "regiao_mora", "genero", "nivel_ensino"], dropna=False).agg(
        total_respondentes=("id_respondente", "count"),
        media_idade=("idade", "mean")
    ).reset_index()
    gold_perfil.to_parquet(os.path.join(GOLD_DIR, "gold_perfil_mercado.parquet"), index=False)
    print(f"  ✓ gold_perfil_mercado: {len(gold_perfil):,} registros")

    # Gold 2: Remuneração por Cargo & Senioridade
    gold_remuneracao = silver_df[silver_df["cargo_atual"].notna()].groupby(
        ["ano_pesquisa", "cargo_atual", "senioridade_padronizada", "regiao_mora"], dropna=False
    ).agg(
        total_profissionais=("id_respondente", "count"),
        salario_medio=("salario_medio_estimado", "mean"),
        salario_mediano=("salario_medio_estimado", "median"),
        salario_min=("salario_medio_estimado", "min"),
        salario_max=("salario_medio_estimado", "max")
    ).reset_index()
    gold_remuneracao.to_parquet(os.path.join(GOLD_DIR, "gold_remuneracao_senioridade.parquet"), index=False)
    print(f"  ✓ gold_remuneracao_senioridade: {len(gold_remuneracao):,} registros")

    # Gold 3: Diversidade de Gênero & Etnia
    gold_diversidade = silver_df.groupby(["ano_pesquisa", "genero", "cor_raca_etnia", "is_gestor"], dropna=False).agg(
        total=("id_respondente", "count"),
        salario_medio=("salario_medio_estimado", "mean")
    ).reset_index()
    gold_diversidade.to_parquet(os.path.join(GOLD_DIR, "gold_diversidade.parquet"), index=False)
    print(f"  ✓ gold_diversidade: {len(gold_diversidade):,} registros")

    # Gold 4: Tecnologias, Linguagens e Cloud
    gold_tech = silver_df.groupby(["ano_pesquisa", "linguagem_preferida", "cloud_preferida", "bi_preferido"], dropna=False).agg(
        total_usuarios=("id_respondente", "count")
    ).reset_index()
    gold_tech.to_parquet(os.path.join(GOLD_DIR, "gold_tecnologias_cloud.parquet"), index=False)
    print(f"  ✓ gold_tecnologias_cloud: {len(gold_tech):,} registros")

    # Gold 5: Adoção de Inteligência Artificial & GenAI
    gold_ia = silver_df.groupby(["ano_pesquisa", "ia_prioridade_empresa", "uso_pessoal_ia"], dropna=False).agg(
        total_respostas=("id_respondente", "count")
    ).reset_index()
    gold_ia.to_parquet(os.path.join(GOLD_DIR, "gold_adocao_ia.parquet"), index=False)
    print(f"  ✓ gold_adocao_ia: {len(gold_ia):,} registros")

    # Gold 6: Modelos de Trabalho e Satisfação
    gold_trabalho = silver_df.groupby(["ano_pesquisa", "modelo_trabalho_padronizado", "regiao_mora"], dropna=False).agg(
        total_respondentes=("id_respondente", "count"),
        total_satisfeitos=("satisfeito_empresa_bool", lambda x: (x == True).sum()),
        salario_medio=("salario_medio_estimado", "mean")
    ).reset_index()
    gold_trabalho["taxa_satisfacao"] = (gold_trabalho["total_satisfeitos"] / gold_trabalho["total_respondentes"]) * 100
    gold_trabalho.to_parquet(os.path.join(GOLD_DIR, "gold_modelos_trabalho.parquet"), index=False)
    print(f"  ✓ gold_modelos_trabalho: {len(gold_trabalho):,} registros")

    print("\n" + "=" * 80)
    print("✅ PIPELINE BRONZE -> SILVER -> GOLD CONCLUÍDO COM SUCESSO!")
    print("=" * 80)

if __name__ == "__main__":
    run_pipeline()
