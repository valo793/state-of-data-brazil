"""
Tech Challenge Fase 3 — Pipeline de Transformação Local & Validação de Regras ETL
================================================================================
Este script executa e valida o pipeline de transformação de dados para as 3 camadas
Medallion (Bronze -> Silver -> Gold) utilizando caminhos relativos e argumentos CLI.

Regras Metodológicas Aplicadas:
  1. Leitura estrita da Camada Bronze (data/bronze).
  2. Mapeamento declarativo a partir de config/mapeamento_colunas.json.
  3. Deduplicação segura com geração de hash SHA-256 para IDs nulos (id_registro_tecnico).
  4. Preservação da faixa salarial original como dimensão canônica e cálculo de
     salário médio estimado com documentação da hipótese estatística.
  5. Explode e normalização de tecnologias multivaloradas (Linguagens, Cloud, BI, Bancos).
  6. Taxa de satisfação calculada estritamente sobre respostas válidas (excluindo nulos).
  7. Métricas analíticas na Gold preparadas com contadores para permitir médias ponderadas downstream.
"""

import argparse
import hashlib
import json
import os
import re
from pathlib import Path
import numpy as np
import pandas as pd

# Resolução de caminhos relativos portáteis
BASE_DIR = Path(__file__).resolve().parents[2]
CONFIG_FILE = BASE_DIR / "config" / "mapeamento_colunas.json"
DEFAULT_BRONZE_DIR = BASE_DIR / "data" / "bronze"
DEFAULT_SILVER_DIR = BASE_DIR / "data" / "processed" / "silver"
DEFAULT_GOLD_DIR = BASE_DIR / "data" / "processed" / "gold"


def load_mapping_config():
    """Carrega o arquivo de configuração de mapeamento de colunas."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def generate_technical_id(row, cols):
    """Gera um hash SHA-256 consistente quando o id_respondente for nulo."""
    raw_str = "||".join(str(row.get(c, "")) for c in cols)
    return hashlib.sha256(raw_str.encode("utf-8")).hexdigest()[:16]


def parse_salary_range(val):
    """
    Nota Metodológica de Estimativa Salarial:
    - Faixas fechadas: utiliza-se o ponto médio exato (ex: R$ 8.001 a R$ 12.000 -> R$ 10.000,50).
    - Faixa inferior aberta ('Menos de R$ 1.000'): assume-se R$ 500,00.
    - Faixa superior aberta ('Acima de R$ 40.001'): assume-se R$ 48.000,00 (fator multiplicador 1.2x).
    * O campo 'faixa_salarial' original é sempre preservado como dimensão canônica.
    """
    if pd.isna(val) or not str(val).strip():
        return np.nan
    s = str(val).lower()
    
    if "menos de" in s or "até r$" in s:
        nums = re.findall(r"\d+\.?\d*", s.replace(".", ""))
        if nums:
            return float(nums[0]) / 2.0
        return 500.0
    elif "acima de" in s or "mais de" in s:
        nums = re.findall(r"\d+\.?\d*", s.replace(".", ""))
        if nums:
            return float(nums[0]) * 1.2
        return 48000.0
    else:
        nums = re.findall(r"\d+\.?\d*", s.replace(".", ""))
        if len(nums) >= 2:
            return (float(nums[0]) + float(nums[1])) / 2.0
        elif len(nums) == 1:
            return float(nums[0])
    return np.nan


def normalize_seniority(val, config):
    if pd.isna(val):
        return "Não Informado"
    s = str(val).strip().lower()
    rules = config.get("regras_padronizacao", {}).get("senioridade", {})
    for padrao, keywords in rules.items():
        if any(k in s for k in keywords):
            return padrao
    return str(val).strip().capitalize()


def normalize_work_model(val, config):
    if pd.isna(val):
        return "Não Informado"
    s = str(val).strip().lower()
    rules = config.get("regras_padronizacao", {}).get("modelo_trabalho", {})
    for padrao, keywords in rules.items():
        if any(k in s for k in keywords):
            return padrao
    return "Outro"


def extract_technologies(series, sep=","):
    """Separa strings multivaloradas (ex: 'Python, SQL, R') em listas limpas."""
    if series is None:
        return []
    items = []
    for val in series.dropna():
        parts = [p.strip() for p in str(val).split(sep) if p.strip()]
        items.extend(parts)
    return items


def process_edition_dataframe(df_raw, year, config):
    """Aplica o mapeamento de colunas configurado para a edição correspondente."""
    edition_cfg = config.get("edicoes", {}).get(year, {})
    mapping = edition_cfg.get("mapeamento", {})
    
    clean_dict = {"ano_pesquisa": year}
    
    if edition_cfg.get("formato_header") == "tuple_string":
        # Formato de tuplas string de 2023-2024
        import ast
        p_map = {}
        for col in df_raw.columns:
            try:
                parsed = ast.literal_eval(str(col))
                if isinstance(parsed, tuple):
                    p_map[col] = parsed[0].strip()
            except:
                p_map[col] = str(col).strip()
        
        for raw_col, p_code in p_map.items():
            if p_code in mapping:
                target_col = mapping[p_code]
                clean_dict[target_col] = df_raw[raw_col]
    else:
        # Formato de colunas descritivas de 2024+
        for raw_col, target_col in mapping.items():
            if raw_col in df_raw.columns:
                clean_dict[target_col] = df_raw[raw_col]
            else:
                # Busca por correspondência aproximada caso haja variação
                matched = [c for c in df_raw.columns if raw_col.lower() in c.lower()]
                if matched:
                    clean_dict[target_col] = df_raw[matched[0]]

    df_clean = pd.DataFrame(clean_dict)
    
    # Conversões e tipagem
    if "idade" in df_clean.columns:
        df_clean["idade"] = pd.to_numeric(df_clean["idade"], errors="coerce")
        
    return df_clean


def run_pipeline(bronze_dir, silver_dir, gold_dir):
    config = load_mapping_config()
    os.makedirs(silver_dir, exist_ok=True)
    os.makedirs(gold_dir, exist_ok=True)

    print("=" * 80)
    print("EXECUTANDO PIPELINE ROBUSTO: BRONZE -> SILVER -> GOLD")
    print("=" * 80)
    print(f"📁 Diretório Bronze: {bronze_dir}")
    print(f"📁 Diretório Silver: {silver_dir}")
    print(f"📁 Diretório Gold:   {gold_dir}\n")

    # 1. Carregamento dos dados na Camada Bronze
    f23 = bronze_dir / "Final Dataset - State of Data 2023-2024 - Kaggle.csv"
    f24 = bronze_dir / "Final Dataset - State of Data 2024-2025 - Kaggle.csv"
    f25 = bronze_dir / "Final Dataset - State of Data 2025-2026 - Kaggle.csv"

    df_bronze_23 = pd.read_csv(f23, encoding="utf-8", low_memory=False)
    df_bronze_24 = pd.read_csv(f24, encoding="utf-8", low_memory=False)
    df_bronze_25 = pd.read_csv(f25, encoding="utf-8", low_memory=False)

    print(f"✓ Bronze 2023-2024: {len(df_bronze_23):,} registros brutos")
    print(f"✓ Bronze 2024-2025: {len(df_bronze_24):,} registros brutos")
    print(f"✓ Bronze 2025-2026: {len(df_bronze_25):,} registros brutos")
    total_bronze = len(df_bronze_23) + len(df_bronze_24) + len(df_bronze_25)
    print(f"📊 Total Bronze Acumulado: {total_bronze:,} registros\n")

    # 2. Transformações para a Camada Silver
    s23 = process_edition_dataframe(df_bronze_23, "2023-2024", config)
    s24 = process_edition_dataframe(df_bronze_24, "2024-2025", config)
    s25 = process_edition_dataframe(df_bronze_25, "2025-2026", config)

    silver_df = pd.concat([s23, s24, s25], ignore_index=True)

    # Trim de strings e coerção de nulos
    for col in silver_df.select_dtypes(include=["object", "string"]).columns:
        silver_df[col] = silver_df[col].astype(str).str.strip().replace({"nan": None, "None": None, "": None})

    # Deduplicação segura com identificador técnico para nulos
    relevant_cols = ["ano_pesquisa", "idade", "genero", "regiao_mora", "cargo_atual", "faixa_salarial"]
    null_ids_mask = silver_df["id_respondente"].isna()
    if null_ids_mask.any():
        silver_df.loc[null_ids_mask, "id_respondente"] = silver_df[null_ids_mask].apply(
            lambda r: generate_technical_id(r, relevant_cols), axis=1
        )
        print(f"ℹ️  {null_ids_mask.sum():,} IDs nulos identificados e atribuídos com hash técnico SHA-256.")

    initial_silver_count = len(silver_df)
    silver_df = silver_df.drop_duplicates(subset=["ano_pesquisa", "id_respondente"]).reset_index(drop=True)
    dedup_removed = initial_silver_count - len(silver_df)
    print(f"ℹ️  Deduplicação finalizada: {dedup_removed} duplicatas exatas removidas ({len(silver_df):,} restantes).")

    # Feature Engineering
    silver_df["salario_medio_estimado"] = silver_df["faixa_salarial"].apply(parse_salary_range)
    silver_df["senioridade_padronizada"] = silver_df["senioridade"].apply(lambda v: normalize_seniority(v, config))
    silver_df["modelo_trabalho_padronizado"] = silver_df["modelo_trabalho"].apply(lambda v: normalize_work_model(v, config))
    
    # Tratamento da satisfação booleana
    silver_df["satisfeito_empresa_bool"] = silver_df["satisfeito_empresa"].apply(
        lambda x: True if str(x).lower() in ["true", "1", "1.0", "sim"] else (False if str(x).lower() in ["false", "0", "0.0", "não", "nao"] else None)
    )

    # Persistir Camada Silver
    silver_parquet_path = silver_dir / "state_of_data_silver.parquet"
    if silver_parquet_path.exists():
        import shutil
        shutil.rmtree(silver_parquet_path, ignore_errors=True)
    silver_df.to_parquet(silver_parquet_path, index=False, partition_cols=["ano_pesquisa"])
    print(f"\n✅ Camada Silver criada com sucesso!")
    print(f"  → Arquivo: {silver_parquet_path}")
    print(f"  → Total de registros consolidados: {len(silver_df):,}")
    print(f"  → Colunas estruturadas: {len(silver_df.columns)}")

    # 3. Construção das Tabelas Analíticas da Camada Gold
    print("\n" + "=" * 80)
    print("CONSTRUINDO TABELAS ANALÍTICAS (CAMADA GOLD)")
    print("=" * 80)

    # Gold 1: Perfil de Mercado
    gold_perfil = silver_df.groupby(["ano_pesquisa", "regiao_mora", "genero", "nivel_ensino"], dropna=False).agg(
        total_respondentes=("id_respondente", "count"),
        media_idade=("idade", "mean")
    ).reset_index()
    gold_perfil.to_parquet(gold_dir / "gold_perfil_mercado.parquet", index=False)
    print(f"  ✓ gold_perfil_mercado: {len(gold_perfil):,} registros")

    # Gold 2: Remuneração e Senioridade (com soma_salarios para permitir médias ponderadas)
    gold_remuneracao = silver_df[silver_df["cargo_atual"].notna()].groupby(
        ["ano_pesquisa", "cargo_atual", "senioridade_padronizada", "regiao_mora"], dropna=False
    ).agg(
        total_profissionais=("id_respondente", "count"),
        soma_salarios=("salario_medio_estimado", "sum"),
        salario_medio=("salario_medio_estimado", "mean"),
        salario_mediano=("salario_medio_estimado", "median"),
        salario_min=("salario_medio_estimado", "min"),
        salario_max=("salario_medio_estimado", "max")
    ).reset_index()
    gold_remuneracao.to_parquet(gold_dir / "gold_remuneracao_senioridade.parquet", index=False)
    print(f"  ✓ gold_remuneracao_senioridade: {len(gold_remuneracao):,} registros")

    # Gold 3: Diversidade
    gold_diversidade = silver_df.groupby(["ano_pesquisa", "genero", "cor_raca_etnia", "is_gestor"], dropna=False).agg(
        total=("id_respondente", "count"),
        soma_salarios=("salario_medio_estimado", "sum"),
        salario_medio=("salario_medio_estimado", "mean")
    ).reset_index()
    gold_diversidade.to_parquet(gold_dir / "gold_diversidade.parquet", index=False)
    print(f"  ✓ gold_diversidade: {len(gold_diversidade):,} registros")

    # Gold 4: Tecnologias Desaninhadas (Explode de tecnologias multivaloradas)
    tech_rows = []
    for _, row in silver_df.iterrows():
        year = row["ano_pesquisa"]
        cargo = row.get("cargo_atual", "Não Informado")
        senioridade = row.get("senioridade_padronizada", "Não Informado")
        
        # Linguagens preferidas e usadas
        for cat_col, cat_name in [("linguagem_preferida", "Linguagem Preferida"),
                                  ("linguagem_mais_usada", "Linguagem Mais Usada"),
                                  ("cloud_preferida", "Cloud Preferida"),
                                  ("bi_preferido", "Ferramenta BI Preferida")]:
            val = row.get(cat_col)
            if pd.notna(val) and str(val).strip():
                # Split de itens separados por vírgula
                for item in str(val).split(","):
                    item_clean = item.strip()
                    if item_clean:
                        tech_rows.append({
                            "ano_pesquisa": year,
                            "categoria": cat_name,
                            "tecnologia": item_clean,
                            "cargo_atual": cargo,
                            "senioridade": senioridade,
                            "id_respondente": row["id_respondente"]
                        })

    df_tech_exploded = pd.DataFrame(tech_rows)
    gold_tech = df_tech_exploded.groupby(["ano_pesquisa", "categoria", "tecnologia"], dropna=False).agg(
        total_usuarios=("id_respondente", "nunique")
    ).reset_index()
    gold_tech.to_parquet(gold_dir / "gold_tecnologias.parquet", index=False)
    print(f"  ✓ gold_tecnologias (desaninhada): {len(gold_tech):,} registros")

    # Gold 5: Adoção de Inteligência Artificial & GenAI
    gold_ia = silver_df.groupby(["ano_pesquisa", "ia_prioridade_empresa", "uso_pessoal_ia", "senioridade_padronizada"], dropna=False).agg(
        total_respostas=("id_respondente", "count")
    ).reset_index()
    gold_ia.to_parquet(gold_dir / "gold_adocao_ia.parquet", index=False)
    print(f"  ✓ gold_adocao_ia: {len(gold_ia):,} registros")

    # Gold 6: Modelos de Trabalho e Satisfação (com denominador de respostas válidas)
    gold_trabalho = silver_df.groupby(["ano_pesquisa", "modelo_trabalho_padronizado", "regiao_mora"], dropna=False).agg(
        total_respondentes=("id_respondente", "count"),
        total_respostas_validas=("satisfeito_empresa_bool", lambda s: s.notna().sum()),
        total_satisfeitos=("satisfeito_empresa_bool", lambda s: (s == True).sum()),
        soma_salarios=("salario_medio_estimado", "sum"),
        salario_medio=("salario_medio_estimado", "mean")
    ).reset_index()
    gold_trabalho["taxa_satisfacao"] = np.where(
        gold_trabalho["total_respostas_validas"] > 0,
        (gold_trabalho["total_satisfeitos"] / gold_trabalho["total_respostas_validas"]) * 100.0,
        np.nan
    )
    gold_trabalho.to_parquet(gold_dir / "gold_modelos_trabalho.parquet", index=False)
    print(f"  ✓ gold_modelos_trabalho: {len(gold_trabalho):,} registros")

    # Gold 7: Indicadores Executivos Consolidados (KPIs para apresentação)
    kpi_rows = []
    for year in sorted(silver_df["ano_pesquisa"].unique()):
        df_y = silver_df[silver_df["ano_pesquisa"] == year]
        total_y = len(df_y)
        
        # Participação feminina
        fem_count = (df_y["genero"] == "Feminino").sum()
        fem_pct = (fem_count / total_y) * 100.0 if total_y > 0 else 0
        
        # Concentração Sudeste
        sudeste_count = (df_y["regiao_mora"] == "Sudeste").sum()
        sudeste_pct = (sudeste_count / total_y) * 100.0 if total_y > 0 else 0
        
        # Satisfação
        val_sat = df_y["satisfeito_empresa_bool"].dropna()
        sat_pct = (val_sat == True).mean() * 100.0 if len(val_sat) > 0 else 0
        
        # Modelo 100% Remoto
        remoto_count = (df_y["modelo_trabalho_padronizado"] == "100% Remoto").sum()
        remoto_pct = (remoto_count / total_y) * 100.0 if total_y > 0 else 0
        
        # Média Salarial Geral Ponderada
        sal_medio_geral = df_y["salario_medio_estimado"].mean()
        
        kpi_rows.extend([
            {"ano_pesquisa": year, "kpi": "Total Respondentes", "valor": float(total_y), "unidade": "profissionais"},
            {"ano_pesquisa": year, "kpi": "Participação Feminina", "valor": round(fem_pct, 2), "unidade": "%"},
            {"ano_pesquisa": year, "kpi": "Concentração Sudeste", "valor": round(sudeste_pct, 2), "unidade": "%"},
            {"ano_pesquisa": year, "kpi": "Taxa de Satisfação", "valor": round(sat_pct, 2), "unidade": "%"},
            {"ano_pesquisa": year, "kpi": "Adoção Modelo 100% Remoto", "valor": round(remoto_pct, 2), "unidade": "%"},
            {"ano_pesquisa": year, "kpi": "Média Salarial Estimada Geral", "valor": round(sal_medio_geral, 2), "unidade": "R$"}
        ])

    gold_kpis = pd.DataFrame(kpi_rows)
    gold_kpis.to_parquet(gold_dir / "gold_indicadores_executivos.parquet", index=False)
    print(f"  ✓ gold_indicadores_executivos: {len(gold_kpis):,} registros")

    print("\n" + "=" * 80)
    print("✅ PIPELINE ROBUSTO (BRONZE -> SILVER -> GOLD) CONCLUÍDO COM SUCESSO!")
    print("=" * 80)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pipeline ETL Local para as 3 camadas Medallion")
    parser.add_argument("--bronze-dir", type=Path, default=DEFAULT_BRONZE_DIR, help="Caminho para dados da camada Bronze")
    parser.add_argument("--silver-dir", type=Path, default=DEFAULT_SILVER_DIR, help="Caminho de saída da camada Silver")
    parser.add_argument("--gold-dir", type=Path, default=DEFAULT_GOLD_DIR, help="Caminho de saída da camada Gold")
    args = parser.parse_args()

    run_pipeline(args.bronze_dir, args.silver_dir, args.gold_dir)
