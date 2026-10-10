import random

cidades = [
    ('Regional Norte', 'RNO'),
    ('Manaus', 'AM'),
    ('Belém', 'PA'),
    ('São Luís', 'MA'),
    ('Ananindeua', 'PA'),
    ('Macapá', 'AP'),
    ('Santana', 'AP'),
    ('Imperatriz', 'MA'),
    ('Castanhal', 'PA'),
    ('Parauapebas', 'PA'),
    ('Marabá', 'PA'),
    ('Paragominas', 'PA'),
    ('Timon', 'MA'),
    ('Caxias', 'MA'),
    ('Boa Vista', 'RR'),
]

canais = ['PAP', 'Lojas', 'Televendas', 'Agente Autorizado']
produtos = [
    ('Dados', 'Produto Banda Larga'),
    ('Vídeo', 'TV Tradicional'),
    ('Box', 'TV Box')
]
safras_fpd = [
    ('mai/26', '2026-05'),
    ('abr/26', '2026-04'),
    ('mar/26', '2026-03'),
]

parceiros = [
    ('TOP CONNECT TELECOM', 'PAP', 7.8, 5.9),
    ('SADDI E SANTOS LTDA.', 'PAP', 9.2, 7.1),
    ('FLEX CELL COMERCIO', 'Lojas', 5.1, 3.4),
    ('CLARO SA LOJAS PROPRIAS', 'Lojas', 4.5, 3.0),
    ('CALLINK TELEMARKETING', 'Televendas', 8.4, 6.2),
    ('BRASILCENTER TELEVENDAS', 'Televendas', 7.9, 5.8),
    ('ALLIANCE CONTACT CENTER', 'Televendas', 8.1, 6.0),
    ('AEC CENTRO DE CONTATOS', 'Televendas', 8.6, 6.5),
    ('JNNVB TELECOM', 'Agente Autorizado', 6.8, 4.9),
    ('REDE CONECTA SERVICOS', 'PAP', 8.9, 6.8),
    ('SPEED COMERCIO E SERVICOS', 'Agente Autorizado', 7.2, 5.1),
    ('NORTE CELL DISTRIBUIDORA', 'Lojas', 5.8, 3.9),
]

vendedores = [
    ('Carlos Eduardo Silva', 'PAP'),
    ('Mariana Oliveira Costa', 'Lojas'),
    ('Lucas Pereira Santos', 'Televendas'),
    ('Juliana Almeida Rocha', 'Agente Autorizado'),
    ('Rodrigo Souza Lima', 'PAP'),
    ('Fernanda Ribeiro Melo', 'Lojas'),
    ('Gabriel Martins Barbosa', 'Televendas'),
    ('Aline Carvalho Castro', 'Agente Autorizado'),
]

sql_lines = []
sql_lines.append("-- LIMPAR E POPULAR FATO_FPD COM DADOS 100% EXCLUSIVOS DE FPD")
sql_lines.append("DELETE FROM fato_fpd;")

# 1. Inserir fatos agregados de FPD (por cidade, canal, produto e safra)
cnt = 0
for cid, uf in cidades:
    for can in canais:
        for p_code, p_name in produtos:
            for saf_label, saf_ord in safras_fpd:
                cnt += 1
                fid = f"fpd-{cnt:05d}"
                # Base volume
                if cid == 'Regional Norte':
                    inst = random.randint(4000, 6000)
                elif cid in ['Manaus', 'Belém', 'São Luís']:
                    inst = random.randint(900, 1600)
                else:
                    inst = random.randint(250, 650)
                
                # FPD 30 rate 6.5% - 10.5%
                tx_fpd30 = round(random.uniform(6.5, 10.5), 2)
                fpd30 = int(inst * tx_fpd30 / 100.0)
                
                # Cura 22% - 32%
                tx_cura = round(random.uniform(22.0, 32.0), 2)
                cura = int(fpd30 * tx_cura / 100.0)
                
                # FPD 60 rate = FPD 30 - Cura efetiva
                fpd60 = fpd30 - cura
                tx_fpd60 = round(100.0 * fpd60 / inst, 2)
                
                # Associar um parceiro e vendedor representativo
                parc_cand = [p for p in parceiros if p[1] == can] or parceiros
                p_item = random.choice(parc_cand)
                vend_cand = [v for v in vendedores if v[1] == can] or vendedores
                v_item = random.choice(vend_cand)

                sql_lines.append(
                    f"INSERT INTO fato_fpd (id, safra, safra_ord, cidade, uf, canal, familia_produto, parceiro, vendedor, instalacoes, fpd30, taxa_fpd30, fpd60, taxa_fpd60, cura, taxa_cura, faixa_risco) "
                    f"VALUES ('{fid}', '{saf_label}', '{saf_ord}', '{cid}', '{uf}', '{can}', '{p_code}', '{p_item[0]}', '{v_item[0]}', {inst}, {fpd30}, {tx_fpd30}, {fpd60}, {tx_fpd60}, {cura}, {tx_cura}, 'MEDIO');"
                )

# 2. Inserir linhas dedicadas por parceiro na safra mais recente (para ranking detalhado de parceiros no FPD)
for p_name, p_can, base_fpd30, base_fpd60 in parceiros:
    for saf_label, saf_ord in safras_fpd:
        for cid, uf in cidades:
            cnt += 1
            fid = f"fpd-parc-{cnt:05d}"
            inst = random.randint(80, 450) if cid != 'Regional Norte' else random.randint(1200, 2800)
            tx_fpd30 = round(base_fpd30 + random.uniform(-1.0, 1.2), 2)
            fpd30 = int(inst * tx_fpd30 / 100.0)
            tx_cura = round(random.uniform(22.0, 30.0), 2)
            cura = int(fpd30 * tx_cura / 100.0)
            fpd60 = max(1, fpd30 - cura)
            tx_fpd60 = round(100.0 * fpd60 / inst, 2)

            sql_lines.append(
                f"INSERT INTO fato_fpd (id, safra, safra_ord, cidade, uf, canal, familia_produto, parceiro, vendedor, instalacoes, fpd30, taxa_fpd30, fpd60, taxa_fpd60, cura, taxa_cura, faixa_risco) "
                f"VALUES ('{fid}', '{saf_label}', '{saf_ord}', '{cid}', '{uf}', '{p_can}', 'Dados', '{p_name}', 'Consultor PJ', {inst}, {fpd30}, {tx_fpd30}, {fpd60}, {tx_fpd60}, {cura}, {tx_cura}, 'MEDIO');"
            )

# 3. POPULAR FATO_SPEECH_ANALYTICS (Últimos 3 meses: Set/26, Ago/26, Jul/26)
sql_lines.append("\n-- LIMPAR E POPULAR FATO_SPEECH_ANALYTICS")
sql_lines.append("DELETE FROM fato_speech_analytics;")

motivos_speech_base = [
    ('Acha Caro / Aumento no Valor', 26.5, 1.2, 'Alta'),
    ('Técnico - Internet / Lentidão', 19.8, -0.8, 'Queda'),
    ('Não Concorda e/ou Consulta Valores', 14.2, 0.4, 'Estável'),
    ('Mudança de Endereço / Inviabilidade', 11.5, 0.9, 'Alta'),
    ('Não Pedi / Não Reconhece Contratação', 8.7, -0.3, 'Estável'),
    ('Concorrência / Ofertas Mais Baratas', 7.9, 0.2, 'Estável'),
    ('Sem / Pouca Utilização do Serviço', 5.4, -0.5, 'Queda'),
    ('Dificuldade Financeira / Desemprego', 3.8, -0.7, 'Queda'),
    ('Reajuste Anual de Contrato', 2.2, -0.4, 'Estável'),
]

meses_speech = [
    ('Set/26', '2026-09', 1.0),
    ('Ago/26', '2026-08', 0.95),
    ('Jul/26', '2026-07', 0.90),
]

s_cnt = 0
for cid, uf in cidades:
    for m_label, m_ord, m_factor in meses_speech:
        for s_name, s_pct, s_mom, s_tend in motivos_speech_base:
            s_cnt += 1
            sid = f"speech-{s_cnt:05d}"
            # Ajustar ligeiramente por mês
            val_pct = round(s_pct * m_factor + random.uniform(-0.4, 0.4), 1)
            val_mom = round(s_mom + random.uniform(-0.2, 0.2), 1) if m_ord == '2026-09' else round(random.uniform(-0.6, 0.6), 1)
            sql_lines.append(
                f"INSERT INTO fato_speech_analytics (id, mes_referencia, mes_ord, cidade, uf, motivo_speech, pct_mix, mom_pp, tendencia) "
                f"VALUES ('{sid}', '{m_label}', '{m_ord}', '{cid}', '{uf}', '{s_name}', {val_pct}, {val_mom}, '{s_tend}');"
            )

# 4. POPULAR FATO_MOTIVOS_OS (Últimos 3 meses: Set/26, Ago/26, Jul/26)
sql_lines.append("\n-- LIMPAR E POPULAR FATO_MOTIVOS_OS")
sql_lines.append("DELETE FROM fato_motivos_os;")

motivos_procura_base = [
    ('Financeiro / Fatura', 2400, 27.1, 214, 8.9, -0.8, 'Controlado'),
    ('Cancelamento Automático (URA)', 1700, 19.2, 446, 26.3, 0.8, 'Alto'),
    ('Lentidão / Sem Conexão', 1450, 16.4, 510, 35.2, 1.5, 'Crítico'),
    ('Mudança de Endereço', 890, 10.0, 342, 38.5, 3.7, 'Crítico'),
    ('Concorrência / Portabilidade', 1050, 11.8, 160, 15.2, -0.2, 'Moderado'),
    ('Atrito de Atendimento', 530, 6.0, 56, 10.6, -0.4, 'Controlado'),
]

m_cnt = 0
for cid, uf in cidades:
    for m_label, m_ord, m_factor in meses_speech:
        for mot_name, b_calls, b_mix, b_os, b_tx, b_mom, b_stat in motivos_procura_base:
            m_cnt += 1
            mid = f"mot-{m_cnt:05d}"
            cid_scale = 1.0 if cid == 'Regional Norte' else (0.35 if cid in ['Manaus', 'Belém', 'São Luís'] else 0.12)
            c_calls = int(b_calls * cid_scale * m_factor)
            c_tx_os = round(b_tx + random.uniform(-1.2, 1.5), 1)
            c_os = int(c_calls * c_tx_os / 100.0)
            c_mom = round(b_mom + random.uniform(-0.3, 0.3), 1) if m_ord == '2026-09' else round(random.uniform(-0.8, 0.8), 1)
            
            sql_lines.append(
                f"INSERT INTO fato_motivos_os (id, mes_referencia, mes_ord, cidade, uf, motivo_procura, ligacoes, mix_pct, os_geradas, taxa_os_pct, taxa_os_mom_pp, status) "
                f"VALUES ('{mid}', '{m_label}', '{m_ord}', '{cid}', '{uf}', '{mot_name}', {c_calls}, {b_mix}, {c_os}, {c_tx_os}, {c_mom}, '{b_stat}');"
            )

with open('scripts/generated_seed_datasets.sql', 'w', encoding='utf-8') as f:
    f.write('\n'.join(sql_lines))

print(f"Gerado com sucesso! Linhas SQL: {len(sql_lines)}")
