# Relatório de Auditoria e Qualidade de Dados (Data Quality Report)

## Visão Geral da Auditoria
Este relatório documenta os testes de integridade, higienização, tipagem e reconciliação volumétrica realizados entre as 3 camadas do Data Lake (**Bronze ➔ Silver ➔ Gold**) para o projeto **State of Data Brazil (Tech Challenge Fase 3)**.

---

## 1. Reconciliação Volumétrica (Bronze ➔ Silver)

| Edição da Pesquisa | Registros Brutos (Bronze) | Registros Limpos (Silver) | Duplicatas Removidas | Status |
| :--- | :---: | :---: | :---: | :---: |
| **2023-2024** | 5,293 | 5,293 | 0 | ✅ Aprovado |
| **2024-2025** | 5,217 | 5,215 | 2 | ✅ Aprovado |
| **2025-2026** | 3,495 | 3,494 | 1 | ✅ Aprovado |
| **TOTAL** | **14,005** | **14,002** | **3** | ✅ Reconciliado |

> [!NOTE]
> A deduplicação foi executada considerando a chave composta `(ano_pesquisa, id_respondente)`. Para registros com ID nulo, foi gerado previamente um hash criptográfico SHA-256 (`id_registro_tecnico`) para evitar a eliminação inadvertida de respostas válidas distintas.

---

## 2. Integridade de Chaves Primárias e Unicidade

* **IDs Nulos após Tratamento**: `0` (Zero nulos)
* **IDs Únicos Consolidados**: `14,002`
* **Duplicidades Exatas Restantes**: `0` (Zero duplicatas)

---

## 3. Matriz de Completude da Camada Silver

| Campo Padronizado | Tipo Inferido | Registros Válidos | Completude (%) | Observação |
| :--- | :---: | :---: | :---: | :--- |
| `ano_pesquisa` | `string` | 14,002 | 100.0% | Partição da tabela |
| `id_respondente` | `string` | 14,002 | 100.0% | Chave primária |
| `genero` | `string` | 14,002 | 100.0% | Categoria demográfica |
| `regiao_mora` | `string` | 13,611 | 97.2% | Dimensão geográfica |
| `senioridade_padronizada` | `string` | 14,002 | 100.0% | Harmonizado em 4 níveis |
| `cargo_atual` | `string` | 10,173 | 72.7% | Nomenclatura profissional |
| `faixa_salarial` | `string` | 12,841 | 91.7% | Dimensão canônica original |
| `salario_medio_estimado` | `float64` | 12,841 | 91.7% | Métrica contínua estimada |
| `modelo_trabalho_padronizado` | `string` | 14,002 | 100.0% | Remoto, Híbrido, Presencial |
| `satisfeito_empresa_bool` | `boolean` | 12,841 | 91.7% | Respostas booleanas válidas |

---

## 4. Reconciliação com a Camada Gold (Data Marts)

| Tabela Gold | Registros Gerados | Eixo Analítico Atendido |
| :--- | :---: | :--- |
| `gold_perfil_mercado.parquet` | 253 | Demografia, região e escolaridade |
| `gold_remuneracao_senioridade.parquet` | 675 | Salários por cargo, senioridade e região |
| `gold_diversidade.parquet` | 97 | Gênero, raça/etnia e liderança |
| `gold_tecnologias.parquet` | 368 | Linguagens, Cloud e BI (desaninhadas) |
| `gold_adocao_ia.parquet` | 213 | Prioridade empresarial e uso individual de IA |
| `gold_modelos_trabalho.parquet` | 90 | Modelo de trabalho e índice de satisfação |
| `gold_indicadores_executivos.parquet` | 18 | Resumo consolidado de KPIs estratégicos |

---

## 5. Conclusão da Auditoria
Todos os testes de integridade foram executados com **100% de conformidade**. A base de dados estruturada na camada **Silver** e os Data Marts na camada **Gold** estão validados e prontos para consultas analíticas no Amazon Athena e geração do material executivo.
