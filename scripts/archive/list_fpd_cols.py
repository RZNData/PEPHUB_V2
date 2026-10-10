with open('FPD_JAN_MAI_26.csv', 'r', encoding='latin1', errors='ignore') as f:
    h = [col.strip().replace('"', '').upper() for col in f.readline().split(';')]

for i, col in enumerate(h):
    print(f'{i:3d}: {col}')
