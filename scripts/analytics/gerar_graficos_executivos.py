"""Gera gráficos executivos a partir dos CSVs exportados do Amazon Athena."""

import argparse
import tempfile
import zipfile
from pathlib import Path
from textwrap import fill

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter


BLUE = "#2563EB"
NAVY = "#17365D"
ORANGE = "#F59E0B"
PINK = "#D95F8D"
TEAL = "#0F9D8A"
GRAY = "#64748B"
LIGHT = "#E2E8F0"
YEARS = ["2023-2024", "2024-2025", "2025-2026"]
YEAR_LABELS = ["23–24", "24–25", "25–26"]
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT_DIR = PROJECT_ROOT / "output" / "resultados_athena"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "output" / "graficos_executivos"


def parse_args():
    parser = argparse.ArgumentParser(description="Gera os gráficos executivos do Tech Challenge")
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--input-dir", type=Path, help="Pasta contendo os CSVs do Athena")
    source.add_argument("--input-zip", type=Path, help="ZIP contendo a pasta resultados_athena")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--dpi", type=int, default=180)
    return parser.parse_args()


def resolve_input(args, temporary):
    if args.input_zip:
        with zipfile.ZipFile(args.input_zip) as archive:
            archive.extractall(temporary)
        root = Path(temporary)
    else:
        root = args.input_dir or DEFAULT_INPUT_DIR
        if not root.exists():
            raise FileNotFoundError(
                f"Pasta de entrada não encontrada: {root}\n"
                "Execute primeiro extrair_resultados_athena.py ou informe --input-dir."
            )
    matches = list(root.rglob("08_indicadores_executivos.csv"))
    if len(matches) != 1:
        raise FileNotFoundError("Não foi possível localizar unicamente os CSVs do Athena")
    return matches[0].parent


def load(root, filename):
    return pd.read_csv(root / filename)


def base_style():
    plt.rcParams.update({
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.edgecolor": LIGHT,
        "axes.labelcolor": "#334155",
        "axes.titlecolor": "#0F172A",
        "axes.titlesize": 17,
        "axes.titleweight": "bold",
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "xtick.color": "#475569",
        "ytick.color": "#475569",
        "grid.color": LIGHT,
        "grid.linewidth": 0.8,
    })


def title(ax, text, subtitle=None):
    ax.set_title(text, loc="left", pad=20)
    if subtitle:
        ax.text(0, 1.01, subtitle, transform=ax.transAxes, color=GRAY, fontsize=9, va="bottom")


def source_note(fig, text="Fonte: State of Data Brasil | Processamento próprio em AWS Glue/Athena"):
    fig.text(0.01, 0.012, text, fontsize=7.5, color=GRAY)


def save(fig, output, name, dpi):
    source_note(fig)
    fig.savefig(output / name, dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def pct(v):
    return f"{v:.1f}%".replace(".", ",")


def brl(v):
    return "R$ " + f"{v:,.0f}".replace(",", ".")


def short_role(value):
    text = str(value)
    replacements = [
        ("Engenheiro de Machine Learning/ML Engineer/AI Engineer", "Engenheiro de ML/IA"),
        ("Engenheiro de Dados/Data Engineer/Data Architect", "Engenheiro de Dados"),
        ("Engenheiro de Dados/Arquiteto de Dados/Data Engineer/Data Architect", "Engenheiro de Dados"),
        ("Cientista de Dados/Data Scientist", "Cientista de Dados"),
        ("Desenvolvedor/ Engenheiro de Software/ Analista de Sistemas", "Engenheiro de Software"),
        ("Analista de Dados/Data Analyst", "Analista de Dados"),
    ]
    for original, concise in replacements:
        if original in text:
            return concise
    return text


def chart_kpis(df, output, dpi):
    metrics = [
        ("participacao_feminina_pct", "Participação feminina", "%"),
        ("concentracao_sudeste_pct", "Concentração no Sudeste", "%"),
        ("satisfacao_trabalho_pct", "Satisfação no trabalho", "%"),
        ("trabalho_remoto_pct", "Trabalho 100% remoto", "%"),
        ("media_salarial_estimada_reais", "Média salarial estimada", "R$"),
    ]
    df = df.set_index("ano_pesquisa").reindex(YEARS)
    fig, axes = plt.subplots(1, 5, figsize=(13.33, 7.5))
    for ax, (column, label, unit) in zip(axes, metrics):
        values = df[column].astype(float).values
        latest, initial = values[-1], values[0]
        latest_label = pct(latest) if unit == "%" else brl(latest)
        delta = latest - initial
        delta_label = (f"{delta:+.1f} p.p." if unit == "%" else f"{delta / initial:+.1%}")
        ax.set_facecolor("#F8FAFC")
        for spine in ax.spines.values():
            spine.set_color(LIGHT)
        ax.set_xticks([]); ax.set_yticks([])
        ax.text(.08, .84, fill(label, 18), transform=ax.transAxes, fontsize=11,
                fontweight="bold", color="#334155", va="top")
        ax.text(.08, .58, latest_label, transform=ax.transAxes, fontsize=19,
                fontweight="bold", color=NAVY, va="center")
        ax.text(.08, .43, "2025–2026", transform=ax.transAxes, fontsize=9, color=GRAY)
        ax.text(.08, .18, f"{delta_label} vs. 2023–2024", transform=ax.transAxes,
                fontsize=9, color=BLUE, fontweight="bold")
    fig.suptitle("Mercado de dados em cinco indicadores", x=.04, y=.93, ha="left",
                 fontsize=20, fontweight="bold", color="#0F172A")
    fig.text(.04, .855, "Última edição e variação acumulada no período", color=GRAY, fontsize=10)
    fig.subplots_adjust(left=.04, right=.98, top=.73, bottom=.22, wspace=.16)
    save(fig, output, "01_kpis_executivos.png", dpi)


def chart_region(df, output, dpi):
    pivot = df.pivot(index="regiao", columns="ano_pesquisa", values="percentual_regiao").fillna(0)
    order = pivot[YEARS[-1]].sort_values().index
    fig, ax = plt.subplots(figsize=(12, 6.75))
    y = np.arange(len(order)); h = 0.22
    colors = [LIGHT, "#94A3B8", BLUE]
    for i, year in enumerate(YEARS):
        vals = pivot.loc[order, year]
        ax.barh(y + (i - 1) * h, vals, height=h, color=colors[i], label=YEAR_LABELS[i])
    ax.set_yticks(y, [fill(x, 20) for x in order])
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:.0f}%"))
    ax.grid(axis="x"); ax.set_axisbelow(True); ax.spines[["top", "right", "left"]].set_visible(False)
    title(ax, "Distribuição regional dos profissionais", "Participação no total de respondentes de cada edição")
    ax.legend(frameon=False, ncol=3, loc="lower right")
    fig.subplots_adjust(left=0.2, bottom=0.1)
    save(fig, output, "02_distribuicao_regional.png", dpi)


def chart_diversity(df, output, dpi):
    female = df[df["genero"] == "Feminino"].set_index("ano_pesquisa").reindex(YEARS)
    male = df[df["genero"] == "Masculino"].set_index("ano_pesquisa").reindex(YEARS)
    fig, axes = plt.subplots(1, 2, figsize=(12, 6.75))
    axes[0].plot(YEAR_LABELS, female["percentual_genero"], color=PINK, marker="o", linewidth=2.8)
    for x, v in zip(YEAR_LABELS, female["percentual_genero"]):
        axes[0].annotate(pct(v), (x, v), xytext=(0, 10), textcoords="offset points", ha="center", fontweight="bold")
    axes[0].set_ylim(18, 27); axes[0].grid(axis="y"); axes[0].spines[["top", "right"]].set_visible(False)
    title(axes[0], "Participação feminina", "Percentual sobre todos os respondentes")
    gap = (male["salario_medio_ponderado"] - female["salario_medio_ponderado"]) / male["salario_medio_ponderado"] * 100
    axes[1].bar(YEAR_LABELS, gap, color=ORANGE, width=0.58)
    for x, v in zip(YEAR_LABELS, gap):
        axes[1].text(x, v + 0.5, pct(v), ha="center", fontweight="bold")
    axes[1].set_ylim(0, max(gap) * 1.25); axes[1].yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:.0f}%"))
    axes[1].grid(axis="y"); axes[1].set_axisbelow(True); axes[1].spines[["top", "right"]].set_visible(False)
    title(axes[1], "Diferença salarial de gênero", "Quanto a média feminina está abaixo da média masculina")
    fig.subplots_adjust(top=0.82, wspace=0.28, bottom=0.1)
    save(fig, output, "03_diversidade_genero.png", dpi)


def chart_salary(df, output, dpi):
    latest = df[df["ano_pesquisa"] == YEARS[-1]].copy()
    latest = latest.sort_values("salario_medio_ponderado", ascending=False).head(6).sort_values("salario_medio_ponderado")
    labels = [fill(f"{short_role(c)} — {s}", 30)
              for c, s in zip(latest["cargo_atual"], latest["senioridade_padronizada"])]
    fig, ax = plt.subplots(figsize=(12, 6.75))
    bars = ax.barh(labels, latest["salario_medio_ponderado"], color=BLUE)
    ax.bar_label(bars, labels=[brl(v) for v in latest["salario_medio_ponderado"]], padding=5, fontsize=9)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"R$ {x/1000:.0f} mil"))
    ax.grid(axis="x"); ax.set_axisbelow(True); ax.spines[["top", "right", "left"]].set_visible(False)
    title(ax, "Perfis com maior remuneração média", "Top 6 em 2025–2026; mínimo de 30 salários válidos")
    ax.set_xlim(0, latest["salario_medio_ponderado"].max() * 1.2)
    fig.subplots_adjust(left=0.38, bottom=0.08)
    save(fig, output, "04_remuneracao_perfis.png", dpi)


def chart_technology(df, output, dpi):
    latest = df[df["ano_pesquisa"] == YEARS[-1]].copy()
    # Mantém os percentuais calculados sobre o denominador original, mas não
    # trata respostas de ausência de preferência como se fossem tecnologias.
    non_technology = latest["tecnologia"].astype(str).str.lower().str.startswith("não")
    latest = latest[~non_technology]
    categories = ["Linguagem Preferida", "Ferramenta BI Preferida", "Cloud Preferida"]
    display_names = {
        "Amazon Web Services (AWS)": "AWS",
        "Google Cloud (GCP)": "Google Cloud",
        "Azure (Microsoft)": "Microsoft Azure",
        "Microsoft PowerBI": "Power BI",
        "Amazon Quicksight": "Amazon QuickSight",
    }
    fig, axes = plt.subplots(1, 3, figsize=(13.33, 7.5))
    for ax, category in zip(axes, categories):
        part = latest[latest["categoria"] == category].nlargest(5, "percentual_adocao").sort_values("percentual_adocao")
        labels = [fill(display_names.get(x, x), 18) for x in part["tecnologia"]]
        bars = ax.barh(labels, part["percentual_adocao"], color=TEAL)
        ax.bar_label(bars, labels=[pct(x) for x in part["percentual_adocao"]], padding=3, fontsize=8.5)
        ax.set_title(category.replace(" Preferida", ""), loc="left", fontsize=12, fontweight="bold")
        ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:.0f}%"))
        ax.grid(axis="x"); ax.set_axisbelow(True); ax.spines[["top", "right", "left"]].set_visible(False)
        ax.set_xlim(0, max(part["percentual_adocao"].max() * 1.18, 10))
    fig.suptitle("Tecnologias com maior adoção em 2025–2026", x=0.01, ha="left", fontsize=19,
                 fontweight="bold", color="#0F172A")
    fig.text(0.01, 0.925, "Top 5 por categoria; linguagens permitem múltiplas respostas", color=GRAY, fontsize=9)
    fig.subplots_adjust(left=0.1, right=0.98, top=0.82, bottom=0.1, wspace=0.55)
    save(fig, output, "05_tecnologias_top5.png", dpi)


def priority_bucket(text):
    text = str(text).lower()
    if "principal prioridade" in text:
        return "Principal prioridade"
    if "principais prioridades" in text:
        return "Entre as prioridades"
    if "mais ou menos" in text:
        return "Iniciativas isoladas"
    if "não é uma iniciativa" in text:
        return "Não é prioridade"
    return "Não sabe opinar"


def chart_ai_priority(df, output, dpi):
    df = df.copy(); df["categoria"] = df["ia_prioridade_empresa"].map(priority_bucket)
    pivot = df.pivot(index="categoria", columns="ano_pesquisa", values="percentual").reindex(
        ["Principal prioridade", "Entre as prioridades", "Iniciativas isoladas", "Não é prioridade", "Não sabe opinar"]
    )
    fig, ax = plt.subplots(figsize=(12, 6.75)); x=np.arange(len(pivot)); w=.24
    for i, year in enumerate(YEARS):
        bars=ax.bar(x+(i-1)*w,pivot[year],w,label=YEAR_LABELS[i],color=[LIGHT,"#94A3B8",BLUE][i])
        if i==2: ax.bar_label(bars,labels=[pct(v) for v in pivot[year]],padding=3,fontsize=8.5)
    ax.set_xticks(x,[fill(v,18) for v in pivot.index]); ax.yaxis.set_major_formatter(FuncFormatter(lambda x,_:f"{x:.0f}%"))
    ax.grid(axis="y"); ax.set_axisbelow(True); ax.spines[["top","right"]].set_visible(False)
    title(ax,"Prioridade de IA nas empresas","Distribuição entre respondentes válidos da pergunta")
    ax.legend(frameon=False,ncol=3); fig.subplots_adjust(bottom=.18)
    save(fig,output,"06_prioridade_ia.png",dpi)


def chart_ai_use(df, output, dpi):
    labels={
        "Utiliza soluções gratuitas":"Gratuitas",
        "Não utiliza IA generativa":"Não utiliza",
        "Utiliza solução do tipo Copilot":"Copilot",
        "Utiliza solução paga com recurso próprio":"Paga pelo profissional",
        "Utiliza solução paga pela empresa":"Paga pela empresa",
    }
    df=df.copy();df["categoria"]=df["uso_pessoal_ia"].map(labels)
    pivot=df.pivot(index="categoria",columns="ano_pesquisa",values="percentual").reindex(
        ["Não utiliza","Gratuitas","Copilot","Paga pelo profissional","Paga pela empresa"])
    fig,ax=plt.subplots(figsize=(12,6.75));x=np.arange(len(pivot));w=.24
    for i,year in enumerate(YEARS):
        bars=ax.bar(x+(i-1)*w,pivot[year],w,label=YEAR_LABELS[i],color=[LIGHT,"#94A3B8",BLUE][i])
        if i==2:ax.bar_label(bars,labels=[pct(v) for v in pivot[year]],padding=3,fontsize=8.5)
    ax.set_xticks(x,[fill(v,18) for v in pivot.index]);ax.yaxis.set_major_formatter(FuncFormatter(lambda x,_:f"{x:.0f}%"))
    ax.grid(axis="y");ax.set_axisbelow(True);ax.spines[["top","right"]].set_visible(False)
    title(ax,"Uso pessoal de soluções de IA","Pergunta multiseleção; percentuais não precisam somar 100%")
    ax.legend(frameon=False,ncol=3);fig.subplots_adjust(bottom=.18)
    save(fig,output,"07_uso_pessoal_ia.png",dpi)


def chart_work(df, output, dpi):
    latest=df[(df["ano_pesquisa"]==YEARS[-1]) & (df["modelo_trabalho_padronizado"]!="Não Informado")].copy()
    latest=latest.sort_values("percentual_modelo")
    fig,axes=plt.subplots(1,2,figsize=(12,6.75))
    labels=[fill(x,22) for x in latest["modelo_trabalho_padronizado"]]
    b=axes[0].barh(labels,latest["percentual_modelo"],color=BLUE)
    axes[0].bar_label(b,labels=[pct(v) for v in latest["percentual_modelo"]],padding=4)
    title(axes[0],"Distribuição dos modelos","Participação em 2025–2026")
    b=axes[1].barh(labels,latest["taxa_satisfacao_valida_pct"],color=ORANGE)
    axes[1].bar_label(b,labels=[pct(v) for v in latest["taxa_satisfacao_valida_pct"]],padding=4)
    title(axes[1],"Satisfação por modelo","Sobre respostas válidas em 2025–2026")
    for ax in axes:
        ax.xaxis.set_major_formatter(FuncFormatter(lambda x,_:f"{x:.0f}%"));ax.grid(axis="x");ax.set_axisbelow(True)
        ax.spines[["top","right","left"]].set_visible(False);ax.set_xlim(0,max(ax.get_xlim()[1],100 if ax is axes[1] else 45))
    fig.subplots_adjust(left=.15,wspace=.36,bottom=.1)
    save(fig,output,"08_modelos_trabalho_satisfacao.png",dpi)


def main():
    args=parse_args();args.output_dir.mkdir(parents=True,exist_ok=True);base_style()
    with tempfile.TemporaryDirectory() as temporary:
        root=resolve_input(args,temporary)
        data={p.name:load(root,p.name) for p in root.glob("*.csv")}
        chart_kpis(data["08_indicadores_executivos.csv"],args.output_dir,args.dpi)
        chart_region(data["02_distribuicao_regional.csv"],args.output_dir,args.dpi)
        chart_diversity(data["04_diversidade_genero.csv"],args.output_dir,args.dpi)
        chart_salary(data["03_remuneracao_senioridade.csv"],args.output_dir,args.dpi)
        chart_technology(data["05_tecnologias.csv"],args.output_dir,args.dpi)
        chart_ai_priority(data["06a_prioridade_ia.csv"],args.output_dir,args.dpi)
        chart_ai_use(data["06b_uso_pessoal_ia.csv"],args.output_dir,args.dpi)
        chart_work(data["07_modelos_trabalho.csv"],args.output_dir,args.dpi)
    print(f"8 gráficos gerados em: {args.output_dir.resolve()}")


if __name__=="__main__":
    main()
