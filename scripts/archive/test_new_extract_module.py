import openpyxl
import pyxlsb
import pandas as pd
import json
import os

def parse_num(v):
    if v is None or pd.isna(v): return None
    s = str(v).strip().replace(' ', '')
    if s in ['', '-', '#DIV/0!', 'nan', 'None']: return None
    if '.' in s and ',' not in s:
        parts = s.split('.')
        if len(parts) == 2 and len(parts[1]) == 3: s = s.replace('.', '')
    elif ',' in s: s = s.replace('.', '').replace(',', '.')
    try: return float(s)
    except: return None

def normalize_city_id(name):
    s = str(name).upper().replace('Ã','A').replace('Á','A').replace('Â','A').replace('É','E').replace('Í','I').replace('Ó','O').replace('Ú','U').replace('Ç','C').strip()
    s = s.replace(' ', '_').replace('-', '_')
    if 'SAO_LUIS' in s or 'SAO_LUIZ' in s: return 'SAO_LUIS'
    if 'BELEM' in s: return 'BELEM'
    if 'GM_NORTE' in s or 'GRANDES' in s: return 'GM'
    if 'MD_NORTE' in s or 'DESENVOLVIMENTO' in s: return 'MD'
    if s == 'NORTE': return 'NORTE'
    return s

cities_meta = [
    {'id': 'NORTE', 'nome': 'Regional Norte', 'tipo': 'TOTAL', 'grupo': 'REGIONAL', 'uf': 'RNO'},
    {'id': 'GM', 'nome': 'Grandes Mercados', 'tipo': 'SUBTOTAL', 'grupo': 'GM', 'uf': 'GM'},
    {'id': 'ANANINDEUA', 'nome': 'Ananindeua', 'tipo': 'CIDADE', 'grupo': 'GM', 'uf': 'PA'},
    {'id': 'BELEM', 'nome': 'Belém', 'tipo': 'CIDADE', 'grupo': 'GM', 'uf': 'PA'},
    {'id': 'MACAPA', 'nome': 'Macapá', 'tipo': 'CIDADE', 'grupo': 'GM', 'uf': 'AP'},
    {'id': 'MANAUS', 'nome': 'Manaus', 'tipo': 'CIDADE', 'grupo': 'GM', 'uf': 'AM'},
    {'id': 'SANTANA', 'nome': 'Santana', 'tipo': 'CIDADE', 'grupo': 'GM', 'uf': 'AP'},
    {'id': 'SAO_LUIS', 'nome': 'São Luís', 'tipo': 'CIDADE', 'grupo': 'GM', 'uf': 'MA'},
    {'id': 'MD', 'nome': 'Mercados em Desenvolvimento', 'tipo': 'SUBTOTAL', 'grupo': 'MD', 'uf': 'MD'},
    {'id': 'CASTANHAL', 'nome': 'Castanhal', 'tipo': 'CIDADE', 'grupo': 'MD', 'uf': 'PA'},
    {'id': 'CAXIAS', 'nome': 'Caxias', 'tipo': 'CIDADE', 'grupo': 'MD', 'uf': 'MA'},
    {'id': 'IMPERATRIZ', 'nome': 'Imperatriz', 'tipo': 'CIDADE', 'grupo': 'MD', 'uf': 'MA'},
    {'id': 'MARABA', 'nome': 'Marabá', 'tipo': 'CIDADE', 'grupo': 'MD', 'uf': 'PA'},
    {'id': 'PARAGOMINAS', 'nome': 'Paragominas', 'tipo': 'CIDADE', 'grupo': 'MD', 'uf': 'PA'},
    {'id': 'PARAUAPEBAS', 'nome': 'Parauapebas', 'tipo': 'CIDADE', 'grupo': 'MD', 'uf': 'PA'},
    {'id': 'TIMON', 'nome': 'Timon', 'tipo': 'CIDADE', 'grupo': 'MD', 'uf': 'MA'}
]

MONTHS_21_KEYS = [
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

CC_MONTHS_META = [
    ('2025-01', 'Jan/25', 0), ('2025-02', 'Fev/25', 1), ('2025-03', 'Mar/25', 2),
    ('2025-04', 'Abr/25', 3), ('2025-05', 'Mai/25', 4), ('2025-06', 'Jun/25', 5),
    ('2025-07', 'Jul/25', 6), ('2025-08', 'Ago/25', 7), ('2025-09', 'Set/25', 8),
    ('2025-10', 'Out/25', 9), ('2025-11', 'Nov/25', 10), ('2025-12', 'Dez/25', 11),
    ('2026-01', 'Jan/26', 12), ('2026-02', 'Fev/26', 13), ('2026-03', 'Mar/26', 14),
    ('2026-04', 'Abr/26', 15), ('2026-05', 'Mai/26', 16), ('2026-06', 'Jun/26', 17),
    ('2026-07', 'Jul/26', 18), ('2026-08', 'Ago/26', 19), ('2026-09', 'Set/26', 20)
]

SPEECH_MONTHS = [
    ('2026-01', 'Jan/26', 692), ('2026-02', 'Fev/26', 701), ('2026-03', 'Mar/26', 710),
    ('2026-04', 'Abr/26', 719), ('2026-05', 'Mai/26', 728), ('2026-06', 'Jun/26', 737),
    ('2026-07', 'Jul/26', 746), ('2026-08', 'Ago/26', 755), ('2026-09', 'Set/26', 764)
]

SPEECH_NAMES = [
    ('tecnico', 'Técnico - Internet', 4, '#2a5d8f'),
    ('me', 'Mudança de Endereço', 8, '#9b1c1c'),
    ('nao_concorda', 'Não Concorda / Consulta Valores', 7, '#1b2430'),
    ('nao_pedi', 'Não Pedi / Não Solicitei', 3, '#6b4b8a'),
    ('concorrencia', 'Concorrência', 5, '#e23a1e'),
    ('pouca_util', 'Sem / Pouca Utilização', 2, '#516173'),
    ('acha_caro', 'Acha Caro / Reclama de Valor', 0, '#c0392b'),
    ('dif_financ', 'Dificuldade Financeira', 6, '#8a0f18'),
    ('reajuste', 'Reajuste de Valor', 1, '#c98a15')
]

print("Setup completed cleanly.")
