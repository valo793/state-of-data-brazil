"""
Tech Challenge Fase 3 — AWS Glue Job: Bronze → Silver
=====================================================
PySpark Job para transformar dados brutos da Camada Bronze para a Camada Silver no Data Lake S3.

Responsabilidades deste Job:
  1. Ingestão dos CSVs das 3 edições da pesquisa a partir da Camada Bronze (s3://<bucket>/bronze/).
  2. Parsing e harmonização de esquemas heterogêneos (trata tuplas-string de 2023 e notações ponto de 2024+).
  3. Higienização de strings, tratamento de valores nulos e remoção de duplicatas.
  4. Conversão e inferência de tipos (int, float, boolean, string).
  5. Feature Engineering:
     - Extração numérica de salário médio estimado a partir das faixas salariais.
     - Padronização de senioridade (Júnior, Pleno, Sênior, Especialista).
     - Padronização de modelos de trabalho (100% Remoto, Híbrido Flexível, Híbrido Dias Fixos, 100% Presencial).
  6. Escrita em formato columnar Parquet compactado (Snappy), particionado por `ano_pesquisa`.

Execução no AWS Glue:
  - Glue Version: 4.0 (Spark 3.3, Python 3)
  - Worker Type: G.1X (2 workers)
  - Argumentos:
      --JOB_NAME: tc3_bronze_to_silver
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
args = getResolvedOptions(sys.argv, ["JOB_NAME", "BUCKET_NAME", "DATABASE_NAME"])
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

# UDF para cálculo numérico de salário médio estimado
@F.udf(returnType=DoubleType())
def parse_salary_udf(val):
    if val is None or str(val).strip() == "":
        return None
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
    return None

# UDF para padronização de senioridade
@F.udf(returnType=StringType())
def normalize_seniority_udf(val):
    if val is None or str(val).strip() == "":
        return "Não Informado"
    s = str(val).strip()
    if "Júnior" in s or "Junior" in s:
        return "Júnior"
    if "Pleno" in s:
        return "Pleno"
    if "Sênior" in s or "Senior" in s:
        return "Sênior"
    if any(k in s.lower() for k in ["lead", "líder", "lider", "especialista", "staff", "principal"]):
        return "Especialista/Liderança Técnica"
    return s

# UDF para padronização de modelo de trabalho
@F.udf(returnType=StringType())
def normalize_work_model_udf(val):
    if val is None or str(val).strip() == "":
        return "Não Informado"
    s = str(val).strip().lower()
    if "100% remoto" in s or "totalmente remoto" in s:
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


# 1. Carregamento dos dados brutos da Camada Bronze
print("[PASSO 1] Lendo bases de dados da Camada Bronze no S3...")

# 2023-2024
df23_raw = spark.read.option("header", "true").option("inferSchema", "false") \
    .csv(f"{BRONZE_PATH}*2023-2024*.csv")

# Mapear colunas de 2023-2024 (código P)
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

df23 = df23_raw.select(
    F.lit("2023-2024").alias("ano_pesquisa"),
    F.col(c_id_23).alias("id_respondente"),
    F.col(c_idade_23).cast(IntegerType()).alias("idade"),
    F.col(c_faixa_idade_23).alias("faixa_idade"),
    F.col(c_genero_23).alias("genero"),
    F.col(c_raca_23).alias("cor_raca_etnia"),
    F.col(c_pcd_23).alias("pcd"),
    F.col(c_uf_23).alias("uf_mora"),
    F.col(c_regiao_23).alias("regiao_mora"),
    F.col(c_ensino_23).alias("nivel_ensino"),
    F.col(c_area_23).alias("area_formacao"),
    F.col(c_sit_23).alias("situacao_trabalho"),
    F.col(c_setor_23).alias("setor"),
    F.col(c_tam_23).alias("tamanho_empresa"),
    F.col(c_gestor_23).alias("is_gestor"),
    F.col(c_cargest_23).alias("cargo_gestor"),
    F.col(c_cargo_23).alias("cargo_atual"),
    F.col(c_senior_23).alias("senioridade"),
    F.col(c_sal_23).alias("faixa_salarial"),
    F.col(c_exp_dados_23).alias("tempo_experiencia_dados"),
    F.col(c_exp_ti_23).alias("tempo_experiencia_ti"),
    F.col(c_sat_23).alias("satisfeito_empresa"),
    F.col(c_mot_insat_23).alias("motivo_insatisfacao"),
    F.col(c_mod_trab_23).alias("modelo_trabalho"),
    F.col(c_ling_usada_23).alias("linguagem_mais_usada"),
    F.col(c_ling_pref_23).alias("linguagem_preferida"),
    F.col(c_cloud_pref_23).alias("cloud_preferida"),
    F.col(c_bi_pref_23).alias("bi_preferido"),
    F.col(c_ia_prio_23).alias("ia_prioridade_empresa"),
    F.col(c_ia_tipo_23).alias("tipo_uso_ia_empresa"),
    F.col(c_ia_uso_23).alias("uso_pessoal_ia")
)

# 2024-2025
df24_raw = spark.read.option("header", "true").option("inferSchema", "false") \
    .csv(f"{BRONZE_PATH}*2024-2025*.csv")

df24 = df24_raw.select(
    F.lit("2024-2025").alias("ano_pesquisa"),
    F.col("0.a_token").alias("id_respondente"),
    F.col("1.a_idade").cast(IntegerType()).alias("idade"),
    F.col("1.a.1_faixa_idade").alias("faixa_idade"),
    F.col("1.b_genero").alias("genero"),
    F.col("1.c_cor/raca/etnia").alias("cor_raca_etnia"),
    F.col("1.d_pcd").alias("pcd"),
    F.col("1.i.1_uf_onde_mora").alias("uf_mora"),
    F.col("1.i.2_regiao_onde_mora").alias("regiao_mora"),
    F.col("1.l_nivel_de_ensino").alias("nivel_ensino"),
    F.col("1.m_area_de_formacao").alias("area_formacao"),
    F.col("2.a_situacao_atual").alias("situacao_trabalho"),
    F.col("2.b_setor").alias("setor"),
    F.col("2.c_numero_de_funcionarios").alias("tamanho_empresa"),
    F.col("2.d_gestor").alias("is_gestor"),
    F.col("2.e_cargo_como_gestor").alias("cargo_gestor"),
    F.col("2.f_cargo_atual").alias("cargo_atual"),
    F.col("2.g_nivel").alias("senioridade"),
    F.col("2.h_faixa_salarial").alias("faixa_salarial"),
    F.col("2.i_tempo_de_experiencia_em_dados").alias("tempo_experiencia_dados"),
    F.col("2.j_tempo_de_experiencia_em_ti").alias("tempo_experiencia_ti"),
    F.col("2.k_satisfeito_atualmente").alias("satisfeito_empresa"),
    F.col("2.l_motivo_insatisfacao").alias("motivo_insatisfacao"),
    F.col("2.r_modelo_de_trabalho_atual").alias("modelo_trabalho"),
    F.col("4.e_linguagem_mais_utilizada").alias("linguagem_mais_usada"),
    F.col("4.f_linguagem_preferida").alias("linguagem_preferida"),
    F.col("4.i_cloud_preferida").alias("cloud_preferida"),
    F.col("4.k_ferramenta_de_bi_preferida").alias("bi_preferido"),
    F.col("3.e_ai_generativa_e_llm_é_uma_prioridade?").alias("ia_prioridade_empresa"),
    F.col("3.f_tipo_de_uso_de_ai_generativa_e_llm_na_empresa").alias("tipo_uso_ia_empresa"),
    F.col("4.m_usa_chatgpt_ou_copilot_no_trabalho?").alias("uso_pessoal_ia")
)

# 2025-2026
df25_raw = spark.read.option("header", "true").option("inferSchema", "false") \
    .csv(f"{BRONZE_PATH}*2025-2026*.csv")

df25 = df25_raw.select(
    F.lit("2025-2026").alias("ano_pesquisa"),
    F.col("0.a_token").alias("id_respondente"),
    F.col("1.a_idade").cast(IntegerType()).alias("idade"),
    F.col("1.a.1_faixa_idade").alias("faixa_idade"),
    F.col("1.b_genero").alias("genero"),
    F.col("1.c_cor/raca/etnia").alias("cor_raca_etnia"),
    F.col("1.d_pcd").alias("pcd"),
    F.col("1.i.1_uf_onde_mora").alias("uf_mora"),
    F.col("1.i.2_regiao_onde_mora").alias("regiao_mora"),
    F.col("1.l_nivel_de_ensino").alias("nivel_ensino"),
    F.col("1.m_area_de_formacao").alias("area_formacao"),
    F.col("2.a_situacao_atual").alias("situacao_trabalho"),
    F.col("2.b_setor").alias("setor"),
    F.col("2.c_numero_de_funcionarios").alias("tamanho_empresa"),
    F.col("2.d_gestor").alias("is_gestor"),
    F.col("2.e_cargo_como_gestor").alias("cargo_gestor"),
    F.col("2.f_cargo_atual").alias("cargo_atual"),
    F.col("2.g_nivel").alias("senioridade"),
    F.col("2.h_faixa_salarial").alias("faixa_salarial"),
    F.col("2.i_tempo_de_experiencia_em_dados").alias("tempo_experiencia_dados"),
    F.col("2.j_tempo_de_experiencia_em_ti").alias("tempo_experiencia_ti"),
    F.col("2.k_satisfeito_atualmente").alias("satisfeito_empresa"),
    F.col("2.l_motivo_insatisfacao").alias("motivo_insatisfacao"),
    F.col("2.q_modelo_de_trabalho_atual").alias("modelo_trabalho"),
    F.col("4.b_linguagem_mais_utilizada").alias("linguagem_mais_usada"),
    F.col("4.c_linguagem_preferida").alias("linguagem_preferida"),
    F.col("4.f_cloud_preferida").alias("cloud_preferida"),
    F.col("4.h_ferramenta_de_bi_preferida").alias("bi_preferido"),
    F.col("3.e_ai_generativa_e_llm_é_uma_prioridade?").alias("ia_prioridade_empresa"),
    F.col("3.f_tipo_de_uso_de_ai_generativa_e_llm_na_empresa").alias("tipo_uso_ia_empresa"),
    F.col("4.j_usa_chatgpt_ou_copilot_no_trabalho?").alias("uso_pessoal_ia")
)

# União dos 3 DataFrames
df_unified = df23.unionByName(df24).unionByName(df25)

# Limpeza e transformações avançadas
df_silver = df_unified \
    .withColumn("salario_medio_estimado", parse_salary_udf(F.col("faixa_salarial"))) \
    .withColumn("senioridade_padronizada", normalize_seniority_udf(F.col("senioridade"))) \
    .withColumn("modelo_trabalho_padronizado", normalize_work_model_udf(F.col("modelo_trabalho"))) \
    .withColumn(
        "satisfeito_empresa_bool",
        F.when(F.lower(F.col("satisfeito_empresa")).isin("true", "1", "1.0", "sim"), F.lit(True))
         .when(F.lower(F.col("satisfeito_empresa")).isin("false", "0", "0.0", "não", "nao"), F.lit(False))
         .otherwise(None)
    ) \
    .dropDuplicates(["ano_pesquisa", "id_respondente"])

print(f"[PASSO 2] Gravando Camada Silver em {SILVER_PATH} particionado por ano_pesquisa...")

df_silver.write \
    .mode("overwrite") \
    .partitionBy("ano_pesquisa") \
    .parquet(SILVER_PATH)

print("[SUCESSO] Camada Silver criada com sucesso!")
job.commit()
