import sys
import subprocess
import os

sys.stdout.reconfigure(encoding='utf-8')

with open('scripts/seed_real_corporate_data.sql', 'r', encoding='utf-8') as f:
    full_sql = f.read()

# Split into individual statements
stmts = [s.strip() for s in full_sql.split(';') if s.strip() and not s.strip().startswith('--')]
print(f"Total SQL statements to execute: {len(stmts)}")

batch_size = 80
batches = [stmts[i:i + batch_size] for i in range(0, len(stmts), batch_size)]
print(f"Total batches: {len(batches)}")

batch_file = 'scripts/temp_batch.sql'

for idx, b in enumerate(batches):
    print(f"\nExecuting batch {idx+1}/{len(batches)} ({len(b)} statements)...")
    with open(batch_file, 'w', encoding='utf-8') as bf:
        bf.write(';\n'.join(b) + ';\n')
    
    cmd = "npx wrangler d1 execute pephub-db --remote --file=scripts/temp_batch.sql"
    res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', shell=True)
    if res.returncode != 0:
        print(f"Error on batch {idx+1}:")
        print(res.stderr or res.stdout)
        sys.exit(1)
    else:
        print(f"Batch {idx+1} OK!")

if os.path.exists(batch_file):
    os.remove(batch_file)

print("\n=== TODOS OS BATCHES FORAM EXECUTADOS COM SUCESSO NO D1 REMOTO! ===")
