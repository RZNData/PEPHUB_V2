import sys
with open('Painel_Churn_Safra 28.html', 'r', encoding='utf-8', errors='ignore') as f:
    full = f.read()

# achar ocorrencias de PAYLOAD no script
idx = 0
while True:
    pos = full.find('PAYLOAD', idx)
    if pos == -1:
        break
    if pos > 45400 and pos < 477900:
        # pular o meio do json do payload
        idx = 477900
        continue
    print(f"PAYLOAD em {pos}:")
    print(full[max(0, pos - 50): min(len(full), pos + 250)])
    idx = pos + 7
