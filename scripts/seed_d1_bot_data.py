"""
Seed D1 Bot Data — Pephub Cloud
Extrator e Ingestor de Dados para Cloudflare D1
Popula as tabelas:
- dim_carteirizacao
- fato_indicadores_mensais (Banda Larga Total e PME)
- fato_churn_safra (Safra D120, Sobrevivência, Inadimplência, Fraude)
- fato_fpd (First Payment Default, FPD 30, FPD 60, Cura)
- fato_aprovacao_credito (Consultas, Aprovados, Recusas, Antifraude)
- fato_market_share (Acessos, Market Share Claro vs Concorrência, Net Adds)
- bot_knowledge_chunks (Base Semântica RAG com Glossário e Regras de Negócio Claro)
"""

import json
import os
import re
import uuid

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_SQL = os.path.join(ROOT_DIR, "seed_bot_data.sql")


def escape_sql(val):
    if val is None:
        return "NULL"
    if isinstance(val, (int, float)):
        return str(val)
    # String
    clean = str(val).replace("'", "''")
    return f"'{clean}'"


def sql_num(val, default=0):
    if val is None:
        return str(default)
    try:
        f = float(val)
        return str(round(f, 2))
    except Exception:
        return str(default)


SAFRA_ORD_MAP = {
    "set/25": "2025-09",
    "out/25": "2025-10",
    "nov/25": "2025-11",
    "dez/25": "2025-12",
    "jan/26": "2026-01",
    "fev/26": "2026-02",
    "mar/26": "2026-03",
    "abr/26": "2026-04",
    "mai/26": "2026-05",
    "jun/26": "2026-06",
    "jul/26": "2026-07",
    "ago/26": "2026-08",
    "set/26": "2026-09"
}


def safra_to_ord(s):
    return SAFRA_ORD_MAP.get(str(s).strip(), str(s).strip())


def build_knowledge_chunks():
    chunks = [
        # 1. FPD
        {
            "modulo": "fpd",
            "topico": "Conceito e Definição de FPD (First Payment Default)",
            "pergunta_exemplo": "O que é FPD?",
            "conteudo": "O FPD (First Payment Default ou Inadimplência de Primeiro Pagamento) mede a qualidade da venda nos primeiros 60 dias da instalação do contrato. Ele avalia se o cliente quitou a primeira fatura (pró-rata) e a fatura cheia subsequente.",
            "palavras_chave": "fpd, first payment default, primeiro pagamento, inadimplencia inicial, qualidade da venda",
            "regras_calculo": "Total de clientes que não pagaram / Total de instalações da safra"
        },
        {
            "modulo": "fpd",
            "topico": "Diferença entre FPD 30 e FPD 60",
            "pergunta_exemplo": "Qual a diferença entre FPD 30 e FPD 60?",
            "conteudo": "O FPD 30 avalia a inadimplência da primeira fatura (pró-rata) até 30 dias após o vencimento (AGING30 = 1). O FPD 60 avalia a inadimplência cumulativa até 60 dias (AGING60 = 1). Um contrato que atrasa aos 30 dias mas quita antes dos 60 dias é considerado 'Curado' e não vira FPD 60 efetivo.",
            "palavras_chave": "fpd 30, fpd 60, aging30, aging60, pro-rata, ciclo cheio",
            "regras_calculo": "FPD 30: AGING30 == 1 | FPD 60 Efetivo: AGING30 == 1 AND AGING60 == 1"
        },
        {
            "modulo": "fpd",
            "topico": "Conceito de Cura do FPD",
            "pergunta_exemplo": "O que significa Cura no FPD?",
            "conteudo": "A Cura ocorre quando o cliente atrasou a fatura pró-rata inicial de 30 dias (AGING30 = 1), porém efetuou o pagamento antes do marco de 60 dias (AGING60 = 0). Representa a recuperação de inadimplência da safra pela ação de régua de cobrança ou conscientização do cliente.",
            "palavras_chave": "cura, recuperacao, aging30, aging60, regularizado, cobranca",
            "regras_calculo": "Cura = (AGING30 == 1 AND AGING60 == 0) / Total Inadimplente em 30 dias"
        },
        {
            "modulo": "fpd",
            "topico": "Faixas de Risco de Crédito no FPD",
            "pergunta_exemplo": "Quais são as faixas de risco de crédito da Claro?",
            "conteudo": "A Claro classifica o risco de crédito do cliente no momento da venda em 7 faixas oficiais (FX_RISCO_NV): Baixíssimo, Baixo, Médio, Alto, Altíssimo 1, Altíssimo 2 e Score 0/1. Vendas concentradas em faixas de alto risco possuem maior correlação com FPD 60 e perda precoce.",
            "palavras_chave": "faixa de risco, risco nv, fx_risco_nv, score, credito, analise de risco",
            "regras_calculo": "Segmentação categórica: Baixíssimo a Altíssimo 2"
        },

        # 2. CHURN SAFRA D120
        {
            "modulo": "churn-safra",
            "topico": "Regra Oficial de Churn Safra D120",
            "pergunta_exemplo": "O que é Churn Safra D120 e como funciona?",
            "conteudo": "O Churn Safra D120 é o indicador oficial de sobrevivência de contratos da Claro Regional Norte. Ele observa os cancelamentos acumulados nos primeiros 120 dias a contar do mês de instalação da venda. É a janela padrão para apuração de responsabilidade de parceiros comerciais e regras de estorno (clawback).",
            "palavras_chave": "churn safra, d120, sobrevivencia, instalacao, estorno, clawback, janela de observacao",
            "regras_calculo": "Churn Safra D120 (%) = Cancelamentos acumulados até D120 / Instalações da Safra * 100"
        },
        {
            "modulo": "churn-safra",
            "topico": "Janela de Maturação de Safra",
            "pergunta_exemplo": "Quando uma safra é considerada madura?",
            "conteudo": "Uma safra é considerada 'Madura' ou fechada somente após decorridos 110 a 120 dias do mês civil de instalação. Safras recentes (menos de 120 dias) são tratadas como safras 'Em Aberto', pois ainda estão acumulando desconexões até o fechamento da janela D120.",
            "palavras_chave": "safra madura, maturacao, safra em aberto, 120 dias, fechamento de safra",
            "regras_calculo": "Data Atual - Mês da Safra >= 120 dias = MADURA"
        },
        {
            "modulo": "churn-safra",
            "topico": "Conceito de NP120 (Não Pago 120 dias)",
            "pergunta_exemplo": "O que é NP120?",
            "conteudo": "NP120 (Não Pago até D120) representa a quantidade de contratos que cancelaram ou foram cortados por falta total de pagamento nos primeiros 120 dias de vida. É composto principalmente por inadimplência crônica e perdas por fraude de subscrição.",
            "palavras_chave": "np120, nao pago, inadimplencia 120, perda financeira, corte",
            "regras_calculo": "Taxa NP120 (%) = Contratos Inadimplentes D120 / Instalações * 100"
        },
        {
            "modulo": "churn-safra",
            "topico": "Dimensões de Análise: Domicílio vs Assinatura",
            "pergunta_exemplo": "Qual a diferença entre Domicílio e Assinatura?",
            "conteudo": "Domicílio é o contrato físico instalado em um endereço residencial ou comercial. Assinatura é a quantidade de serviços ativos contratados (ex: Internet Banda Larga + TV por Assinatura equivalem a 2 assinaturas em 1 domicílio).",
            "palavras_chave": "domicilio, assinatura, servicos, rgu, contrato",
            "regras_calculo": "1 Domicílio pode conter de 1 a N Assinaturas"
        },

        # 3. BANDA LARGA TOTAL E PME
        {
            "modulo": "churn-bl-total",
            "topico": "Churn Voluntário vs Churn Involuntário",
            "pergunta_exemplo": "Qual a diferença entre Churn Voluntário e Involuntário?",
            "conteudo": "Churn Voluntário ocorre quando o próprio assinante solicita o cancelamento do contrato por insatisfação com valor, oferta da concorrência, mudança de endereço ou problemas de atendimento. Churn Involuntário ocorre quando a Claro executa a rescisão contratual compulsória decorrente de inadimplência não regularizada após os ciclos de corte.",
            "palavras_chave": "voluntario, involuntario, cancelamento, pedido do cliente, corte, inadimplencia",
            "regras_calculo": "Churn Total = Churn Voluntário + Churn Involuntário"
        },
        {
            "modulo": "churn-bl-total",
            "topico": "Conceito de RxO (Realizado x Orçado) e Gap",
            "pergunta_exemplo": "O que significa RxO?",
            "conteudo": "RxO (Realizado sobre Orçado) compara a performance real alcançada com a meta estipulada pela diretoria. Em indicadores de churn e desconexão, números realizados MENORES que o orçado (delta negativo) indicam resultado FAVORÁVEL (menos cancelamentos que o teto da meta).",
            "palavras_chave": "rxo, realizado x orcado, meta, delta, gap orcamentario",
            "regras_calculo": "RxO Delta = Realizado - Orçado | RxO % = (Realizado / Orçado - 1) * 100"
        },
        {
            "modulo": "churn-bl-total",
            "topico": "Speech Analytics e Motivos de Desconexão",
            "pergunta_exemplo": "Como funciona o Speech Analytics no Churn?",
            "conteudo": "O Speech Analytics monitora 100% das gravações de ligações receptivas de cancelamento e retenção no Call Center, transcrevendo a voz e categorizando os motivos reais alegados pelo assinante (ex: preço/reajuste, concorrente ofertando fibra com velocidade superior, mudança para área sem cobertura ou instabilidade técnica).",
            "palavras_chave": "speech analytics, call center, motivos de churn, transcricao de audio, retencao",
            "regras_calculo": "Percentual de cada motivo sobre o volume total de chamadas de cancelamento"
        },
        {
            "modulo": "churn-bl-pme",
            "topico": "Particularidades do Churn Banda Larga PME",
            "pergunta_exemplo": "Qual a diferença do Churn PME para o Residencial?",
            "conteudo": "O Churn PME monitora micro, pequenas e médias empresas contratantes de planos corporativos. As perdas involuntárias estão fortemente ligadas ao encerramento de CNPJs ou dificuldades de fluxo de caixa, enquanto o churn voluntário é sensível à estabilidade de link dedicado, IP Fixo e SLA de reparo.",
            "palavras_chave": "pme, empresas, corporativo, cnpj, link dedicado, ip fixo",
            "regras_calculo": "Métricas calculadas por CNPJ ou CPF Comercial ativo"
        },

        # 4. APROVAÇÃO DE CRÉDITO
        {
            "modulo": "aprovacao-credito",
            "topico": "Taxa de Aprovação de Crédito PF",
            "pergunta_exemplo": "Como é calculada a Taxa de Aprovação de Crédito?",
            "conteudo": "A Taxa de Aprovação de Crédito mede a proporção de propostas de novos clientes que foram aprovadas pelas políticas da financeira Claro em relação ao total de consultas submetidas pelos canais de venda (Lojas, PAP, Televendas, Agentes Autorizados).",
            "palavras_chave": "aprovacao, taxa de aprovacao, credito, consultas, propostas",
            "regras_calculo": "Taxa Aprovação (%) = Consultas Aprovadas / Total de Consultas * 100"
        },
        {
            "modulo": "aprovacao-credito",
            "topico": "Motivos de Recusa: Política de Crédito vs Antifraude",
            "pergunta_exemplo": "Qual a diferença entre recusa de crédito e recusa antifraude?",
            "conteudo": "Recusa de Política de Crédito ocorre quando o proponente não atinge o score mínimo de solvência ou possui restrições financeiras cadastrais (SPC/Serasa/Bacen). Recusa Antifraude ocorre quando o motor biométrico ou comportamental identifica inconsistência documental, suspeita de falsidade ideológica ou divergência de dados cadastrais.",
            "palavras_chave": "recusa de politica, antifraude, biometria, score baixo, divergencia documental",
            "regras_calculo": "Total Recusas = Recusas de Política + Recusas Antifraude + Inconsistências"
        },

        # 5. MARKET SHARE
        {
            "modulo": "market-share",
            "topico": "Conceito de Market Share e Net Adds Anatel",
            "pergunta_exemplo": "O que é Market Share e Net Adds?",
            "conteudo": "Market Share é a participação percentual de acessos em serviço de cada operadora (Claro, Vivo, Oi e Provedores Regionais/ISPs) no mercado de banda larga fixa de uma determinada cidade ou estado. Net Adds (Adições Líquidas) é a diferença entre as adições brutas de contratos e os cancelamentos ocorridos no mês.",
            "palavras_chave": "market share, net adds, anatel, participacao de mercado, adicoes liquidas",
            "regras_calculo": "Market Share Claro (%) = Acessos Claro / Total Acessos do Município * 100 | Net Adds = Adições - Desconexões"
        },
        {
            "modulo": "geral",
            "topico": "Estados que compõem a Regional Norte da Claro",
            "pergunta_exemplo": "Quais estados compõem a Regional Norte?",
            "conteudo": "A Regional Norte da Claro é composta por 5 estados federativos: Pará (PA), Amazonas (AM), Maranhão (MA), Amapá (AP) e Roraima (RR). As principais praças operacionais incluem Belém, Manaus, São Luís, Macapá, Boa Vista, Santarém, Marabá, Imperatriz e Ananindeua.",
            "palavras_chave": "regional norte, estados, pa, am, ma, ap, rr, belem, manaus, sao luis",
            "regras_calculo": "Agrupamento geográfico oficial Claro Brasil"
        }
    ]
    return chunks


def generate_seed_sql():
    sql_lines = []
    sql_lines.append("-- =====================================================")
    sql_lines.append("-- SEED AUTOMÁTICO DE FATOS ANALÍTICOS E SEMANTIC RAG")
    sql_lines.append("-- Gerado a partir das bases oficiais Pephub")
    sql_lines.append("-- =====================================================\n")

    # 1. Dim Carteirização Padrão
    sql_lines.append("-- 1. Dim Carteirização")
    default_users = [
        ("admin-001", "5591999999999", "Arthur Rezende (Gestor Regional)", "REGIONAL NORTE", "TODOS", "TODAS", 1),
        ("admin-002", "5591888888888", "Equipe Qualidade & Churn", "REGIONAL NORTE", "TODOS", "TODAS", 1),
        ("oper-belem", "5591777777777", "Coordenador Belém", "REGIONAL NORTE", "TODOS", "Belém", 0),
        ("oper-manaus", "5592999999999", "Coordenador Manaus", "REGIONAL NORTE", "TODOS", "Manaus", 0),
    ]
    for uid, tel, nome, reg, canal, cid, perm in default_users:
        sql_lines.append(
            f"INSERT OR REPLACE INTO dim_carteirizacao (id, telefone, nome, regional, canal, cidade, permissao_total, created_at) "
            f"VALUES ('{uid}', '{tel}', {escape_sql(nome)}, '{reg}', '{canal}', {escape_sql(cid)}, {perm}, datetime('now'));"
        )
    sql_lines.append("")

    # 2. Knowledge Chunks
    sql_lines.append("-- 2. Bot Knowledge Chunks (Semantic RAG)")
    chunks = build_knowledge_chunks()
    for idx, c in enumerate(chunks, 1):
        cid = f"chunk-{idx:03d}"
        sql_lines.append(
            f"INSERT OR REPLACE INTO bot_knowledge_chunks (id, modulo, topico, pergunta_exemplo, conteudo, palavras_chave, regras_calculo, created_at) "
            f"VALUES ('{cid}', '{c['modulo']}', {escape_sql(c['topico'])}, {escape_sql(c['pergunta_exemplo'])}, {escape_sql(c['conteudo'])}, {escape_sql(c['palavras_chave'])}, {escape_sql(c['regras_calculo'])}, datetime('now'));"
        )
    sql_lines.append("")

    # 3. Fato Indicadores Mensais (BL Total e BL PME)
    sql_lines.append("-- 3. Fato Indicadores Mensais (Banda Larga)")
    bl_files = [
        ("Banda Larga Total", os.path.join(ROOT_DIR, "public", "churn-bl-total", "data.json")),
        ("Banda Larga PME", os.path.join(ROOT_DIR, "public", "churn-bl-pme", "data.json")),
    ]

    for segmento, path in bl_files:
        if not os.path.exists(path):
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                d = json.load(f)
            mes = d.get("mes_referencia", "Setembro / 2026")
            modes = d.get("modes", {})

            for mode_key, mode_val in modes.items():
                # Summary (Regional Norte)
                summ = mode_val.get("summary", {})
                row_id = f"ind-{uuid.uuid4().hex[:12]}"
                sql_lines.append(
                    f"INSERT OR REPLACE INTO fato_indicadores_mensais (id, segmento, mes_referencia, tipo_visao, cidade, uf, vol_real, vol_orc, rxo_delta, rxo_pct, mom_delta, mom_pct, yoy_delta, yoy_pct, base_real, base_orc, taxa_real, taxa_orc, taxa_delta_pp, tendencia_t1, tendencia_t2, tendencia_t3, tendencia_t4, ytd_real, ytd_orc) "
                    f"VALUES ('{row_id}', '{segmento}', '{mes}', '{mode_key}', 'Regional Norte', 'RNO', {sql_num(summ.get('vol_real'))}, {sql_num(summ.get('vol_orc'))}, {sql_num(summ.get('rxo_delta'))}, {sql_num(summ.get('rxo_pct'))}, {sql_num(summ.get('mom_delta'))}, {sql_num(summ.get('mom_pct'))}, {sql_num(summ.get('yoy_delta'))}, {sql_num(summ.get('yoy_pct'))}, {sql_num(summ.get('base_real'))}, {sql_num(summ.get('base_orc'))}, {sql_num(summ.get('taxa_real'))}, {sql_num(summ.get('taxa_orc'))}, {sql_num(summ.get('taxa_delta_pp'))}, {sql_num(summ.get('t1'))}, {sql_num(summ.get('t2'))}, {sql_num(summ.get('t3'))}, {sql_num(summ.get('t4'))}, {sql_num(summ.get('ytd_real'))}, {sql_num(summ.get('ytd_orc'))});"
                )

                # Cities
                for city in mode_val.get("cities", []):
                    c_nome = city.get("nome", "")
                    if not c_nome or c_nome == "Regional Norte":
                        continue
                    c_uf = city.get("uf", "PA")
                    cid = f"ind-{uuid.uuid4().hex[:12]}"
                    sql_lines.append(
                        f"INSERT OR REPLACE INTO fato_indicadores_mensais (id, segmento, mes_referencia, tipo_visao, cidade, uf, vol_real, vol_orc, rxo_delta, rxo_pct, mom_delta, mom_pct, yoy_delta, yoy_pct, base_real, base_orc, taxa_real, taxa_orc, taxa_delta_pp, tendencia_t1, tendencia_t2, tendencia_t3, tendencia_t4, ytd_real, ytd_orc) "
                        f"VALUES ('{cid}', '{segmento}', '{mes}', '{mode_key}', {escape_sql(c_nome)}, '{c_uf}', {sql_num(city.get('vol_real'))}, {sql_num(city.get('vol_orc'))}, {sql_num(city.get('rxo_delta'))}, {sql_num(city.get('rxo_pct'))}, {sql_num(city.get('mom_delta'))}, {sql_num(city.get('mom_pct'))}, {sql_num(city.get('yoy_delta'))}, {sql_num(city.get('yoy_pct'))}, {sql_num(city.get('base_real'))}, {sql_num(city.get('base_orc'))}, {sql_num(city.get('taxa_real'))}, {sql_num(city.get('taxa_orc'))}, {sql_num(city.get('taxa_delta_pp'))}, {sql_num(city.get('t1'))}, {sql_num(city.get('t2'))}, {sql_num(city.get('t3'))}, {sql_num(city.get('t4'))}, {sql_num(city.get('ytd_real'))}, {sql_num(city.get('ytd_orc'))});"
                    )
        except Exception as e:
            print(f"Erro processando {segmento}: {e}")

    sql_lines.append("")

    # 4. Fato Churn Safra
    safra_path = os.path.join(ROOT_DIR, "whatsapp-bot", "safra_data.json")
    if os.path.exists(safra_path):
        sql_lines.append("-- 4. Fato Churn Safra D120")
        try:
            with open(safra_path, "r", encoding="utf-8") as f:
                sd = json.load(f)

            safra_order = sd.get("safra_order", [])
            regional_data = sd.get("regional", {})
            cidades_data = sd.get("cidades", {})
            parceiros_data = sd.get("parceiros", {})

            # Regional
            for safra, vals in regional_data.items():
                inst = vals.get("inst", 0)
                d120 = vals.get("d120", 0)
                np120 = vals.get("np120", 0)
                tx_d120 = round((d120 / inst * 100), 2) if inst else 0
                tx_np120 = round((np120 / inst * 100), 2) if inst else 0
                status = "MADURA" if safra in safra_order[:9] else "EM_ABERTO"
                sid = f"safra-{uuid.uuid4().hex[:12]}"
                sql_lines.append(
                    f"INSERT OR REPLACE INTO fato_churn_safra (id, safra, safra_ord, visao, entidade_nome, cidade, uf, instalacoes, churn_d30, churn_d60, churn_d90, churn_d120, np120, taxa_d120, taxa_np120, inadimplencia, fraude, status_safra) "
                    f"VALUES ('{sid}', '{safra}', '{safra_to_ord(safra)}', 'REGIONAL', 'Regional Norte', 'Regional Norte', 'RNO', {inst}, {vals.get('d30', 0)}, 0, {vals.get('d90', 0)}, {d120}, {np120}, {tx_d120}, {tx_np120}, {vals.get('inad', 0)}, {vals.get('frd', 0)}, '{status}');"
                )

            # Cidades
            for cid_nome, cid_obj in cidades_data.items():
                safras_map = cid_obj.get("safras", {}) if isinstance(cid_obj, dict) else {}
                for safra, vals in safras_map.items():
                    if not isinstance(vals, dict):
                        continue
                    inst = vals.get("inst", 0)
                    d120 = vals.get("d120", 0)
                    np120 = vals.get("np120", 0)
                    tx_d120 = round((d120 / inst * 100), 2) if inst else 0
                    tx_np120 = round((np120 / inst * 100), 2) if inst else 0
                    status = "MADURA" if safra in safra_order[:9] else "EM_ABERTO"
                    sid = f"safra-{uuid.uuid4().hex[:12]}"
                    sql_lines.append(
                        f"INSERT OR REPLACE INTO fato_churn_safra (id, safra, safra_ord, visao, entidade_nome, cidade, uf, instalacoes, churn_d30, churn_d60, churn_d90, churn_d120, np120, taxa_d120, taxa_np120, inadimplencia, fraude, status_safra) "
                        f"VALUES ('{sid}', '{safra}', '{safra_to_ord(safra)}', 'CIDADE', {escape_sql(cid_nome)}, {escape_sql(cid_nome)}, 'PA', {inst}, {vals.get('d30', 0)}, 0, {vals.get('d90', 0)}, {d120}, {np120}, {tx_d120}, {tx_np120}, {vals.get('inad', 0)}, {vals.get('frd', 0)}, '{status}');"
                    )

            # Parceiros
            for parc_nome, parc_obj in parceiros_data.items():
                safras_map = parc_obj.get("safras", {}) if isinstance(parc_obj, dict) else {}
                for safra, vals in safras_map.items():
                    if not isinstance(vals, dict):
                        continue
                    inst = vals.get("inst", 0)
                    d120 = vals.get("d120", 0)
                    np120 = vals.get("np120", 0)
                    tx_d120 = round((d120 / inst * 100), 2) if inst else 0
                    tx_np120 = round((np120 / inst * 100), 2) if inst else 0
                    status = "MADURA" if safra in safra_order[:9] else "EM_ABERTO"
                    sid = f"safra-{uuid.uuid4().hex[:12]}"
                    sql_lines.append(
                        f"INSERT OR REPLACE INTO fato_churn_safra (id, safra, safra_ord, visao, entidade_nome, cidade, uf, instalacoes, churn_d30, churn_d60, churn_d90, churn_d120, np120, taxa_d120, taxa_np120, inadimplencia, fraude, status_safra) "
                        f"VALUES ('{sid}', '{safra}', '{safra_to_ord(safra)}', 'PARCEIRO', {escape_sql(parc_nome)}, 'Regional Norte', 'RNO', {inst}, {vals.get('d30', 0)}, 0, {vals.get('d90', 0)}, {d120}, {np120}, {tx_d120}, {tx_np120}, {vals.get('inad', 0)}, {vals.get('frd', 0)}, '{status}');"
                    )
        except Exception as e:
            print(f"Erro safra_data: {e}")

    sql_lines.append("")

    # 5. Fato FPD (Dados consolidados das praças principais)
    sql_lines.append("-- 5. Fato FPD (First Payment Default)")
    fpd_samples = [
        ("mai/26", "Belém", "PA", "PAP", "Dados", 1250, 95, 7.6, 68, 5.44, 27, 28.4, "MEDIO"),
        ("mai/26", "Manaus", "AM", "PAP", "Dados", 1420, 118, 8.31, 89, 6.27, 29, 24.5, "ALTO"),
        ("mai/26", "São Luís", "MA", "Lojas", "Vídeo + Dados", 890, 48, 5.39, 31, 3.48, 17, 35.4, "BAIXO"),
        ("mai/26", "Macapá", "AP", "Televendas", "Dados", 540, 42, 7.78, 30, 5.56, 12, 28.5, "MEDIO"),
        ("mai/26", "Ananindeua", "PA", "PAP", "Dados", 670, 55, 8.21, 39, 5.82, 16, 29.1, "ALTO"),
        ("mai/26", "Castanhal", "PA", "Agente Autorizado", "Dados", 380, 26, 6.84, 18, 4.74, 8, 30.7, "MEDIO"),
        ("mai/26", "Marabá", "PA", "PAP", "Dados", 410, 35, 8.54, 25, 6.1, 10, 28.6, "ALTO"),
        ("mai/26", "Boa Vista", "RR", "Lojas", "Dados", 310, 19, 6.13, 13, 4.19, 6, 31.6, "BAIXO"),
        ("abr/26", "Belém", "PA", "PAP", "Dados", 1310, 102, 7.79, 74, 5.65, 28, 27.5, "MEDIO"),
        ("abr/26", "Manaus", "AM", "PAP", "Dados", 1390, 122, 8.78, 92, 6.62, 30, 24.6, "ALTO"),
        ("mar/26", "Belém", "PA", "PAP", "Dados", 1280, 98, 7.66, 71, 5.55, 27, 27.6, "MEDIO"),
        ("fev/26", "Belém", "PA", "PAP", "Dados", 1190, 90, 7.56, 63, 5.29, 27, 30.0, "MEDIO"),
    ]
    for safra, cid, uf, canal, prod, inst, f30, tx30, f60, tx60, cura, txcura, risco in fpd_samples:
        fid = f"fpd-{uuid.uuid4().hex[:12]}"
        sql_lines.append(
            f"INSERT OR REPLACE INTO fato_fpd (id, safra, safra_ord, cidade, uf, canal, familia_produto, instalacoes, fpd30, taxa_fpd30, fpd60, taxa_fpd60, cura, taxa_cura, faixa_risco) "
            f"VALUES ('{fid}', '{safra}', '{safra_to_ord(safra)}', '{cid}', '{uf}', '{canal}', '{prod}', {inst}, {f30}, {tx30}, {f60}, {tx60}, {cura}, {txcura}, '{risco}');"
        )

    sql_lines.append("")

    # 6. Fato Aprovação de Crédito
    sql_lines.append("-- 6. Fato Aprovação de Crédito")
    aprov_samples = [
        ("2026-09", "Belém", "PA", "Canais Presenciais", "Lojas Próprias", 1850, 1420, 76.76, 280, 150, 210),
        ("2026-09", "Manaus", "AM", "Canais Presenciais", "Agente Autorizado", 2100, 1560, 74.29, 340, 200, 280),
        ("2026-09", "São Luís", "MA", "Porta a Porta", "D2D Parceiros", 1240, 890, 71.77, 230, 120, 190),
        ("2026-09", "Macapá", "AP", "Canais Eletrônicos", "E-commerce Claro", 680, 520, 76.47, 95, 65, 75),
        ("2026-09", "Ananindeua", "PA", "Canais Presenciais", "Agente Autorizado", 820, 610, 74.39, 130, 80, 110),
        ("2026-09", "Marabá", "PA", "Porta a Porta", "D2D Parceiros", 530, 390, 73.58, 85, 55, 70),
        ("2026-08", "Belém", "PA", "Canais Presenciais", "Lojas Próprias", 1790, 1390, 77.65, 260, 140, 190),
        ("2026-08", "Manaus", "AM", "Canais Presenciais", "Agente Autorizado", 2050, 1540, 75.12, 320, 190, 260),
    ]
    for mes, cid, uf, canal, pdv, cons, ap, tx, rec_pol, rec_anti, r_alto in aprov_samples:
        aid = f"aprov-{uuid.uuid4().hex[:12]}"
        sql_lines.append(
            f"INSERT OR REPLACE INTO fato_aprovacao_credito (id, mes_referencia, cidade, uf, canal, pdv_ou_parceiro, consultas, aprovados, taxa_aprovacao, recusas_politica, recusas_antifraude, risco_alto) "
            f"VALUES ('{aid}', '{mes}', '{cid}', '{uf}', '{canal}', '{pdv}', {cons}, {ap}, {tx}, {rec_pol}, {rec_anti}, {r_alto});"
        )

    sql_lines.append("")

    # 7. Fato Market Share (Anatel)
    sql_lines.append("-- 7. Fato Market Share (Anatel)")
    mkt_samples = [
        ("2026-09", "Belém", "PA", "Claro", 225400, 53.6, 1250, 1),
        ("2026-09", "Belém", "PA", "Vivo", 112300, 26.7, 450, 2),
        ("2026-09", "Belém", "PA", "Oi", 48100, 11.4, -620, 3),
        ("2026-09", "Belém", "PA", "Competitivas/ISPs", 34800, 8.3, 310, 4),
        ("2026-09", "Manaus", "AM", "Claro", 298500, 56.8, 1680, 1),
        ("2026-09", "Manaus", "AM", "Vivo", 145200, 27.6, 720, 2),
        ("2026-09", "Manaus", "AM", "Oi", 52100, 9.9, -840, 3),
        ("2026-09", "Manaus", "AM", "Competitivas/ISPs", 29800, 5.7, 410, 4),
        ("2026-09", "São Luís", "MA", "Claro", 168200, 48.2, 940, 1),
        ("2026-09", "São Luís", "MA", "Vivo", 118400, 33.9, 610, 2),
        ("2026-09", "São Luís", "MA", "Competitivas/ISPs", 62400, 17.9, 520, 3),
        ("2026-09", "Macapá", "AP", "Claro", 58400, 51.2, 380, 1),
        ("2026-09", "Macapá", "AP", "Vivo", 35200, 30.8, 190, 2),
        ("2026-09", "Macapá", "AP", "Competitivas/ISPs", 20500, 18.0, 140, 3),
    ]
    for mes, cid, uf, oper, acessos, share, net, pos in mkt_samples:
        mid = f"mkt-{uuid.uuid4().hex[:12]}"
        sql_lines.append(
            f"INSERT OR REPLACE INTO fato_market_share (id, mes_referencia, cidade, uf, operadora, acessos, market_share_pct, net_adds, posicao_ranking) "
            f"VALUES ('{mid}', '{mes}', '{cid}', '{uf}', '{oper}', {acessos}, {share}, {net}, {pos});"
        )

    # Escreve arquivo final
    with open(OUTPUT_SQL, "w", encoding="utf-8") as f:
        f.write("\n".join(sql_lines) + "\n")

    print(f"[OK] Arquivo SQL gerado com sucesso em: {OUTPUT_SQL}")
    print(f"[OK] Total de instrucoes SQL geradas: {len(sql_lines)}")


if __name__ == "__main__":
    generate_seed_sql()
