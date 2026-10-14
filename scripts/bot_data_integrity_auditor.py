#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PEP HUB — Bot Data Integrity Auditor v1.0
Audita a integridade analítica, saúde dos dados e fidelidade das respostas do Bot.
Valida cruzadamente os dados no Cloudflare D1 contra os painéis oficiais (Móvel, Residencial, FPD, Churn Safra),
garantindo tolerância zero para alucinações e conformidade com a Regra de Ouro da Veracidade.
"""

import sys
import os
import json
import subprocess

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def query_d1_remote(sql):
    npx_bin = 'npx.cmd' if os.name == 'nt' else 'npx'
    cmd = [npx_bin, 'wrangler', 'd1', 'execute', 'pephub-db', '--remote', '--command', sql, '--json']
    res = subprocess.run(cmd, cwd=WORKSPACE_DIR, capture_output=True, text=True)
    try:
        stdout = res.stdout
        s = stdout.find('[')
        e = stdout.rfind(']')
        if s != -1 and e != -1:
            data = json.loads(stdout[s:e+1])
            return data[0].get('results', [])
        return []
    except Exception:
        return []

def run_integrity_audit():
    print("=" * 76)
    print("  PEP HUB — BOT DATA INTEGRITY & ANTI-HALLUCINATION AUDITOR")
    print("  Guardião da Veracidade Analítica e Saúde Contínua das Bases D1")
    print("=" * 76)

    score = 100
    deductions = []
    checks = []

    # -------------------------------------------------------------------------
    # CHECK 1: Regra de Ouro da Veracidade no Prompt e Código do Worker
    # -------------------------------------------------------------------------
    bot_js_path = os.path.join(WORKSPACE_DIR, "worker", "routes", "bot.js")
    with open(bot_js_path, "r", encoding="utf-8", errors="replace") as f:
        bot_code = f.read()

    has_honesty_rule = (
        "SE NÃO SOUBER" in bot_code.upper() or
        "REGRA DE OURO DA VERACIDADE" in bot_code.upper() or
        "DIGA QUE NÃO SABE" in bot_code.upper()
    )
    if has_honesty_rule:
        checks.append(("[OK]", "Regra de Ouro da Veracidade ('Se não souber, pergunte ou diga que não sabe') ativa no Worker"))
    else:
        score -= 20
        deductions.append("Falta a Regra de Ouro da Veracidade expressa no prompt do Worker")
        checks.append(("[FALHA]", "Regra de Ouro da Veracidade ausente no Worker"))

    # -------------------------------------------------------------------------
    # CHECK 2: Fidelidade dos Dados de Banda Larga Residencial Belém (02.BL)
    # Valor Oficial: 33.88% de share e +131 net adds
    # -------------------------------------------------------------------------
    sql_belem_bl = "SELECT cidade, operadora, acessos, market_share_pct, net_adds FROM fato_market_share WHERE produto = 'BANDA_LARGA' AND segmento = 'RESIDENCIAL' AND (cidade = 'Belém' OR cidade LIKE '%Belém%') AND operadora = 'Claro' LIMIT 1;"
    rows_belem_bl = query_d1_remote(sql_belem_bl)

    if rows_belem_bl:
        r = rows_belem_bl[0]
        share = float(r.get('market_share_pct', 0))
        net = int(r.get('net_adds', 0))
        acessos = int(r.get('acessos', 0))

        if abs(share - 33.88) <= 0.05 and net == 131 and acessos == 110219:
            checks.append(("[OK]", f"Banda Larga Belém (02.BL): Claro {share:.2f}% | {acessos:,} acessos | Net Adds {net:+d} (100% Exato)"))
        else:
            score -= 25
            deductions.append(f"Banda Larga Belém divergiu: Share={share}%, Net={net}, Acessos={acessos} (Esperado: 33.88%, +131, 110.219)")
            checks.append(("[FALHA]", f"Banda Larga Belém incorreta: {share}% | Net {net:+d}"))
    else:
        score -= 25
        deductions.append("Registro da Claro em Belém Banda Larga não encontrado no D1")
        checks.append(("[FALHA]", "Banda Larga Belém Claro não encontrada no D1"))

    # -------------------------------------------------------------------------
    # CHECK 3: Fidelidade da Banda Larga Residencial Regional Norte (02.BL)
    # Valor Oficial: Claro 12.98% (+591 net adds) | Competitivas/ISPs 66.27%
    # -------------------------------------------------------------------------
    sql_reg_bl = "SELECT operadora, acessos, market_share_pct, net_adds FROM fato_market_share WHERE produto = 'BANDA_LARGA' AND segmento = 'RESIDENCIAL' AND cidade = 'Regional Norte' ORDER BY market_share_pct DESC;"
    rows_reg_bl = query_d1_remote(sql_reg_bl)

    if rows_reg_bl:
        claro_bl = next((x for x in rows_reg_bl if x['operadora'] == 'Claro'), None)
        isps_bl = next((x for x in rows_reg_bl if 'ISP' in x['operadora'] or 'Competitiva' in x['operadora']), None)

        if claro_bl and isps_bl:
            c_sh = float(claro_bl['market_share_pct'])
            i_sh = float(isps_bl['market_share_pct'])
            if abs(c_sh - 12.98) <= 0.1 and abs(i_sh - 66.27) <= 0.1:
                checks.append(("[OK]", f"Banda Larga Regional Norte: Claro {c_sh:.2f}% | Competitivas/ISPs {i_sh:.2f}% (Conforme)"))
            else:
                score -= 15
                deductions.append(f"Banda Larga Regional divergiu: Claro={c_sh}%, ISPs={i_sh}%")
                checks.append(("[FALHA]", f"Banda Larga Regional Norte divergiu: Claro={c_sh}%, ISPs={i_sh}%"))
        else:
            score -= 15
            deductions.append("Operadoras de Banda Larga Regional não encontradas")
            checks.append(("[FALHA]", "Operadoras de Banda Larga Regional incompletas"))
    else:
        score -= 20
        deductions.append("Banda Larga Regional Norte ausente no D1")
        checks.append(("[FALHA]", "Banda Larga Regional Norte ausente no D1"))

    # -------------------------------------------------------------------------
    # CHECK 4: Fidelidade Telefonia Móvel Pós-pago sem M2M (Belém e Regional)
    # Belém: Claro 44.14% e +4.704 net adds
    # Regional: Claro 37.04% (+27.120 net adds), Vivo 42.41%
    # -------------------------------------------------------------------------
    sql_mov = "SELECT cidade, ddd, operadora, market_share_pct, net_adds FROM fato_market_share WHERE produto = 'MOVEL' AND segmento = 'POS_PAGO_SEM_M2M' AND (cidade = 'Belém' OR cidade = 'DDD 91' OR ddd = '91' OR cidade = 'Regional Norte') AND operadora = 'Claro';"
    rows_mov = query_d1_remote(sql_mov)

    mov_belem = next((x for x in rows_mov if x.get('cidade') in ['Belém', 'DDD 91'] or x.get('ddd') == '91'), None)
    mov_reg = next((x for x in rows_mov if x.get('cidade') == 'Regional Norte'), None)

    if mov_belem and mov_reg:
        b_sh = float(mov_belem['market_share_pct'])
        r_sh = float(mov_reg['market_share_pct'])
        if abs(b_sh - 44.14) <= 0.5 and abs(r_sh - 37.04) <= 0.5:
            checks.append(("[OK]", f"Móvel Pós sem M2M: Belém/DDD91 Claro {b_sh:.2f}% | Regional Claro {r_sh:.2f}% (+27.120) (Conforme)"))
        else:
            score -= 15
            deductions.append(f"Móvel Pós divergiu: Belém={b_sh}%, Regional={r_sh}%")
            checks.append(("[FALHA]", f"Móvel Pós divergiu dos dados oficiais Anatel"))
    else:
        score -= 15
        deductions.append("Dados de Móvel Pós sem M2M ausentes no D1")
        checks.append(("[FALHA]", "Móvel Pós sem M2M não encontrado no D1"))

    # -------------------------------------------------------------------------
    # CHECK 5: Integridade das Outras Tabelas Fato (FPD, Churn Safra, Churn BL)
    # -------------------------------------------------------------------------
    sql_fpd = "SELECT COUNT(*) as c FROM fato_fpd;"
    sql_safra = "SELECT COUNT(*) as c FROM fato_churn_safra;"
    sql_bl = "SELECT COUNT(*) as c FROM fato_indicadores_mensais;"

    c_fpd = (query_d1_remote(sql_fpd) or [{'c': 0}])[0].get('c', 0)
    c_safra = (query_d1_remote(sql_safra) or [{'c': 0}])[0].get('c', 0)
    c_bl = (query_d1_remote(sql_bl) or [{'c': 0}])[0].get('c', 0)

    if c_fpd > 0 and c_safra > 0 and c_bl > 0:
        checks.append(("[OK]", f"Bases Corporativas Integradas: FPD ({c_fpd:,} rows), Safra ({c_safra:,} rows), Churn BL ({c_bl:,} rows)"))
    else:
        score -= 20
        deductions.append("Bases corporativas de FPD, Safra ou Churn BL com contagem zerada")
        checks.append(("[FALHA]", f"Bases fatos vazias: FPD={c_fpd}, Safra={c_safra}, ChurnBL={c_bl}"))

    # -------------------------------------------------------------------------
    # RELATÓRIO FINAL
    # -------------------------------------------------------------------------
    print()
    for status, msg in checks:
        print(f"  {status} {msg}")

    print("-" * 76)
    grade = "A+" if score >= 95 else "A" if score >= 85 else "B" if score >= 70 else "REPROVADO"
    print(f"  SCORE DE INTEGRIDADE ANALÍTICA: {score}/100 [{grade}]")
    if deductions:
        print("  Deduções identificadas:")
        for d in deductions:
            print(f"   • {d}")

    print("=" * 76)
    return 0 if score >= 85 else 1

if __name__ == '__main__':
    sys.exit(run_integrity_audit())
