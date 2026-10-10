import os
import base64
import subprocess

CHUNK_SIZE = 512 * 1024 # 512KB por chunk (Base64 ~682KB < 1MB limit de SQLITE_TOOBIG)
PROPOSAL_ID = '72d61919-0a30-47bb-b4ff-df464753d4a2'

with open('cirio_tv_optimized.mp4', 'rb') as f:
    opt_bytes = f.read()

total_chunks = (len(opt_bytes) + CHUNK_SIZE - 1) // CHUNK_SIZE
print(f'Total de fatias de 512KB para inserir: {total_chunks}')

# Limpa registros antigos
subprocess.run(['npx', 'wrangler', 'd1', 'execute', 'pephub-db', '--remote', '--command', f"DELETE FROM tv_media_chunks WHERE proposal_id = '{PROPOSAL_ID}';"], shell=True, check=True)

for idx in range(total_chunks):
    start = idx * CHUNK_SIZE
    end = min(len(opt_bytes), start + CHUNK_SIZE)
    slice_b = opt_bytes[start:end]
    b64_str = base64.b64encode(slice_b).decode('ascii')
    
    sql_path = f'temp_chunk_{idx}.sql'
    chunk_id = f'opt-{PROPOSAL_ID[:8]}-{idx:04d}'
    with open(sql_path, 'w', encoding='utf-8') as sf:
        sf.write(f"INSERT INTO tv_media_chunks (id, proposal_id, chunk_index, chunk_data) VALUES ('{chunk_id}', '{PROPOSAL_ID}', {idx}, '{b64_str}');\n")
    
    size_kb = os.path.getsize(sql_path) / 1024
    print(f'Gravando chunk {idx + 1}/{total_chunks} ({size_kb:.1f} KB)...')
    res = subprocess.run(['npx', 'wrangler', 'd1', 'execute', 'pephub-db', '--remote', f'--file={sql_path}'], capture_output=True, encoding='utf-8', errors='replace', shell=True)
    if res.returncode != 0:
        err_msg = (res.stderr or '') + (res.stdout or '')
        clean_err = err_msg.encode('ascii', 'replace').decode('ascii')
        print(f'Erro no chunk {idx}: {clean_err[:300]}')
        break
    else:
        print(f'  -> Chunk {idx + 1}/{total_chunks} gravado com sucesso!')
    if os.path.exists(sql_path):
        os.remove(sql_path)

print('Upload de todas as fatias concluído!')
