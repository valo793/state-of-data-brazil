# Instruções de Apresentação e Impressão — Tech Challenge Fase 3

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
