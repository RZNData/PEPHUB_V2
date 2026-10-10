import subprocess
import json
import base64
import os

FFMPEG_PATH = r"C:\Users\F138138\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin\ffmpeg.exe"
PROPOSAL_ID = "72d61919-0a30-47bb-b4ff-df464753d4a2"
RAW_MP4 = "cirio_full.mp4"
OPT_MP4 = "cirio_tv_optimized.mp4"

print("[1/5] Extraindo chunks diretamente do D1 via wrangler...")
# Pega a contagem de chunks
cmd = ['npx', 'wrangler', 'd1', 'execute', 'pephub-db', '--remote', '--json', '--command',
       f"SELECT chunk_index, chunk_data FROM tv_media_chunks WHERE proposal_id = '{PROPOSAL_ID}' ORDER BY chunk_index ASC"]

# Como 57 chunks com base64 pode ser grande para uma única query CLI, vamos buscar em lotes de 10 chunks
full_file_bytes = bytearray()
BATCH_SIZE = 10
total_chunks_count = 57

for start_idx in range(0, total_chunks_count, BATCH_SIZE):
    end_idx = min(total_chunks_count - 1, start_idx + BATCH_SIZE - 1)
    print(f"  Baixando chunks {start_idx} a {end_idx}...")
    batch_cmd = [
        'npx', 'wrangler', 'd1', 'execute', 'pephub-db', '--remote', '--json', '--command',
        f"SELECT chunk_index, chunk_data FROM tv_media_chunks WHERE proposal_id = '{PROPOSAL_ID}' AND chunk_index >= {start_idx} AND chunk_index <= {end_idx} ORDER BY chunk_index ASC"
    ]
    proc = subprocess.run(batch_cmd, capture_output=True, encoding='utf-8', errors='replace', shell=True)
    out = proc.stdout
    json_start = out.find('[')
    json_end = out.rfind(']') + 1
    if json_start == -1:
        print("Erro ao extrair batch:", out)
        exit(1)
    data = json.loads(out[json_start:json_end])
    rows = data[0]['results']
    for r in rows:
        chunk_b64 = r['chunk_data']
        bin_data = base64.b64decode(chunk_b64)
        full_file_bytes.extend(bin_data)

print(f"Vídeo original reconstruído com sucesso! Tamanho: {len(full_file_bytes) / (1024*1024):.2f} MB")
with open(RAW_MP4, "wb") as f:
    f.write(full_file_bytes)

print("[2/5] Otimizando com FFmpeg para padrão de Smart TV / Firestick...")
# Reduz para 1080p com bitrate de 2.2 Mbps, áudio AAC, moov atom no início (+faststart), YUV420P
cmd_ffmpeg = [
    FFMPEG_PATH, "-y",
    "-i", RAW_MP4,
    "-c:v", "libx264",
    "-preset", "medium",
    "-crf", "22",
    "-maxrate", "2500k",
    "-bufsize", "5000k",
    "-pix_fmt", "yuv420p",
    "-profile:v", "high",
    "-level", "4.0",
    "-movflags", "+faststart",
    "-an", # Mudo (TV Corporativa opera sem áudio para não poluir o ambiente)
    OPT_MP4
]
subprocess.run(cmd_ffmpeg, check=True)

opt_size = os.path.getsize(OPT_MP4)
print(f"Vídeo otimizado criado com sucesso! Tamanho: {opt_size / (1024*1024):.2f} MB (era {len(full_file_bytes) / (1024*1024):.2f} MB)")

print("[3/5] Fatiando em chunks de 1MB...")
CHUNK_SIZE = 1024 * 1024
with open(OPT_MP4, "rb") as f:
    opt_bytes = f.read()

total_new_chunks = (len(opt_bytes) + CHUNK_SIZE - 1) // CHUNK_SIZE
print(f"Total de novos chunks leves: {total_new_chunks}")

chunks_list = []
for i in range(total_new_chunks):
    start = i * CHUNK_SIZE
    end = min(len(opt_bytes), start + CHUNK_SIZE)
    slice_b = opt_bytes[start:end]
    b64_str = base64.b64encode(slice_b).decode('ascii')
    chunks_list.append((i, b64_str))

print("[4/5] Atualizando tabela tv_media_chunks no D1...")
# 1. Deletar chunks antigos
del_cmd = [
    'npx', 'wrangler', 'd1', 'execute', 'pephub-db', '--remote', '--command',
    f"DELETE FROM tv_media_chunks WHERE proposal_id = '{PROPOSAL_ID}';"
]
subprocess.run(del_cmd, check=True, shell=True)

# 2. Inserir chunks novos um a um via statements rápidos
for idx, b64_str in chunks_list:
    chunk_id = f"opt-{PROPOSAL_ID[:8]}-{idx:04d}"
    ins_sql = f"INSERT INTO tv_media_chunks (id, proposal_id, chunk_index, chunk_data) VALUES ('{chunk_id}', '{PROPOSAL_ID}', {idx}, '{b64_str}');"
    ins_cmd = [
        'npx', 'wrangler', 'd1', 'execute', 'pephub-db', '--remote', '--command', ins_sql
    ]
    subprocess.run(ins_cmd, check=True, shell=True)
    print(f"  Chunk {idx + 1}/{total_new_chunks} gravado com sucesso.")

print("PROCESSO 100% CONCLUÍDO! O banco agora possui o vídeo leve e otimizado.")
