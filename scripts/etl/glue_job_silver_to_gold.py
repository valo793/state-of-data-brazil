"""
Tech Challenge Fase 3 — AWS Glue Job: Silver → Gold
===================================================
PySpark Job para transformar dados limpos da Camada Silver em Data Marts agregados na Camada Gold.

Tabelas Analíticas Criadas na Camada Gold:
  1. `gold_perfil_mercado`: Distribuição geográfica, demográfica e educacional dos profissionais.
  2. `gold_remuneracao_senioridade`: Estatísticas salariais (soma, médias, medianas, min, max) por cargo, senioridade e região.
  3. `gold_diversidade`: Métricas de gênero, raça/etnia e representatividade em liderança.
  4. `gold_tecnologias`: Métricas desaninhadas de linguagens, ferramentas de BI e clouds com contagem de usuários únicos.
  5. `gold_adocao_ia`: Priorização empresarial de IA e adesão individual a ferramentas como ChatGPT/Copilots.
  6. `gold_modelos_trabalho`: Distribuição dos modelos de trabalho, taxa de satisfação sobre respostas válidas e salários.
  7. `gold_indicadores_executivos`: Resumo consolidado de KPIs estratégicos para apresentação executiva.

Execução no AWS Glue:
  - Glue Version: 4.0 (Spark 3.3, Python 3)
  - Worker Type: G.1X (2 workers)
  - Argumentos:
      --JOB_NAME: tc3_silver_to_gold
      --BUCKET_NAME: <seu-bucket-datalake>
      --DATABASE_NAME: tech_challenge_3_db
"""

import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql import functions as F

args = getResolvedOptions(sys.argv, ["JOB_NAME", "BUCKET_NAME", "DATABASE_NAME"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

BUCKET = args["BUCKET_NAME"]
DATABASE = args["DATABASE_NAME"]

SILVER_PATH = f"s3://{BUCKET}/silver/state_of_data/"
GOLD_PATH = f"s3://{BUCKET}/gold/"

print(f"[INFO] Lendo dados Silver de: {SILVER_PATH}")
df_silver = spark.read.parquet(SILVER_PATH)

# =========================================================================
# 1. Gold: Perfil de Mercado
# =========================================================================
print("[STEP 1] Gerando gold_perfil_mercado...")
gold_perfil = df_silver.groupBy("ano_pesquisa", "regiao_mora", "genero", "nivel_ensino") \
    .agg(
        F.count("id_respondente").alias("total_respondentes"),
        F.avg("idade").alias("media_idade")
    )
gold_perfil.write.mode("overwrite").parquet(f"{GOLD_PATH}gold_perfil_mercado/")

# =========================================================================
# 2. Gold: Remuneração e Senioridade (com soma_salarios para médias ponderadas)
# =========================================================================
print("[STEP 2] Gerando gold_remuneracao_senioridade...")
gold_remuneracao = df_silver.filter(F.col("cargo_atual").isNotNull()) \
    .groupBy("ano_pesquisa", "cargo_atual", "senioridade_padronizada", "regiao_mora") \
    .agg(
        F.count("id_respondente").alias("total_profissionais"),
        F.sum("salario_medio_estimado").alias("soma_salarios"),
        F.avg("salario_medio_estimado").alias("salario_medio"),
        F.median("salario_medio_estimado").alias("salario_mediano"),
        F.min("salario_medio_estimado").alias("salario_min"),
        F.max("salario_medio_estimado").alias("salario_max")
    )
gold_remuneracao.write.mode("overwrite").parquet(f"{GOLD_PATH}gold_remuneracao_senioridade/")

# =========================================================================
# 3. Gold: Diversidade
# =========================================================================
print("[STEP 3] Gerando gold_diversidade...")
gold_diversidade = df_silver.groupBy("ano_pesquisa", "genero", "cor_raca_etnia", "is_gestor") \
    .agg(
        F.count("id_respondente").alias("total"),
        F.sum("salario_medio_estimado").alias("soma_salarios"),
        F.avg("salario_medio_estimado").alias("salario_medio")
    )
gold_diversidade.write.mode("overwrite").parquet(f"{GOLD_PATH}gold_diversidade/")

# =========================================================================
# 4. Gold: Tecnologias Desaninhadas (Explode de tecnologias multivaloradas)
# =========================================================================
print("[STEP 4] Gerando gold_tecnologias...")
# Desaninha linguagem preferida
df_ling_pref = df_silver.filter(F.col("linguagem_preferida").isNotNull()) \
    .withColumn("tecnologia", F.explode(F.split(F.col("linguagem_preferida"), ","))) \
    .withColumn("tecnologia", F.trim(F.col("tecnologia"))) \
    .filter(F.col("tecnologia") != "") \
    .withColumn("categoria", F.lit("Linguagem Preferida"))

# Desaninha cloud preferida
df_cloud_pref = df_silver.filter(F.col("cloud_preferida").isNotNull()) \
    .withColumn("tecnologia", F.explode(F.split(F.col("cloud_preferida"), ","))) \
    .withColumn("tecnologia", F.trim(F.col("tecnologia"))) \
    .filter(F.col("tecnologia") != "") \
    .withColumn("categoria", F.lit("Cloud Preferida"))

# Desaninha BI preferido
df_bi_pref = df_silver.filter(F.col("bi_preferido").isNotNull()) \
    .withColumn("tecnologia", F.explode(F.split(F.col("bi_preferido"), ","))) \
    .withColumn("tecnologia", F.trim(F.col("tecnologia"))) \
    .filter(F.col("tecnologia") != "") \
    .withColumn("categoria", F.lit("Ferramenta BI Preferida"))

df_tech_all = df_ling_pref.unionByName(df_cloud_pref).unionByName(df_bi_pref)

gold_tech = df_tech_all.groupBy("ano_pesquisa", "categoria", "tecnologia") \
    .agg(
        F.countDistinct("id_respondente").alias("total_usuarios")
    )
gold_tech.write.mode("overwrite").parquet(f"{GOLD_PATH}gold_tecnologias/")

# =========================================================================
# 5. Gold: Adoção de Inteligência Artificial e GenAI
# =========================================================================
print("[STEP 5] Gerando gold_adocao_ia...")
gold_ia = df_silver.groupBy("ano_pesquisa", "ia_prioridade_empresa", "uso_pessoal_ia", "senioridade_padronizada") \
    .agg(
        F.count("id_respondente").alias("total_respostas")
    )
gold_ia.write.mode("overwrite").parquet(f"{GOLD_PATH}gold_adocao_ia/")

# =========================================================================
# 6. Gold: Modelos de Trabalho e Satisfação (com denominador válido)
# =========================================================================
print("[STEP 6] Gerando gold_modelos_trabalho...")
gold_trabalho = df_silver.groupBy("ano_pesquisa", "modelo_trabalho_padronizado", "regiao_mora") \
    .agg(
        F.count("id_respondente").alias("total_respondentes"),
        F.sum(F.when(F.col("satisfeito_empresa_bool").isNotNull(), 1).otherwise(0)).alias("total_respostas_validas"),
        F.sum(F.when(F.col("satisfeito_empresa_bool") == True, 1).otherwise(0)).alias("total_satisfeitos"),
        F.sum("salario_medio_estimado").alias("soma_salarios"),
        F.avg("salario_medio_estimado").alias("salario_medio")
    ) \
    .withColumn(
        "taxa_satisfacao",
        F.when(
            F.col("total_respostas_validas") > 0,
            (F.col("total_satisfeitos") / F.col("total_respostas_validas")) * 100.0
        ).otherwise(None)
    )
gold_trabalho.write.mode("overwrite").parquet(f"{GOLD_PATH}gold_modelos_trabalho/")

# =========================================================================
# 7. Gold: Indicadores Executivos Consolidados
# =========================================================================
print("[STEP 7] Gerando gold_indicadores_executivos...")
gold_kpis = df_silver.groupBy("ano_pesquisa") \
    .agg(
        F.count("id_respondente").alias("total_respondentes"),
        F.round(F.avg(F.when(F.col("genero") == "Feminino", 1).otherwise(0)) * 100.0, 2).alias("pct_feminino"),
        F.round(F.avg(F.when(F.col("regiao_mora") == "Sudeste", 1).otherwise(0)) * 100.0, 2).alias("pct_sudeste"),
        F.round(
            F.sum(F.when(F.col("satisfeito_empresa_bool") == True, 1).otherwise(0)) * 100.0 /
            F.nullif(F.sum(F.when(F.col("satisfeito_empresa_bool").isNotNull(), 1).otherwise(0)), 0),
            2
        ).alias("taxa_satisfacao_geral"),
        F.round(F.avg(F.when(F.col("modelo_trabalho_padronizado") == "100% Remoto", 1).otherwise(0)) * 100.0, 2).alias("pct_remoto"),
        F.round(F.avg("salario_medio_estimado"), 2).alias("media_salarial_geral")
    )
gold_kpis.write.mode("overwrite").parquet(f"{GOLD_PATH}gold_indicadores_executivos/")

print("\n[SUCESSO] Todas as tabelas da Camada Gold foram geradas e gravadas no S3!")
job.commit()
