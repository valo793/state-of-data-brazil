"""
Tech Challenge Fase 3 — Upload dos Dados para S3
=================================================
Faz o upload dos CSVs locais para o bucket S3, organizados por ano.

Uso:
    python upload_to_s3.py --bucket NOME_DO_BUCKET --data-dir ./data/raw

Pré-requisitos:
    - AWS CLI configurado (credenciais do AWS Academy Lab)
    - pip install boto3
"""

import argparse
import os
import sys
import boto3
from pathlib import Path


def upload_files(bucket_name: str, data_dir: str, region: str = "us-east-1"):
    """Upload all CSV files from data_dir to S3 raw/ layer."""
    s3_client = boto3.client("s3", region_name=region)
    data_path = Path(data_dir)

    if not data_path.exists():
        print(f"❌ Diretório não encontrado: {data_path}")
        sys.exit(1)

    csv_files = list(data_path.rglob("*.csv"))
    if not csv_files:
        print(f"⚠️  Nenhum arquivo CSV encontrado em {data_path}")
        sys.exit(1)

    print(f"📁 Encontrados {len(csv_files)} arquivo(s) CSV em {data_path}")
    print(f"📤 Upload para s3://{bucket_name}/raw/\n")

    for csv_file in csv_files:
        # Determine the year from filename or parent directory
        relative_path = csv_file.relative_to(data_path)
        s3_key = f"raw/{relative_path.as_posix()}"

        print(f"  Enviando: {csv_file.name}")
        print(f"    → s3://{bucket_name}/{s3_key}")

        try:
            s3_client.upload_file(
                str(csv_file),
                bucket_name,
                s3_key,
                ExtraArgs={"ContentType": "text/csv"},
            )
            print(f"    ✓ Upload concluído")
        except Exception as e:
            print(f"    ❌ Erro: {e}")

    print(f"\n✅ Upload finalizado! {len(csv_files)} arquivo(s) enviado(s).")
    print(f"\nVerifique com:")
    print(f"  aws s3 ls s3://{bucket_name}/raw/ --recursive")


def main():
    parser = argparse.ArgumentParser(
        description="Upload dos dados do State of Data Brasil para S3"
    )
    parser.add_argument(
        "--bucket",
        required=True,
        help="Nome do bucket S3",
    )
    parser.add_argument(
        "--data-dir",
        default="./data/raw",
        help="Diretório local com os CSVs (default: ./data/raw)",
    )
    parser.add_argument(
        "--region",
        default="us-east-1",
        help="Região AWS (default: us-east-1)",
    )
    args = parser.parse_args()

    upload_files(args.bucket, args.data_dir, args.region)


if __name__ == "__main__":
    main()
