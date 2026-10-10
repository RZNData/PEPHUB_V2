import pandas as pd

# Check Base sheet around col 764
df_base = pd.read_excel('SUMÁRIO - CALL CENTER - S4 - 092026.xlsb', engine='pyxlsb', sheet_name='Base', header=None, nrows=10)

print("Base sheet cols 700 to 800:")
for c in range(700, min(800, df_base.shape[1])):
    r1 = df_base.iloc[1, c]
    r2 = df_base.iloc[2, c]
    if pd.notna(r1) or pd.notna(r2):
        print(f"Col {c}: row1='{r1}', row2='{r2}'")

# Check sheets list in SUMÁRIO - CALL CENTER
with pd.ExcelFile('SUMÁRIO - CALL CENTER - S4 - 092026.xlsb', engine='pyxlsb') as xls:
    print("\nAll sheets:", xls.sheet_names)
    speech_sheets = [s for s in xls.sheet_names if 'SPEECH' in s.upper()]
    print("Speech sheets:", speech_sheets)
