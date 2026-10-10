with open('scripts/extract_churn_data.py', 'r', encoding='utf-8') as f:
    code = f.read()

new_extract = '''def extract_full_churn_data(filepath, segment_name, is_xlsb=False):
    print(f"Extracting {segment_name} from {filepath}...")
    if is_xlsb:
        df_ana = pd.read_excel(filepath, engine='pyxlsb', sheet_name=0, header=None)
        df_gr = pd.read_excel(filepath, engine='pyxlsb', sheet_name=2, header=None)
        base_rows = {'TOTAL': 5, 'VOLUNTARIA': 22, 'INVOLUNTARIA': 39}
        gr_offset = 45
        col_current = 69 # Out/26 (T1)
        col_mom = 68     # Set/26 (MoM)
        col_yoy = 57     # Out/25 (YoY)
        col_p1, col_p2, col_p3, col_p4 = 72, 73, 74, 75
        col_orc_current = None
        start_hist_col = 36 # Jan/24
        ytd_2026_range = range(60, 70) # Jan/26..Out/26 (10 meses)
        ytd_2025_range = range(48, 58) # Jan/25..Out/25 (10 meses)
        ytd_orc_range = []
    else:
        wb = openpyxl.load_workbook(filepath, data_only=True)
        ws_ana = wb.worksheets[0]
        ws_gr = wb.worksheets[2]
        df_ana = pd.DataFrame([[ws_ana.cell(r, c).value for c in range(1, 130)] for r in range(1, 65)])
        df_gr = pd.DataFrame([[ws_gr.cell(r, c).value for c in range(1, 65)] for r in range(1, 100)])
        wb.close()
        base_rows = {'TOTAL': 5, 'VOLUNTARIA': 22, 'INVOLUNTARIA': 39}
        gr_offset = 45
        col_current = 69 # Out/26 (T1)
        col_mom = 68     # Set/26 (MoM)
        col_yoy = 57     # Out/25 (YoY)
        col_p1, col_p2, col_p3, col_p4 = 72, 73, 74, 75
        col_orc_current = 111 # Out/26 Orçado
        start_hist_col = 36 # Jan/24
        start_orc_hist_col = 78 # Jan/24 Orçado
        ytd_2026_range = range(60, 70) # Jan/26..Out/26 (10 meses)
        ytd_2025_range = range(48, 58) # Jan/25..Out/25 (10 meses)
        ytd_orc_range = range(102, 112) # Jan/26..Out/26 Orçado

    modes_data = {}

    for mode_key in ['TOTAL', 'VOLUNTARIA', 'INVOLUNTARIA']:
        b_r = base_rows[mode_key]
        mode_label = "Desconexão Total" if mode_key == "TOTAL" else ("Desconexão Voluntária" if mode_key == "VOLUNTARIA" else "Desconexão Involuntária")
        
        cities_list = []
        for i, cm in enumerate(cities_meta):
            r = b_r + i
            r_gr = gr_offset + i
            
            v_curr = parse_num(df_ana.iloc[r, col_current]) or 0
            v_mom = parse_num(df_ana.iloc[r, col_mom]) or 0
            v_yoy = parse_num(df_ana.iloc[r, col_yoy]) or 0
            
            v_p1 = parse_num(df_ana.iloc[r, col_p1]) or v_curr
            v_p2 = parse_num(df_ana.iloc[r, col_p2]) or v_curr
            v_p3 = parse_num(df_ana.iloc[r, col_p3]) or v_curr
            v_p4 = parse_num(df_ana.iloc[r, col_p4]) or v_curr
            
            # YTD 2026 e YTD 2025
            ytd_2026_vals = [parse_num(df_ana.iloc[r, c]) for c in ytd_2026_range]
            ytd_2026 = sum([x for x in ytd_2026_vals if x is not None])
            
            ytd_2025_vals = [parse_num(df_ana.iloc[r, c]) for c in ytd_2025_range]
            ytd_2025 = sum([x for x in ytd_2025_vals if x is not None])

            ytd_26x25_delta = round(ytd_2026 - ytd_2025, 1)
            ytd_26x25_pct = round(((ytd_2026 - ytd_2025) / ytd_2025) * 100, 2) if ytd_2025 > 0 else 0

            if is_xlsb:
                v_orc = None
                d_rxo = None
                pct_rxo = None
                ytd_orc = None
                ytd_rxo_delta = None
                ytd_rxo_pct = None
                base_real = parse_num(df_gr.iloc[r_gr, 4]) if df_gr.shape[0] > r_gr and df_gr.shape[1] > 4 else None
                base_orc = None
                taxa_real = round((v_curr / base_real) * 100, 2) if (base_real and base_real > 0 and v_curr is not None) else None
                taxa_orc = None
                taxa_delta_pp = None
            else:
                v_orc = parse_num(df_ana.iloc[r, col_orc_current]) if (col_orc_current and df_ana.shape[1] > col_orc_current) else None
                d_rxo = round(v_curr - v_orc, 1) if (v_curr is not None and v_orc is not None) else None
                pct_rxo = round(((v_curr - v_orc) / v_orc) * 100, 2) if (v_orc and v_orc > 0 and v_curr is not None) else None

                ytd_orc_vals = [parse_num(df_ana.iloc[r, c]) for c in ytd_orc_range] if len(ytd_orc_range) > 0 and df_ana.shape[1] > max(ytd_orc_range) else []
                ytd_orc = sum([x for x in ytd_orc_vals if x is not None])
                ytd_rxo_delta = round(ytd_2026 - ytd_orc, 1) if (ytd_2026 is not None and ytd_orc is not None) else None
                ytd_rxo_pct = round(((ytd_2026 - ytd_orc) / ytd_orc) * 100, 2) if (ytd_orc and ytd_orc > 0 and ytd_2026 is not None) else None

                base_real = parse_num(df_gr.iloc[r_gr, 4]) if df_gr.shape[0] > r_gr and df_gr.shape[1] > 4 else None
                base_orc = parse_num(df_gr.iloc[r_gr, 5]) if df_gr.shape[0] > r_gr and df_gr.shape[1] > 5 else None

                taxa_real = round((v_curr / base_real) * 100, 2) if (base_real and base_real > 0 and v_curr is not None) else None
                taxa_orc = round((v_orc / base_orc) * 100, 2) if (base_orc and base_orc > 0 and v_orc is not None) else None
                taxa_delta_pp = round(taxa_real - taxa_orc, 2) if (taxa_real is not None and taxa_orc is not None) else None

            d_mom = round(v_curr - v_mom, 1)
            pct_mom = round(((v_curr - v_mom) / v_mom) * 100, 2) if v_mom > 0 else 0

            d_yoy = round(v_curr - v_yoy, 1)
            pct_yoy = round(((v_curr - v_yoy) / v_yoy) * 100, 2) if v_yoy > 0 else 0

            cities_list.append({
                **cm,
                'vol_real': round(v_curr, 1),
                'vol_orc': round(v_orc, 1) if v_orc is not None else None,
                'rxo_delta': d_rxo,
                'rxo_pct': pct_rxo,
                'vol_ago26': round(v_mom, 1),
                'mom_delta': d_mom,
                'mom_pct': pct_mom,
                'vol_sep25': round(v_yoy, 1),
                'yoy_delta': d_yoy,
                'yoy_pct': pct_yoy,
                't1': round(v_p1, 1),
                't2': round(v_p2, 1),
                't3': round(v_p3, 1),
                't4': round(v_p4, 1),
                'ytd_real': round(ytd_2026, 1),
                'ytd_2025': round(ytd_2025, 1),
                'ytd_26x25_delta': ytd_26x25_delta,
                'ytd_26x25_pct': ytd_26x25_pct,
                'ytd_orc': round(ytd_orc, 1) if ytd_orc is not None else None,
                'ytd_rxo_delta': ytd_rxo_delta,
                'ytd_rxo_pct': ytd_rxo_pct,
                'base_real': int(base_real) if base_real else 0,
                'base_orc': int(base_orc) if base_orc else None,
                'taxa_real': taxa_real,
                'taxa_orc': taxa_orc,
                'taxa_delta_pp': taxa_delta_pp
            })

        timeline_list = []
        for idx, (m_iso, m_lbl) in enumerate(MONTH_NAMES):
            c = start_hist_col + idx
            
            r_tot = b_r + 0
            r_gm = b_r + 1
            r_md = b_r + 8
            
            v_tot = parse_num(df_ana.iloc[r_tot, c]) if df_ana.shape[1] > c else None
            v_gm = parse_num(df_ana.iloc[r_gm, c]) if df_ana.shape[1] > c else None
            v_md = parse_num(df_ana.iloc[r_md, c]) if df_ana.shape[1] > c else None
            
            if is_xlsb:
                v_orc_tot = None
                v_orc_gm = None
                v_orc_md = None
            else:
                c_orc = start_orc_hist_col + idx
                v_orc_tot = parse_num(df_ana.iloc[r_tot, c_orc]) if df_ana.shape[1] > c_orc else None
                v_orc_gm = parse_num(df_ana.iloc[r_gm, c_orc]) if df_ana.shape[1] > c_orc else None
                v_orc_md = parse_num(df_ana.iloc[r_md, c_orc]) if df_ana.shape[1] > c_orc else None

            c_dict = {}
            for i_cm, cm in enumerate(cities_meta):
                if cm['tipo'] == 'CIDADE':
                    r_c = b_r + i_cm
                    v_c = parse_num(df_ana.iloc[r_c, c]) if df_ana.shape[1] > c else None
                    v_orc_c = parse_num(df_ana.iloc[r_c, c_orc]) if (not is_xlsb and df_ana.shape[1] > c_orc) else None
                    c_dict[cm['id']] = {
                        'realizado': round(v_c, 1) if v_c is not None else None,
                        'orcamento': round(v_orc_c, 1) if v_orc_c is not None else None
                    }

            timeline_list.append({
                'iso': m_iso,
                'label': m_lbl,
                'realizado': round(v_tot, 1) if v_tot is not None else None,
                'orcamento': round(v_orc_tot, 1) if v_orc_tot is not None else None,
                'gm_real': round(v_gm, 1) if v_gm is not None else None,
                'md_real': round(v_md, 1) if v_md is not None else None,
                'gm_orc': round(v_orc_gm, 1) if v_orc_gm is not None else None,
                'md_orc': round(v_orc_md, 1) if v_orc_md is not None else None,
                'cities': c_dict
            })

        reg = cities_list[0]
        modes_data[mode_key] = {
            'key': mode_key,
            'label': mode_label,
            'summary': {
                'vol_real': reg['vol_real'],
                'vol_orc': reg['vol_orc'],
                'rxo_delta': reg['rxo_delta'],
                'rxo_pct': reg['rxo_pct'],
                'vol_ago26': reg['vol_ago26'],
                'mom_delta': reg['mom_delta'],
                'mom_pct': reg['mom_pct'],
                'vol_sep25': reg['vol_sep25'],
                'yoy_delta': reg['yoy_delta'],
                'yoy_pct': reg['yoy_pct'],
                't1': reg['t1'],
                't2': reg['t2'],
                't3': reg['t3'],
                't4': reg['t4'],
                'ytd_real': reg['ytd_real'],
                'ytd_2025': reg['ytd_2025'],
                'ytd_26x25_delta': reg['ytd_26x25_delta'],
                'ytd_26x25_pct': reg['ytd_26x25_pct'],
                'ytd_orc': reg['ytd_orc'],
                'ytd_rxo_delta': reg['ytd_rxo_delta'],
                'ytd_rxo_pct': reg['ytd_rxo_pct'],
                'base_real': reg['base_real'],
                'base_orc': reg['base_orc'],
                'taxa_real': reg['taxa_real'],
                'taxa_orc': reg['taxa_orc'],
                'taxa_delta_pp': reg['taxa_delta_pp']
            },
            'cities': cities_list,
            'timeline': timeline_list
        }

    bases_map = {c['id']: c['base_real'] for c in modes_data['TOTAL']['cities']}
    proj_invol = extract_involuntary_projection(is_pme=is_xlsb, bases_map=bases_map)
    cc_summary = extract_callcenter_summary(bases_map=bases_map)

    return {
        'segmento': segment_name,
        'mes_referencia': 'Outubro / 2026',
        'data_posicao': '01/10/2026',
        'tendencia_atual': '1ª Tendência (T1)',
        'default_mode': 'TOTAL',
        'modes': modes_data,
        'involuntaria_proj': proj_invol,
        'callcenter': cc_summary
    }

if __name__ == '__main__':
    data_total = extract_full_churn_data('1Tend_Out26_Acompanhamento Churn Horizontal_v13.xlsm', 'Banda Larga Total', is_xlsb=False)
    data_pme = extract_full_churn_data('1Tend_Out26_Acompanhamento Churn Horizontal_PME_v2.xlsb', 'Banda Larga PME', is_xlsb=True)

    os.makedirs('public/churn-bl-total', exist_ok=True)
    os.makedirs('public/churn-bl-pme', exist_ok=True)

    with open('public/churn-bl-total/data.json', 'w', encoding='utf-8') as f:
        json.dump(data_total, f, ensure_ascii=False, indent=2)

    with open('public/churn-bl-pme/data.json', 'w', encoding='utf-8') as f:
        json.dump(data_pme, f, ensure_ascii=False, indent=2)

    print("Success! Both data.json extracted with Out/26 (T1) and full histories integrated.")
'''

idx = code.find('def extract_full_churn_data')
updated_code = code[:idx] + new_extract
with open('scripts/extract_churn_data.py', 'w', encoding='utf-8') as f:
    f.write(updated_code)

print('Updated scripts/extract_churn_data.py successfully!')
