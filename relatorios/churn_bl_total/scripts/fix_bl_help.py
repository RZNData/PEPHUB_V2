"""Insere verbete 'tipo_desconexao' no HLP_CONTENT dos paineis BL Total e BL PME"""

VERBETE_JS = """  tipo_desconexao: `<h4>Tipos de Desconexao</h4><p>Classifica as desconexoes de Banda Larga de acordo com a causa raiz registrada no sistema Claro.</p><p><strong>Involuntaria Base:</strong> Inadimplencia com regra padrao de corte por atraso no pagamento das mensalidades.</p><p><strong>FPD (First Payment Default):</strong> Cliente nao pagou a primeira fatura — desconexao ocorre na propria safra de instalacao.</p><p><strong>Opcao:</strong> Cliente solicitou o cancelamento voluntariamente (saiu por escolha propria).</p><p><strong>Fraude SSI:</strong> Desconexao por identificacao de fraude na contratacao ou uso indevido do servico.</p>`,
"""

FILES = [
    'public/churn-bl-total/index.html',
    'public/churn-bl-pme/index.html',
]

TARGET = '  filtros: `<h4>Filtros Executivos'

for path in FILES:
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        if 'tipo_desconexao' in content:
            print(f'SKIP {path}: tipo_desconexao ja existe.')
            continue

        if TARGET not in content:
            print(f'SKIP {path}: target nao encontrado. Buscando alternativa...')
            # Tentar encontrar o inicio do HLP_CONTENT
            idx = content.find('const HLP_CONTENT = {')
            if idx == -1:
                print(f'  ERRO: HLP_CONTENT nao encontrado.')
                continue
            # Inserir como primeira chave
            insert_after = content.find('\n', idx) + 1
            content = content[:insert_after] + VERBETE_JS + content[insert_after:]
        else:
            content = content.replace(TARGET, VERBETE_JS + TARGET, 1)

        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'OK {path}: tipo_desconexao inserido.')
    except Exception as e:
        print(f'ERRO {path}: {e}')
