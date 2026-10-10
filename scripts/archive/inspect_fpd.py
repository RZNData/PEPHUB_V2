import csv
import json
import re

print("=== 1. ANALISANDO FPD_JAN_MAI_26.csv ===")
with open('FPD_JAN_MAI_26.csv', 'r', encoding='latin1', errors='ignore') as f:
    reader = csv.reader(f, delimiter=';')
    headers = next(reader)
    print(f"Total de colunas: {len(headers)}")
    
    # Identificar colunas importantes
    keywords = ['SAFRA', 'PARCEIRO', 'VENDEDOR', 'CIDADE', 'CANAL', 'SCORE', 'FPD', 'INAD', 'BASE', 'DENOMINADOR', 'PAG', 'OVER', 'AGING', 'PRODUTO', 'UF', 'REGIONAL', 'STATUS', 'VALOR', 'VL']
    key_cols = [(idx, h) for idx, h in enumerate(headers) if any(k in h.upper() for k in keywords)]
    print("\nColunas relevantes encontradas:")
    for idx, h in key_cols:
        print(f"  [{idx:3d}] {h}")
        
    # Ler primeiras 5 linhas para ver exemplos de valores
    sample_rows = [next(reader) for _ in range(5)]
    print("\nExemplo de valores para colunas chave na 1a linha:")
    first = sample_rows[0]
    for idx, h in key_cols[:25]:
        val = first[idx] if idx < len(first) else ""
        print(f"  {h} = {val}")

print("\n=== 2. ANALISANDO ESTRUTURA DO fpd_dashboard_standalone.html ===")
with open('fpd_dashboard_standalone.html', 'r', encoding='utf-8', errors='ignore') as f:
    # Ler chunks para procurar strings de métricas e abas
    text = f.read(2000000) # primeiros 2MB
    
    # Procurar padrões de títulos, abas ou KPIs
    terms = ['Taxa FPD', 'FPD', 'Primeiro Pagamento', 'First Payment', 'Inadimplência', 'Safra', 'Parceiro', 'Vendedor', 'Canal', 'Score', 'Aging']
    for t in terms:
        count = text.count(t)
        print(f"Ocorrências de '{t}': {count}")

