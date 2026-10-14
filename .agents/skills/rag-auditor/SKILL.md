---
name: rag-auditor
description: Agente especialista em governança, validação de fluxos e qualidade das respostas do RAG (Pephub Bot). Audita separação de canais (Web sem prefixo #? vs WhatsApp), tolerância zero a alucinações e cruzamento incorreto de indicadores, postura questionadora proativa em perguntas ambíguas, cobertura dimensional completa (14 cidades, DDDs 91-99, canais, parceiros e vendedores), Text-to-SQL determinístico seguro e integridade analítica.
---

# Skill: RAG Auditor — Agente de Governança, Anti-Alucinação e Qualidade Analítica do Bot

Agente corporativo especializado em assegurar a precisão matemática, estabilidade de roteamento e integridade cognitiva do ecossistema RAG e Text-to-SQL da Regional Norte (Claro PEP HUB).

---

## 7 Pilares Universais de Governança e Qualidade do RAG

### 1. Separação Estrita de Canais (Web Corporativa vs WhatsApp)
- **Canal Web (`channel = 'web'`)**:
  - Usuários interagem diretamente em linguagem natural no portal web, **SEM nenhuma necessidade de prefixos como `#?` ou `＃?`**.
  - Respostas, menus e footers no canal Web **NÃO podem conter** links `https://wa.me/...`, nem comandos de WhatsApp como `#dados` ou `#ajuda`.
  - Devem conter navegação por colchetes limpos (ex: `[1]`, `[2]`), atalhos clicáveis e mensagens executivas com linguagem de portal web.
- **Canal WhatsApp (`channel = 'whatsapp'`)**:
  - Requer o gatilho estrito `#?` para segregação do tráfego corporativo em números pessoais.
  - Mantém links de retorno `https://wa.me/...` para facilidade em dispositivos móveis.

### 2. Tolerância Zero a Alucinações, Integridade dos Dados e Regra da Veracidade
- **Regra de Ouro da Veracidade**: *"Se não souber um valor ou ficar em dúvida, pergunte ou diga que não sabe."* Jamais inventar, extrapolar ou alucinar dados quando não estiverem explicitamente consolidados nas bases do D1.
- **Não-Cruzamento de Indicadores**: Jamais responder uma pergunta sobre um indicador utilizando dados ou relatórios de outro.
  - Se a pergunta é sobre **FPD**, a resposta DEVE vir estritamente de `fato_fpd` / `REPORT_REGISTRY.FPD`.
  - Se a pergunta é sobre **Churn Banda Larga**, DEVE vir de `fato_indicadores_mensais` / `REPORT_REGISTRY.CHURN_BL`.
  - Se a pergunta é sobre **Churn Safra D120**, DEVE vir de `fato_churn_safra` / `REPORT_REGISTRY.CHURN_SAFRA`.
  - Se a pergunta é sobre **Aprovação de Crédito**, DEVE vir de `fato_aprovacao_credito` / `REPORT_REGISTRY.CREDITO`.
  - Se a pergunta é sobre **Market Share Residencial**, DEVE vir estritamente de `fato_market_share` com filtro de serviço `02.BL` (Banda Larga Fixa), com dados exatos como Belém Claro = 33,88% e +131 Net Adds.
  - Se a pergunta é sobre **Market Share Móvel**, DEVE vir de `fato_market_share` (segmento POS_PAGO_SEM_M2M ou 5G).
  - Se a pergunta é sobre **Speech Analytics**, DEVE vir de `fato_speech_analytics` / `REPORT_REGISTRY.SPEECH`.
  - Se a pergunta é sobre **Motivos de Procura e OS**, DEVE vir de `fato_motivos_os` / `REPORT_REGISTRY.MOTIVOS`.
- **Proibição Absoluta**: Proibido tentar adivinhar métricas de outro indicador quando o solicitado não estiver disponível. Se não souber ou a métrica não existir, declarar a indisponibilidade com transparência executiva.

### 3. Postura Questionadora Proativa (Desambiguação Ativa)
- **Princípio**: Diante de dúvidas ou perguntas subespecificadas, o agente RAG deve questionar e esclarecer, em vez de assumir premissas incorretas.
- **Gatilho de Desambiguação**:
  - Quando o usuário mencionar apenas uma entidade dimensional (ex: "Qual o resultado de Belém?", "Como está o canal PAP?", "Resultado do DDD 91", "Parceiro Elite") **SEM especificar qual indicador** ele deseja:
  - O RAG **NÃO DEVE** assumir aleatoriamente que se trata de FPD ou Churn.
  - O RAG **DEVE responder com o menu questionador de esclarecimento proativo**, identificando a entidade detectada e listando os 7 indicadores oficiais para escolha rápida.

### 4. Cobertura Dimensional Completa
O motor semântico e Text-to-SQL deve reconhecer e aplicar filtros precisos para:
- **14 Cidades Oficiais da Regional Norte**:
  - Grandes Mercados (GM): Manaus, Belém, São Luís, Ananindeua, Macapá, Santana.
  - Mercados em Desenvolvimento (MD): Imperatriz, Castanhal, Parauapebas, Marabá, Paragominas, Timon, Caxias, Boa Vista.
- **Mercados e DDDs**:
  - DDDs 91, 92, 93, 94, 95, 96, 97, 98 e 99.
- **Canais de Venda**:
  - PAP (Porta a Porta), Lojas (Próprias e Franquias), Televendas, Agente Autorizado.
- **Pontos de Venda (PDVs) e Parceiros Comerciais**:
  - Mapeamento por padrões parciais (`LIKE %parceiro%`) em `pdv_ou_parceiro` e `dim_carteirizacao`.
- **Vendedor / Equipe Operacional**:
  - Como a base D1 é consolidada a nível de Canal e Parceiro Comercial/PDV, perguntas sobre vendedores devem mapear o canal/parceiro e conter nota explicativa de governança.

### 5. Text-to-SQL Determinístico, Seguro e Sem Injeção
- Consultas estruturadas devem passar por `buildDeterministicAnalyticalSQL` antes de qualquer fallback generativo.
- Todas as queries passam pelo filtro `validateSafeSQL`:
  - Somente comandos `SELECT` são autorizados.
  - Bloqueio estrito de palavras de modificação (`INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `TRUNCATE`, `EXEC`).
  - Limite de varredura obrigatório (`LIMIT 1`, `LIMIT 5` ou `LIMIT 10`).

### 6. Transparência de Dados e Limites de Escopo
- Se a base não possuir registros para o filtro solicitado, responder informando que o recorte não retornou dados para o período e orientar sobre os filtros válidos.
- Proibição de inventar números fictícios ou extrapolar históricos não consolidados.

### 7. Interface Web Interativa com Perguntas Predefinidas
- O chatbot no portal web (`header-widget.js`) deve oferecer:
  - Abas/gaveta retrátil de perguntas frequentes categorizadas por relatório (FPD, Safra, Churn BL, Crédito, Market Share, Speech, Motivos & OS).
  - Execução imediata com 1 clique através de delegação de eventos no chatbox (`[data-rag-cmd]`).
  - Input aberto em linguagem natural fluida.
  - Histórico de sessão persistido em `sessionStorage` para conveniência analítica do gestor.

### 8. Mecanismo de Feedback Analítico & Calibração Contínua
- Cada resposta analítica do bot no portal web é acompanhada de uma barra de feedback com 3 estados:
  - 🟢 **Totalmente correta** (`correct`): envia confirmação direta ao D1.
  - 🟡 **Parcialmente correta** (`partially_correct`): abre campo de texto inline para comentários opcionais.
  - 🔴 **Incorreta** (`incorrect`): abre campo de texto inline para detalhes da divergência ou indicador esperado.
- Todos os feedbacks são gravados na tabela `bot_feedback` no Cloudflare D1 via `POST /api/bot/feedback` contendo `user_id`, `user_name`, `message_id`, `query`, `response_text`, `report_id`, `rating` e `comment`.

### 9. Transparência, Disclaimer Analítico, Link para o Relatório Oficial e Chips
- Toda resposta gerada contém disclaimer analítico obrigatório: *"⚠️ Respostas geradas com base no contexto D1 do PEP HUB. Supervisão humana recomendada."*
- Botão direto para o Relatório Oficial: `[📊 Abrir no Relatório Oficial (${m.reportName}) ➔]` com parâmetros de URL pré-configurados (ex: `/churn-bl/?cidade=Manaus` ou `/market-share-residencial/?cidade=Belém`).
- Chips contextuais no rodapé da mensagem sugerindo aberturas, aprofundamentos de cenários e próximos passos analíticos.

---

## Bateria de Testes Cognitivos de Alta Variabilidade (No Mínimo 20 Cenários)

O RAG Auditor deve obrigatoriamente executar a suíte `scripts/test_rag_20_scenarios.js`, validando **22 cenários humanos realistas** com variabilidade de comandos, aberturas, profundidade e cruzamentos:

1. **Q01 - Churn BL Manaus (Anti-Colisão)**: Roteamento exato para `CHURN_BL` sem ser interceptado por Market Share, extração de Manaus e URL oficial.
2. **Q02 - Market Share Belém Área Cabeada**: Mapeia `isAreaCabeada` e Belém, gerando nota regulatória sobre escopo municipal Anatel.
3. **Q03 - Grandes Mercados (GMs)**: Reconhece cluster GM (Manaus, Belém, São Luís, Ananindeua, Macapá, Santana) e faz síntese agrupada.
4. **Q04 - Mercados em Desenvolvimento (MEDs)**: Reconhece cluster MEDs (Castanhal, Marabá, etc.) e analisa penetração regional.
5. **Q05 - Churn Safra por Canal (Guarda Dimensional)**: Detecta canal sem parceiro, recusa listar parceiros como canais e direciona para FPD e Crédito.
6. **Q06 - Churn Safra por Parceiro (Profundidade)**: Consulta a parceiros em Safra com `visao = 'PARCEIRO'`.
7. **Q07 - FPD Regional Consolidado (Abertura)**: Indicadores consolidados de FPD 60, FPD 30 e taxa de cura.
8. **Q08 - FPD por Canal PAP (Profundidade)**: Filtro exato de canal `PAP` em `fato_fpd`.
9. **Q09 - FPD Cruzado por DDD 91 (Geográfico)**: Mapeamento de DDD 91 (Belém) e filtro determinístico.
10. **Q10 - Aprovação de Crédito Regional (Abertura)**: Eficiência da esteira, volume de consultas e taxa de aprovação regional.
11. **Q11 - Antifraude por Cidade (Profundidade)**: Ranking de cidades com maior incidência de recusas antifraude.
12. **Q12 - Churn Banda Larga PME (Segmento)**: Segmentação explícita de Churn BL para o segmento PME.
13. **Q13 - RxO Churn BL (Metas Orçamentárias)**: Confronto entre realizado vs orçado com cálculo de desvio em p.p.
14. **Q14 - Speech Analytics Motivos (Qualitativo)**: Extração de top motivos de cancelamento na base de transcrição de chamadas.
15. **Q15 - Motivo Speech Acha Caro em Belém**: Cruzamento de motivo específico e cidade Belém.
16. **Q16 - Taxa de OS Técnica Regional (Operacional)**: Volume de ordens de serviço e taxa de visita técnica.
17. **Q17 - Taxa de OS em Manaus (Profundidade Geográfica)**: Indicadores de visita técnica em Manaus.
18. **Q18 - Market Share Móvel DDD 98**: Filtro de serviço SMP pós-pago no DDD 98 (Maranhão).
19. **Q19 - Conceitual FPD 30 vs 60 (Regra de Negócio)**: Explicação executiva sem disparar SQL desnecessário.
20. **Q20 - Pergunta Ambígua Apenas Cidade**: Gatilho de desambiguação questionadora proativa com as 7 opções.
21. **Q21 - Churn Voluntário vs Involuntário**: Quebra comparativa de tipologia de desconexão.
22. **Q22 - Vendedores Ofensores em FPD**: Ranking de qualidade de venda individual por vendedor.

---

## Critérios de Auditoria e Pontuação no Release Gate

O script de auditoria `scripts/rag_auditor.py` avalia 10 testes com peso 10 cada (Total: 100 pontos):
1. **[T01]** Suporte nativo ao parâmetro `channel` (`web` vs `whatsapp`) no `worker/routes/bot.js` e `worker/bot_registry.js`.
2. **[T02]** Ausência de prefixo `#?` e ausência de links `wa.me` nas respostas formatadas para `channel = 'web'`.
3. **[T03]** Existência e integridade da função de desambiguação questionadora proativa (`buildProactiveClarificationResponse`).
4. **[T04]** Cobertura dimensional e qualificadores avançados (14 cidades, DDDs, clusters GM/MED, área cabeada, canais, parceiros).
5. **[T05]** Isolamento estrito de indicadores, anti-colisão e guardas dimensionais em `resolveTargetReport`.
6. **[T06]** Text-to-SQL determinístico seguro com `validateSafeSQL` e suporte a vendedores, PME e RxO.
7. **[T07]** Interface Web com abas, gaveta de perguntas predefinidas funcionais com 1 clique e feedback bar (3 estados).
8. **[T08]** Metadados ricos: `reportUrl` parametrizado, chips contextuais e disclaimer analítico obrigatório.
9. **[T09]** Bateria de no mínimo 20 testes cognitivos humanos (`scripts/test_rag_20_scenarios.js`) 100% aprovados.
10. **[T10]** Tabela `bot_feedback` no D1 e rota `POST /api/bot/feedback` ativas para calibração contínua.
