# Regras de Transformação e Metodologia de Tratamento

Este documento descreve as decisões metodológicas e as regras de transformação aplicadas na transição entre as camadas **Bronze ➔ Silver ➔ Gold**.

---

## 1. Tratamento e Deduplicação de Chaves Primárias

### 1.1 IDs Nulos e Hash Criptográfico
Em algumas edições da pesquisa, certos registros não possuem o identificador de token (`id_respondente` nulo ou vazio).
* **Regra**: Em vez de descartar registros que possam conter respostas válidas, geramos um hash criptográfico **SHA-256** concatenando os atributos essenciais da resposta:
  $$\text{id\_registro\_tecnico} = \text{SHA256}(\text{ano} \parallel \text{idade} \parallel \text{genero} \parallel \text{regiao} \parallel \text{cargo} \parallel \text{faixa\_salarial})$$
* **Deduplicação**: A remoção de duplicatas é executada com base no par `(ano_pesquisa, id_registro_tecnico)`.

---

## 2. Metodologia de Estimativa Salarial

As pesquisas coletam a remuneração em faixas textuais mensais brutas. Para viabilizar cruzamentos numéricos e agregações estatísticas, adotamos o seguinte critério:

1. **Preservação da Faixa Canônica**: O campo original `faixa_salarial` é mantido intacto como dimensão categórica primária.
2. **Cálculo da Métrica Contínua (`salario_medio_estimado`)**:
   * **Faixas Fechadas**: Ponto médio exato da faixa.
     $$\text{Ponto Médio} = \frac{\text{Piso} + \text{Teto}}{2}$$
     *Exemplo:* `de R$ 8.001/mês a R$ 12.000/mês` $\rightarrow$ **R\$ 10.000,50**.
   * **Faixa Inferior Aberta**: `Menos de R$ 1.000/mês` $\rightarrow$ **R\$ 500,00**.
   * **Faixa Superior Aberta**: `Acima de R$ 40.001/mês` $\rightarrow$ **R\$ 48.000,00** (fator de sensibilidade $1.2\times$ sobre o piso).
3. **Média Ponderada em Agregações**: Para evitar a distorção estatística da "média de médias", toda agregação de remuneração pondera pelo volume de profissionais do estrato:
   $$\bar{x}_{\text{ponderada}} = \frac{\sum (\bar{x}_i \cdot n_i)}{\sum n_i}$$

---

## 3. Desaninhamento de Tecnologias Multivaloradas (Explode)

Perguntas relativas a tecnologias (Linguagens, Provedores de Nuvem, Ferramentas de BI e Bancos de Dados) permitem seleção múltipla pelos respondentes, resultando em strings delimitadas por vírgula (ex: `"Python, SQL, R"`).

* **Regra na Camada Gold (`gold_tecnologias`)**:
  1. Aplicação de `split(coluna, ',')` seguido de `explode()`.
  2. Higienização com `trim()` e remoção de strings vazias.
  3. Agregação calculando a contagem de respondentes únicos distintos (`countDistinct("id_respondente")`).
* **Benefício**: Evita a contagem distorcida de combinações arbitrárias de strings e fornece o percentual real de adoção de cada ferramenta isolada no mercado.

---

## 4. Cálculo da Taxa de Satisfação Profissional

A pergunta sobre satisfação no trabalho (`satisfeito_empresa`) possui abstenções (nulos).

* **Regra**: O cálculo da taxa de satisfação utiliza estritamente o total de respostas válidas como denominador:
  $$\text{Taxa de Satisfação (\%)} = \frac{\text{Total de Respondentes Satisfeitos}}{\text{Total de Respostas Válidas (Sim ou Não)}} \times 100$$
* **Benefício**: Impede a subestimação artificial da satisfação decorrente de respondentes que optaram por não responder à pergunta.
