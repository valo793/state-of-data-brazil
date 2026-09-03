# Dicionário de Dados — State of Data Brazil Data Lake

Este documento define o catálogo e a semântica das variáveis estruturadas na Camada Silver (`state_of_data_silver`) e nas tabelas da Camada Gold do Data Lake.

---

## 1. Camada Silver: `state_of_data_silver`

| Coluna Padronizada | Tipo de Dado | Descrição de Negócio | Valores Permitidos / Exemplo |
| :--- | :---: | :--- | :--- |
| `ano_pesquisa` | `STRING` | Edição da pesquisa State of Data Brasil (partição) | `2023-2024`, `2024-2025`, `2025-2026` |
| `id_respondente` | `STRING` | Identificador único do respondente ou hash técnico SHA-256 | `b08e7a688b...` |
| `idade` | `INTEGER` | Idade contínua informada pelo respondente | `18` a `75` |
| `faixa_idade` | `STRING` | Faixa etária agrupada | `17-21`, `22-24`, `25-29`, `30-34`, `35-39`, `40-44`, `45-49`, `50-54`, `55+` |
| `genero` | `STRING` | Identidade de gênero declarada | `Masculino`, `Feminino`, `Não binário`, `Outro`, `Prefiro não informar` |
| `cor_raca_etnia` | `STRING` | Autodeclaração étnico-racial | `Branca`, `Parda`, `Preta`, `Amarela`, `Indígena`, `Outra` |
| `pcd` | `STRING` | Pessoa com deficiência | `Sim`, `Não`, `Prefiro não informar` |
| `uf_mora` | `STRING` | Unidade Federativa de residência atual | `SP`, `RJ`, `MG`, `RS`, `PR`, `SC`, `BA`, etc. |
| `regiao_mora` | `STRING` | Grande Região do Brasil onde reside | `Sudeste`, `Sul`, `Nordeste`, `Centro-Oeste`, `Norte` |
| `nivel_ensino` | `STRING` | Grau mais elevado de escolaridade concluído ou em andamento | `Graduação/Bacharelado`, `Pós-graduação`, `Mestrado`, `Doutorado`, `Estudante` |
| `area_formacao` | `STRING` | Área do curso de graduação principal | `Computação / Engenharia de Software / Sistemas`, `Estatística/Matemática`, etc. |
| `situacao_trabalho` | `STRING` | Vínculo ou situação profissional atual | `Empregado (CLT)`, `Pessoa Jurídica (PJ)`, `Servidor Público`, `Freelancer`, etc. |
| `setor` | `STRING` | Setor da economia da empresa em que atua | `Finanças ou Bancos`, `Tecnologia/Software`, `Varejo`, `Consultoria`, `Saúde`, etc. |
| `tamanho_empresa` | `STRING` | Número estimado de colaboradores da empresa | `de 1 a 100`, `de 101 a 500`, `de 501 a 1000`, `de 1001 a 3000`, `Acima de 3000` |
| `is_gestor` | `STRING` | Atua formalmente como gestor / liderança de pessoas? | `Sim`, `Não`, `0.0`, `1.0` |
| `cargo_gestor` | `STRING` | Nomenclatura da função de liderança | `Gerente`, `Coordenador`, `Tech Lead`, `Head`, `Diretor` |
| `cargo_atual` | `STRING` | Cargo profissional principal no mercado de dados | `Analista de Dados`, `Cientista de Dados`, `Engenheiro de Dados`, `Analytics Engineer` |
| `senioridade` | `STRING` | Nível de maturidade profissional original | `Júnior`, `Pleno`, `Sênior`, `Especialista`, `Lead` |
| `senioridade_padronizada` | `STRING` | Classificação harmonizada em 4 níveis corporativos | `Júnior`, `Pleno`, `Sênior`, `Especialista/Liderança Técnica` |
| `faixa_salarial` | `STRING` | Faixa salarial mensal bruta declarada (dimensão canônica) | `de R$ 8.001/mês a R$ 12.000/mês`, `Acima de R$ 40.001/mês`, etc. |
| `salario_medio_estimado` | `DOUBLE` | Estimativa numérica contínua em Reais (R$) calculada a partir da faixa | `10000.50` (ponto médio de 8k-12k) |
| `tempo_experiencia_dados` | `STRING` | Tempo de experiência acumulada na área de dados | `Não tenho experiência`, `Menos de 1 ano`, `de 1 a 2 anos`, `de 3 a 4 anos`, `5+` |
| `tempo_experiencia_ti` | `STRING` | Tempo prévio em TI / Engenharia de Software | `Não tenho experiência`, `de 1 a 2 anos`, `3 a 5 anos`, etc. |
| `satisfeito_empresa` | `STRING` | Resposta original se está satisfeito no emprego atual | `True`, `False`, `1.0`, `0.0`, `Sim`, `Não` |
| `satisfeito_empresa_bool` | `BOOLEAN` | Indicador booleano padronizado de satisfação | `true`, `false`, `null` |
| `motivo_insatisfacao` | `STRING` | Principal motivo de insatisfação apontado | `Falta de oportunidade de crescimento`, `Salário abaixo do mercado`, etc. |
| `modelo_trabalho` | `STRING` | Forma de trabalho declarada | `Modelo 100% remoto`, `Híbrido flexível`, `100% presencial` |
| `modelo_trabalho_padronizado`| `STRING` | Classificação harmonizada do modelo de trabalho | `100% Remoto`, `Híbrido Flexível`, `Híbrido Dias Fixos`, `100% Presencial` |
| `linguagem_mais_usada` | `STRING` | Linguagem de programação mais utilizada no dia a dia | `Python`, `SQL`, `R`, `Scala`, `Java` |
| `linguagem_preferida` | `STRING` | Linguagem de programação predileta | `Python`, `SQL`, `R`, `Julia`, `Rust` |
| `cloud_preferida` | `STRING` | Provedor de Cloud preferido para projetos de dados | `Amazon Web Services (AWS)`, `Google Cloud (GCP)`, `Azure (Microsoft)` |
| `bi_preferido` | `STRING` | Ferramenta de Business Intelligence de preferência | `Microsoft PowerBI`, `Tableau`, `Metabase`, `Looker`, `Qlik` |
| `ia_prioridade_empresa` | `STRING` | Grau de priorização de IA / LLMs na empresa atual | `Sim, é uma das principais prioridades`, `Não é prioridade`, etc. |
| `tipo_uso_ia_empresa` | `STRING` | Formas de aplicação de IA Generativa no negócio | `Copilots`, `Produtos Internos`, `Produtos Externos`, `Descentralizado` |
| `uso_pessoal_ia` | `STRING` | Adesão individual a ferramentas como ChatGPT/Copilots | `Uso soluções gratuitas`, `Uso e pago`, `Empresa paga`, `Não uso` |

---

## 2. Camada Gold (Data Marts Analíticos)

### 2.1 `gold_perfil_mercado`
* **Grão**: `ano_pesquisa` × `regiao_mora` × `genero` × `nivel_ensino`
* **Métricas**: `total_respondentes`, `media_idade`

### 2.2 `gold_remuneracao_senioridade`
* **Grão**: `ano_pesquisa` × `cargo_atual` × `senioridade_padronizada` × `regiao_mora`
* **Métricas**: `total_profissionais`, `soma_salarios`, `salario_medio`, `salario_mediano`, `salario_min`, `salario_max`

### 2.3 `gold_diversidade`
* **Grão**: `ano_pesquisa` × `genero` × `cor_raca_etnia` × `is_gestor`
* **Métricas**: `total`, `soma_salarios`, `salario_medio`

### 2.4 `gold_tecnologias` (Desaninhada)
* **Grão**: `ano_pesquisa` × `categoria` × `tecnologia`
* **Métricas**: `total_usuarios` (contagem de respondentes únicos distintos)

### 2.5 `gold_adocao_ia`
* **Grão**: `ano_pesquisa` × `ia_prioridade_empresa` × `uso_pessoal_ia` × `senioridade_padronizada`
* **Métricas**: `total_respostas`

### 2.6 `gold_modelos_trabalho`
* **Grão**: `ano_pesquisa` × `modelo_trabalho_padronizado` × `regiao_mora`
* **Métricas**: `total_respondentes`, `total_respostas_validas`, `total_satisfeitos`, `taxa_satisfacao` (%), `salario_medio`

### 2.7 `gold_indicadores_executivos`
* **Grão**: `ano_pesquisa` × `kpi`
* **Métricas**: `valor`, `unidade`
