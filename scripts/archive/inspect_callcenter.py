import pandas as pd

df = pd.read_excel('SUMÁRIO - CALL CENTER - S4 - 092026.xlsb', engine='pyxlsb', sheet_name='Base', header=None, nrows=10)

print(f"Base shape: {df.shape}")
# Let's inspect row 0 to 5 across columns
for r in range(5):
    items = [(c, df.iloc[r, c]) for c in range(df.shape[1]) if pd.notna(df.iloc[r, c])]
    print(f"Row {r} sample ({len(items)} items): {items[:25]}")
