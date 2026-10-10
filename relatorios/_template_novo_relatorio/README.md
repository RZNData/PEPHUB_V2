# Guia de Criação de Novos Relatórios (Pephub)

Este diretório serve como modelo (template) para introduzir novos relatórios desenvolvidos por qualquer membro da equipe da Regional Norte.

---

## 🚀 Como Adicionar um Novo Relatório

1. **Copie esta pasta:**
   * Crie uma cópia de `_template_novo_relatorio` dentro de `relatorios/` com o nome do seu indicador (exemplo: `relatorios/cobranca/` ou `relatorios/qualidade_rede/`).

2. **Organize seus arquivos:**
   * `index.html`: O painel HTML principal. Pode ser um HTML próprio ou exportado (PowerBI, script Python, etc.).
   * `dados/`: Coloque aqui suas planilhas brutas (Excel, CSV, JSON). Elas ficam isoladas e **não** sobrecarregam o Pephub.
   * `scripts/`: Se você usa scripts (Python, R, Node) para transformar suas bases e gerar o HTML, mantenha-os aqui.
   * `report_config.json`: Edite os metadados do relatório (título, rota no Pephub, responsável).

3. **Publicar no Pephub:**
   Na raiz do projeto `Churn_Safra/`, execute:
   ```bash
   python publish_report.py nome_da_sua_pasta
   ```
   * O script irá validar o HTML e copiá-lo automaticamente para a pasta de produção `public/<rota>/index.html`.
   * Depois, para disponibilizar em produção para toda a empresa:
   ```bash
   npx wrangler deploy
   ```

---

## 🤖 (Opcional) Integração com o WhatsApp Bot

Se o seu relatório possuir indicadores-chave (KPIs, metas, rankings) que você deseja disponibilizar no Bot do WhatsApp da Regional Norte:
1. No arquivo `report_config.json`, ative `"bot_enabled": true`.
2. Crie um script `scripts/export_bot_data.py` (ou preencha `dados/bot_summary.json`) contendo os números consolidados.
3. Dessa forma, o Bot sempre responderá dados 100% reais e oficiais, sem alucinação e sem risco de quebrar seu relatório.
