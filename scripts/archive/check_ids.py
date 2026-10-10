with open('Painel_FPD_Regional_Norte.html', 'r', encoding='utf-8') as f:
    text = f.read()

s_idx = text.find('<script>')
html = text[:s_idx]

ids_to_check = [
    'tabsEst', 'tabsNp', 'rkSearch', 'rkMin', 'rkClosed',
    'fDrawer', 'btnDrawer', 'fToggleBar', 'drawerIco',
    'tabsMtx', 'mtxMature', 'mtxDim', 'tabsScatComp', 'tabsScatDim',
    'tabsRiscoMode', 'chScatter', 'chRisco', 'tblRisco', 'tblMtx',
    'kpis', 'chSafra', 'chEsteira', 'tblEsteira', 'tblRank', 'mapCv'
]

for el_id in ids_to_check:
    found = f'id="{el_id}"' in html or f"id='{el_id}'" in html
    status = "OK" if found else "AUSENTE"
    print(f"{el_id:15s}: {status}")
