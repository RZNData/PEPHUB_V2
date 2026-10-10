import pandas as pd

months_keys = [
    ('2025-01', 'Jan/25', ['jan/25', 'j/25']),
    ('2025-02', 'Fev/25', ['fev/25', 'f/25']),
    ('2025-03', 'Mar/25', ['mar/25', 'm/25']),
    ('2025-04', 'Abr/25', ['abr/25', 'a/25']),
    ('2025-05', 'Mai/25', ['mai/25', 'm/25']),
    ('2025-06', 'Jun/25', ['jun/25', 'j/25']),
    ('2025-07', 'Jul/25', ['jul/25', 'j/25']),
    ('2025-08', 'Ago/25', ['ago/25', 'a/25']),
    ('2025-09', 'Set/25', ['set/25', 's/25']),
    ('2025-10', 'Out/25', ['out/25', 'o/25']),
    ('2025-11', 'Nov/25', ['nov/25', 'n/25']),
    ('2025-12', 'Dez/25', ['dez/25', 'd/25']),
    ('2026-01', 'Jan/26', ['jan/26', 'j/26']),
    ('2026-02', 'Fev/26', ['fev/26', 'f/26']),
    ('2026-03', 'Mar/26', ['mar/26', 'm/26']),
    ('2026-04', 'Abr/26', ['abr/26', 'a/26']),
    ('2026-05', 'Mai/26', ['mai/26', 'm/26']),
    ('2026-06', 'Jun/26', ['jun/26', 'j/26']),
    ('2026-07', 'Jul/26', ['jul/26', 'j/26']),
    ('2026-08', 'Ago/26', ['ago/26', 'a/26']),
    ('2026-09', 'Set/26', ['set/26', 's/26'])
]

def map_invol_sheet(sheet_name):
    df = pd.read_excel('MODELO_PROJEÇÃO_CIDADE_RESIDENCIAL - SET S4_V2.xlsb', engine='pyxlsb', sheet_name=sheet_name, header=None)
    # Search Banda Larga columns
    # Find col of BANDA LARGA in row 1
    bl_start = 236
    bl_end = 466
    for c in range(df.shape[1]):
        val = str(df.iloc[1, c]).upper()
        if 'BANDA LARGA' in val: bl_start = c
        if 'TV' in val and c > bl_start:
            bl_end = c
            break
            
    print(f"{sheet_name}: BL range cols {bl_start} to {bl_end}")
    
    # Map months
    mapped = []
    # Loop over all columns in BL range
    col_map = {}
    for c in range(bl_start, bl_end):
        m = str(df.iloc[2, c]).strip().lower()
        sub = str(df.iloc[3, c]).strip().upper()
        if m and m != 'nan':
            # Check if this month matches
            for iso, lbl, patterns in months_keys:
                if any(p in m for p in patterns):
                    # prefer Fech. or S4 or late column
                    col_map.setdefault(iso, []).append((c, m, sub))
                    
    # For each month, select the best column (Fech. or highest week or last)
    final_cols = []
    for iso, lbl, patterns in months_keys:
        candidates = col_map.get(iso, [])
        if not candidates:
            continue
        # find candidate with 'fech' or 's4' or last candidate
        best = None
        for c, m, sub in candidates:
            if 'fech' in m: best = c; break
            if 's4' in m: best = c
        if best is None:
            best = candidates[-1][0]
        final_cols.append((iso, lbl, best))
        
    print(f"Mapped {len(final_cols)} / {len(months_keys)} months.")
    for iso, lbl, col in final_cols[:5]:
        print(f"  {lbl} -> col {col}: row11={[df.iloc[11, col+k] for k in range(5)]}")
    print("  ...")
    for iso, lbl, col in final_cols[-5:]:
        print(f"  {lbl} -> col {col}: row11={[df.iloc[11, col+k] for k in range(5)]}")

map_invol_sheet('ÁREA CABEADA TOTAL')
map_invol_sheet('ÁREA CABEADA PME')
