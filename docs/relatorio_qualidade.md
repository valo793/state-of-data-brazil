# Relatório de Auditoria e Qualidade de Dados (Data Quality Gate)

## Visão Geral da Auditoria
Este relatório documenta os testes de integridade, higienização, tipagem e reconciliação volumétrica com critérios explícitos de asserção (*Quality Gate Rules*) entre as 3 camadas do Data Lake (**Bronze ➔ Silver ➔ Gold**) para o projeto **State of Data Brazil (Tech Challenge Fase 3)**.

---

## 1. Quality Gate: Resultados dos Testes de Asserção

| Teste de Integridade | Critério de Aceite / Limiar | Resultado da Execução |
| :--- | :---: | :---: |
| `Reconciliação Volumétrica` | `total_silver <= total_bronze` | ✅ Aprovado |
| `Zero IDs Nulos` | `null_ids == 0` | ✅ Aprovado |
| `Zero Duplicidades` | `dups == 0` | ✅ Aprovado |
| `Completude genero` | `>= 95%` | ✅ Aprovado |
| `Completude regiao_mora` | `>= 90%` | ✅ Aprovado |
| `Completude senioridade_padronizada` | `>= 95%` | ✅ Aprovado |
| `Completude faixa_salarial` | `>= 85%` | ✅ Aprovado |
| `Completude salario_medio_estimado` | `>= 85%` | ✅ Aprovado |
| `Completude modelo_trabalho_padronizado` | `>= 95%` | ✅ Aprovado |
| `Data Mart gold_adocao_ia` | `count > 0` | ✅ Aprovado |
| `Data Mart gold_diversidade` | `count > 0` | ✅ Aprovado |
| `Data Mart gold_indicadores_executivos` | `count > 0` | ✅ Aprovado |
| `Data Mart gold_modelos_trabalho` | `count > 0` | ✅ Aprovado |
| `Data Mart gold_perfil_mercado` | `count > 0` | ✅ Aprovado |
| `Data Mart gold_remuneracao_senioridade` | `count > 0` | ✅ Aprovado |
| `Data Mart gold_tecnologias` | `count > 0` | ✅ Aprovado |

---

## 2. Reconciliação Volumétrica Detalhada (Bronze ➔ Silver)

| Edição da Pesquisa | Registros Brutos (Bronze) | Registros Limpos (Silver) | Duplicatas Removidas | Status |
| :--- | :---: | :---: | :---: | :---: |
| **2023-2024** | 5,293 | 5,293 | 0 | ✅ Aprovado |
| **2024-2025** | 5,217 | 5,215 | 2 | ✅ Aprovado |
| **2025-2026** | 3,495 | 3,494 | 1 | ✅ Aprovado |
| **TOTAL** | **14,005** | **14,002** | **3** | ✅ Reconciliado |

> [!NOTE]
> A deduplicação foi executada considerando a chave composta `(ano_pesquisa, id_respondente)`. Para registros com ID nulo, foi gerado previamente um hash criptográfico SHA-256 (`id_registro_tecnico`) para evitar a eliminação inadvertida de respostas válidas distintas.

---

## 3. Integridade de Chaves Primárias

* **IDs Nulos após Tratamento**: `0` (Zero nulos — Regra: `assert null_ids == 0`)
* **IDs Únicos Consolidados**: `14,002`
* **Duplicidades Exatas Restantes**: `0` (Zero duplicatas — Regra: `assert dups == 0`)

---

## 4. Matriz de Completude e Limiares

| Campo Padronizado | Tipo Inferido | Registros Válidos | Completude Real | Limiar Mínimo | Status |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `genero` | `string` | 14,002 | 100.0% | >= 95.0% | ✅ Aprovado |
| `regiao_mora` | `string` | 13,611 | 97.2% | >= 90.0% | ✅ Aprovado |
| `senioridade_padronizada` | `string` | 14,002 | 100.0% | >= 95.0% | ✅ Aprovado |
| `faixa_salarial` | `string` | 12,841 | 91.7% | >= 85.0% | ✅ Aprovado |
| `salario_medio_estimado` | `float64` | 12,841 | 91.7% | >= 85.0% | ✅ Aprovado |
| `modelo_trabalho_padronizado` | `string` | 14,002 | 100.0% | >= 95.0% | ✅ Aprovado |

---

## 5. Reconciliação com a Camada Gold (Data Marts)

| Tabela Gold | Registros Gerados | Eixo Analítico Atendido | Status |
| :--- | :---: | :--- | :---: |
| `gold_perfil_mercado.parquet` | 253 | Demografia, região e escolaridade | ✅ Validado |
| `gold_remuneracao_senioridade.parquet` | 675 | Salários por cargo, senioridade e região | ✅ Validado |
| `gold_diversidade.parquet` | 97 | Gênero, raça/etnia e liderança | ✅ Validado |
| `gold_tecnologias.parquet` | 368 | Linguagens, Cloud e BI (desaninhadas) | ✅ Validado |
| `gold_adocao_ia.parquet` | 213 | Prioridade empresarial e uso individual de IA | ✅ Validado |
| `gold_modelos_trabalho.parquet` | 90 | Modelo de trabalho e índice de satisfação | ✅ Validado |
| `gold_indicadores_executivos.parquet` | 18 | Resumo consolidado de KPIs estratégicos | ✅ Validado |

---

## 6. Conclusão da Auditoria
Todos os **16 testes de asserção** foram executados com **sucesso e conformidade estrita**. A base de dados estruturada na camada **Silver** e os Data Marts na camada **Gold** estão auditados e certificados para consumo no Amazon Athena e elaboração do Material Executivo.
