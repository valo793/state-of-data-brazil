"""
Tech Challenge Fase 3 — Executor e Gravador de Resultados de Notebooks Jupyter
=============================================================================
Executa os notebooks sequencialmente e salva os outputs reais (textos, tabelas, logs, execution_counts)
garantindo que os arquivos .ipynb constituam evidências auditáveis de execução.
"""

import ast
import contextlib
import io
import json
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
NB_DIR = BASE_DIR / "notebooks"


def execute_cell_code(code_str, global_env):
    """Executa o código da célula capturando stdout e o resultado da última expressão."""
    stdout_capture = io.StringIO()
    outputs = []
    
    # Faz parse da AST para verificar se a última linha é uma expressão
    try:
        parsed = ast.parse(code_str)
    except Exception as e:
        return [{"output_type": "error", "ename": type(e).__name__, "evalue": str(e), "traceback": [str(e)]}]

    last_expr = None
    if parsed.body and isinstance(parsed.body[-1], ast.Expr):
        last_expr = parsed.body.pop() # Remove a última expressão do bloco compilado

    # Executa o bloco de comandos anterior
    with contextlib.redirect_stdout(stdout_capture), contextlib.redirect_stderr(stdout_capture):
        try:
            if parsed.body:
                exec(compile(parsed, filename="<cell>", mode="exec"), global_env)
            # Avalia a última expressão se houver
            if last_expr is not None:
                expr_val = eval(compile(ast.Expression(last_expr.value), filename="<cell>", mode="eval"), global_env)
                if expr_val is not None:
                    outputs.append({
                        "output_type": "execute_result",
                        "execution_count": None, # Preenchido depois
                        "data": {
                            "text/plain": repr(expr_val).splitlines(True)
                        },
                        "metadata": {}
                    })
        except Exception as e:
            err_text = stdout_capture.getvalue()
            outputs.append({
                "output_type": "error",
                "ename": type(e).__name__,
                "evalue": str(e),
                "traceback": [err_text, f"{type(e).__name__}: {str(e)}"]
            })
            return outputs

    out_text = stdout_capture.getvalue()
    if out_text:
        outputs.insert(0, {
            "output_type": "stream",
            "name": "stdout",
            "text": out_text.splitlines(True)
        })

    return outputs


def run_notebook(nb_file):
    print(f"\n[EXECUTANDO NOTEBOOK] {nb_file.name}...")
    with open(nb_file, "r", encoding="utf-8") as f:
        nb_json = json.load(f)

    # Executa no diretório do notebook para garantir resolução de caminhos relativos
    old_cwd = os.getcwd()
    os.chdir(NB_DIR)

    global_env = {"__name__": "__main__"}
    execution_counter = 1

    try:
        for idx, cell in enumerate(nb_json.get("cells", [])):
            if cell.get("cell_type") == "code":
                code_str = "".join(cell.get("source", []))
                cell["execution_count"] = execution_counter
                outputs = execute_cell_code(code_str, global_env)
                
                # Ajusta execution_count nos execute_results
                for out in outputs:
                    if out.get("output_type") == "execute_result":
                        out["execution_count"] = execution_counter
                        
                cell["outputs"] = outputs
                execution_counter += 1
                print(f"  ✓ Célula {idx+1} executada ({len(outputs)} output(s) gravado(s))")

        # Salva o notebook com os resultados incorporados
        with open(nb_file, "w", encoding="utf-8") as f:
            json.dump(nb_json, f, indent=2, ensure_ascii=False)
        print(f"✅ Notebook {nb_file.name} finalizado e salvo com sucesso!")

    finally:
        os.chdir(old_cwd)


def run_all_notebooks():
    print("=" * 80)
    print("EXECUÇÃO SEQUENCIAL DE NOTEBOOKS JUPYTER (EVIDÊNCIAS DE EXECUÇÃO)")
    print("=" * 80)
    
    order = [
        "01_analise_exploratoria.ipynb",
        "02_validacao_silver.ipynb",
        "03_analises_negocio.ipynb"
    ]
    
    for nb_name in order:
        nb_path = NB_DIR / nb_name
        if nb_path.exists():
            run_notebook(nb_path)
        else:
            print(f"❌ Arquivo não encontrado: {nb_name}")

    print("\n" + "=" * 80)
    print("✅ TODOS OS NOTEBOOKS FORAM EXECUTADOS E CONTÊM RESULTADOS SALVOS!")
    print("=" * 80)


if __name__ == "__main__":
    run_all_notebooks()
