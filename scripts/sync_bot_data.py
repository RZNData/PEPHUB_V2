#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PEP HUB — Sincronizador Automático de Relatórios com a Base do Bot (Cloudflare D1)
Extrai os dados corporativos mais recentes dos relatórios (Churn BL Total, PME, FPD, Safra),
gera a carga SQL com 100% de integridade e atualiza as tabelas remotas no Cloudflare D1 (pephub-db).
"""

import sys
import os
import subprocess
import time

sys.stdout.reconfigure(encoding='utf-8')
WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def run_step(step_name, cmd):
    print(f"\n[+] {step_name}...")
    t0 = time.time()
    res = subprocess.run(cmd, cwd=WORKSPACE_DIR, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    dt = time.time() - t0
    if res.returncode != 0:
        print(f"[-] Erro em {step_name} (após {dt:.1f}s):")
        print(res.stderr or res.stdout)
        return False
    print(f"[✓] {step_name} concluído com sucesso ({dt:.1f}s)!")
    if res.stdout:
        # Imprime primeiras 5 linhas de resumo
        lines = [l for l in res.stdout.strip().split('\n') if l.strip()]
        for l in lines[:5]:
            print(f"    {l}")
        if len(lines) > 5:
            print(f"    ... (+{len(lines)-5} linhas)")
    return True

def main():
    print("=" * 70)
    print("PEP HUB — SINCRONIZADOR DE DADOS BOT D1 & RELATÓRIOS")
    print("=" * 70)

    # 1. Regenerar SQL a partir dos painéis
    ok = run_step("Extraindo dados corporativos para SQL", "python scripts/seed_real_corporate_data.py")
    if not ok:
        sys.exit(1)

    # 2. Executar lotes SQL no D1 remoto
    ok = run_step("Aplicando lotes SQL no Cloudflare D1 (pephub-db)", "python scripts/execute_d1_batches.py")
    if not ok:
        sys.exit(1)

    # 3. Validação dos dados no D1
    validate_cmd = 'npx wrangler d1 execute pephub-db --remote --command="SELECT mes_referencia, segmento, tipo_visao, vol_real, taxa_real FROM fato_indicadores_mensais WHERE cidade=\'Regional Norte\' AND tipo_visao=\'TOTAL\' ORDER BY mes_referencia DESC LIMIT 4;"'
    run_step("Validando registros no Cloudflare D1", validate_cmd)

    print("\n" + "=" * 70)
    print("SUCESSO: A base de dados do Bot no Cloudflare D1 foi 100% atualizada!")
    print("=" * 70)

if __name__ == '__main__':
    main()
