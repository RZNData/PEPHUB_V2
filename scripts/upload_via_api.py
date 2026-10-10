import urllib.request
import ssl
import json
import base64
import os

PROPOSAL_ID = "72d61919-0a30-47bb-b4ff-df464753d4a2"
FILE_PATH = "cirio_tv_optimized.mp4"
CHUNK_SIZE = 1024 * 1024 # 1MB por fatia

ctx = ssl._create_unverified_context()

print(f"[1/3] Lendo arquivo otimizado {FILE_PATH} ({os.path.getsize(FILE_PATH)/(1024*1024):.2f} MB)...")
with open(FILE_PATH, "rb") as f:
    video_bytes = f.read()

total_chunks = (len(video_bytes) + CHUNK_SIZE - 1) // CHUNK_SIZE
print(f"Total de fatias: {total_chunks}")

print("[2/3] Limpando chunks anteriores no D1 via reset-chunks...")
reset_req = urllib.request.Request(
    f"https://pephub.cloud/api/tv/proposals/{PROPOSAL_ID}/reset-chunks",
    data=b"{}",
    headers={
        "Content-Type": "application/json",
        "x-admin-key": "pephub-tv-sync-2026",
        "User-Agent": "Mozilla/5.0"
    },
    method="POST"
)
with urllib.request.urlopen(reset_req, context=ctx) as r:
    print("Reset status:", r.status, r.read().decode())

print("[3/3] Enviando novas fatias otimizadas...")
for idx in range(total_chunks):
    start = idx * CHUNK_SIZE
    end = min(len(video_bytes), start + CHUNK_SIZE)
    slice_data = video_bytes[start:end]
    b64_str = base64.b64encode(slice_data).decode("ascii")

    payload = json.dumps({
        "chunk_index": idx,
        "chunk_data": b64_str
    }).encode("utf-8")

    chunk_req = urllib.request.Request(
        f"https://pephub.cloud/api/tv/proposals/{PROPOSAL_ID}/chunk",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-admin-key": "pephub-tv-sync-2026",
            "User-Agent": "Mozilla/5.0"
        },
        method="POST"
    )
    with urllib.request.urlopen(chunk_req, context=ctx) as cr:
        res = json.loads(cr.read().decode())
        print(f"  Chunk {idx + 1}/{total_chunks} enviado com sucesso! (Index {res.get('chunk_index')})")

print("TODOS OS CHUNKS OTIMIZADOS FORAM CARREGADOS COM SUCESSO NO D1!")
