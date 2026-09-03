# Mapeamento e Harmonização entre as Edições da Pesquisa

Este documento detalha o mapeamento das variáveis originais das três edições analisadas (**2023-2024**, **2024-2025** e **2025-2026**) da pesquisa State of Data Brasil.

---

## 1. Desafio de Heterogeneidade de Esquemas

* **Edição 2023-2024**: Utiliza cabeçalhos em formato de tupla-string Python, ex: `('P1_a ', 'Idade')`. A chave primária é o código P (`P1_a`), acompanhado da descrição da pergunta.
* **Edições 2024-2025 e 2025-2026**: Utilizam cabeçalhos hierárquicos com numeração de seção por ponto, ex: `1.a_idade`, `2.r_modelo_de_trabalho_atual`.

---

## 2. Matriz de Correspondência de Colunas

| Coluna Canônica (Silver) | Código 2023-2024 | Nome 2024-2025 | Nome 2025-2026 | Tipo Canônico |
| :--- | :--- | :--- | :--- | :---: |
| `id_respondente` | `P0` | `0.a_token` | `0.a_token` | `STRING` |
| `idade` | `P1_a` | `1.a_idade` | `1.a_idade` | `INTEGER` |
| `faixa_idade` | `P1_a_1` | `1.a.1_faixa_idade` | `1.a.1_faixa_idade` | `STRING` |
| `genero` | `P1_b` | `1.b_genero` | `1.b_genero` | `STRING` |
| `cor_raca_etnia` | `P1_c` | `1.c_cor/raca/etnia` | `1.c_cor/raca/etnia` | `STRING` |
| `pcd` | `P1_d` | `1.d_pcd` | `1.d_pcd` | `STRING` |
| `uf_mora` | `P1_i_1` | `1.i.1_uf_onde_mora` | `1.i.1_uf_onde_mora` | `STRING` |
| `regiao_mora` | `P1_i_2` | `1.i.2_regiao_onde_mora` | `1.i.2_regiao_onde_mora` | `STRING` |
| `nivel_ensino` | `P1_l` | `1.l_nivel_de_ensino` | `1.l_nivel_de_ensino` | `STRING` |
| `area_formacao` | `P1_m` | `1.m_area_de_formacao` | `1.m_area_de_formacao` | `STRING` |
| `situacao_trabalho` | `P2_a` | `2.a_situacao_atual` | `2.a_situacao_atual` | `STRING` |
| `setor` | `P2_b` | `2.b_setor` | `2.b_setor` | `STRING` |
| `tamanho_empresa` | `P2_c` | `2.c_numero_de_funcionarios`| `2.c_numero_de_funcionarios`| `STRING` |
| `is_gestor` | `P2_d` | `2.d_gestor` | `2.d_gestor` | `STRING` |
| `cargo_gestor` | `P2_e` | `2.e_cargo_como_gestor` | `2.e_cargo_como_gestor` | `STRING` |
| `cargo_atual` | `P2_f` | `2.f_cargo_atual` | `2.f_cargo_atual` | `STRING` |
| `senioridade` | `P2_g` | `2.g_nivel` | `2.g_nivel` | `STRING` |
| `faixa_salarial` | `P2_h` | `2.h_faixa_salarial` | `2.h_faixa_salarial` | `STRING` |
| `tempo_experiencia_dados` | `P2_i` | `2.i_tempo_de_experiencia_em_dados` | `2.i_tempo_de_experiencia_em_dados` | `STRING` |
| `tempo_experiencia_ti` | `P2_j` | `2.j_tempo_de_experiencia_em_ti` | `2.j_tempo_de_experiencia_em_ti` | `STRING` |
| `satisfeito_empresa` | `P2_k` | `2.k_satisfeito_atualmente` | `2.k_satisfeito_atualmente` | `STRING` |
| `motivo_insatisfacao` | `P2_l` | `2.l_motivo_insatisfacao` | `2.l_motivo_insatisfacao` | `STRING` |
| `modelo_trabalho` | `P2_r` | `2.r_modelo_de_trabalho_atual` | `2.q_modelo_de_trabalho_atual` | `STRING` |
| `linguagem_mais_usada` | `P4_e` | `4.e_linguagem_mais_utilizada` | `4.b_linguagem_mais_utilizada` | `STRING` |
| `linguagem_preferida` | `P4_f` | `4.f_linguagem_preferida` | `4.c_linguagem_preferida` | `STRING` |
| `cloud_preferida` | `P4_i` | `4.i_cloud_preferida` | `4.f_cloud_preferida` | `STRING` |
| `bi_preferido` | `P4_k` | `4.k_ferramenta_de_bi_preferida` | `4.h_ferramenta_de_bi_preferida` | `STRING` |
| `ia_prioridade_empresa`| `P3_e` | `3.e_ai_generativa_e_llm_é_uma_prioridade?` | `3.e_ai_generativa_e_llm_é_uma_prioridade?` | `STRING` |
| `tipo_uso_ia_empresa` | `P4_l` | `3.f_tipo_de_uso_de_ai_generativa_e_llm_na_empresa` | `3.f_tipo_de_uso_de_ai_generativa_e_llm_na_empresa` | `STRING` |
| `uso_pessoal_ia` | `P4_m` | `4.m_usa_chatgpt_ou_copilot_no_trabalho?` | `4.j_usa_chatgpt_ou_copilot_no_trabalho?` | `STRING` |

---

## 3. Arquivo de Configuração Centralizado
Para garantir rastreabilidade, auditoria e facilidade de manutenção, todas as correspondências acima estão formalizadas em formato JSON no arquivo:
👉 [`config/mapeamento_colunas.json`](../config/mapeamento_colunas.json)
