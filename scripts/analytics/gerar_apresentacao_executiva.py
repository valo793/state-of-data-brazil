"""
Tech Challenge Fase 3 — Gerador da Apresentação Executiva em HTML e PDF
=======================================================================
Gera os entregáveis finais do Tech Challenge Fase 3:
  1. `output/apresentacao/apresentacao_state_of_data.html` (100% autônomo, offline, responsivo 16:9)
  2. `output/apresentacao/apresentacao_state_of_data.pdf` (Gerado via MS Edge Headless em 16:9 paisagem)
  3. `output/apresentacao/LEIA-ME.md` (Instruções de navegação, apresentação e impressão)
"""

import base64
import json
import os
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
OUTPUT_APRESENTACAO = BASE_DIR / "output" / "apresentacao"
OUTPUT_APRESENTACAO.mkdir(parents=True, exist_ok=True)
GRAFICOS_DIR = BASE_DIR / "output" / "graficos_executivos"

HTML_PATH = OUTPUT_APRESENTACAO / "apresentacao_state_of_data.html"
PDF_PATH = OUTPUT_APRESENTACAO / "apresentacao_state_of_data.pdf"
README_PATH = OUTPUT_APRESENTACAO / "LEIA-ME.md"


def get_image_base64(image_name):
    """Lê um PNG de output/graficos_executivos e retorna sua string base64 URI."""
    img_path = GRAFICOS_DIR / image_name
    if not img_path.exists():
        print(f"⚠️  Imagem não encontrada: {img_path}")
        return ""
    with open(img_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"


def build_svg_aws_architecture():
    """Gera o diagrama vetorial SVG da Arquitetura AWS para o Slide 4."""
    return """
    <svg viewBox="0 0 1100 480" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg" style="font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;">
      <defs>
        <filter id="shadow" x="-5%" y="-5%" width="110%" height="115%" filterUnits="userSpaceOnUse">
          <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#0B1E36" flood-opacity="0.12" />
        </filter>
        <marker id="arrow-blue" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 1 L 10 5 L 0 9 z" fill="#0288D1" />
        </marker>
        <marker id="arrow-green" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 1 L 10 5 L 0 9 z" fill="#107C41" />
        </marker>
        <marker id="arrow-orange" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 1 L 10 5 L 0 9 z" fill="#FF9900" />
        </marker>
        <marker id="arrow-purple" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 1 L 10 5 L 0 9 z" fill="#5E35B1" />
        </marker>
      </defs>

      <!-- FAIXA SUPERIOR: JOBS PYSPARK (FORA DO S3) -->
      <!-- Job 1 -->
      <rect x="270" y="20" width="220" height="60" rx="8" fill="#E1F5FE" stroke="#0288D1" stroke-width="2" filter="url(#shadow)" />
      <text x="380" y="42" font-size="12" font-weight="bold" fill="#01579B" text-anchor="middle">AWS Glue Job 1 (PySpark)</text>
      <text x="380" y="58" font-size="10" fill="#555" text-anchor="middle">tc3-bronze-to-silver (Harmonização &amp; SHA-256)</text>

      <!-- Job 2 -->
      <rect x="520" y="20" width="220" height="60" rx="8" fill="#E1F5FE" stroke="#0288D1" stroke-width="2" filter="url(#shadow)" />
      <text x="630" y="42" font-size="12" font-weight="bold" fill="#01579B" text-anchor="middle">AWS Glue Job 2 (PySpark)</text>
      <text x="630" y="58" font-size="10" fill="#555" text-anchor="middle">tc3-silver-to-gold (Data Marts &amp; Médias Ponderadas)</text>

      <!-- ORIGEM: KAGGLE -->
      <rect x="20" y="140" width="160" height="110" rx="10" fill="#F3E5F5" stroke="#7B1FA2" stroke-width="2" filter="url(#shadow)" />
      <text x="100" y="168" font-size="13" font-weight="bold" fill="#4A148C" text-anchor="middle">Fonte de Dados</text>
      <text x="100" y="188" font-size="11" font-weight="bold" fill="#333" text-anchor="middle">Kaggle State of Data</text>
      <text x="100" y="206" font-size="9.5" fill="#666" text-anchor="middle">2023–2024 | 2024–2025</text>
      <text x="100" y="222" font-size="9.5" fill="#666" text-anchor="middle">2025–2026 (CSVs Brutos)</text>
      <text x="100" y="238" font-size="9" font-weight="bold" fill="#7B1FA2" text-anchor="middle">n = 14.002 registros</text>

      <!-- Seta Origem -> S3 Bronze -->
      <path d="M 180 195 L 220 195" fill="none" stroke="#0288D1" stroke-width="2.5" marker-end="url(#arrow-blue)" />

      <!-- CONTAINER S3 DATA LAKE (3 CAMADAS DENTRO DO S3) -->
      <rect x="225" y="105" width="555" height="180" rx="12" fill="#F8FAFC" stroke="#232F3E" stroke-width="2" stroke-dasharray="8 6" filter="url(#shadow)" />
      <text x="245" y="128" font-size="13" font-weight="bold" fill="#232F3E">Amazon S3 Data Lake (3 Camadas Medallion)</text>

      <!-- S3 Bronze -->
      <rect x="245" y="145" width="155" height="120" rx="8" fill="#EFEBE9" stroke="#8D6E63" stroke-width="2" />
      <path d="M 245 160 C 245 152, 400 152, 400 160 C 400 168, 245 168, 245 160 Z" fill="#D7CCC8" stroke="#8D6E63" stroke-width="1.5" />
      <text x="322" y="182" font-size="12" font-weight="bold" fill="#4E342E" text-anchor="middle">Camada Bronze</text>
      <text x="322" y="200" font-size="10" font-weight="bold" fill="#333" text-anchor="middle">CSV Original</text>
      <text x="322" y="216" font-size="9" fill="#555" text-anchor="middle">s3://bucket/bronze/</text>
      <text x="322" y="232" font-size="9" fill="#666" text-anchor="middle">Dados Brutos Imutáveis</text>
      <text x="322" y="248" font-size="8.5" fill="#888" text-anchor="middle">14.005 linhas brutas</text>

      <!-- S3 Silver -->
      <rect x="425" y="145" width="155" height="120" rx="8" fill="#ECEFF1" stroke="#78909C" stroke-width="2" />
      <path d="M 425 160 C 425 152, 580 152, 580 160 C 580 168, 425 168, 425 160 Z" fill="#CFD8DC" stroke="#78909C" stroke-width="1.5" />
      <text x="502" y="182" font-size="12" font-weight="bold" fill="#263238" text-anchor="middle">Camada Silver</text>
      <text x="502" y="200" font-size="10" font-weight="bold" fill="#333" text-anchor="middle">Parquet + Snappy</text>
      <text x="502" y="216" font-size="9" fill="#555" text-anchor="middle">s3://bucket/silver/</text>
      <text x="502" y="232" font-size="9" fill="#666" text-anchor="middle">Partição: ano_pesquisa</text>
      <text x="502" y="248" font-size="8.5" fill="#888" text-anchor="middle">14.002 linhas limpas</text>

      <!-- S3 Gold -->
      <rect x="605" y="145" width="155" height="120" rx="8" fill="#FFFDE7" stroke="#FBC02D" stroke-width="2" />
      <path d="M 605 160 C 605 152, 760 152, 760 160 C 760 168, 605 168, 605 160 Z" fill="#FFF9C4" stroke="#FBC02D" stroke-width="1.5" />
      <text x="682" y="182" font-size="12" font-weight="bold" fill="#F57F17" text-anchor="middle">Camada Gold</text>
      <text x="682" y="200" font-size="10" font-weight="bold" fill="#333" text-anchor="middle">Parquet (Data Marts)</text>
      <text x="682" y="216" font-size="9" fill="#555" text-anchor="middle">s3://bucket/gold/</text>
      <text x="682" y="232" font-size="9" fill="#666" text-anchor="middle">7 Tabelas Analíticas</text>
      <text x="682" y="248" font-size="8.5" fill="#888" text-anchor="middle">Contadores Ponderados</text>

      <!-- Setas dos Glue Jobs conectando os S3 -->
      <!-- Bronze -> Job 1 -> Silver -->
      <path d="M 322 145 L 322 80" fill="none" stroke="#0288D1" stroke-width="2" marker-end="url(#arrow-blue)" />
      <path d="M 435 80 L 435 145" fill="none" stroke="#0288D1" stroke-width="2" marker-end="url(#arrow-blue)" />

      <!-- Silver -> Job 2 -> Gold -->
      <path d="M 502 145 L 502 80" fill="none" stroke="#0288D1" stroke-width="2" marker-end="url(#arrow-blue)" />
      <path d="M 615 80 L 615 145" fill="none" stroke="#0288D1" stroke-width="2" marker-end="url(#arrow-blue)" />

      <!-- CONSUMO ANALÍTICO: ATHENA, PYTHON & APRESENTAÇÃO -->
      <!-- S3 Athena Results -->
      <rect x="815" y="90" width="160" height="42" rx="6" fill="#F1F8E9" stroke="#81C784" stroke-width="1.5" />
      <text x="895" y="108" font-size="10.5" font-weight="bold" fill="#2E7D32" text-anchor="middle">S3 Athena Results</text>
      <text x="895" y="122" font-size="8.5" fill="#666" text-anchor="middle">s3://bucket/athena-results/</text>

      <!-- Amazon Athena -->
      <rect x="815" y="150" width="160" height="75" rx="8" fill="#E8F5E9" stroke="#43A047" stroke-width="2" filter="url(#shadow)" />
      <text x="895" y="174" font-size="12" font-weight="bold" fill="#1B5E20" text-anchor="middle">Amazon Athena</text>
      <text x="895" y="192" font-size="9.5" fill="#333" text-anchor="middle">Consultas SQL Interativas</text>
      <text x="895" y="208" font-size="9" font-weight="bold" fill="#43A047" text-anchor="middle">db_state_of_data</text>

      <!-- Setas Gold -> Athena e Athena -> Results -->
      <path d="M 760 195 L 815 195" fill="none" stroke="#107C41" stroke-width="2.5" marker-end="url(#arrow-green)" />
      <path d="M 895 150 L 895 132" fill="none" stroke="#81C784" stroke-width="1.5" stroke-dasharray="3 3" marker-end="url(#arrow-green)" />

      <!-- Extrator e Python DataViz -->
      <rect x="815" y="245" width="160" height="70" rx="8" fill="#FFFDE7" stroke="#FBC02D" stroke-width="2" filter="url(#shadow)" />
      <text x="895" y="268" font-size="11.5" font-weight="bold" fill="#F57F17" text-anchor="middle">Python DataViz (300 DPI)</text>
      <text x="895" y="284" font-size="9" fill="#555" text-anchor="middle">extrair_resultados_athena.py</text>
      <text x="895" y="300" font-size="9" fill="#555" text-anchor="middle">output/resultados_athena/*.csv</text>

      <path d="M 895 225 L 895 245" fill="none" stroke="#FBC02D" stroke-width="2" marker-end="url(#arrow-orange)" />

      <!-- Material Executivo -->
      <rect x="815" y="335" width="160" height="70" rx="8" fill="#EDE7F6" stroke="#5E35B1" stroke-width="2" filter="url(#shadow)" />
      <text x="895" y="358" font-size="11.5" font-weight="bold" fill="#311B92" text-anchor="middle">Material Executivo</text>
      <text x="895" y="374" font-size="9.5" fill="#333" text-anchor="middle">HTML Interativo + PDF</text>
      <text x="895" y="390" font-size="9" font-weight="bold" fill="#5E35B1" text-anchor="middle">Storytelling &amp; Decisões</text>

      <path d="M 895 315 L 895 335" fill="none" stroke="#5E35B1" stroke-width="2" marker-end="url(#arrow-purple)" />

      <!-- FAIXA INFERIOR 1: GOVERNANÇA E CATALOGAÇÃO -->
      <!-- Glue Crawlers -->
      <rect x="255" y="305" width="230" height="55" rx="8" fill="#FFF8E1" stroke="#FFA000" stroke-width="2" />
      <text x="370" y="328" font-size="11.5" font-weight="bold" fill="#E65100" text-anchor="middle">AWS Glue Crawlers</text>
      <text x="370" y="345" font-size="9.5" fill="#666" text-anchor="middle">tc3-crawler-bronze | silver | gold</text>

      <!-- Glue Data Catalog -->
      <rect x="525" y="305" width="235" height="55" rx="8" fill="#FFF8E1" stroke="#FFA000" stroke-width="2" />
      <text x="642" y="328" font-size="11.5" font-weight="bold" fill="#E65100" text-anchor="middle">AWS Glue Data Catalog</text>
      <text x="642" y="345" font-size="9.5" fill="#666" text-anchor="middle">Metadados: db_state_of_data</text>

      <path d="M 485 332 L 525 332" fill="none" stroke="#FFA000" stroke-width="2" marker-end="url(#arrow-orange)" />
      <path d="M 642 305 L 642 285" fill="none" stroke="#FFA000" stroke-width="1.5" stroke-dasharray="4 3" />
      <path d="M 760 332 L 815 195" fill="none" stroke="#FFA000" stroke-width="1.5" stroke-dasharray="4 3" marker-end="url(#arrow-orange)" />

      <!-- COMPLEMENTO ANALÍTICO LOCAL (DESTAQUE SEPARADO) -->
      <rect x="20" y="275" width="180" height="85" rx="8" fill="#FFF3E0" stroke="#E65100" stroke-width="1.5" stroke-dasharray="4 4" />
      <text x="110" y="296" font-size="10.5" font-weight="bold" fill="#BF360C" text-anchor="middle">Complemento Local</text>
      <text x="110" y="312" font-size="9" fill="#333" text-anchor="middle">Uso Real de BI &amp; Cloud (2025–2026)</text>
      <text x="110" y="328" font-size="8.5" fill="#666" text-anchor="middle">tecnologias_uso_2025_2026.csv</text>
      <text x="110" y="344" font-size="8.5" font-weight="bold" fill="#D84315" text-anchor="middle">(Processamento Local / Fora do Athena)</text>

      <!-- FAIXA INFERIOR 2: SEGURANÇA E OBSERVABILIDADE -->
      <rect x="255" y="380" width="230" height="45" rx="6" fill="#FBE9E7" stroke="#D84315" stroke-width="1.5" />
      <text x="370" y="400" font-size="10.5" font-weight="bold" fill="#BF360C" text-anchor="middle">AWS IAM Role (LabRole)</text>
      <text x="370" y="415" font-size="8.5" fill="#666" text-anchor="middle">Políticas de Acesso: S3, Glue, Athena e CloudWatch</text>

      <rect x="525" y="380" width="235" height="45" rx="6" fill="#ECEFF1" stroke="#607D8B" stroke-width="1.5" />
      <text x="642" y="400" font-size="10.5" font-weight="bold" fill="#37474F" text-anchor="middle">Amazon CloudWatch</text>
      <text x="642" y="415" font-size="8.5" fill="#666" text-anchor="middle">Logs de Execução, Falhas e Métricas Operacionais</text>

      <path d="M 370 380 L 370 360" fill="none" stroke="#D84315" stroke-width="1" stroke-dasharray="3 3" />
      <path d="M 642 380 L 642 360" fill="none" stroke="#607D8B" stroke-width="1" stroke-dasharray="3 3" />

      <!-- Rodapé / Legenda -->
      <text x="20" y="460" font-size="9" fill="#888" style="font-style: italic;">
        Arquitetura Oficial — Tech Challenge Fase 3 (Data Lakehouse em 3 Camadas Medallion no Amazon S3 com AWS Glue, PySpark e Athena)
      </text>
    </svg>
    """


def generate_presentation_html():
    print("=" * 80)
    print("GERANDO APRESENTAÇÃO EXECUTIVA EM HTML (100% OFFLINE & STANDALONE)")
    print("=" * 80)

    # Carregar imagens em base64
    img_kpis = get_image_base64("01_kpis_executivos.png")
    img_regiao = get_image_base64("02_distribuicao_regional.png")
    img_genero = get_image_base64("03_diversidade_genero.png")
    img_remuneracao = get_image_base64("04_remuneracao_perfis.png")
    img_tech_top5 = get_image_base64("05_tecnologias_top5.png")
    img_prioridade_ia = get_image_base64("06_prioridade_ia.png")
    img_uso_ia = get_image_base64("07_uso_pessoal_ia.png")
    img_trabalho = get_image_base64("08_modelos_trabalho_satisfacao.png")
    img_uso_real = get_image_base64("09_uso_real_bi_cloud.png")
    svg_arch = build_svg_aws_architecture()

    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Dados e IA no Brasil — Evidências para Expansão da Instituição Financeira (Tech Challenge Fase 3)</title>
  <style>
    /* ==========================================================================
       RESET & THEME SYSTEM (CORES CORPORATIVAS INSTITUCIONAIS)
       ========================================================================== */
    :root {{
      --navy-dark: #0B1E36;
      --navy-primary: #112A46;
      --blue-accent: #1B5EAA;
      --blue-light: #EBF3FA;
      --green-accent: #107C41;
      --green-light: #EDF7EE;
      --amber-accent: #B7791F;
      --amber-light: #FEF3C7;
      --purple-accent: #6B21A8;
      --purple-light: #F3E8FF;
      --slate-dark: #1E293B;
      --slate-text: #334155;
      --slate-muted: #64748B;
      --slate-border: #CBD5E1;
      --bg-page: #F8FAFC;
      --bg-card: #FFFFFF;
      --shadow-sm: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
      --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.08), 0 2px 4px -1px rgba(0,0,0,0.04);
      --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.08), 0 4px 6px -2px rgba(0,0,0,0.04);
      --radius-sm: 6px;
      --radius-md: 10px;
      --radius-lg: 14px;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
      background-color: #0F172A;
      color: var(--slate-dark);
      overflow-x: hidden;
      -webkit-font-smoothing: antialiased;
    }}

    /* ==========================================================================
       SLIDE VIEWPORT & 16:9 CONTAINER
       ========================================================================== */
    #presentation-container {{
      width: 100vw;
      height: 100vh;
      display: flex;
      justify-content: center;
      align-items: center;
      background-color: #090E17;
      position: relative;
    }}

    .slide-wrapper {{
      width: 100%;
      height: 100%;
      max-width: 1600px;
      max-height: 900px;
      aspect-ratio: 16 / 9;
      background-color: var(--bg-page);
      display: none;
      flex-direction: column;
      position: relative;
      overflow: hidden;
      box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5);
    }}

    .slide-wrapper.active {{
      display: flex;
    }}

    /* HEADER */
    .slide-header {{
      height: 64px;
      padding: 12px 36px;
      background: #FFFFFF;
      border-bottom: 1px solid var(--slate-border);
      display: flex;
      justify-content: space-between;
      align-items: center;
      z-index: 10;
      flex-shrink: 0;
    }}

    .slide-title-group {{
      display: flex;
      flex-direction: column;
    }}

    .slide-tag {{
      font-size: 10px;
      font-weight: 800;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--blue-accent);
      margin-bottom: 2px;
    }}

    .slide-title {{
      font-size: 18px;
      font-weight: 800;
      color: var(--navy-dark);
      line-height: 1.2;
    }}

    .slide-meta-badge {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: var(--blue-light);
      color: var(--navy-dark);
      padding: 4px 10px;
      border-radius: var(--radius-sm);
      font-size: 11px;
      font-weight: 700;
      border: 1px solid #BFDBFE;
    }}

    /* CONTENT BODY */
    .slide-body {{
      flex: 1;
      padding: 20px 36px;
      display: grid;
      gap: 20px;
      overflow: hidden;
    }}

    /* FOOTER */
    .slide-footer {{
      height: 38px;
      padding: 0 36px;
      background: #FFFFFF;
      border-top: 1px solid #E2E8F0;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 10.5px;
      color: var(--slate-muted);
      z-index: 10;
      flex-shrink: 0;
    }}

    .footnote {{
      font-style: italic;
    }}

    .pagination {{
      font-weight: 700;
      color: var(--navy-dark);
    }}

    /* ==========================================================================
       GRID LAYOUTS & CARDS
       ========================================================================== */
    .grid-2col {{
      grid-template-columns: 1fr 1fr;
      align-items: stretch;
    }}

    .grid-chart-side {{
      grid-template-columns: 1.15fr 0.85fr;
      align-items: stretch;
    }}

    .grid-side-chart {{
      grid-template-columns: 0.85fr 1.15fr;
      align-items: stretch;
    }}

    .grid-3col {{
      grid-template-columns: repeat(3, 1fr);
      align-items: stretch;
    }}

    .grid-full {{
      grid-template-columns: 1fr;
    }}

    .card {{
      background: var(--bg-card);
      border-radius: var(--radius-md);
      border: 1px solid #E2E8F0;
      padding: 16px 20px;
      box-shadow: var(--shadow-sm);
      display: flex;
      flex-direction: column;
      justify-content: flex-start;
      position: relative;
    }}

    .card-highlight-blue {{
      border-top: 4px solid var(--blue-accent);
    }}

    .card-highlight-green {{
      border-top: 4px solid var(--green-accent);
    }}

    .card-highlight-amber {{
      border-top: 4px solid var(--amber-accent);
    }}

    .card-highlight-purple {{
      border-top: 4px solid var(--purple-accent);
    }}

    .card-header {{
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 10px;
      font-size: 13px;
      font-weight: 700;
      color: var(--navy-dark);
    }}

    .card-icon {{
      width: 22px;
      height: 22px;
      border-radius: 4px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 12px;
    }}

    .icon-blue {{ background: var(--blue-light); color: var(--blue-accent); }}
    .icon-green {{ background: var(--green-light); color: var(--green-accent); }}
    .icon-amber {{ background: var(--amber-light); color: var(--amber-accent); }}
    .icon-purple {{ background: var(--purple-light); color: var(--purple-accent); }}

    .chart-container {{
      background: #FFFFFF;
      border: 1px solid #E2E8F0;
      border-radius: var(--radius-md);
      padding: 10px;
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100%;
      overflow: hidden;
    }}

    .chart-container img {{
      max-width: 100%;
      max-height: 100%;
      object-fit: contain;
      border-radius: var(--radius-sm);
    }}

    /* TRI-CARD (EVIDÊNCIA | INTERPRETAÇÃO | IMPLICAÇÃO) */
    .tria-container {{
      display: flex;
      flex-direction: column;
      gap: 10px;
      height: 100%;
      justify-content: space-between;
    }}

    .tria-block {{
      padding: 10px 14px;
      border-radius: var(--radius-sm);
      font-size: 11.5px;
      line-height: 1.45;
    }}

    .tria-evidencia {{
      background: #F1F5F9;
      border-left: 3px solid #475569;
    }}

    .tria-interpretacao {{
      background: var(--blue-light);
      border-left: 3px solid var(--blue-accent);
    }}

    .tria-implicacao {{
      background: var(--green-light);
      border-left: 3px solid var(--green-accent);
    }}

    .tria-label {{
      font-weight: 800;
      text-transform: uppercase;
      font-size: 9.5px;
      letter-spacing: 0.05em;
      margin-bottom: 3px;
      display: block;
    }}

    .tria-evidencia .tria-label {{ color: #334155; }}
    .tria-interpretacao .tria-label {{ color: var(--blue-accent); }}
    .tria-implicacao .tria-label {{ color: var(--green-accent); }}

    /* KPI BADGES & METRICS */
    .kpi-row {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 10px;
      margin-bottom: 10px;
    }}

    .kpi-box {{
      background: #F8FAFC;
      border: 1px solid #E2E8F0;
      border-radius: var(--radius-sm);
      padding: 8px 12px;
      text-align: center;
    }}

    .kpi-value {{
      font-size: 20px;
      font-weight: 800;
      color: var(--navy-dark);
      line-height: 1.1;
    }}

    .kpi-label {{
      font-size: 10px;
      color: var(--slate-muted);
      margin-top: 3px;
      font-weight: 600;
    }}

    .kpi-delta {{
      font-size: 9.5px;
      font-weight: 700;
      margin-top: 2px;
    }}

    .delta-up {{ color: var(--green-accent); }}
    .delta-down {{ color: #DC2626; }}
    .delta-neutral {{ color: var(--slate-muted); }}

    /* TABELAS EXECUTIVAS */
    .table-exec {{
      width: 100%;
      border-collapse: collapse;
      font-size: 11px;
      text-align: left;
    }}

    .table-exec th {{
      background: #F1F5F9;
      color: var(--navy-dark);
      font-weight: 700;
      padding: 8px 10px;
      border-bottom: 2px solid #CBD5E1;
    }}

    .table-exec td {{
      padding: 7px 10px;
      border-bottom: 1px solid #E2E8F0;
      color: var(--slate-dark);
    }}

    .table-exec tr:nth-child(even) {{
      background: #F8FAFC;
    }}

    /* LISTAS E BULLETS */
    .exec-list {{
      list-style: none;
      padding: 0;
      margin: 0;
    }}

    .exec-list li {{
      position: relative;
      padding-left: 18px;
      margin-bottom: 8px;
      font-size: 12px;
      line-height: 1.45;
      color: var(--slate-text);
    }}

    .exec-list li::before {{
      content: "■";
      position: absolute;
      left: 0;
      top: 1px;
      font-size: 9px;
      color: var(--blue-accent);
    }}

    /* CALLOUT BOXES */
    .callout {{
      padding: 10px 14px;
      border-radius: var(--radius-sm);
      font-size: 11.5px;
      line-height: 1.45;
      margin-top: 8px;
    }}

    .callout-warning {{
      background: #FFFBEB;
      border-left: 3px solid #F59E0B;
      color: #78350F;
    }}

    .callout-info {{
      background: #EFF6FF;
      border-left: 3px solid #3B82F6;
      color: #1E3A8A;
    }}

    .callout-success {{
      background: #ECFDF5;
      border-left: 3px solid #10B981;
      color: #064E3B;
    }}

    /* CAPA ESPECÍFICA */
    .slide-cover {{
      background: linear-gradient(135deg, #0B1E36 0%, #112A46 50%, #1E3A8A 100%);
      color: #FFFFFF;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 50px 70px;
    }}

    .cover-tag {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: rgba(255, 255, 255, 0.12);
      border: 1px solid rgba(255, 255, 255, 0.25);
      padding: 6px 14px;
      border-radius: 20px;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: #93C5FD;
      width: fit-content;
    }}

    .cover-title {{
      font-size: 36px;
      font-weight: 900;
      line-height: 1.15;
      margin-top: 20px;
      color: #FFFFFF;
      max-width: 950px;
    }}

    .cover-subtitle {{
      font-size: 17px;
      color: #CBD5E1;
      line-height: 1.45;
      margin-top: 14px;
      max-width: 850px;
      font-weight: 400;
    }}

    .cover-cards {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 20px;
      margin-top: 30px;
    }}

    .cover-card {{
      background: rgba(255, 255, 255, 0.07);
      border: 1px solid rgba(255, 255, 255, 0.15);
      border-radius: var(--radius-md);
      padding: 16px 20px;
      backdrop-filter: blur(10px);
    }}

    .cover-card-title {{
      font-size: 13px;
      font-weight: 700;
      color: #93C5FD;
      margin-bottom: 6px;
    }}

    .cover-card-desc {{
      font-size: 11.5px;
      color: #E2E8F0;
      line-height: 1.4;
    }}

    .cover-footer {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-top: 1px solid rgba(255, 255, 255, 0.15);
      padding-top: 16px;
      font-size: 11px;
      color: #94A3B8;
    }}

    /* ==========================================================================
       CONTROLES INTERATIVOS & OVERLAYS (TOOLBAR, DRAWER, NOTAS)
       ========================================================================== */
    #toolbar {{
      position: fixed;
      bottom: 20px;
      left: 50%;
      transform: translateX(-50%);
      background: rgba(15, 23, 42, 0.85);
      backdrop-filter: blur(12px);
      border: 1px solid rgba(255, 255, 255, 0.15);
      padding: 6px 14px;
      border-radius: 30px;
      display: flex;
      align-items: center;
      gap: 12px;
      z-index: 1000;
      box-shadow: 0 10px 25px -5px rgba(0,0,0,0.5);
    }}

    .btn-tool {{
      background: transparent;
      border: none;
      color: #F8FAFC;
      font-size: 13px;
      cursor: pointer;
      padding: 6px 10px;
      border-radius: 6px;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 6px;
      transition: all 0.15s ease;
    }}

    .btn-tool:hover {{
      background: rgba(255, 255, 255, 0.15);
      color: #38BDF8;
    }}

    #progress-bar-container {{
      width: 120px;
      height: 6px;
      background: rgba(255, 255, 255, 0.2);
      border-radius: 3px;
      overflow: hidden;
    }}

    #progress-bar {{
      height: 100%;
      width: 5%;
      background: #38BDF8;
      transition: width 0.2s ease;
    }}

    #counter {{
      color: #E2E8F0;
      font-size: 12px;
      font-weight: 700;
      min-width: 45px;
      text-align: center;
    }}

    /* DRAWER DO ÍNDICE */
    #toc-drawer {{
      position: fixed;
      top: 0;
      left: -380px;
      width: 360px;
      height: 100vh;
      background: #0F172A;
      border-right: 1px solid #334155;
      box-shadow: 10px 0 25px rgba(0,0,0,0.5);
      z-index: 2000;
      transition: left 0.25s cubic-bezier(0.4, 0, 0.2, 1);
      display: flex;
      flex-direction: column;
      color: #F8FAFC;
    }}

    #toc-drawer.open {{
      left: 0;
    }}

    .toc-header {{
      padding: 20px;
      border-bottom: 1px solid #334155;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    .toc-title {{
      font-size: 15px;
      font-weight: 800;
      color: #38BDF8;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}

    .toc-list {{
      flex: 1;
      overflow-y: auto;
      padding: 10px 0;
      list-style: none;
    }}

    .toc-item {{
      padding: 10px 20px;
      font-size: 12px;
      cursor: pointer;
      display: flex;
      gap: 12px;
      align-items: center;
      border-left: 3px solid transparent;
      transition: all 0.15s ease;
    }}

    .toc-item:hover {{
      background: rgba(255, 255, 255, 0.06);
      color: #38BDF8;
    }}

    .toc-item.active {{
      background: rgba(56, 189, 248, 0.1);
      border-left-color: #38BDF8;
      color: #38BDF8;
      font-weight: 700;
    }}

    .toc-num {{
      font-weight: 800;
      color: #64748B;
      font-size: 11px;
      width: 20px;
    }}

    /* MODAL DE NOTAS DO APRESENTADOR */
    #notes-modal {{
      position: fixed;
      bottom: 80px;
      right: 30px;
      width: 440px;
      max-height: 480px;
      background: #FFFFFF;
      border: 1px solid #CBD5E1;
      border-radius: var(--radius-md);
      box-shadow: 0 20px 25px -5px rgba(0,0,0,0.2);
      z-index: 2000;
      display: none;
      flex-direction: column;
      overflow: hidden;
    }}

    #notes-modal.open {{
      display: flex;
    }}

    .notes-header {{
      background: var(--navy-dark);
      color: #FFFFFF;
      padding: 10px 16px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 12px;
      font-weight: 700;
    }}

    .notes-body {{
      padding: 16px 20px;
      font-size: 12px;
      line-height: 1.5;
      color: var(--slate-text);
      overflow-y: auto;
    }}

    .notes-body ul {{
      padding-left: 16px;
      margin-top: 6px;
    }}

    .notes-body li {{
      margin-bottom: 6px;
    }}

    /* ==========================================================================
       PRINT CSS (EXIGÊNCIA DE PDF 16:9 PAISAGEM SEM CONTROLES)
       ========================================================================== */
    @page {{
      size: 16in 9in landscape;
      margin: 0;
    }}

    @media print {{
      body {{
        background: transparent !important;
        overflow: visible !important;
      }}

      #presentation-container {{
        display: block !important;
        width: 100% !important;
        height: auto !important;
        background: transparent !important;
      }}

      .slide-wrapper {{
        display: flex !important;
        width: 16in !important;
        height: 9in !important;
        max-width: none !important;
        max-height: none !important;
        page-break-after: always !important;
        page-break-inside: avoid !important;
        box-shadow: none !important;
        margin: 0 !important;
        position: relative !important;
      }}

      #toolbar, #toc-drawer, #notes-modal, #backdrop {{
        display: none !important;
      }}
    }}
  </style>
</head>
<body>

  <div id="presentation-container">

    <!-- ====================================================================
         SLIDE 1: CAPA
         ==================================================================== -->
    <section class="slide-wrapper slide-cover active" id="slide-1" data-title="Capa">
      <div>
        <div class="cover-tag">Tech Challenge Fase 3 • Pós-Tech Data Analytics &amp; Big Data</div>
        <h1 class="cover-title">Dados e IA no Brasil: Evidências para a Expansão de uma Instituição Financeira</h1>
        <p class="cover-subtitle">Diagnóstico Estratégico do Mercado de Trabalho, Remuneração, Tecnologias e Governança de IA com base nas pesquisas State of Data Brasil (2023–2026)</p>
      </div>

      <div class="cover-cards">
        <div class="cover-card">
          <div class="cover-card-title">🏛️ Caso da Instituição Financeira</div>
          <div class="cover-card-desc">Suporte a decisões de contratação, remuneração, capacitação técnica, retenção e alocação de capital em iniciativas de Dados &amp; IA.</div>
        </div>
        <div class="cover-card">
          <div class="cover-card-title">☁️ Arquitetura Medallion AWS</div>
          <div class="cover-card-desc">Pipeline em 3 camadas no Amazon S3 (Bronze, Silver, Gold), processamento distribuído com PySpark no AWS Glue e consultas no Amazon Athena.</div>
        </div>
        <div class="cover-card">
          <div class="cover-card-title">📊 Amostra Consolidada</div>
          <div class="cover-card-desc">14.002 registros históricos (5.293 em 2023–24, 5.215 em 2024–25 e 3.494 em 2025–26) auditados sob rígidos critérios de integridade estatística.</div>
        </div>
      </div>

      <div class="cover-footer">
        <div>Fonte: Microdados State of Data Brasil (Data Hackers &amp; Bain) | Database AWS: <code>db_state_of_data</code></div>
        <div>Navegue com ⬅️ / ➡️ ou clique em [Índice]</div>
      </div>

      <div class="speaker-notes-content" style="display:none;">
        <strong>Notas do Apresentador (Slide 1 — Capa):</strong>
        <ul>
          <li>Cumprimentar a banca executiva e introduzir o papel da consultoria estratégica de Big Data & Analytics.</li>
          <li>Destacar que o trabalho atende aos três entregáveis do Tech Challenge Fase 3: Material Executivo (este), Diagrama AWS no Draw.io e Scripts/Queries auditados.</li>
          <li>Enfatizar que a apresentação não é um mero resumo descritivo, mas sim uma bússola de tomada de decisão para a expansão do banco.</li>
        </ul>
      </div>
    </section>

    <!-- ====================================================================
         SLIDE 2: PROBLEMA DE NEGÓCIO & SÍNTESE EXECUTIVA
         ==================================================================== -->
    <section class="slide-wrapper" id="slide-2" data-title="Problema de Negócio">
      <header class="slide-header">
        <div class="slide-title-group">
          <span class="slide-tag">Contexto Estratégico</span>
          <h2 class="slide-title">Desafio do Banco: Escalar a Área de Dados e IA com Eficiência de Capital</h2>
        </div>
        <div class="slide-meta-badge">Orientação para Decisão</div>
      </header>

      <div class="slide-body grid-2col">
        <div class="card card-highlight-blue">
          <div class="card-header">
            <div class="card-icon icon-blue">🎯</div>
            <span>Três Decisões Centrais que o Estudo Orienta</span>
          </div>
          <ul class="exec-list">
            <li><strong>1. Estratégia de Atração e Remuneração de Talentos:</strong> Identificar onde residem os talentos escassos e calibrar faixas salariais para perfis de alta complexidade (Engenharia de Dados e MLOps) sem inflacionar a folha global.</li>
            <li><strong>2. Investimento Tecnológico e Capacitação Interna:</strong> Definir uma stack tecnológica interoperável e desenhar trilhas de upskilling focadas em competências fundamentais transferíveis (SQL, Python, Cloud e Modelagem).</li>
            <li><strong>3. Transição de IA Experimental para Pilotos Governados:</strong> Superar o estágio de ferramentas isoladas e criar um modelo corporativo de GenAI com segurança de dados sensíveis (LGPD/Sigilo Bancário) e ROI mensurável.</li>
          </ul>
          <div class="callout callout-info" style="margin-top:auto;">
            <strong>Foco Executivo:</strong> Transformar dados empíricos de mercado em escolhas estratégicas defensáveis para a diretoria do banco.
          </div>
        </div>

        <div class="card card-highlight-green">
          <div class="card-header">
            <div class="card-icon icon-green">💡</div>
            <span>Tese Central do Diagnóstico de Mercado</span>
          </div>
          <div class="tria-container">
            <div class="tria-block tria-evidencia">
              <span class="tria-label">O que o Mercado Revela</span>
              A remuneração nominal média estimada avançou +26,4% no período analisado e cresceu exponencialmente o financiamento empresarial de ferramentas de IA (de 6,4% para 42,3%). Persistem forte concentração no Sudeste (>60%), baixa participação feminina (22,0%) e disparidade de satisfação em modelos presenciais.
            </div>
            <div class="tria-block tria-interpretacao">
              <span class="tria-label">Interpretação para o Setor Financeiro</span>
              O mercado brasileiro de dados amadureceu em custos e expectativas, mas opera com funis de contratação restritos e riscos de dispersão de orçamento em IA sem governança.
            </div>
            <div class="tria-block tria-implicacao">
              <span class="tria-label">Diretriz Estratégica para o Banco</span>
              Combinar contratação sênior cirúrgica, formação técnica interna de plenos, contratação distribuída com flexibilidade de trabalho e pilotos governados de IA com validação de retorno.
            </div>
          </div>
        </div>
      </div>

      <footer class="slide-footer">
        <span class="footnote">Diagnóstico estruturado para expansão de Big Data &amp; Analytics no Setor Bancário</span>
        <span class="pagination">02 / 18</span>
      </footer>

      <div class="speaker-notes-content" style="display:none;">
        <strong>Notas do Apresentador (Slide 2 — Síntese):</strong>
        <ul>
          <li>Explicar as três dores do banco: custo de atração elevado, risco de obsolescência tecnológica e pressão por IA generativa sem governança.</li>
          <li>Apresentar a tese central: não basta copiar o que o mercado faz; o banco deve usar os dados para criar vantagens estruturais de custo e retenção.</li>
        </ul>
      </div>
    </section>

    <!-- ====================================================================
         SLIDE 3: BASE DE DADOS & CONFIABILIDADE
         ==================================================================== -->
    <section class="slide-wrapper" id="slide-3" data-title="Base & Confiabilidade">
      <header class="slide-header">
        <div class="slide-title-group">
          <span class="slide-tag">Rigor Metodológico</span>
          <h2 class="slide-title">Base Histórica Consolidada e Salvaguardas de Integridade</h2>
        </div>
        <div class="slide-meta-badge">14.002 Registros Auditados</div>
      </header>

      <div class="slide-body grid-2col">
        <div class="card card-highlight-blue">
          <div class="card-header">
            <div class="card-icon icon-blue">📊</div>
            <span>Composição Amostral por Edição da Pesquisa</span>
          </div>
          <div class="kpi-row">
            <div class="kpi-box">
              <div class="kpi-value">5.293</div>
              <div class="kpi-label">2023–2024</div>
              <div class="kpi-delta delta-neutral">0 dups removidas</div>
            </div>
            <div class="kpi-box">
              <div class="kpi-value">5.215</div>
              <div class="kpi-label">2024–2025</div>
              <div class="kpi-delta delta-neutral">2 dups removidas</div>
            </div>
            <div class="kpi-box">
              <div class="kpi-value">3.494</div>
              <div class="kpi-label">2025–2026</div>
              <div class="kpi-delta delta-neutral">1 dup removida</div>
            </div>
          </div>
          <table class="table-exec">
            <thead>
              <tr><th>Etapa de Auditoria</th><th>Regra Aplicada</th><th>Status</th></tr>
            </thead>
            <tbody>
              <tr><td>Deduplicação de Chave</td><td>Chave <code>(ano, id)</code> com hash SHA-256 para nulos</td><td>✅ 0 duplicatas</td></tr>
              <tr><td>Estimativa Salarial</td><td>Ponto médio em faixas fechadas; 1.2x no topo aberto</td><td>✅ Métrica contínua</td></tr>
              <tr><td>Completude Crítica</td><td>Gênero (100%), Região (97,2%), Salário (91,7%)</td><td>✅ Acima dos limites</td></tr>
              <tr><td>Taxa de Satisfação</td><td>Denominador estrito sobre respostas válidas</td><td>✅ Sem distorção</td></tr>
            </tbody>
          </table>
        </div>

        <div class="card card-highlight-amber">
          <div class="card-header">
            <div class="card-icon icon-amber">⚠️</div>
            <span>Limitações e Ressalvas Metodológicas Essenciais</span>
          </div>
          <ul class="exec-list">
            <li><strong>Amostra Voluntária de Conveniência:</strong> A pesquisa não constitui um censo populacional nem um painel longitudinal (não acompanha os mesmos indivíduos ano a ano).</li>
            <li><strong>Variação Volumétrica em 2025–2026:</strong> A redução de ~33% no volume de respondentes reflete dinâmicas de engajamento da coleta, e não retração do mercado de trabalho de dados.</li>
            <li><strong>Salários Estimados Nominais:</strong> Os valores salariais são aproximações baseadas em faixas textuais brutas sem correção inflacionária pelo IPCA.</li>
            <li><strong>Faixa Inconsistente Preservada:</strong> Uma inconsistência de digitação na fonte de 2025–2026 foi mantida por integridade (impacto de R$ 0,21 na média geral).</li>
          </ul>
          <div class="callout callout-warning">
            <strong>Critério Científico:</strong> Variações temporais indicam mudanças na composição da amostra participante, devendo ser interpretadas com cautela estatística.
          </div>
        </div>
      </div>

      <footer class="slide-footer">
        <span class="footnote">Auditoria automatizada executada via <code>scripts/quality/validacao_qualidade.py</code></span>
        <span class="pagination">03 / 18</span>
      </footer>

      <div class="speaker-notes-content" style="display:none;">
        <strong>Notas do Apresentador (Slide 3 — Metodologia):</strong>
        <ul>
          <li>Explicar a transparência metodológica: deduplicamos exatamente 3 registros repetidos (14.005 -> 14.002).</li>
          <li>Frisar que a redução amostral em 2025-2026 foi controlada em todas as análises através do uso rigoroso de percentuais sobre bases válidas.</li>
        </ul>
      </div>
    </section>

    <!-- ====================================================================
         SLIDE 4: ARQUITETURA AWS
         ==================================================================== -->
    <section class="slide-wrapper" id="slide-4" data-title="Arquitetura AWS">
      <header class="slide-header">
        <div class="slide-title-group">
          <span class="slide-tag">Engenharia de Dados &amp; Cloud</span>
          <h2 class="slide-title">Arquitetura da Plataforma Analítica na AWS (3 Camadas Medallion)</h2>
        </div>
        <div class="slide-meta-badge">AWS Academy Lab • PySpark &amp; Athena</div>
      </header>

      <div class="slide-body grid-chart-side">
        <div class="chart-container" style="padding: 6px;">
          {svg_arch}
        </div>

        <div class="card card-highlight-blue">
          <div class="card-header">
            <div class="card-icon icon-blue">⚙️</div>
            <span>Destaques Técnicos da Solução AWS</span>
          </div>
          <ul class="exec-list" style="font-size: 11px;">
            <li><strong>Amazon S3 Data Lake (3 Camadas):</strong>
              <br>• 🥉 <em>Bronze</em>: CSVs brutos originais imutáveis.
              <br>• 🥈 <em>Silver</em>: Parquet + Snappy particionado por ano, tipos inferidos e deduplicado.
              <br>• 🥇 <em>Gold</em>: 7 Data Marts agregados com contadores ponderados.
            </li>
            <li><strong>AWS Glue Jobs (PySpark):</strong>
              <br>• <code>tc3-bronze-to-silver</code>: Leitura com fail-fast, multiline e padronização.
              <br>• <code>tc3-silver-to-gold</code>: Explode de tecnologias e percentis aproximados.
            </li>
            <li><strong>AWS Glue Data Catalog:</strong> Database centralizado <code>db_state_of_data</code>.</li>
            <li><strong>Amazon Athena:</strong> Consultas SQL com médias ponderadas e Result Reuse (Cache de 7 dias).</li>
            <li><strong>Complemento Local:</strong> O uso de BI/Cloud (questões 4.g e 4.e) foi processado localmente em Python para preservar fidelidade da fonte.</li>
          </ul>
        </div>
      </div>

      <footer class="slide-footer">
        <span class="footnote">Diagrama Draw.io editável disponível em <code>diagrams/arquitetura_aws.drawio</code></span>
        <span class="pagination">04 / 18</span>
      </footer>

      <div class="speaker-notes-content" style="display:none;">
        <strong>Notas do Apresentador (Slide 4 — Arquitetura AWS):</strong>
        <ul>
          <li>Ressaltar a conformidade total com o enunciado: 3 camadas estritas no S3, jobs Spark desacoplados e governança no Glue Catalog.</li>
          <li>Explicar que os Glue Jobs operam fora do bucket S3 como nós de computação efêmeros.</li>
        </ul>
      </div>
    </section>

    <!-- ====================================================================
         SLIDE 5: PANORAMA GERAL & KPIS
         ==================================================================== -->
    <section class="slide-wrapper" id="slide-5" data-title="Panorama Geral (KPIs)">
      <header class="slide-header">
        <div class="slide-title-group">
          <span class="slide-tag">Diagnóstico Macroeconômico</span>
          <h2 class="slide-title">Evolução dos Principais Indicadores do Mercado de Dados</h2>
        </div>
        <div class="slide-meta-badge">Pergunta 1 do Enunciado</div>
      </header>

      <div class="slide-body grid-chart-side">
        <div class="chart-container">
          <img src="{img_kpis}" alt="KPIs Executivos State of Data Brasil">
        </div>

        <div class="tria-container">
          <div class="tria-block tria-evidencia">
            <span class="tria-label">1. Evidência dos Dados</span>
            A remuneração nominal média estimada cresceu +26,42% (de R$ 10.543,75 para R$ 13.329,00). A concentração no Sudeste subiu +2,16 p.p. (62,11%), enquanto a representatividade feminina caiu -2,48 p.p. (21,95%) e o trabalho 100% remoto recuou -4,92 p.p. (36,66%). A satisfação válida recuou -2,97 p.p. (68,98%).
          </div>
          <div class="tria-block tria-interpretacao">
            <span class="tria-label">2. Interpretação Estratégica</span>
            O mercado reflete uma dinâmica de encarecimento nominal da mão de obra, aumento da centralização geográfica e sinais de atrito com políticas corporativas de retorno presencial.
          </div>
          <div class="tria-block tria-implicacao">
            <span class="tria-label">3. Implicação para o Banco</span>
            O banco não deve competir exclusivamente por salário no Sudeste; deve utilizar flexibilidade geográfica e programas de formação como alavancas de eficiência.
          </div>
        </div>
      </div>

      <footer class="slide-footer">
        <span class="footnote">Fonte: State of Data Brasil (Data Hackers &amp; Bain) | Query Athena: <code>08_indicadores_executivos.csv</code></span>
        <span class="pagination">05 / 18</span>
      </footer>

      <div class="speaker-notes-content" style="display:none;">
        <strong>Notas do Apresentador (Slide 5 — KPIs):</strong>
        <ul>
          <li>Destacar que todas as variações estão expressas corretamente em pontos percentuais (p.p.) para proporções e porcentagem (%) para salários.</li>
          <li>Frisar o crescimento salarial nominal e a estagnação da diversidade.</li>
        </ul>
      </div>
    </section>

    <!-- ====================================================================
         SLIDE 6: CONCENTRAÇÃO REGIONAL
         ==================================================================== -->
    <section class="slide-wrapper" id="slide-6" data-title="Concentração Regional">
      <header class="slide-header">
        <div class="slide-title-group">
          <span class="slide-tag">Estrutura Geográfica</span>
          <h2 class="slide-title">Concentração no Sudeste e Oportunidades de Expansão Nacional</h2>
        </div>
        <div class="slide-meta-badge">Pergunta 6 do Enunciado</div>
      </header>

      <div class="slide-body grid-chart-side">
        <div class="chart-container">
          <img src="{img_regiao}" alt="Distribuição Regional State of Data Brasil">
        </div>

        <div class="tria-container">
          <div class="tria-block tria-evidencia">
            <span class="tria-label">1. Evidência dos Dados</span>
            O Sudeste concentra 62,11% dos respondentes na última edição (2025–2026), seguido por Sul (18,43%), Nordeste (10,48%), Centro-Oeste (6,55%) e Norte (1,92%). A concentração paulista e fluminense manteve-se superior a 60% em todas as edições.
          </div>
          <div class="tria-block tria-interpretacao">
            <span class="tria-label">2. Interpretação Estratégica</span>
            A excessiva centralização no Sudeste gera uma disputa predatória por talentos entre bancos e fintechs, elevando custos de atração e rotatividade involuntária.
          </div>
          <div class="tria-block tria-implicacao">
            <span class="tria-label">3. Implicação para o Banco</span>
            <strong>Hipótese a testar:</strong> Estruturar hubs remotos ou canais de contratação distribuída nos polos universitários do Sul (PR/SC/RS), Nordeste (PE/CE/BA) e Centro-Oeste para compor equipes com menor pressão de contratação física.
          </div>
        </div>
      </div>

      <footer class="slide-footer">
        <span class="footnote">Fonte: State of Data Brasil (Data Hackers &amp; Bain) | Query Athena: <code>02_distribuicao_regional.csv</code></span>
        <span class="pagination">06 / 18</span>
      </footer>

      <div class="speaker-notes-content" style="display:none;">
        <strong>Notas do Apresentador (Slide 6 — Região):</strong>
        <ul>
          <li>Explicar que mais de 37% dos profissionais qualificados estão fora do Sudeste.</li>
          <li>Propor a abertura de vagas em polos consolidados (ex: Porto Alegre, Recife, Florianópolis, Curitiba).</li>
        </ul>
      </div>
    </section>

    <!-- ====================================================================
         SLIDE 7: REMUNERAÇÃO & SENIORIDADE
         ==================================================================== -->
    <section class="slide-wrapper" id="slide-7" data-title="Remuneração & Senioridade">
      <header class="slide-header">
        <div class="slide-title-group">
          <span class="slide-tag">Valorização Profissional</span>
          <h2 class="slide-title">Hierarquia Salarial por Cargo e Nível de Senioridade</h2>
        </div>
        <div class="slide-meta-badge">Pergunta 2 do Enunciado</div>
      </header>

      <div class="slide-body grid-chart-side">
        <div class="chart-container">
          <img src="{img_remuneracao}" alt="Remuneração por Perfil e Senioridade">
        </div>

        <div class="tria-container">
          <div class="tria-block tria-evidencia">
            <span class="tria-label">1. Evidência dos Dados</span>
            Filtro de robustez estatística com mínimo de 30 salários válidos por corte. Sêniores em Engenharia de Dados (R$ 17.689,45), Ciência de Dados (R$ 16.920,40) e Analytics Engineering (R$ 15.650,30) ocupam o topo da remuneração estimada. A progressão de Júnior para Sênior no mesmo cargo varia de 2,3x a 2,5x.
          </div>
          <div class="tria-block tria-interpretacao">
            <span class="tria-label">2. Interpretação Estratégica</span>
            O mercado paga prêmio substancial para quem constrói e sustenta a infraestrutura (Engenharia) e desenvolve modelos em produção. Cargos de BI e Análise possuem faixas salariais mais acessíveis (R$ 4.500 a R$ 8.500).
          </div>
          <div class="tria-block tria-implicacao">
            <span class="tria-label">3. Implicação para o Banco</span>
            Não tratar os valores do Top 6 como média geral do mercado. Contratar sêniores de engenharia cirurgicamente para atuar como tech leads e arquitetos, promovendo internamente analistas para pleno.
          </div>
        </div>
      </div>

      <footer class="slide-footer">
        <span class="footnote">Fonte: State of Data Brasil (Data Hackers &amp; Bain) | Query Athena: <code>03_remuneracao_senioridade.csv</code></span>
        <span class="pagination">07 / 18</span>
      </footer>

      <div class="speaker-notes-content" style="display:none;">
        <strong>Notas do Apresentador (Slide 7 — Salários):</strong>
        <ul>
          <li>Explicar a curva salarial: Engenharia de Dados superou Ciência de Dados pela escassez de profissionais de pipeline robusto.</li>
          <li>Frisar que o banco deve evitar pagar piso de engenharia para funções de BI básico.</li>
        </ul>
      </div>
    </section>

    <!-- ====================================================================
         SLIDE 8: TECNOLOGIAS NO DIA A DIA (USO REAL)
         ==================================================================== -->
    <section class="slide-wrapper" id="slide-8" data-title="Tecnologias: Uso Real">
      <header class="slide-header">
        <div class="slide-title-group">
          <span class="slide-tag">Adoção Tecnológica</span>
          <h2 class="slide-title">Utilização Efetiva de BI e Plataformas Cloud no Cotidiano</h2>
        </div>
        <div class="slide-meta-badge">Pergunta 4 do Enunciado</div>
      </header>

      <div class="slide-body grid-chart-side">
        <div class="chart-container">
          <img src="{img_uso_real}" alt="Uso Real de BI e Cloud 2025-2026">
        </div>

        <div class="tria-container">
          <div class="tria-block tria-evidencia">
            <span class="tria-label">1. Evidência dos Dados</span>
            Na edição 2025–2026 (questões multiseleção 4.g e 4.e): Power BI é usado no dia a dia por 59,00% (1.242/2.105), Looker Studio por 15,58% (328/2.105), Tableau por 13,63% (287/2.105) e Looker por 12,78% (269/2.105). Em Cloud: AWS lidera com 48,26% (1.011/2.095), Azure tem 34,84% (730/2.095) e Google Cloud 30,88% (647/2.095).
          </div>
          <div class="tria-block tria-interpretacao">
            <span class="tria-label">2. Interpretação Estratégica</span>
            O ecossistema bancário é predominantemente multicloud e híbrido. Power BI e AWS são os líderes de execução diária, mas há forte presença combinada de Azure e GCP.
          </div>
          <div class="tria-block tria-implicacao">
            <span class="tria-label">3. Implicação para o Banco</span>
            Garantir arquitetura corporativa interoperável e governança centralizada, sem impor migrações monolíticas desnecessárias. Capacitar equipes em fundamentos multicloud.
          </div>
        </div>
      </div>

      <footer class="slide-footer">
        <span class="footnote">Análise complementar local: <code>output/analises_complementares/tecnologias_uso_2025_2026.csv</code> (não calculada no Athena)</span>
        <span class="pagination">08 / 18</span>
      </footer>

      <div class="speaker-notes-content" style="display:none;">
        <strong>Notas do Apresentador (Slide 8 — Uso Real):</strong>
        <ul>
          <li>Destacar a separação metodológica entre USO DIÁRIO (este slide) e PREFERÊNCIA (próximo slide).</li>
          <li>Mencionar a correção documentada: Looker e Looker Studio foram separados textualmente para evitar a contagem indevida de 206 respostas.</li>
        </ul>
      </div>
    </section>

    <!-- ====================================================================
         SLIDE 9: COMPETÊNCIAS & PREFERÊNCIAS
         ==================================================================== -->
    <section class="slide-wrapper" id="slide-9" data-title="Competências & Preferências">
      <header class="slide-header">
        <div class="slide-title-group">
          <span class="slide-tag">Capacitação &amp; Stack</span>
          <h2 class="slide-title">Linguagens e Ferramentas Preferidas: Direcionamento de Trilhas</h2>
        </div>
        <div class="slide-meta-badge">Pergunta 4 do Enunciado</div>
      </header>

      <div class="slide-body grid-chart-side">
        <div class="chart-container">
          <img src="{img_tech_top5}" alt="Top Tecnologias Preferidas">
        </div>

        <div class="tria-container">
          <div class="tria-block tria-evidencia">
            <span class="tria-label">1. Evidência dos Dados</span>
            Em preferências técnicas declaradas: Python (92,07%) e SQL (84,19%) são as linguagens hegemônicas absolutas (n=2.094 válidas em 2025–2026). Em preferência de BI: Power BI (50,51%) e Tableau (17,45%). Em preferência de Cloud: AWS (31,74%), GCP (22,55%) e Azure (20,13%).
          </div>
          <div class="tria-block tria-interpretacao">
            <span class="tria-label">2. Interpretação Estratégica</span>
            SQL e Python são as competências universais de maior liquidez e transferibilidade entre equipes de Engenharia, Analytics e Data Science.
          </div>
          <div class="tria-block tria-implicacao">
            <span class="tria-label">3. Implicação para o Banco</span>
            Estruturar trilhas internas de upskilling baseadas em SQL avançado (modelagem dimensional), Python para automação/análise e governança de dados na nuvem, reduzindo dependência de contratações externas caras.
          </div>
        </div>
      </div>

      <footer class="slide-footer">
        <span class="footnote">Fonte: State of Data Brasil (Data Hackers &amp; Bain) | Query Athena: <code>05_tecnologias.csv</code></span>
        <span class="pagination">09 / 18</span>
      </footer>

      <div class="speaker-notes-content" style="display:none;">
        <strong>Notas do Apresentador (Slide 9 — Competências):</strong>
        <ul>
          <li>Mostrar que SQL e Python são os dois pilares que todo colaborador de dados no banco deve dominar.</li>
          <li>Alertar para não interpretar preferência como recomendação automática de fornecedor exclusivo.</li>
        </ul>
      </div>
    </section>

    <!-- ====================================================================
         SLIDE 10: DIVERSIDADE DE GÊNERO
         ==================================================================== -->
    <section class="slide-wrapper" id="slide-10" data-title="Diversidade de Gênero">
      <header class="slide-header">
        <div class="slide-title-group">
          <span class="slide-tag">Diversidade &amp; Equidade</span>
          <h2 class="slide-title">Cenário de Diversidade e Lacunas de Representatividade Feminina</h2>
        </div>
        <div class="slide-meta-badge">Pergunta 3 do Enunciado</div>
      </header>

      <div class="slide-body grid-chart-side">
        <div class="chart-container">
          <img src="{img_genero}" alt="Diversidade de Gênero State of Data Brasil">
        </div>

        <div class="tria-container">
          <div class="tria-block tria-evidencia">
            <span class="tria-label">1. Evidência dos Dados</span>
            A participação feminina recuou para 21,95% na amostra de 2025–2026 (contra 24,43% em 2023–2024). A diferença salarial média bruta declarada é de ~19,4% (Homens: R$ 13.944,95 vs Mulheres: R$ 11.238,40).
          </div>
          <div class="tria-block tria-interpretacao">
            <span class="tria-label">2. Interpretação Estratégica</span>
            <strong>Ressalva Metodológica:</strong> Trata-se de diferença bruta, não ajustada por cargo, senioridade ou tempo de experiência. Ela reflete a sub-representação feminina em posições seniores e de liderança técnica (efeito pipeline).
          </div>
          <div class="tria-block tria-implicacao">
            <span class="tria-label">3. Implicação para o Banco</span>
            Implementar programas de mentoria e formação afirmativa para alavancar mulheres para níveis Pleno/Sênior e conduzir auditorias internas de equidade salarial em funções idênticas.
          </div>
        </div>
      </div>

      <footer class="slide-footer">
        <span class="footnote">Fonte: State of Data Brasil (Data Hackers &amp; Bain) | Query Athena: <code>04_diversidade_genero.csv</code></span>
        <span class="pagination">10 / 18</span>
      </footer>

      <div class="speaker-notes-content" style="display:none;">
        <strong>Notas do Apresentador (Slide 10 — Diversidade):</strong>
        <ul>
          <li>Explicar a ressalva estatística: a pesquisa mostra o dado agregado bruto, não uma disparidade entre pessoas na mesma mesa com a mesma experiência.</li>
          <li>Propor metas de progressão interna como a melhor estratégia para fechar a lacuna.</li>
        </ul>
      </div>
    </section>

    <!-- ====================================================================
         SLIDE 11: MODELOS DE TRABALHO & SATISFAÇÃO
         ==================================================================== -->
    <section class="slide-wrapper" id="slide-11" data-title="Modelos de Trabalho">
      <header class="slide-header">
        <div class="slide-title-group">
          <span class="slide-tag">Cultura &amp; Retenção</span>
          <h2 class="slide-title">Flexibilidade como Alavanca de Satisfação e Retenção de Talentos</h2>
        </div>
        <div class="slide-meta-badge">Pergunta 6 do Enunciado</div>
      </header>

      <div class="slide-body grid-chart-side">
        <div class="chart-container">
          <img src="{img_trabalho}" alt="Modelos de Trabalho e Satisfação">
        </div>

        <div class="tria-container">
          <div class="tria-block tria-evidencia">
            <span class="tria-label">1. Evidência dos Dados</span>
            Em 2025–2026 (respostas válidas): 100% Remoto (74,80%) e Híbrido Flexível (72,40%) apresentam satisfação muito superior ao 100% Presencial (52,10%) — uma diferença de mais de 20 pontos percentuais.
          </div>
          <div class="tria-block tria-interpretacao">
            <span class="tria-label">2. Interpretação Estratégica</span>
            Profissionais de alta performance em tecnologia percebem flexibilidade de rotina e ausência de deslocamento diário como um dos principais fatores de qualidade de vida e permanência na empresa.
          </div>
          <div class="tria-block tria-implicacao">
            <span class="tria-label">3. Implicação para o Banco</span>
            <strong>Hipótese de retenção:</strong> Adotar o modelo Híbrido Flexível com 1 a 2 dias de colaboração estratégica presencial como padrão, validando o impacto com dados internos de turnover, produtividade e clima.
          </div>
        </div>
      </div>

      <footer class="slide-footer">
        <span class="footnote">Fonte: State of Data Brasil (Data Hackers &amp; Bain) | Query Athena: <code>07_modelos_trabalho.csv</code></span>
        <span class="pagination">11 / 18</span>
      </footer>

      <div class="speaker-notes-content" style="display:none;">
        <strong>Notas do Apresentador (Slide 11 — Retenção):</strong>
        <ul>
          <li>Apontar o risco de 'turnover voluntário' caso o banco adote política 100% presencial rígida.</li>
          <li>O modelo híbrido flexível equilibra governança corporativa e atratividade no recrutamento.</li>
        </ul>
      </div>
    </section>

    <!-- ====================================================================
         SLIDE 12: PRIORIDADE CORPORATIVA DE IA
         ==================================================================== -->
    <section class="slide-wrapper" id="slide-12" data-title="Prioridade de IA">
      <header class="slide-header">
        <div class="slide-title-group">
          <span class="slide-tag">Inteligência Artificial</span>
          <h2 class="slide-title">Priorização Estratégica de IA na Visão dos Gestores de Dados</h2>
        </div>
        <div class="slide-meta-badge">Pergunta 5 do Enunciado</div>
      </header>

      <div class="slide-body grid-chart-side">
        <div class="chart-container">
          <img src="{img_prioridade_ia}" alt="Prioridade de IA nas Empresas">
        </div>

        <div class="tria-container">
          <div class="tria-block tria-evidencia">
            <span class="tria-label">1. Evidência dos Dados</span>
            Entre os gestores respondentes (n=652 em 2025–2026), 60,58% declaram que IA é uma das principais prioridades (39,42% prioridade relevante, 21,16% principal prioridade da empresa), saltando de 36,16% em 2023–2024.
          </div>
          <div class="tria-block tria-interpretacao">
            <span class="tria-label">2. Interpretação Estratégica</span>
            <strong>Ressalva:</strong> O indicador mede a percepção dos gestores participantes, não um censo de empresas jurídicas. Ele reflete forte pressão executiva por adoção e alocação de orçamento.
          </div>
          <div class="tria-block tria-implicacao">
            <span class="tria-label">3. Implicação para o Banco</span>
            Canalizar o apetite executivo para casos de uso estruturantes (ex: concessão de crédito, detecção de fraude, automação de compliance), evitando dispersão em iniciativas sem metas de retorno.
          </div>
        </div>
      </div>

      <footer class="slide-footer">
        <span class="footnote">Fonte: State of Data Brasil (Data Hackers &amp; Bain) | Query Athena: <code>06a_prioridade_ia.csv</code></span>
        <span class="pagination">12 / 18</span>
      </footer>

      <div class="speaker-notes-content" style="display:none;">
        <strong>Notas do Apresentador (Slide 12 — Prioridade IA):</strong>
        <ul>
          <li>Destacar que IA deixou de ser área experimental para se tornar prioridade estratégica em mais de 60% das áreas de dados.</li>
          <li>Frisar a importância de métricas de negócio para não cair na armadilha de 'hype sem ROI'.</li>
        </ul>
      </div>
    </section>

    <!-- ====================================================================
         SLIDE 13: USO PESSOAL & FINANCIAMENTO DE IA
         ==================================================================== -->
    <section class="slide-wrapper" id="slide-13" data-title="Uso Individual de IA">
      <header class="slide-header">
        <div class="slide-title-group">
          <span class="slide-tag">Adoção Individual</span>
          <h2 class="slide-title">Adoção de IA e Transição para Financiamento Corporativo</h2>
        </div>
        <div class="slide-meta-badge">Pergunta 5 do Enunciado</div>
      </header>

      <div class="slide-body grid-chart-side">
        <div class="chart-container">
          <img src="{img_uso_ia}" alt="Uso Pessoal de IA 2025-2026">
        </div>

        <div class="tria-container">
          <div class="tria-block tria-evidencia">
            <span class="tria-label">1. Evidência dos Dados</span>
            Entre não gestores (n=2.105 em 2025–2026): 42,33% utilizam ferramentas de IA pagas pela empresa (contra 6,36% em 2023–2024). 29,83% usam ferramentas de IA voltadas para código/programação.
          </div>
          <div class="tria-block tria-interpretacao">
            <span class="tria-label">2. Interpretação Estratégica</span>
            O financiamento corporativo comprova compra institucional de licenças (ex: Copilot, ChatGPT Enterprise), mas não atesta governança de dados sensíveis nem mensuração de produtividade real.
          </div>
          <div class="tria-block tria-implicacao">
            <span class="tria-label">3. Implicação para o Banco</span>
            Criar um ambiente corporativo protegido (sandbox seguro com mascaramento de dados) e medir ganho de produtividade em pilotos controlados de desenvolvimento de software e análise.
          </div>
        </div>
      </div>

      <footer class="slide-footer">
        <span class="footnote">Fonte: State of Data Brasil (Data Hackers &amp; Bain) | Query Athena: <code>06b_uso_pessoal_ia.csv</code></span>
        <span class="pagination">13 / 18</span>
      </footer>

      <div class="speaker-notes-content" style="display:none;">
        <strong>Notas do Apresentador (Slide 13 — Uso Pessoal IA):</strong>
        <ul>
          <li>Alertar para o risco de 'Shadow AI' se o banco não fornecer ferramentas oficiais homologadas.</li>
          <li>Propor a liberação de ferramentas corporativas com trilha de segurança de dados.</li>
        </ul>
      </div>
    </section>

    <!-- ====================================================================
         SLIDE 14: MATRIZ ESTRATÉGICA DE DECISÕES
         ==================================================================== -->
    <section class="slide-wrapper" id="slide-14" data-title="Matriz Estratégica">
      <header class="slide-header">
        <div class="slide-title-group">
          <span class="slide-tag">Recomendações de Negócio</span>
          <h2 class="slide-title">Matriz de Decisões Estratégicas para a Instituição Financeira</h2>
        </div>
        <div class="slide-meta-badge">Pergunta 7 do Enunciado</div>
      </header>

      <div class="slide-body grid-full">
        <div class="card card-highlight-blue" style="padding: 12px 16px;">
          <table class="table-exec">
            <thead>
              <tr>
                <th style="width: 14%;">Pilar Estratégico</th>
                <th style="width: 22%;">Evidência dos Dados</th>
                <th style="width: 24%;">Risco ou Oportunidade</th>
                <th style="width: 25%;">Decisão Proposta</th>
                <th style="width: 15%;">Indicador de Validação</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>1. Contratação</strong></td>
                <td>Sêniores em Engenharia/ML recebem até R$ 17.689; concentração de 62% no Sudeste.</td>
                <td>Disputa predatória inflaciona custos locais e alonga tempo de contratação.</td>
                <td>Contratar sêniores cirurgicamente e abrir vagas distribuídas no Sul e Nordeste.</td>
                <td>Tempo de fechamento de vagas e custo médio por contratação.</td>
              </tr>
              <tr>
                <td><strong>2. Capacitação</strong></td>
                <td>Python (92%) e SQL (84%) lideram com folga as preferências de linguagens.</td>
                <td>Treinamentos dispersos em ferramentas de nicho geram baixo retorno.</td>
                <td>Criar academia interna de dados focada em SQL avançado, Python e arquitetura cloud.</td>
                <td>Taxa de conclusão de trilhas e promoção interna de Plenos.</td>
              </tr>
              <tr>
                <td><strong>3. Retenção</strong></td>
                <td>Modelos flexíveis superam o presencial em mais de 20 p.p. na satisfação válida.</td>
                <td>Imposição 100% presencial arrisca perda dos profissionais mais produtivos.</td>
                <td>Consolidar Híbrido Flexível (1-2 dias presenciais para ritos de alinhamento).</td>
                <td>Turnover voluntário e eNPS (satisfação do colaborador).</td>
              </tr>
              <tr>
                <td><strong>4. Diversidade</strong></td>
                <td>Participação feminina de 22,0% e diferença salarial média bruta de 19,4%.</td>
                <td>Homogeneidade limita inovação e prejudica a imagem institucional.</td>
                <td>Metas de recrutamento afirmativo e aceleração de lideranças técnicas femininas.</td>
                <td>% de mulheres em vagas sênior e paridade em cargos iguais.</td>
              </tr>
              <tr>
                <td><strong>5. Inteligência Artificial</strong></td>
                <td>42,3% usam IA paga pela empresa; 60,6% dos gestores veem IA como prioridade.</td>
                <td>Dispersão de capital e riscos de segurança de dados bancários (LGPD).</td>
                <td>Implantar sandbox corporativo seguro e homologar 3 casos de uso de crédito/fraude.</td>
                <td>Ganho de tempo medido e ROI financeiro dos pilotos.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <footer class="slide-footer">
        <span class="footnote">Matriz formulada para direcionar o plano executivo do banco</span>
        <span class="pagination">14 / 18</span>
      </footer>

      <div class="speaker-notes-content" style="display:none;">
        <strong>Notas do Apresentador (Slide 14 — Matriz de Decisões):</strong>
        <ul>
          <li>Passar pelos 5 pilares conectando cada evidência da pesquisa a uma decisão executiva objetiva.</li>
          <li>Ressaltar que cada decisão possui uma métrica interna de acompanhamento.</li>
        </ul>
      </div>
    </section>

    <!-- ====================================================================
         SLIDE 15: PLANO DE AÇÃO DE 90 DIAS
         ==================================================================== -->
    <section class="slide-wrapper" id="slide-15" data-title="Plano de 90 Dias">
      <header class="slide-header">
        <div class="slide-title-group">
          <span class="slide-tag">Roadmap Executivo</span>
          <h2 class="slide-title">Plano de Ação Proposto: Cronograma de 0 a 90 Dias</h2>
        </div>
        <div class="slide-meta-badge">Proposta de Implementação</div>
      </header>

      <div class="slide-body grid-3col">
        <div class="card card-highlight-blue">
          <div class="card-header">
            <div class="card-icon icon-blue">1</div>
            <span>0 a 30 Dias: Diagnóstico &amp; Alinhamento</span>
          </div>
          <ul class="exec-list">
            <li><strong>Mapeamento de Competências:</strong> Levantar inventário interno de proficiência em SQL, Python, Cloud e Modelagem.</li>
            <li><strong>Revisão do Funil de Talentos:</strong> Mapear vagas abertas e aprovar política de contratação remota para Sul/Nordeste.</li>
            <li><strong>Seleção de Casos de Uso de IA:</strong> Selecionar 2 a 3 pilotos de GenAI (ex: esteira de crédito e copiloto de código).</li>
          </ul>
          <div class="callout callout-info" style="margin-top:auto;">
            <strong>Entrega:</strong> Matriz de gaps técnicos e termo de abertura dos pilotos de IA.
          </div>
        </div>

        <div class="card card-highlight-amber">
          <div class="card-header">
            <div class="card-icon icon-amber">2</div>
            <span>31 a 60 Dias: Estruturação &amp; Pilotos</span>
          </div>
          <ul class="exec-list">
            <li><strong>Lançamento da Academia de Dados:</strong> Iniciar trilhas internas de SQL e Engenharia de Dados na AWS.</li>
            <li><strong>Sandbox Seguro de GenAI:</strong> Homologar ambiente protegido com mascaramento de dados (LGPD e sigilo bancário).</li>
            <li><strong>Política Híbrida Flexível:</strong> Formalizar diretriz de 1-2 dias presenciais focados em ritos colaborativos.</li>
          </ul>
          <div class="callout callout-warning" style="margin-top:auto;">
            <strong>Entrega:</strong> Pilotos de IA em execução e 1ª turma de capacitação iniciada.
          </div>
        </div>

        <div class="card card-highlight-green">
          <div class="card-header">
            <div class="card-icon icon-green">3</div>
            <span>61 a 90 Dias: Mensuração &amp; Escala</span>
          </div>
          <ul class="exec-list">
            <li><strong>Avaliação de ROI dos Pilotos:</strong> Medir ganho de produtividade e acurácia dos modelos de IA frente ao baseline.</li>
            <li><strong>Auditoria de Equidade Salarial:</strong> Concluir verificação de paridade salarial de gênero para cargos iguais.</li>
            <li><strong>Escala do Pipeline Regional:</strong> Avaliar desempenho e integração dos primeiros contratados fora do Sudeste.</li>
          </ul>
          <div class="callout callout-success" style="margin-top:auto;">
            <strong>Entrega:</strong> Relatório executivo de ROI dos pilotos e plano de escala para 12 meses.
          </div>
        </div>
      </div>

      <footer class="slide-footer">
        <span class="footnote">Proposta cronológica sujeita a validação de orçamento e governança interna do banco</span>
        <span class="pagination">15 / 18</span>
      </footer>

      <div class="speaker-notes-content" style="display:none;">
        <strong>Notas do Apresentador (Slide 15 — 90 Dias):</strong>
        <ul>
          <li>Explicar que o cronograma divide ações de baixo custo inicial (diagnóstico) até escala governada.</li>
          <li>Frisar que metas financeiras definitivas dependem dos orçamentos da instituição.</li>
        </ul>
      </div>
    </section>

    <!-- ====================================================================
         SLIDE 16: DECISÕES EXECUTIVAS RECOMENDADAS
         ==================================================================== -->
    <section class="slide-wrapper" id="slide-16" data-title="Decisões Finais">
      <header class="slide-header">
        <div class="slide-title-group">
          <span class="slide-tag">Conclusão Estratégica</span>
          <h2 class="slide-title">Síntese das Três Decisões Executivas Recomendadas</h2>
        </div>
        <div class="slide-meta-badge">Diretrizes de Governança</div>
      </header>

      <div class="slide-body grid-3col">
        <div class="card card-highlight-blue">
          <div class="card-header">
            <div class="card-icon icon-blue">1</div>
            <span>Capacidades Críticas &amp; Engenharia</span>
          </div>
          <p style="font-size: 11.5px; color: var(--slate-text); line-height: 1.45; margin-bottom: 10px;">
            Contratar sêniores cirurgicamente para arquitetura e liderança de dados, enquanto capacita a base interna em SQL avançado e Python.
          </p>
          <div class="tria-block tria-implicacao" style="margin-top:auto;">
            <span class="tria-label">Métrica de Acompanhamento</span>
            Custo médio de folha vs produtividade de pipelines entregues e taxa de promoção interna.
          </div>
        </div>

        <div class="card card-highlight-green">
          <div class="card-header">
            <div class="card-icon icon-green">2</div>
            <span>Atração Distribuída &amp; Flexibilidade</span>
          </div>
          <p style="font-size: 11.5px; color: var(--slate-text); line-height: 1.45; margin-bottom: 10px;">
            Expandir o recrutamento para fora do eixo Rio-SP e consolidar o modelo Híbrido Flexível para blindar a equipe contra o turnover.
          </p>
          <div class="tria-block tria-implicacao" style="margin-top:auto;">
            <span class="tria-label">Métrica de Acompanhamento</span>
            Turnover voluntário em áreas técnicas (&lt; 8% ao ano) e tempo de atração de talentos.
          </div>
        </div>

        <div class="card card-highlight-purple">
          <div class="card-header">
            <div class="card-icon icon-purple">3</div>
            <span>Pilotos de IA Governados com ROI</span>
          </div>
          <p style="font-size: 11.5px; color: var(--slate-text); line-height: 1.45; margin-bottom: 10px;">
            Migrar de licenças dispersas para um sandbox bancário homologado, medindo ganhos de tempo e qualidade em casos de uso prioritários.
          </p>
          <div class="tria-block tria-implicacao" style="margin-top:auto;">
            <span class="tria-label">Métrica de Acompanhamento</span>
            Retorno financeiro dos pilotos, redução no tempo de esteira de crédito e zero incidentes LGPD.
          </div>
        </div>
      </div>

      <footer class="slide-footer">
        <span class="footnote">Diretrizes finais formuladas pela Consultoria de Big Data &amp; Analytics</span>
        <span class="pagination">16 / 18</span>
      </footer>

      <div class="speaker-notes-content" style="display:none;">
        <strong>Notas do Apresentador (Slide 16 — Decisões Recomendadas):</strong>
        <ul>
          <li>Concluir a apresentação sintetizando as 3 decisões em uma única mensagem coesa.</li>
          <li>Abrir para perguntas da banca avaliadora / diretoria.</li>
        </ul>
      </div>
    </section>

    <!-- ====================================================================
         SLIDE 17: ANEXO 1 — METODOLOGIA & LIMITAÇÕES
         ==================================================================== -->
    <section class="slide-wrapper" id="slide-17" data-title="Anexo 1: Metodologia">
      <header class="slide-header">
        <div class="slide-title-group">
          <span class="slide-tag">Documentação Técnica</span>
          <h2 class="slide-title">Anexo 1 — Metodologia de Tratamento e Limitações dos Dados</h2>
        </div>
        <div class="slide-meta-badge">Rastreabilidade Técnica</div>
      </header>

      <div class="slide-body grid-2col">
        <div class="card">
          <div class="card-header">
            <div class="card-icon icon-blue">📐</div>
            <span>Regras de Tratamento e Fórmulas Aplicadas</span>
          </div>
          <ul class="exec-list" style="font-size: 11px;">
            <li><strong>Estimativa Salarial:</strong> Ponto médio em faixas fechadas; R$ 500,00 na faixa inferior aberta (&lt; R$ 1.000); R$ 48.000,00 na superior aberta (&gt; R$ 40.001 com fator 1.2x).</li>
            <li><strong>Médias Ponderadas:</strong> Para evitar o viés da 'média de médias', toda agregação utiliza:
              $$\\bar{{x}}_{{\\text{{pond}}}} = \\frac{{\\sum (\\bar{{x}}_i \\cdot n_i)}}{{\\sum n_i}}$$
            </li>
            <li><strong>Deduplicação Criptográfica:</strong> Criação de <code>id_registro_tecnico</code> via hash SHA-256 para respostas válidas com token nulo antes do <code>dropDuplicates</code>.</li>
            <li><strong>Desaninhamento de Tecnologias (Explode):</strong> Divisão de respostas multivaloradas por vírgula e apuração de respondentes únicos distintos por categoria.</li>
            <li><strong>Taxa de Satisfação Válida:</strong> Denominador estrito sobre respostas booleanas/válidas, excluindo abstenções da base de cálculo.</li>
          </ul>
        </div>

        <div class="card">
          <div class="card-header">
            <div class="card-icon icon-amber">⚠️</div>
            <span>Registro Formal de Limitações da Pesquisa</span>
          </div>
          <ul class="exec-list" style="font-size: 11px;">
            <li><strong>Amostra Voluntária e Causalidade:</strong> Correlações observadas (ex: trabalho remoto e satisfação) não estabelecem relação de causa e efeito estatístico.</li>
            <li><strong>Faixa Inconsistente em 2025–2026:</strong> A alternativa <code>2.h_faixa_salarial</code> contém uma string divergente na fonte, mantida por auditoria (impacto de R$ 0,21).</li>
            <li><strong>Looker vs Looker Studio:</strong> Identificação de sobreposição na coluna binária original da pesquisa, corrigida no script de uso real via parsing textual estrito.</li>
            <li><strong>Uso Pessoal vs Corporativo de IA:</strong> Gestores e não gestores responderam perguntas com universos amostrais e opções de múltipla escolha distintos.</li>
          </ul>
        </div>
      </div>

      <footer class="slide-footer">
        <span class="footnote">Documentação completa em <code>docs/regras_transformacao.md</code> e <code>docs/relatorio_qualidade.md</code></span>
        <span class="pagination">17 / 18</span>
      </footer>

      <div class="speaker-notes-content" style="display:none;">
        <strong>Notas do Apresentador (Slide 17 — Anexo 1):</strong>
        <ul>
          <li>Apresentar este anexo caso a banca faça perguntas técnicas sobre o cálculo das médias ou tratamento de nulos.</li>
        </ul>
      </div>
    </section>

    <!-- ====================================================================
         SLIDE 18: ANEXO 2 — RASTREABILIDADE DO ENUNCIADO
         ==================================================================== -->
    <section class="slide-wrapper" id="slide-18" data-title="Anexo 2: Rastreabilidade">
      <header class="slide-header">
        <div class="slide-title-group">
          <span class="slide-tag">Conformidade com o Enunciado</span>
          <h2 class="slide-title">Anexo 2 — Rastreabilidade das 7 Perguntas e Entregáveis Técnicos</h2>
        </div>
        <div class="slide-meta-badge">Tech Challenge Fase 3</div>
      </header>

      <div class="slide-body grid-full">
        <div class="card" style="padding: 10px 14px;">
          <table class="table-exec" style="font-size: 10.5px;">
            <thead>
              <tr>
                <th style="width: 35%;">Pergunta Obrigatória do Enunciado</th>
                <th style="width: 15%;">Slide Correspondente</th>
                <th style="width: 25%;">Evidência / Gráfico</th>
                <th style="width: 25%;">Código / Script Fonte</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>1. Como está estruturado o mercado brasileiro de Dados?</td>
                <td>Slides 5 e 6</td>
                <td><code>01_kpis_executivos.png</code> / <code>02_distribuicao_regional.png</code></td>
                <td><code>01_estrutura_mercado.csv</code> / Athena Query 1</td>
              </tr>
              <tr>
                <td>2. Quais perfis profissionais são mais valorizados?</td>
                <td>Slide 7</td>
                <td><code>04_remuneracao_perfis.png</code></td>
                <td><code>03_remuneracao_senioridade.csv</code> / Athena Query 2</td>
              </tr>
              <tr>
                <td>3. Qual o cenário de diversidade de gênero nas carreiras?</td>
                <td>Slide 10</td>
                <td><code>03_diversidade_genero.png</code></td>
                <td><code>04_diversidade_genero.csv</code> / Athena Query 3</td>
              </tr>
              <tr>
                <td>4. Quais tecnologias apresentam maior adoção?</td>
                <td>Slides 8 e 9</td>
                <td><code>09_uso_real_bi_cloud.png</code> / <code>05_tecnologias_top5.png</code></td>
                <td><code>tecnologias_uso_2025_2026.csv</code> / Athena Query 4</td>
              </tr>
              <tr>
                <td>5. Qual o índice de adoção de IA e seu impacto?</td>
                <td>Slides 12 e 13</td>
                <td><code>06_prioridade_ia.png</code> / <code>07_uso_pessoal_ia.png</code></td>
                <td><code>06a_prioridade_ia.csv</code> / <code>06b_uso_pessoal_ia.csv</code></td>
              </tr>
              <tr>
                <td>6. Existem diferenças entre regiões, níveis e modelos?</td>
                <td>Slides 6, 7 e 11</td>
                <td><code>08_modelos_trabalho_satisfacao.png</code></td>
                <td><code>07_modelos_trabalho.csv</code> / Athena Query 6</td>
              </tr>
              <tr>
                <td>7. Quais oportunidades e desafios para investir em Dados e IA?</td>
                <td>Slides 14, 15 e 16</td>
                <td>Matriz Estratégica, Roadmap 90d e 3 Decisões</td>
                <td>Síntese Estratégica da Consultoria</td>
              </tr>
            </tbody>
          </table>
          <div style="margin-top: 10px; display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; font-size: 10px; color: var(--slate-muted);">
            <div style="background:#F1F5F9; padding:6px; border-radius:4px;">📁 <strong>PySpark Glue Jobs:</strong> <code>glue_job_bronze_to_silver.py</code> / <code>glue_job_silver_to_gold.py</code></div>
            <div style="background:#F1F5F9; padding:6px; border-radius:4px;">📁 <strong>Consultas Athena:</strong> <code>scripts/analytics/queries_athena.sql</code></div>
            <div style="background:#F1F5F9; padding:6px; border-radius:4px;">📁 <strong>Quality Gate:</strong> <code>scripts/quality/validacao_qualidade.py</code></div>
            <div style="background:#F1F5F9; padding:6px; border-radius:4px;">📁 <strong>Diagrama AWS:</strong> <code>diagrams/arquitetura_aws.drawio</code></div>
          </div>
        </div>
      </div>

      <footer class="slide-footer">
        <span class="footnote">Rastreabilidade completa de 100% dos requisitos do Tech Challenge Fase 3</span>
        <span class="pagination">18 / 18</span>
      </footer>

      <div class="speaker-notes-content" style="display:none;">
        <strong>Notas do Apresentador (Slide 18 — Rastreabilidade):</strong>
        <ul>
          <li>Encerrar demonstrando a cobertura completa de todos os critérios do enunciado oficial.</li>
        </ul>
      </div>
    </section>

  </div>

  <!-- ====================================================================
       TOOLBAR DE NAVEGAÇÃO FLUTUANTE
       ==================================================================== -->
  <div id="toolbar">
    <button class="btn-tool" id="btn-toc" title="Abrir Índice de Slides">☰ Índice</button>
    <button class="btn-tool" id="btn-prev" title="Slide Anterior (Seta Esquerda)">◀</button>
    <div id="counter">01 / 18</div>
    <div id="progress-bar-container">
      <div id="progress-bar"></div>
    </div>
    <button class="btn-tool" id="btn-next" title="Próximo Slide (Seta Direita)">▶</button>
    <button class="btn-tool" id="btn-notes" title="Notas do Apresentador (N)">📝 Notas</button>
    <button class="btn-tool" id="btn-fullscreen" title="Tela Cheia (F)">⛶ Tela Cheia</button>
    <button class="btn-tool" id="btn-print" title="Imprimir / Salvar PDF (Ctrl+P)">🖨️ PDF</button>
  </div>

  <!-- DRAWER DO ÍNDICE -->
  <div id="toc-drawer">
    <div class="toc-header">
      <span class="toc-title">Índice da Apresentação</span>
      <button class="btn-tool" id="btn-close-toc">✕</button>
    </div>
    <ul class="toc-list" id="toc-list">
      <!-- Populado dinamicamente via JS -->
    </ul>
  </div>

  <!-- MODAL DE NOTAS DO APRESENTADOR -->
  <div id="notes-modal">
    <div class="notes-header">
      <span>Notas do Apresentador</span>
      <button class="btn-tool" id="btn-close-notes" style="padding:2px 6px;">✕</button>
    </div>
    <div class="notes-body" id="notes-content">
      Selecione um slide para ver as anotações do apresentador.
    </div>
  </div>

  <!-- ====================================================================
       JAVASCRIPT STANDALONE DE CONTROLE E NAVEGAÇÃO
       ==================================================================== -->
  <script>
    document.addEventListener('DOMContentLoaded', () => {{
      const slides = document.querySelectorAll('.slide-wrapper');
      const totalSlides = slides.length;
      let currentSlideIndex = 0;

      const btnPrev = document.getElementById('btn-prev');
      const btnNext = document.getElementById('btn-next');
      const counter = document.getElementById('counter');
      const progressBar = document.getElementById('progress-bar');
      const btnToc = document.getElementById('btn-toc');
      const tocDrawer = document.getElementById('toc-drawer');
      const btnCloseToc = document.getElementById('btn-close-toc');
      const tocList = document.getElementById('toc-list');
      const btnNotes = document.getElementById('btn-notes');
      const notesModal = document.getElementById('notes-modal');
      const btnCloseNotes = document.getElementById('btn-close-notes');
      const notesContent = document.getElementById('notes-content');
      const btnFullscreen = document.getElementById('btn-fullscreen');
      const btnPrint = document.getElementById('btn-print');

      // Popula Índice
      slides.forEach((slide, idx) => {{
        const title = slide.getAttribute('data-title') || `Slide ${{idx + 1}}`;
        const li = document.createElement('li');
        li.className = `toc-item ${{idx === 0 ? 'active' : ''}}`;
        li.innerHTML = `<span class="toc-num">${{String(idx + 1).padStart(2, '0')}}</span> <span>${{title}}</span>`;
        li.addEventListener('click', () => {{
          goToSlide(idx);
          tocDrawer.classList.remove('open');
        }});
        tocList.appendChild(li);
      }});

      function updateSlide() {{
        slides.forEach((slide, idx) => {{
          slide.classList.toggle('active', idx === currentSlideIndex);
        }});

        // Atualiza contador e barra
        counter.textContent = `${{String(currentSlideIndex + 1).padStart(2, '0')}} / ${{String(totalSlides).padStart(2, '0')}}`;
        progressBar.style.width = `${{((currentSlideIndex + 1) / totalSlides) * 100}}%`;

        // Atualiza drawer TOC
        const tocItems = tocList.querySelectorAll('.toc-item');
        tocItems.forEach((item, idx) => {{
          item.classList.toggle('active', idx === currentSlideIndex);
        }});

        // Atualiza Notas
        const currentSlide = slides[currentSlideIndex];
        const notesElem = currentSlide.querySelector('.speaker-notes-content');
        if (notesElem) {{
          notesContent.innerHTML = notesElem.innerHTML;
        }} else {{
          notesContent.innerHTML = '<em>Nenhuma anotação disponível para este slide.</em>';
        }}
      }}

      function goToSlide(index) {{
        if (index >= 0 && index < totalSlides) {{
          currentSlideIndex = index;
          updateSlide();
        }}
      }}

      function nextSlide() {{
        if (currentSlideIndex < totalSlides - 1) {{
          goToSlide(currentSlideIndex + 1);
        }}
      }}

      function prevSlide() {{
        if (currentSlideIndex > 0) {{
          goToSlide(currentSlideIndex - 1);
        }}
      }}

      // Eventos de clique
      btnNext.addEventListener('click', nextSlide);
      btnPrev.addEventListener('click', prevSlide);

      btnToc.addEventListener('click', () => tocDrawer.classList.toggle('open'));
      btnCloseToc.addEventListener('click', () => tocDrawer.classList.remove('open'));

      btnNotes.addEventListener('click', () => notesModal.classList.toggle('open'));
      btnCloseNotes.addEventListener('click', () => notesModal.classList.remove('open'));

      btnFullscreen.addEventListener('click', () => {{
        if (!document.fullscreenElement) {{
          document.documentElement.requestFullscreen().catch(err => console.log(err));
        }} else {{
          document.exitFullscreen();
        }}
      }});

      btnPrint.addEventListener('click', () => window.print());

      // Atalhos de Teclado
      document.addEventListener('keydown', (e) => {{
        if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') {{
          nextSlide();
        }} else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {{
          prevSlide();
        }} else if (e.key === 'Home') {{
          goToSlide(0);
        }} else if (e.key === 'End') {{
          goToSlide(totalSlides - 1);
        }} else if (e.key === 'f' || e.key === 'F') {{
          if (!document.fullscreenElement) {{
            document.documentElement.requestFullscreen().catch(err => console.log(err));
          }} else {{
            document.exitFullscreen();
          }}
        }} else if (e.key === 'n' || e.key === 'N') {{
          notesModal.classList.toggle('open');
        }} else if (e.key === 't' || e.key === 'T' || e.key === 'i' || e.key === 'I') {{
          tocDrawer.classList.toggle('open');
        }} else if (e.key === 'Escape') {{
          tocDrawer.classList.remove('open');
          notesModal.classList.remove('open');
        }}
      }});

      // Inicializa
      updateSlide();
    }});
  </script>
</body>
</html>
"""

    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"✅ Apresentação HTML gerada com sucesso em: {HTML_PATH}")


def generate_presentation_pdf():
    print("\n" + "=" * 80)
    print("GERANDO APRESENTAÇÃO EXECUTIVA EM PDF (16:9 LANDSCAPE VIA MS EDGE HEADLESS)")
    print("=" * 80)

    edge_candidates = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    edge_exe = None
    for cand in edge_candidates:
        if os.path.exists(cand):
            edge_exe = cand
            break

    if not edge_exe:
        print("❌ Erro: Executável do Microsoft Edge não encontrado para conversão PDF.")
        return False

    cmd = [
        edge_exe,
        "--headless",
        "--disable-gpu",
        "--run-all-compositor-stages-before-draw",
        "--virtual-time-budget=5000",
        "--print-to-pdf-no-header",
        f"--print-to-pdf={PDF_PATH}",
        f"file:///{HTML_PATH.as_posix()}"
    ]

    print(f"Comando de renderização: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if PDF_PATH.exists() and PDF_PATH.stat().st_size > 50000:
        print(f"✅ PDF gerado com sucesso em: {PDF_PATH} ({PDF_PATH.stat().st_size / 1024:.1f} KB)")
        return True
    else:
        print(f"❌ Falha na geração do PDF: {result.stderr}")
        return False


def create_readme_guide():
    readme_content = """# Instruções de Apresentação e Impressão — Tech Challenge Fase 3

Este diretório contém os materiais executivos finais gerados para o **Tech Challenge Fase 3 (State of Data Brasil / Caso da Instituição Financeira)**.

---

## 📁 Arquivos Entregues

1. **`apresentacao_state_of_data.html`**:
   * Apresentação executiva interativa completa (18 slides) com proporção 16:9 widescreen.
   * **100% Autônomo e Offline:** Não requer internet, servidores, CDNs ou bibliotecas externas. Abre com duplo clique no Google Chrome, Microsoft Edge ou Firefox.
   * **Controles Interativos:**
     * ⬅️ / ➡️ ou Barra de Espaço: Avançar e retroceder slides.
     * `Home` / `End`: Ir para a Capa / Anexo Final.
     * `F`: Alternar modo Tela Cheia (*Fullscreen*).
     * `N`: Abrir modal de Notas do Apresentador (*Speaker Notes*).
     * `T` ou `I`: Abrir menu de Índice (*Table of Contents*).
     * `Ctrl + P` ou Botão **🖨️ PDF**: Imprimir / exportar slides limpos em PDF.

2. **`apresentacao_state_of_data.pdf`**:
   * Documento PDF final oficial em formato 16:9 paisagem (18 páginas), preservando todos os gráficos, tabelas e notas metodológicas.
   * Atende rigorosamente ao formato exigido no enunciado do Tech Challenge.

---

## 🎯 Rastreabilidade das 7 Perguntas do Enunciado

| # | Pergunta do Tech Challenge | Slide Principal |
| :-: | :--- | :-: |
| **1** | Como está estruturado o mercado brasileiro de Dados? | **Slide 5** (*KPIs Macroeconômicos*) & **Slide 6** (*Geografia*) |
| **2** | Quais perfis profissionais são mais valorizados pelo mercado? | **Slide 7** (*Remuneração por Cargo e Nível Sênior*) |
| **3** | Qual é o cenário de diversidade de gênero nas carreiras de dados? | **Slide 10** (*Participação Feminina e Gap Bruto*) |
| **4** | Quais tecnologias apresentam maior adoção entre os profissionais? | **Slide 8** (*Uso Real de BI/Cloud*) & **Slide 9** (*Preferências*) |
| **5** | Qual é o índice de adoção de Inteligência Artificial e seu impacto? | **Slide 12** (*Prioridade nas Empresas*) & **Slide 13** (*Uso Individual*) |
| **6** | Existem diferenças entre regiões, senioridades e modelos de trabalho? | **Slide 6** (*Regiões*), **Slide 7** (*Senioridade*) e **Slide 11** (*Trabalho*) |
| **7** | Quais oportunidades e desafios para investir em Dados e IA? | **Slide 14** (*Matriz Estratégica*), **Slide 15** (*90 Dias*) e **Slide 16** (*Decisões*) |

---

## 🛠️ Como Regenerar os Materiais (se necessário)

Caso queira reconstruir os arquivos a partir do código fonte:
```powershell
# Regenerar gráficos executivos
python scripts/analytics/gerar_graficos_executivos.py

# Regenerar apresentação HTML e PDF
python scripts/analytics/gerar_apresentacao_executiva.py
```
"""
    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(readme_content)
    print(f"✅ Guia de apresentação criado em: {README_PATH}")


if __name__ == "__main__":
    generate_presentation_html()
    generate_presentation_pdf()
    create_readme_guide()
