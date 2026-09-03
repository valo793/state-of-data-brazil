"""Executa as análises do Tech Challenge no Athena e baixa os CSVs.

Credenciais são obtidas pela cadeia padrão do Boto3: variáveis de ambiente,
perfil do AWS CLI ou credenciais da máquina. Nunca recebe chaves por argumento.
"""

import argparse
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

DEFAULT_DATABASE = "db_state_of_data"
DEFAULT_REGION = "us-east-1"
DEFAULT_WORKGROUP = "primary"
DEFAULT_S3_OUTPUT = "s3://tc-state-of-data-leonardo-2026/athena-results/automated/"
DEFAULT_LOCAL_OUTPUT = Path(__file__).resolve().parents[2] / "output" / "resultados_athena"


def get_queries(database):
    return {
        "01_estrutura_mercado.csv": f"""
            SELECT ano_pesquisa,
                   SUM(total_respondentes) AS total_respondentes,
                   ROUND(SUM(media_idade * total_respondentes) /
                         NULLIF(SUM(total_respondentes), 0), 1) AS media_idade_ponderada
            FROM {database}.gold_perfil_mercado
            GROUP BY ano_pesquisa
            ORDER BY ano_pesquisa
        """,
        "02_distribuicao_regional.csv": f"""
            SELECT ano_pesquisa,
                   COALESCE(regiao_mora, 'Não Informado') AS regiao,
                   SUM(total_respondentes) AS total_respondentes,
                   ROUND(SUM(total_respondentes) * 100.0 /
                         SUM(SUM(total_respondentes)) OVER (PARTITION BY ano_pesquisa), 2)
                         AS percentual_regiao
            FROM {database}.gold_perfil_mercado
            GROUP BY ano_pesquisa, regiao_mora
            ORDER BY ano_pesquisa, percentual_regiao DESC
        """,
        "03_remuneracao_senioridade.csv": f"""
            SELECT ano_pesquisa, cargo_atual, senioridade_padronizada,
                   SUM(total_salarios_validos) AS total_salarios_validos,
                   ROUND(SUM(soma_salarios) /
                         NULLIF(SUM(total_salarios_validos), 0), 2) AS salario_medio_ponderado,
                   MIN(salario_min) AS salario_min_faixa,
                   MAX(salario_max) AS salario_max_faixa
            FROM {database}.gold_remuneracao_senioridade
            WHERE cargo_atual IS NOT NULL
            GROUP BY ano_pesquisa, cargo_atual, senioridade_padronizada
            HAVING SUM(total_salarios_validos) >= 30
            ORDER BY ano_pesquisa, salario_medio_ponderado DESC
        """,
        "04_diversidade_genero.csv": f"""
            SELECT ano_pesquisa,
                   COALESCE(genero, 'Não Informado') AS genero,
                   SUM(total) AS total_profissionais,
                   ROUND(SUM(total) * 100.0 /
                         SUM(SUM(total)) OVER (PARTITION BY ano_pesquisa), 2)
                         AS percentual_genero,
                   SUM(total_salarios_validos) AS total_salarios_validos,
                   ROUND(SUM(soma_salarios) /
                         NULLIF(SUM(total_salarios_validos), 0), 2) AS salario_medio_ponderado
            FROM {database}.gold_diversidade
            GROUP BY ano_pesquisa, genero
            ORDER BY ano_pesquisa, total_profissionais DESC
        """,
        "05_tecnologias.csv": f"""
            SELECT ano_pesquisa, categoria, tecnologia, total_usuarios,
                   total_respondentes_validos_categoria,
                   percentual_adocao
            FROM {database}.gold_tecnologias
            ORDER BY ano_pesquisa, categoria, total_usuarios DESC
        """,
        "06a_prioridade_ia.csv": f"""
            SELECT ano_pesquisa,
                   resposta_padronizada AS ia_prioridade_empresa,
                   total_respostas,
                   total_respondentes_validos,
                   percentual
            FROM {database}.gold_adocao_ia
            WHERE tipo_indicador = 'Prioridade empresarial'
            ORDER BY ano_pesquisa, percentual DESC
        """,
        "06b_uso_pessoal_ia.csv": f"""
            SELECT ano_pesquisa,
                   resposta_padronizada AS uso_pessoal_ia,
                   total_respostas,
                   total_respondentes_validos,
                   percentual
            FROM {database}.gold_adocao_ia
            WHERE tipo_indicador = 'Uso pessoal'
            ORDER BY ano_pesquisa, percentual DESC
        """,
        "07_modelos_trabalho.csv": f"""
            SELECT ano_pesquisa, modelo_trabalho_padronizado,
                   SUM(total_respondentes) AS total_profissionais,
                   ROUND(SUM(total_respondentes) * 100.0 /
                         SUM(SUM(total_respondentes)) OVER (PARTITION BY ano_pesquisa), 2)
                         AS percentual_modelo,
                   SUM(total_respostas_validas) AS total_respostas_validas,
                   ROUND(SUM(total_satisfeitos) * 100.0 /
                         NULLIF(SUM(total_respostas_validas), 0), 2)
                         AS taxa_satisfacao_valida_pct,
                   SUM(total_salarios_validos) AS total_salarios_validos,
                   ROUND(SUM(soma_salarios) /
                         NULLIF(SUM(total_salarios_validos), 0), 2)
                         AS salario_medio_ponderado
            FROM {database}.gold_modelos_trabalho
            GROUP BY ano_pesquisa, modelo_trabalho_padronizado
            ORDER BY ano_pesquisa, total_profissionais DESC
        """,
        "08_indicadores_executivos.csv": f"""
            SELECT ano_pesquisa, total_respondentes,
                   pct_feminino AS participacao_feminina_pct,
                   pct_sudeste AS concentracao_sudeste_pct,
                   taxa_satisfacao_geral AS satisfacao_trabalho_pct,
                   pct_remoto AS trabalho_remoto_pct,
                   media_salarial_geral AS media_salarial_estimada_reais
            FROM {database}.gold_indicadores_executivos
            ORDER BY ano_pesquisa
        """,
    }


def start_query(client, sql, database, workgroup, s3_output, reuse_minutes):
    request = {
        "QueryString": sql.strip(),
        "QueryExecutionContext": {"Catalog": "AwsDataCatalog", "Database": database},
        "WorkGroup": workgroup,
        "ResultConfiguration": {"OutputLocation": s3_output},
    }
    if reuse_minutes > 0:
        request["ResultReuseConfiguration"] = {
            "ResultReuseByAgeConfiguration": {
                "Enabled": True,
                "MaxAgeInMinutes": reuse_minutes,
            }
        }
    return client.start_query_execution(**request)["QueryExecutionId"]


def wait_for_query(client, query_id, timeout_seconds):
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        execution = client.get_query_execution(QueryExecutionId=query_id)["QueryExecution"]
        state = execution["Status"]["State"]
        if state == "SUCCEEDED":
            stats = execution.get("Statistics", {})
            return (
                execution["ResultConfiguration"]["OutputLocation"],
                stats.get("DataScannedInBytes", 0),
                stats.get("ResultReuseInformation", {}).get("ReusedPreviousResult", False),
            )
        if state in {"FAILED", "CANCELLED"}:
            reason = execution["Status"].get("StateChangeReason", "Sem detalhes")
            raise RuntimeError(f"Athena retornou {state}: {reason}")
        time.sleep(1.5)
    raise TimeoutError(f"Consulta {query_id} excedeu {timeout_seconds} segundos")


def download_result(s3_client, s3_uri, destination):
    parsed = urlparse(s3_uri)
    if parsed.scheme != "s3" or not parsed.netloc or not parsed.path:
        raise ValueError(f"URI de resultado inválida: {s3_uri}")
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    s3_client.download_file(parsed.netloc, parsed.path.lstrip("/"), str(temporary))
    temporary.replace(destination)


def parse_args():
    parser = argparse.ArgumentParser(description="Exporta análises do Athena para CSV")
    parser.add_argument("--profile", help="Perfil opcional configurado no AWS CLI")
    parser.add_argument("--region", default=DEFAULT_REGION)
    parser.add_argument("--database", default=DEFAULT_DATABASE)
    parser.add_argument("--workgroup", default=DEFAULT_WORKGROUP)
    parser.add_argument("--s3-output", default=DEFAULT_S3_OUTPUT)
    parser.add_argument("--local-output", type=Path, default=DEFAULT_LOCAL_OUTPUT)
    parser.add_argument("--reuse-minutes", type=int, default=0,
                        help="Cache do Athena; 0 desabilita (recomendado durante desenvolvimento)")
    parser.add_argument("--timeout", type=int, default=180)
    return parser.parse_args()


def main():
    args = parse_args()
    if args.reuse_minutes < 0:
        raise ValueError("--reuse-minutes não pode ser negativo")

    try:
        import boto3
        from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError
    except ModuleNotFoundError:
        print("ERRO: dependência ausente. Instale com: py -m pip install boto3")
        return 2

    session_options = {"region_name": args.region}
    if args.profile:
        session_options["profile_name"] = args.profile
    session = boto3.Session(**session_options)

    try:
        identity = session.client("sts").get_caller_identity()
        athena = session.client("athena")
        s3 = session.client("s3")
    except (NoCredentialsError, ClientError, BotoCoreError) as exc:
        print(f"ERRO: credencial AWS ausente, expirada ou sem permissão: {exc}")
        print("Atualize as credenciais do AWS Academy e teste: aws sts get-caller-identity")
        return 2

    args.local_output.mkdir(parents=True, exist_ok=True)
    queries = get_queries(args.database)
    failures = []
    total_scanned = 0

    print(f"Identidade AWS validada: {identity.get('Arn', 'desconhecida')}")
    print(f"Database: {args.database} | Workgroup: {args.workgroup}")
    print(f"Consultas: {len(queries)} | Cache: {args.reuse_minutes} minuto(s)\n")

    for position, (filename, sql) in enumerate(queries.items(), 1):
        print(f"[{position}/{len(queries)}] {filename}")
        try:
            query_id = start_query(
                athena, sql, args.database, args.workgroup,
                args.s3_output, args.reuse_minutes,
            )
            uri, scanned, reused = wait_for_query(athena, query_id, args.timeout)
            download_result(s3, uri, args.local_output / filename)
            total_scanned += scanned
            cache_message = " | reutilizado" if reused else ""
            print(f"  OK | {scanned / 1024:.1f} KB lidos{cache_message}")
        except (ClientError, BotoCoreError, RuntimeError, TimeoutError, ValueError) as exc:
            failures.append((filename, str(exc)))
            print(f"  FALHA | {exc}")

    print(f"\nConcluídas: {len(queries) - len(failures)}/{len(queries)}")
    print(f"Dados lidos: {total_scanned / (1024 * 1024):.2f} MB")
    print(f"Destino: {args.local_output}")
    if failures:
        print("\nConsultas com falha:")
        for filename, reason in failures:
            print(f"- {filename}: {reason}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
