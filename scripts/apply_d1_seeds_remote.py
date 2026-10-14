# scripts/apply_d1_seeds_remote.py
import subprocess
import os
import sys
import time

def run_chunk(filepath):
    cmd = f'npx wrangler d1 execute pephub-db --remote --file={filepath}'
    res = subprocess.run(cmd, shell=True)
    return res.returncode == 0

def main():
    print("[*] Lendo seed_market_share_batches.sql...")
    with open("seed_market_share_batches.sql", "r", encoding="utf-8") as f:
        content = f.read()

    # Separa por ponto e vírgula e remove vazios
    raw_stmts = [s.strip().rstrip(';') for s in content.split(';') if s.strip()]
    statements = [s + ';' for s in raw_stmts if len(s) > 10]
    print(f"[*] Total de statements validos a executar: {len(statements)}")

    CHUNK_SIZE = 15
    total_chunks = (len(statements) + CHUNK_SIZE - 1) // CHUNK_SIZE

    for idx, i in enumerate(range(0, len(statements), CHUNK_SIZE), start=1):
        chunk = statements[i:i + CHUNK_SIZE]
        temp_file = f"temp_chunk_{idx}.sql"
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write("\n\n".join(chunk) + "\n")

        print(f"[*] Executando chunk {idx}/{total_chunks} ({len(chunk)} stmts)...")
        success = False
        for attempt in range(3):
            if run_chunk(temp_file):
                success = True
                break
            print(f"[!] Tentativa {attempt + 1} falhou. Tentando novamente em 3s...")
            time.sleep(3)

        try:
            os.remove(temp_file)
        except:
            pass

        if not success:
            print(f"[ERRO] Falha no chunk {idx}. Abortando.")
            sys.exit(1)

        time.sleep(1)

    print("[OK] Carga de Market Share (Movel + Residencial) concluida com 100% de sucesso!")

if __name__ == "__main__":
    main()
