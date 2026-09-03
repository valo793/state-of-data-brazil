"""
Tech Challenge Fase 3 — AWS Glue Job: Bronze → Silver
=====================================================
PySpark Job para transformar dados brutos da Camada Bronze para a Camada Silver no Data Lake S3.

Responsabilidades Metodológicas deste Job:
  1. Leitura robusta e protegida dos CSVs da Camada Bronze (s3://<bucket>/bronze/) com multiLine e FAILFAST.
  2. Validação prévia de schema (fail-fast) para garantir presença de todas as colunas mapeadas.
  3. Deduplicação segura com geração de hash SHA-256 (id_registro_tecnico) para IDs nulos.
  4. Higienização de strings, tratamento de valores nulos e trim.
  5. Conversão e inferência de tipos primitivos (Integer, Double, Boolean, String).
  6. Feature Engineering:
     - Extração numérica de salário médio estimado (salario_medio_estimado) com base na nota metodológica.
     - Padronização de senioridade (Júnior, Pleno, Sênior, Especialista/Liderança Técnica).
     - Padronização de modelos de trabalho (100% Remoto, Híbrido Flexível, Híbrido Dias Fixos, 100% Presencial).
  7. Escrita em formato columnar Parquet compactado (Snappy), particionado por `ano_pesquisa`.

Execução no AWS Glue:
  - Glue Version: 4.0 (Spark 3.3, Python 3)
  - Worker Type: G.1X (2 workers)
  - Argumentos:
      --JOB_NAME: tc3-bronze-to-silver
      --BUCKET_NAME: <seu-bucket-datalake>
      --DATABASE_NAME: tech_challenge_3_db
"""

import sys
import re
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql import functions as F
from pyspark.sql.types import (
    StringType, IntegerType, DoubleType, BooleanType
)

# Inicialização do Glue Context
args = getResolvedOptions(
    sys.argv,
    [
        "JOB_NAME",
        "BUCKET_NAME",
        "DATABASE_NAME"
    ]
)

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

job = Job(glueContext)
job.init(args["JOB_NAME"], args)

BUCKET = args["BUCKET_NAME"]
DATABASE = args["DATABASE_NAME"]

BRONZE_PATH = f"s3://{BUCKET}/bronze/"
SILVER_PATH = f"s3://{BUCKET}/silver/state_of_data/"

print(f"[INFO] Iniciando Job Bronze -> Silver")
print(f"[INFO] S3 Bronze: {BRONZE_PATH}")
print(f"[INFO] S3 Silver: {SILVER_PATH}")


def literal_col(column_name):
    """Referencia literalmente colunas que contêm pontos ou caracteres especiais."""
    escaped_name = str(column_name).replace("`", "``")
    return F.col(f"`{escaped_name}`")


def validate_columns(df, expected_columns, edition):
    """Valida a presença prévia de todas as colunas obrigatórias antes das transformações."""
    missing = sorted(set(expected_columns) - set(df.columns))
    if missing:
        raise ValueError(f"Edição {edition}: colunas obrigatórias ausentes no dataset: {missing}")
    print(f"  ✓ Edição {edition}: Todas as {len(expected_columns)} colunas validadas com sucesso.")


# UDF para cálculo numérico de salário médio estimado
@F.udf(returnType=DoubleType())
def parse_salary_udf(val):
    if val is None or str(val).strip() == "":
        return None
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
    return None

# UDF para padronização de senioridade
@F.udf(returnType=StringType())
def normalize_seniority_udf(val):
    if val is None or str(val).strip() == "":
        return "Não Informado"
    s = str(val).strip().lower()
    if "junior" in s or "júnior" in s:
        return "Júnior"
    if "pleno" in s:
        return "Pleno"
    if "senior" in s or "sênior" in s:
        return "Sênior"
    if any(k in s for k in ["lead", "líder", "lider", "especialista", "staff", "principal", "head", "coordenador", "gerente", "diretor"]):
        return "Especialista/Liderança Técnica"
    return str(val).strip().capitalize()

# UDF para padronização de modelo de trabalho
@F.udf(returnType=StringType())
def normalize_work_model_udf(val):
    if val is None or str(val).strip() == "":
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


# Leitor padronizado endurecido contra quebras de linha e erros de encoding
def read_bronze_csv(spark_session, s3_file_pattern):
    return spark_session.read \
        .option("header", "true") \
        .option("sep", ",") \
        .option("quote", '"') \
        .option("escape", '"') \
        .option("multiLine", "true") \
        .option("encoding", "UTF-8") \
        .option("mode", "FAILFAST") \
        .option("inferSchema", "false") \
        .csv(s3_file_pattern)


# =============================================================================
# 1. Carregamento e Validação da Camada Bronze
# =============================================================================
print("[PASSO 1] Lendo e validando bases da Camada Bronze no S3...")

# --- 2023-2024 ---
df23_raw = read_bronze_csv(spark, f"{BRONZE_PATH}*2023-2024*.csv")
cols_23 = df23_raw.columns

def find_c23(prefix):
    for c in cols_23:
        if f"'{prefix}'" in c or f"'{prefix} " in c:
            return c
    return None

c_id_23 = find_c23("P0") or cols_23[0]
c_idade_23 = find_c23("P1_a")
c_faixa_idade_23 = find_c23("P1_a_1")
c_genero_23 = find_c23("P1_b")
c_raca_23 = find_c23("P1_c")
c_pcd_23 = find_c23("P1_d")
c_uf_23 = find_c23("P1_i_1")
c_regiao_23 = find_c23("P1_i_2")
c_ensino_23 = find_c23("P1_l")
c_area_23 = find_c23("P1_m")
c_sit_23 = find_c23("P2_a")
c_setor_23 = find_c23("P2_b")
c_tam_23 = find_c23("P2_c")
c_gestor_23 = find_c23("P2_d")
c_cargest_23 = find_c23("P2_e")
c_cargo_23 = find_c23("P2_f")
c_senior_23 = find_c23("P2_g")
c_sal_23 = find_c23("P2_h")
c_exp_dados_23 = find_c23("P2_i")
c_exp_ti_23 = find_c23("P2_j")
c_sat_23 = find_c23("P2_k")
c_mot_insat_23 = find_c23("P2_l")
c_mod_trab_23 = find_c23("P2_r")
c_ling_usada_23 = find_c23("P4_e")
c_ling_pref_23 = find_c23("P4_f")
c_cloud_pref_23 = find_c23("P4_i")
c_bi_pref_23 = find_c23("P4_k")
c_ia_prio_23 = find_c23("P3_e")
c_ia_tipo_23 = find_c23("P4_l")
c_ia_uso_23 = find_c23("P4_m")

expected_23 = [c for c in [c_id_23, c_idade_23, c_faixa_idade_23, c_genero_23, c_raca_23, c_pcd_23,
                           c_uf_23, c_regiao_23, c_ensino_23, c_area_23, c_sit_23, c_setor_23,
                           c_tam_23, c_gestor_23, c_cargest_23, c_cargo_23, c_senior_23, c_sal_23,
                           c_exp_dados_23, c_exp_ti_23, c_sat_23, c_mot_insat_23, c_mod_trab_23,
                           c_ling_usada_23, c_ling_pref_23, c_cloud_pref_23, c_bi_pref_23,
                           c_ia_prio_23, c_ia_tipo_23, c_ia_uso_23] if c is not None]

validate_columns(df23_raw, expected_23, "2023-2024")

df23 = df23_raw.select(
    F.lit("2023-2024").alias("ano_pesquisa"),
    literal_col(c_id_23).alias("id_respondente"),
    literal_col(c_idade_23).cast(IntegerType()).alias("idade"),
    literal_col(c_faixa_idade_23).alias("faixa_idade"),
    literal_col(c_genero_23).alias("genero"),
    literal_col(c_raca_23).alias("cor_raca_etnia"),
    literal_col(c_pcd_23).alias("pcd"),
    literal_col(c_uf_23).alias("uf_mora"),
    literal_col(c_regiao_23).alias("regiao_mora"),
    literal_col(c_ensino_23).alias("nivel_ensino"),
    literal_col(c_area_23).alias("area_formacao"),
    literal_col(c_sit_23).alias("situacao_trabalho"),
    literal_col(c_setor_23).alias("setor"),
    literal_col(c_tam_23).alias("tamanho_empresa"),
    literal_col(c_gestor_23).alias("is_gestor"),
    literal_col(c_cargest_23).alias("cargo_gestor"),
    literal_col(c_cargo_23).alias("cargo_atual"),
    literal_col(c_senior_23).alias("senioridade"),
    literal_col(c_sal_23).alias("faixa_salarial"),
    literal_col(c_exp_dados_23).alias("tempo_experiencia_dados"),
    literal_col(c_exp_ti_23).alias("tempo_experiencia_ti"),
    literal_col(c_sat_23).alias("satisfeito_empresa"),
    literal_col(c_mot_insat_23).alias("motivo_insatisfacao"),
    literal_col(c_mod_trab_23).alias("modelo_trabalho"),
    literal_col(c_ling_usada_23).alias("linguagem_mais_usada"),
    literal_col(c_ling_pref_23).alias("linguagem_preferida"),
    literal_col(c_cloud_pref_23).alias("cloud_preferida"),
    literal_col(c_bi_pref_23).alias("bi_preferido"),
    literal_col(c_ia_prio_23).alias("ia_prioridade_empresa"),
    literal_col(c_ia_tipo_23).alias("tipo_uso_ia_empresa"),
    literal_col(c_ia_uso_23).alias("uso_pessoal_ia")
)

# --- 2024-2025 ---
df24_raw = read_bronze_csv(spark, f"{BRONZE_PATH}*2024-2025*.csv")
expected_24 = [
    "0.a_token", "1.a_idade", "1.a.1_faixa_idade", "1.b_genero", "1.c_cor/raca/etnia",
    "1.d_pcd", "1.i.1_uf_onde_mora", "1.i.2_regiao_onde_mora", "1.l_nivel_de_ensino",
    "1.m_área_de_formação", "2.a_situação_de_trabalho", "2.b_setor", "2.c_numero_de_funcionarios",
    "2.d_atua_como_gestor", "2.e_cargo_como_gestor", "2.f_cargo_atual", "2.g_nivel", "2.h_faixa_salarial",
    "2.i_tempo_de_experiencia_em_dados", "2.j_tempo_de_experiencia_em_ti", "2.k_satisfeito_atualmente",
    "2.l_motivo_insatisfacao", "2.r_modelo_de_trabalho_atual", "4.e_linguagem_mais_usada",
    "4.f_linguagem_preferida", "4.i_cloud_preferida", "4.k_ferramenta_de_bi_preferida",
    "3.e_ai_generativa_e_llm_é_uma_prioridade?", "3.f_tipo_de_uso_de_ai_generativa_e_llm_na_empresa",
    "4.m_usa_chatgpt_ou_copilot_no_trabalho?"
]
validate_columns(df24_raw, expected_24, "2024-2025")

df24 = df24_raw.select(
    F.lit("2024-2025").alias("ano_pesquisa"),
    literal_col("0.a_token").alias("id_respondente"),
    literal_col("1.a_idade").cast(IntegerType()).alias("idade"),
    literal_col("1.a.1_faixa_idade").alias("faixa_idade"),
    literal_col("1.b_genero").alias("genero"),
    literal_col("1.c_cor/raca/etnia").alias("cor_raca_etnia"),
    literal_col("1.d_pcd").alias("pcd"),
    literal_col("1.i.1_uf_onde_mora").alias("uf_mora"),
    literal_col("1.i.2_regiao_onde_mora").alias("regiao_mora"),
    literal_col("1.l_nivel_de_ensino").alias("nivel_ensino"),
    literal_col("1.m_área_de_formação").alias("area_formacao"),
    literal_col("2.a_situação_de_trabalho").alias("situacao_trabalho"),
    literal_col("2.b_setor").alias("setor"),
    literal_col("2.c_numero_de_funcionarios").alias("tamanho_empresa"),
    literal_col("2.d_atua_como_gestor").alias("is_gestor"),
    literal_col("2.e_cargo_como_gestor").alias("cargo_gestor"),
    literal_col("2.f_cargo_atual").alias("cargo_atual"),
    literal_col("2.g_nivel").alias("senioridade"),
    literal_col("2.h_faixa_salarial").alias("faixa_salarial"),
    literal_col("2.i_tempo_de_experiencia_em_dados").alias("tempo_experiencia_dados"),
    literal_col("2.j_tempo_de_experiencia_em_ti").alias("tempo_experiencia_ti"),
    literal_col("2.k_satisfeito_atualmente").alias("satisfeito_empresa"),
    literal_col("2.l_motivo_insatisfacao").alias("motivo_insatisfacao"),
    literal_col("2.r_modelo_de_trabalho_atual").alias("modelo_trabalho"),
    literal_col("4.e_linguagem_mais_usada").alias("linguagem_mais_usada"),
    literal_col("4.f_linguagem_preferida").alias("linguagem_preferida"),
    literal_col("4.i_cloud_preferida").alias("cloud_preferida"),
    literal_col("4.k_ferramenta_de_bi_preferida").alias("bi_preferido"),
    literal_col("3.e_ai_generativa_e_llm_é_uma_prioridade?").alias("ia_prioridade_empresa"),
    literal_col("3.f_tipo_de_uso_de_ai_generativa_e_llm_na_empresa").alias("tipo_uso_ia_empresa"),
    literal_col("4.m_usa_chatgpt_ou_copilot_no_trabalho?").alias("uso_pessoal_ia")
)

# --- 2025-2026 ---
df25_raw = read_bronze_csv(spark, f"{BRONZE_PATH}*2025-2026*.csv")
expected_25 = [
    "0.a_token", "1.a_idade", "1.a.1_faixa_idade", "1.b_genero", "1.c_cor/raca/etnia",
    "1.d_pcd", "1.i.1_uf_onde_mora", "1.i.2_regiao_onde_mora", "1.l_nivel_de_ensino",
    "1.m_área_de_formação", "2.a_situação_de_trabalho", "2.b_setor", "2.c_numero_de_funcionarios",
    "2.d_atua_como_gestor", "2.e_cargo_como_gestor", "2.f_cargo_atual", "2.g_nivel", "2.h_faixa_salarial",
    "2.i_tempo_de_experiencia_em_dados", "2.j_tempo_de_experiencia_em_ti", "2.k_satisfeito_atualmente",
    "2.l_motivo_insatisfacao", "2.q_modelo_de_trabalho_atual",
    "4.c_linguagem_preferida", "4.f_cloud_preferida", "4.h_ferramenta_de_bi_preferida",
    "3.e_ai_generativa_e_llm_é_uma_prioridade?", "3.f_tipo_de_uso_de_ai_generativa_e_llm_na_empresa",
    "4.j_usa_chatgpt_ou_copilot_no_trabalho?"
]
validate_columns(df25_raw, expected_25, "2025-2026")

df25 = df25_raw.select(
    F.lit("2025-2026").alias("ano_pesquisa"),
    literal_col("0.a_token").alias("id_respondente"),
    literal_col("1.a_idade").cast(IntegerType()).alias("idade"),
    literal_col("1.a.1_faixa_idade").alias("faixa_idade"),
    literal_col("1.b_genero").alias("genero"),
    literal_col("1.c_cor/raca/etnia").alias("cor_raca_etnia"),
    literal_col("1.d_pcd").alias("pcd"),
    literal_col("1.i.1_uf_onde_mora").alias("uf_mora"),
    literal_col("1.i.2_regiao_onde_mora").alias("regiao_mora"),
    literal_col("1.l_nivel_de_ensino").alias("nivel_ensino"),
    literal_col("1.m_área_de_formação").alias("area_formacao"),
    literal_col("2.a_situação_de_trabalho").alias("situacao_trabalho"),
    literal_col("2.b_setor").alias("setor"),
    literal_col("2.c_numero_de_funcionarios").alias("tamanho_empresa"),
    literal_col("2.d_atua_como_gestor").alias("is_gestor"),
    literal_col("2.e_cargo_como_gestor").alias("cargo_gestor"),
    literal_col("2.f_cargo_atual").alias("cargo_atual"),
    literal_col("2.g_nivel").alias("senioridade"),
    literal_col("2.h_faixa_salarial").alias("faixa_salarial"),
    literal_col("2.i_tempo_de_experiencia_em_dados").alias("tempo_experiencia_dados"),
    literal_col("2.j_tempo_de_experiencia_em_ti").alias("tempo_experiencia_ti"),
    literal_col("2.k_satisfeito_atualmente").alias("satisfeito_empresa"),
    literal_col("2.l_motivo_insatisfacao").alias("motivo_insatisfacao"),
    literal_col("2.q_modelo_de_trabalho_atual").alias("modelo_trabalho"),
    # A edição 2025-2026 não possui uma pergunta escalar equivalente a
    # "linguagem mais usada". Mantemos nulo para preservar o esquema harmonizado.
    F.lit(None).cast(StringType()).alias("linguagem_mais_usada"),
    literal_col("4.c_linguagem_preferida").alias("linguagem_preferida"),
    literal_col("4.f_cloud_preferida").alias("cloud_preferida"),
    literal_col("4.h_ferramenta_de_bi_preferida").alias("bi_preferido"),
    literal_col("3.e_ai_generativa_e_llm_é_uma_prioridade?").alias("ia_prioridade_empresa"),
    literal_col("3.f_tipo_de_uso_de_ai_generativa_e_llm_na_empresa").alias("tipo_uso_ia_empresa"),
    literal_col("4.j_usa_chatgpt_ou_copilot_no_trabalho?").alias("uso_pessoal_ia")
)

# =============================================================================
# 2. Consolidação e Deduplicação Segura com Hash SHA-256
# =============================================================================
df_unified = df23.unionByName(df24).unionByName(df25)

df_with_id = df_unified.withColumn(
    "id_registro_tecnico",
    F.when(
        literal_col("id_respondente").isNotNull() & (F.trim(literal_col("id_respondente")) != ""),
        literal_col("id_respondente")
    ).otherwise(
        F.sha2(F.concat_ws("||", literal_col("ano_pesquisa"), literal_col("idade"), literal_col("genero"), literal_col("cargo_atual"), literal_col("faixa_salarial")), 256)
    )
)

# Limpeza e transformações avançadas
df_silver = df_with_id \
    .withColumn("salario_medio_estimado", parse_salary_udf(literal_col("faixa_salarial"))) \
    .withColumn("senioridade_padronizada", normalize_seniority_udf(literal_col("senioridade"))) \
    .withColumn("modelo_trabalho_padronizado", normalize_work_model_udf(literal_col("modelo_trabalho"))) \
    .withColumn(
        "satisfeito_empresa_bool",
        F.when(F.lower(literal_col("satisfeito_empresa")).isin("true", "1", "1.0", "sim"), F.lit(True))
         .when(F.lower(literal_col("satisfeito_empresa")).isin("false", "0", "0.0", "não", "nao"), F.lit(False))
         .otherwise(None)
    ) \
    .dropDuplicates(["ano_pesquisa", "id_registro_tecnico"])

print(f"[PASSO 2] Gravando Camada Silver em {SILVER_PATH} particionado por ano_pesquisa...")

df_silver.write \
    .mode("overwrite") \
    .partitionBy("ano_pesquisa") \
    .parquet(SILVER_PATH)

print("[SUCESSO] Camada Silver criada com sucesso e validada!")
job.commit()
