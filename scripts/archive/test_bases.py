import pyxlsb
import openpyxl
import pandas as pd

wb = openpyxl.load_workbook('4Tend_Set26_Acompanhamento Churn Horizontal_v13.xlsm', data_only=True)
ws_gr = wb.worksheets[2]
df_gr = pd.DataFrame([[ws_gr.cell(r, c).value for c in range(1, 65)] for r in range(1, 100)])
wb.close()

# Base real row offset is 45
print("Bases from df_gr (Total):")
for i in range(16):
    r_gr = 45 + i
    val = df_gr.iloc[r_gr, 4]
    print(f"Row {r_gr}: base_real={val}")
