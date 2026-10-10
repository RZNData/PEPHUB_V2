import os
import subprocess
import urllib.request
import ssl
import json
import base64

FFMPEG_PATH = r"C:\Users\F138138\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin\ffmpeg.exe"
PROPOSAL_ID = "72d61919-0a30-47bb-b4ff-df464753d4a2"
ORIGINAL_MP4 = "cirio_original.mp4"
OPTIMIZED_MP4 = "cirio_optimized.mp4"

print("[1/5] Baixando vídeo original de 58.9 MB da TV...")
ctx = ssl._create_unverified_context()
url = f"https://pephub.cloud/api/tv/media/{PROPOSAL_ID}"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Range": "bytes=0-58970418"})
with urllib.request.urlopen(req, context=ctx) as resp:
    data = resp.read()
    with open(ORIGINAL_MP4, "wb") as f:
        f.write(data)

orig_size = os.path.getsize(ORIGINAL_MP4)
print(f"Original salvo: {orig_size / (1024*1024):.2f} MB")

print("[2/5] Otimizando vídeo com FFmpeg (H.264 High 4.0, 1080p, 2.5 Mbps, +faststart)...")
# Parâmetros de alta compatibilidade para Firestick/Smart TVs
cmd = [
    FFMPEG_PATH, "-y",
    "-i", ORIGINAL_MP4,
    "-c:v", "libx264",
    "-preset", "medium",
    "-crf", "22",
    "-maxrate", "2800k",
    "-bufsize", "5600k",
    "-pix_fmt", "yuv420p",
    "-profile:v", "high",
    "-level", "4.0",
    "-movflags", "+faststart",
    "-c:a", "aac",
    "-b:a", "128k",
    "-ar", "44100",
    OPTIMIZED_MP4
]
subprocess.run(cmd, check=True)

opt_size = os.path.getsize(OPTIMIZED_MP4)
reduction = (1 - opt_size / orig_size) * 100
print(f"Otimizado salvo: {opt_size / (1024*1024):.2f} MB (Redução de {reduction:.1f}%!)")

print("[3/5] Fatiando novo vídeo em chunks de 1MB...")
CHUNK_SIZE = 1024 * 1024
with open(OPTIMIZED_MP4, "rb") as f:
    opt_bytes = f.read()

total_chunks = (len(opt_bytes) + CHUNK_SIZE - 1) // CHUNK_SIZE
print(f"Total de novos chunks: {total_chunks}")

chunks_data = []
for i in range(total_chunks):
    start = i * CHUNK_SIZE
    end = min(len(opt_bytes), start + CHUNK_SIZE)
    slice_bytes = opt_bytes[start:end]
    b64 = base64.b64encode(slice_bytes).decode('ascii')
    chunks_data.append((i, b64))

print("[4/5] Salvando chunks em script SQL para aplicação no D1...")
sql_file = "update_cirio_chunks.sql"
with open(sql_file, "w", encoding="utf-8") as f:
    f.write(f"DELETE FROM tv_media_chunks WHERE proposal_id = '{PROPOSAL_ID}';\n")
    for idx, b64 in chunks_data:
        chunk_uuid = f"chunk-{PROPOSAL_ID[:8]}-{idx:04d}"
        f.write(f"INSERT INTO tv_media_chunks (id, proposal_id, chunk_index, chunk_data) VALUES ('{chunk_uuid}', '{PROPOSAL_ID}', {idx}, '{b64}');\n")

print(f"Arquivo SQL gerado: {sql_file}")

print("[5/5] Executando atualização no D1 pephub-db...")
d1_cmd = f"npx wrangler d1 execute pephub-db --remote --file={sql_file}"
subprocess.run(d1_cmd, shell=True, check=True)

print("CONCLUÍDO COM SUCESSO! O vídeo agora é leve, rápido e compatível com Firestick.")
