# Instruções de Apresentação e Impressão — Tech Challenge Fase 3

Este diretório contém os materiais executivos finais gerados para o **Tech Challenge Fase 3 (State of Data Brasil / Caso da Instituição Financeira)**.

---

## 📁 Arquivos Entregues

1. **`apresentacao_state_of_data.html`**:
   * Apresentação executiva interativa completa (18 slides) com proporção 16:9 widescreen.
   * **100% Autônomo e Offline:** Não requer internet, servidores, CDNs ou bibliotecas externas. Abre com duplo clique no Google Chrome, Microsoft Edge ou Firefox.
   * **Controles Interativos:**
     * ⬅️ / ➡️ ou Barra de Espaço: Avançar e retroceder slides (exibe estritamente o slide ativo).
     * `Home` / `End`: Ir para a Capa / Anexo Final.
     * `F`: Alternar modo Tela Cheia (*Fullscreen*).
     * `T` ou `I`: Abrir menu de Índice (*Table of Contents*).
     * `Ctrl + P` ou Botão **PDF**: Imprimir / exportar slides limpos em PDF.

2. **`apresentacao_state_of_data.pdf`**:
   * Documento PDF final oficial em formato 16:9 paisagem (18 páginas), preservando todos os gráficos, tabelas e notas metodológicas.
   * Atende rigorosamente ao formato exigido no enunciado do Tech Challenge.

---

## 🛠️ Como Regenerar os Materiais (se necessário)

Caso queira reconstruir os arquivos a partir do código fonte:
```powershell
# Regenerar gráficos executivos
python scripts/analytics/gerar_graficos_executivos.py

# Regenerar apresentação HTML e PDF
python scripts/analytics/gerar_apresentacao_executiva.py
```
