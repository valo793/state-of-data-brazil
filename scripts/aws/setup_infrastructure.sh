#!/bin/bash
# =============================================================================
# Tech Challenge Fase 3 — Setup da Infraestrutura AWS (3 Camadas)
# =============================================================================
# Este script cria a infraestrutura no AWS Academy Lab:
#   - Bucket S3 com as 3 camadas Medallion (bronze, silver, gold)
#   - Glue Database para o catálogo centralizado de metadados
#   - Glue Crawlers para catalogar cada camada
#
# PRÉ-REQUISITOS:
#   - AWS CLI configurado com credenciais do AWS Academy Lab
#   - Permissões para S3, Glue e IAM
#
# USO:
#   chmod +x setup_infrastructure.sh
#   ./setup_infrastructure.sh
# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# CONFIGURAÇÕES — ajuste conforme seu ambiente
# ---------------------------------------------------------------------------
AWS_REGION="us-east-1"
BUCKET_NAME="tech-challenge-3-datalake-$(aws sts get-caller-identity --query Account --output text)"
GLUE_DATABASE="tech_challenge_3_db"
GLUE_ROLE_ARN=""  # Preencha com o ARN da role do Glue no AWS Academy Lab (ex: LabRole)

echo "============================================="
echo " Tech Challenge Fase 3 — Setup AWS (3 Camadas)"
echo "============================================="
echo "Região:   ${AWS_REGION}"
echo "Bucket:   ${BUCKET_NAME}"
echo "Database: ${GLUE_DATABASE}"
echo "============================================="

# ---------------------------------------------------------------------------
# 1. Criar Bucket S3
# ---------------------------------------------------------------------------
echo ""
echo "[1/4] Criando bucket S3..."
if aws s3api head-bucket --bucket "${BUCKET_NAME}" 2>/dev/null; then
    echo "  ✓ Bucket já existe: s3://${BUCKET_NAME}"
else
    aws s3api create-bucket \
        --bucket "${BUCKET_NAME}" \
        --region "${AWS_REGION}" \
    && echo "  ✓ Bucket criado: s3://${BUCKET_NAME}"
fi

# ---------------------------------------------------------------------------
# 2. Criar estrutura das 3 camadas no S3 (Bronze, Silver, Gold)
# ---------------------------------------------------------------------------
echo ""
echo "[2/4] Criando estrutura das 3 camadas Medallion no S3..."
for LAYER in bronze silver gold; do
    aws s3api put-object \
        --bucket "${BUCKET_NAME}" \
        --key "${LAYER}/" \
    && echo "  ✓ Camada criada: s3://${BUCKET_NAME}/${LAYER}/"
done

# Criar subpastas por edição na camada Bronze
for EDITION in "2023_2024" "2024_2025" "2025_2026"; do
    aws s3api put-object \
        --bucket "${BUCKET_NAME}" \
        --key "bronze/state_of_data_${EDITION}/" \
    && echo "  ✓ Subpasta criada: s3://${BUCKET_NAME}/bronze/state_of_data_${EDITION}/"
done

# ---------------------------------------------------------------------------
# 3. Criar Glue Database
# ---------------------------------------------------------------------------
echo ""
echo "[3/4] Criando Glue Database..."
if aws glue get-database --name "${GLUE_DATABASE}" --region "${AWS_REGION}" 2>/dev/null; then
    echo "  ✓ Database já existe: ${GLUE_DATABASE}"
else
    aws glue create-database \
        --region "${AWS_REGION}" \
        --database-input "{
            \"Name\": \"${GLUE_DATABASE}\",
            \"Description\": \"Tech Challenge Fase 3 - State of Data Brasil - Data Lake 3 Camadas\"
        }" \
    && echo "  ✓ Database criada: ${GLUE_DATABASE}"
fi

# ---------------------------------------------------------------------------
# 4. Criar Glue Crawlers (um por camada)
# ---------------------------------------------------------------------------
echo ""
echo "[4/4] Criando Glue Crawlers para as 3 camadas..."

if [ -z "${GLUE_ROLE_ARN}" ]; then
    echo "  ⚠  GLUE_ROLE_ARN não configurado. Pule este passo ou preencha a variável."
    echo "  ⚠  No AWS Academy Lab, use a role padrão: arn:aws:iam::<ACCOUNT_ID>:role/LabRole"
else
    for LAYER in bronze silver gold; do
        CRAWLER_NAME="tc3-crawler-${LAYER}"
        
        if aws glue get-crawler --name "${CRAWLER_NAME}" --region "${AWS_REGION}" 2>/dev/null; then
            echo "  ✓ Crawler já existe: ${CRAWLER_NAME}"
        else
            aws glue create-crawler \
                --region "${AWS_REGION}" \
                --name "${CRAWLER_NAME}" \
                --role "${GLUE_ROLE_ARN}" \
                --database-name "${GLUE_DATABASE}" \
                --table-prefix "${LAYER}_" \
                --targets "{
                    \"S3Targets\": [{
                        \"Path\": \"s3://${BUCKET_NAME}/${LAYER}/\"
                    }]
                }" \
            && echo "  ✓ Crawler criado: ${CRAWLER_NAME}"
        fi
    done
fi

echo ""
echo "============================================="
echo " ✅ Setup concluído!"
echo "============================================="
echo ""
echo "Próximos passos:"
echo "  1. Faça upload dos CSVs brutos para s3://${BUCKET_NAME}/bronze/"
echo "  2. Execute os Glue Crawlers ou Jobs para catalogar e transformar os dados"
echo ""
echo "Comandos úteis:"
echo "  aws s3 ls s3://${BUCKET_NAME}/ --recursive"
echo "  aws glue start-crawler --name tc3-crawler-bronze"
echo "  aws glue get-tables --database-name ${GLUE_DATABASE}"
