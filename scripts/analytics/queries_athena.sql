-- =============================================================================
-- Tech Challenge Fase 3 — Consultas Analíticas no Amazon Athena
-- =============================================================================
-- Database: tech_challenge_3_db
-- Camada: Gold (Parquet catalogado via AWS Glue Data Catalog)
--
-- Estas consultas respondem diretamente às 7 perguntas estratégicas de negócio
-- solicitadas no enunciado do Tech Challenge para a Instituição Financeira.
-- =============================================================================


-- =============================================================================
-- 1. Como está estruturado o mercado brasileiro de Dados?
-- =============================================================================

-- 1.1 Volume total de respondentes e evolução temporal
SELECT 
    ano_pesquisa,
    SUM(total_respondentes) AS total_respondentes,
    ROUND(AVG(media_idade), 1) AS media_idade_geral
FROM tech_challenge_3_db.gold_perfil_mercado
GROUP BY ano_pesquisa
ORDER BY ano_pesquisa;

-- 1.2 Distribuição geográfica por Região
SELECT 
    ano_pesquisa,
    COALESCE(regiao_mora, 'Não Informado') AS regiao,
    SUM(total_respondentes) AS total_respondentes,
    ROUND(SUM(total_respondentes) * 100.0 / SUM(SUM(total_respondentes)) OVER (PARTITION BY ano_pesquisa), 2) AS percentual_regiao
FROM tech_challenge_3_db.gold_perfil_mercado
GROUP BY ano_pesquisa, regiao_mora
ORDER BY ano_pesquisa, percentual_regiao DESC;

-- 1.3 Nível de Instrução / Escolaridade
SELECT 
    ano_pesquisa,
    COALESCE(nivel_ensino, 'Não Informado') AS nivel_ensino,
    SUM(total_respondentes) AS total,
    ROUND(SUM(total_respondentes) * 100.0 / SUM(SUM(total_respondentes)) OVER (PARTITION BY ano_pesquisa), 2) AS percentual
FROM tech_challenge_3_db.gold_perfil_mercado
GROUP BY ano_pesquisa, nivel_ensino
ORDER BY ano_pesquisa, percentual DESC;


-- =============================================================================
-- 2. Quais perfis profissionais são mais valorizados pelo mercado?
-- =============================================================================

-- 2.1 Remuneração Média e Mediana por Cargo e Senioridade
SELECT 
    ano_pesquisa,
    cargo_atual,
    senioridade_padronizada,
    SUM(total_profissionais) AS total_profissionais,
    ROUND(AVG(salario_medio), 2) AS salario_medio_estimado,
    ROUND(AVG(salario_mediano), 2) AS salario_mediano_estimado
FROM tech_challenge_3_db.gold_remuneracao_senioridade
WHERE cargo_atual IS NOT NULL
GROUP BY ano_pesquisa, cargo_atual, senioridade_padronizada
ORDER BY ano_pesquisa, salario_medio_estimado DESC;

-- 2.2 Top 5 Cargos com Maior Média Salarial no Nível Sênior
SELECT 
    cargo_atual,
    ROUND(AVG(salario_medio), 2) AS media_salarial_senior,
    SUM(total_profissionais) AS volume_amostra
FROM tech_challenge_3_db.gold_remuneracao_senioridade
WHERE senioridade_padronizada = 'Sênior'
GROUP BY cargo_atual
ORDER BY media_salarial_senior DESC
LIMIT 5;


-- =============================================================================
-- 3. Qual é o cenário de diversidade de gênero nas carreiras de dados?
-- =============================================================================

-- 3.1 Proporção de Gênero por Ano
SELECT 
    ano_pesquisa,
    COALESCE(genero, 'Não Informado') AS genero,
    SUM(total) AS total_profissionais,
    ROUND(SUM(total) * 100.0 / SUM(SUM(total)) OVER (PARTITION BY ano_pesquisa), 2) AS percentual_genero,
    ROUND(AVG(salario_medio), 2) AS salario_medio_estimado
FROM tech_challenge_3_db.gold_diversidade
GROUP BY ano_pesquisa, genero
ORDER BY ano_pesquisa, total_profissionais DESC;

-- 3.2 Representatividade Feminina em Posições de Liderança / Gestão
SELECT 
    ano_pesquisa,
    genero,
    is_gestor,
    SUM(total) AS total,
    ROUND(SUM(total) * 100.0 / SUM(SUM(total)) OVER (PARTITION BY ano_pesquisa, is_gestor), 2) AS percentual_no_grupo
FROM tech_challenge_3_db.gold_diversidade
WHERE genero IN ('Feminino', 'Masculino') AND is_gestor IS NOT NULL
GROUP BY ano_pesquisa, genero, is_gestor
ORDER BY ano_pesquisa, is_gestor, genero;


-- =============================================================================
-- 4. Quais tecnologias apresentam maior adoção entre os profissionais?
-- =============================================================================

-- 4.1 Provedores de Cloud Preferidos
SELECT 
    ano_pesquisa,
    COALESCE(cloud_preferida, 'Sem Preferência/Não Utiliza') AS cloud,
    SUM(total_usuarios) AS total_usuarios,
    ROUND(SUM(total_usuarios) * 100.0 / SUM(SUM(total_usuarios)) OVER (PARTITION BY ano_pesquisa), 2) AS percentual
FROM tech_challenge_3_db.gold_tecnologias_cloud
WHERE cloud_preferida IS NOT NULL
GROUP BY ano_pesquisa, cloud_preferida
ORDER BY ano_pesquisa, percentual DESC;

-- 4.2 Ferramentas de BI Preferidas
SELECT 
    ano_pesquisa,
    COALESCE(bi_preferido, 'Sem Preferência/Não Utiliza') AS ferramenta_bi,
    SUM(total_usuarios) AS total_usuarios,
    ROUND(SUM(total_usuarios) * 100.0 / SUM(SUM(total_usuarios)) OVER (PARTITION BY ano_pesquisa), 2) AS percentual
FROM tech_challenge_3_db.gold_tecnologias_cloud
WHERE bi_preferido IS NOT NULL
GROUP BY ano_pesquisa, bi_preferido
ORDER BY ano_pesquisa, percentual DESC;


-- =============================================================================
-- 5. Qual é o índice de adoção de Inteligência Artificial e seu impacto?
-- =============================================================================

-- 5.1 Prioridade de IA / GenAI nas Empresas
SELECT 
    ano_pesquisa,
    COALESCE(ia_prioridade_empresa, 'Não informado / Não sei opinar') AS status_prioridade_ia,
    SUM(total_respostas) AS total_respostas,
    ROUND(SUM(total_respostas) * 100.0 / SUM(SUM(total_respostas)) OVER (PARTITION BY ano_pesquisa), 2) AS percentual
FROM tech_challenge_3_db.gold_adocao_ia
GROUP BY ano_pesquisa, ia_prioridade_empresa
ORDER BY ano_pesquisa, percentual DESC;

-- 5.2 Uso Pessoal de Ferramentas de Produtividade (ChatGPT / Copilot)
SELECT 
    ano_pesquisa,
    COALESCE(uso_pessoal_ia, 'Não informado') AS tipo_uso_pessoal,
    SUM(total_respostas) AS total,
    ROUND(SUM(total_respostas) * 100.0 / SUM(SUM(total_respostas)) OVER (PARTITION BY ano_pesquisa), 2) AS percentual
FROM tech_challenge_3_db.gold_adocao_ia
GROUP BY ano_pesquisa, uso_pessoal_ia
ORDER BY ano_pesquisa, percentual DESC;


-- =============================================================================
-- 6. Diferenças entre regiões, senioridades e modelos de trabalho
-- =============================================================================

-- 6.1 Distribuição por Modelo de Trabalho e Taxa de Satisfação
SELECT 
    ano_pesquisa,
    modelo_trabalho_padronizado,
    SUM(total_respondentes) AS total_profissionais,
    ROUND(SUM(total_respondentes) * 100.0 / SUM(SUM(total_respondentes)) OVER (PARTITION BY ano_pesquisa), 2) AS percentual_modelo,
    ROUND(SUM(total_satisfeitos) * 100.0 / SUM(total_respondentes), 2) AS taxa_satisfacao_pct,
    ROUND(AVG(salario_medio), 2) AS salario_medio_estimado
FROM tech_challenge_3_db.gold_modelos_trabalho
GROUP BY ano_pesquisa, modelo_trabalho_padronizado
ORDER BY ano_pesquisa, total_profissionais DESC;

-- 6.2 Variação Salarial Regional
SELECT 
    ano_pesquisa,
    regiao_mora,
    ROUND(AVG(salario_medio), 2) AS media_salarial_regional,
    SUM(total_respondentes) AS amostra
FROM tech_challenge_3_db.gold_modelos_trabalho
WHERE regiao_mora IS NOT NULL
GROUP BY ano_pesquisa, regiao_mora
ORDER BY ano_pesquisa, media_salarial_regional DESC;


-- =============================================================================
-- 7. Quais oportunidades e desafios para investimentos em Dados e IA?
-- =============================================================================
-- Síntese de Indicadores Estratégicos para Instituição Financeira
SELECT 
    'Satisfação Geral' AS dimensao,
    ROUND(SUM(total_satisfeitos) * 100.0 / SUM(total_respondentes), 2) AS valor_indicador,
    '% de profissionais satisfeitos no emprego atual' AS descricao
FROM tech_challenge_3_db.gold_modelos_trabalho
WHERE ano_pesquisa = '2025-2026'

UNION ALL

SELECT 
    'Adoção Remota/Híbrida' AS dimensao,
    ROUND(SUM(CASE WHEN modelo_trabalho_padronizado IN ('100% Remoto', 'Híbrido Flexível', 'Híbrido Dias Fixos') THEN total_respondentes ELSE 0 END) * 100.0 / SUM(total_respondentes), 2) AS valor_indicador,
    '% de profissionais em modelos flexíveis (atração de talentos fora do Sudeste)' AS descricao
FROM tech_challenge_3_db.gold_modelos_trabalho
WHERE ano_pesquisa = '2025-2026';
