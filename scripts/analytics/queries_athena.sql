-- =============================================================================
-- Tech Challenge Fase 3 — Consultas Analíticas no Amazon Athena
-- =============================================================================
-- Database: db_state_of_data
-- Camada: Gold (Parquet catalogado via AWS Glue Data Catalog)
--
-- Estas consultas respondem rigorosamente às 7 perguntas estratégicas de negócio
-- solicitadas no enunciado do Tech Challenge para a Instituição Financeira.
--
-- NOTA METODOLÓGICA:
-- Para evitar o viés estatístico de "média de médias", todas as agregações
-- calculam a média salarial sobre o número de salários válidos:
-- SUM(soma_salarios) / NULLIF(SUM(total_salarios_validos), 0)
-- =============================================================================


-- =============================================================================
-- 1. Como está estruturado o mercado brasileiro de Dados?
-- =============================================================================

-- 1.1 Volume total de respondentes e evolução temporal
SELECT 
    ano_pesquisa,
    SUM(total_respondentes) AS total_respondentes,
    ROUND(SUM(media_idade * total_respondentes) / NULLIF(SUM(total_respondentes), 0), 1) AS media_idade_ponderada
FROM db_state_of_data.gold_perfil_mercado
GROUP BY ano_pesquisa
ORDER BY ano_pesquisa;

-- 1.2 Distribuição geográfica por Região (%)
SELECT 
    ano_pesquisa,
    COALESCE(regiao_mora, 'Não Informado') AS regiao,
    SUM(total_respondentes) AS total_respondentes,
    ROUND(SUM(total_respondentes) * 100.0 / SUM(SUM(total_respondentes)) OVER (PARTITION BY ano_pesquisa), 2) AS percentual_regiao
FROM db_state_of_data.gold_perfil_mercado
GROUP BY ano_pesquisa, regiao_mora
ORDER BY ano_pesquisa, percentual_regiao DESC;

-- 1.3 Nível de Instrução / Escolaridade (%)
SELECT 
    ano_pesquisa,
    COALESCE(nivel_ensino, 'Não Informado') AS nivel_ensino,
    SUM(total_respondentes) AS total,
    ROUND(SUM(total_respondentes) * 100.0 / SUM(SUM(total_respondentes)) OVER (PARTITION BY ano_pesquisa), 2) AS percentual
FROM db_state_of_data.gold_perfil_mercado
GROUP BY ano_pesquisa, nivel_ensino
ORDER BY ano_pesquisa, percentual DESC;


-- =============================================================================
-- 2. Quais perfis profissionais são mais valorizados pelo mercado?
-- =============================================================================

-- 2.1 Remuneração Média Ponderada por Cargo e Senioridade
SELECT 
    ano_pesquisa,
    cargo_atual,
    senioridade_padronizada,
    SUM(total_profissionais) AS total_profissionais,
    ROUND(SUM(soma_salarios) / NULLIF(SUM(total_salarios_validos), 0), 2) AS salario_medio_ponderado,
    MIN(salario_min) AS salario_min_faixa,
    MAX(salario_max) AS salario_max_faixa
FROM db_state_of_data.gold_remuneracao_senioridade
WHERE cargo_atual IS NOT NULL
GROUP BY ano_pesquisa, cargo_atual, senioridade_padronizada
HAVING SUM(total_salarios_validos) >= 30
ORDER BY ano_pesquisa, salario_medio_ponderado DESC;

-- 2.2 Top 5 Cargos com Maior Média Salarial Ponderada no Nível Sênior
SELECT 
    cargo_atual,
    SUM(total_salarios_validos) AS volume_amostra,
    ROUND(SUM(soma_salarios) / NULLIF(SUM(total_salarios_validos), 0), 2) AS media_salarial_ponderada_senior
FROM db_state_of_data.gold_remuneracao_senioridade
WHERE senioridade_padronizada = 'Sênior'
GROUP BY cargo_atual
HAVING SUM(total_salarios_validos) >= 30
ORDER BY media_salarial_ponderada_senior DESC
LIMIT 5;


-- =============================================================================
-- 3. Qual é o cenário de diversidade de gênero nas carreiras de dados?
-- =============================================================================

-- 3.1 Proporção de Gênero por Ano e Média Salarial Ponderada
SELECT 
    ano_pesquisa,
    COALESCE(genero, 'Não Informado') AS genero,
    SUM(total) AS total_profissionais,
    ROUND(SUM(total) * 100.0 / SUM(SUM(total)) OVER (PARTITION BY ano_pesquisa), 2) AS percentual_genero,
    ROUND(SUM(soma_salarios) / NULLIF(SUM(total_salarios_validos), 0), 2) AS salario_medio_ponderado
FROM db_state_of_data.gold_diversidade
GROUP BY ano_pesquisa, genero
ORDER BY ano_pesquisa, total_profissionais DESC;

-- 3.2 Representatividade Feminina em Posições de Liderança / Gestão
SELECT 
    ano_pesquisa,
    genero,
    is_gestor,
    SUM(total) AS total_no_segmento,
    ROUND(SUM(total) * 100.0 / SUM(SUM(total)) OVER (PARTITION BY ano_pesquisa, is_gestor), 2) AS percentual_no_grupo
FROM db_state_of_data.gold_diversidade
WHERE genero IN ('Feminino', 'Masculino') AND is_gestor IS NOT NULL
GROUP BY ano_pesquisa, genero, is_gestor
ORDER BY ano_pesquisa, is_gestor, genero;


-- =============================================================================
-- 4. Quais tecnologias apresentam maior adoção entre os profissionais?
-- =============================================================================

-- 4.1 Provedores de Cloud Preferidos (Amostra Desaninhada de Usuários Únicos)
SELECT 
    ano_pesquisa,
    tecnologia AS provedor_cloud,
    total_usuarios,
    total_respondentes_validos_categoria,
    percentual_adocao AS percentual_adotantes
FROM db_state_of_data.gold_tecnologias
WHERE categoria = 'Cloud Preferida'
ORDER BY ano_pesquisa, total_usuarios DESC;

-- 4.2 Ferramentas de BI Preferidas (Amostra Desaninhada)
SELECT 
    ano_pesquisa,
    tecnologia AS ferramenta_bi,
    total_usuarios,
    total_respondentes_validos_categoria,
    percentual_adocao AS percentual_adotantes
FROM db_state_of_data.gold_tecnologias
WHERE categoria = 'Ferramenta BI Preferida'
ORDER BY ano_pesquisa, total_usuarios DESC;

-- 4.3 Linguagens de Programação Preferidas
SELECT 
    ano_pesquisa,
    tecnologia AS linguagem,
    total_usuarios,
    total_respondentes_validos_categoria,
    percentual_adocao AS percentual_adotantes
FROM db_state_of_data.gold_tecnologias
WHERE categoria = 'Linguagem Preferida'
ORDER BY ano_pesquisa, total_usuarios DESC;


-- =============================================================================
-- 5. Qual é o índice de adoção de Inteligência Artificial e seu impacto?
-- =============================================================================

-- 5.1 Prioridade de IA / GenAI nas Empresas
SELECT 
    ano_pesquisa,
    resposta_padronizada AS status_prioridade_ia,
    total_respostas,
    total_respondentes_validos,
    percentual
FROM db_state_of_data.gold_adocao_ia
WHERE tipo_indicador = 'Prioridade empresarial'
ORDER BY ano_pesquisa, percentual DESC;

-- 5.2 Uso Pessoal de Ferramentas de Produtividade (ChatGPT / Copilots)
-- Pergunta multiseleção: a soma dos percentuais pode ultrapassar 100%.
SELECT 
    ano_pesquisa,
    resposta_padronizada AS tipo_uso_pessoal,
    total_respostas,
    total_respondentes_validos,
    percentual
FROM db_state_of_data.gold_adocao_ia
WHERE tipo_indicador = 'Uso pessoal'
ORDER BY ano_pesquisa, percentual DESC;


-- =============================================================================
-- 6. Diferenças entre regiões, senioridades e modelos de trabalho
-- =============================================================================

-- 6.1 Distribuição por Modelo de Trabalho e Taxa de Satisfação sobre Respostas Válidas
SELECT 
    ano_pesquisa,
    modelo_trabalho_padronizado,
    SUM(total_respondentes) AS total_profissionais,
    ROUND(SUM(total_respondentes) * 100.0 / SUM(SUM(total_respondentes)) OVER (PARTITION BY ano_pesquisa), 2) AS percentual_modelo,
    SUM(total_respostas_validas) AS total_respostas_validas,
    ROUND(SUM(total_satisfeitos) * 100.0 / NULLIF(SUM(total_respostas_validas), 0), 2) AS taxa_satisfacao_valida_pct,
    ROUND(SUM(soma_salarios) / NULLIF(SUM(total_salarios_validos), 0), 2) AS salario_medio_ponderado
FROM db_state_of_data.gold_modelos_trabalho
GROUP BY ano_pesquisa, modelo_trabalho_padronizado
ORDER BY ano_pesquisa, total_profissionais DESC;

-- 6.2 Variação Salarial Regional Ponderada
SELECT 
    ano_pesquisa,
    regiao_mora,
    SUM(total_salarios_validos) AS total_amostra,
    ROUND(SUM(soma_salarios) / NULLIF(SUM(total_salarios_validos), 0), 2) AS media_salarial_regional_ponderada
FROM db_state_of_data.gold_modelos_trabalho
WHERE regiao_mora IS NOT NULL
GROUP BY ano_pesquisa, regiao_mora
ORDER BY ano_pesquisa, media_salarial_regional_ponderada DESC;


-- =============================================================================
-- 7. Resumo Consolidado de KPIs para Apresentação Executiva
-- =============================================================================
SELECT 
    ano_pesquisa,
    total_respondentes,
    pct_feminino AS "Participação Feminina (%)",
    pct_sudeste AS "Concentração Sudeste (%)",
    taxa_satisfacao_geral AS "Satisfação no Trabalho (%)",
    pct_remoto AS "Trabalho 100% Remoto (%)",
    media_salarial_geral AS "Média Salarial Estimada (R$)"
FROM db_state_of_data.gold_indicadores_executivos
ORDER BY ano_pesquisa;
