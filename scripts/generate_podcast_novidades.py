#!/usr/bin/env python3
"""
PEP HUB Podcast Generator - Edição Especial: Novas Entregas, Modernização & Governança (v3.0)
Gera o podcast executivo com 2 apresentadores (Carol e Lucas) no estilo Google NotebookLM Audio Overview:
- O novo botão de perfil corporativo (Profile Widget) no topo direito da plataforma
- Governança cadastral: aprovação formal de Nome, Setor, Função e Telefone pelo Admin via e-mail
- Dropdowns oficiais obrigatórios eliminando digitação livre
- Foto corporativa instantânea sem burocracia via compressão Canvas 2D
- Nova Central de Notificações Corporativa em tempo real e painel de comunicados
- Novo Painel Analítico: Evolução de Carteira com dados consolidados
- Saneamento arquitetural completo: correção da trava D1 de SQLite no Cloudflare Workers e modais
"""

import os
import sys
import ssl
import json
import time
import re
import urllib.request
import urllib.parse

# Ensure UTF-8 output on Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# SSL Context bypass for corporate proxies
SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

DIALOGUE = [
    {
        "speaker": "Carol",
        "text": "Olá a todos! Sejam muito bem-vindos a esta edição especial do PEP HUB Podcast! Hoje nós temos um episódio imperdível, dedicado às grandes novidades, melhorias arquiteturais e inovações de governança que acabaram de entrar em produção no PEP HUB da Regional Norte da Claro, em pephub ponto cloud."
    },
    {
        "speaker": "Lucas",
        "text": "Fala, Carol! E que pacote incrível de entregas! Para quem acompanha o dia a dia da Regional Norte, o PEP HUB deu um salto gigantesco de maturidade corporativa, segurança e experiência do usuário. Hoje vamos dissecar todas as novidades: desde o novo botão de perfil até a central de notificações, passando pelo novo painel de Evolução de Carteira e o saneamento das rotas na borda da Cloudflare."
    },
    {
        "speaker": "Carol",
        "text": "Lucas, vamos começar pelo que o usuário nota logo de cara ao entrar na plataforma: o canto superior direito do cabeçalho. O antigo botão vermelho de sair foi totalmente substituído por um componente corporativo moderno de perfil. Como funciona essa novidade?"
    },
    {
        "speaker": "Lucas",
        "text": "Carol, essa foi uma evolução de usabilidade muito pedida! Em vez daquele botão solto de sair que parecia improvisado, agora temos o Profile Button oficial. Ele exibe a foto do colaborador ou suas iniciais em um círculo elegante, seu primeiro nome e uma seta discreta. Ao clicar, abre-se um dropdown corporativo com o cartão completo do usuário: nome, e-mail institucional e o selo de perfil, seja Administrador ou Colaborador."
    },
    {
        "speaker": "Carol",
        "text": "E dentro desse menu, nós temos três opções bem objetivas e diretas: Perfil, Configurações e Sair. Nada de numerações ou títulos confusos, certo?"
    },
    {
        "speaker": "Lucas",
        "text": "Exatamente! Removemos qualquer resquício de numeração de rascunho. Agora é puramente Perfil, Configurações e Sair. E quando o colaborador clica em Perfil, abre-se uma tela modal com a ficha cadastral completa: nome, login corporativo de rede, e-mail da Claro, setor, função e telefone."
    },
    {
        "speaker": "Carol",
        "text": "E aqui entra um ponto crucial de governança que a liderança da Regional Norte exigiu: como funciona a alteração desses dados cadastrais?"
    },
    {
        "speaker": "Lucas",
        "text": "Essa regra de negócio ficou impecável, Carol! Por padrão, os campos são apenas de leitura. Se o usuário quiser alterar Nome, Setor, Função ou Telefone, ele clica em Solicitar Alteração. Mas esses dados não mudam de imediato: o sistema dispara um e-mail formal ao administrador com a tabela comparativa mostrando o valor anterior e o novo valor solicitado. O administrador pode aprovar ou rejeitar com um único clique direto no e-mail!"
    },
    {
        "speaker": "Carol",
        "text": "E para garantir que ninguém saia digitando cargos inexistentes ou setores abreviados de forma errada, agora nós temos os dropdowns oficiais de cadastro, né?"
    },
    {
        "speaker": "Lucas",
        "text": "Com certeza! Nada de campo de texto livre para setor ou cargo. As opções foram padronizadas com a lista oficial da Regional Norte: Marketing, Agente Autorizado, Lojas Próprias, PME, Varejo, Porta a Porta, Engenharia, Técnica, Distribuição, Diretoria e Outros. E para funções, temos Diretor, Gerente, Especialista, Coordenador, Consultor, Supervisor e Executivo de Contas. Isso zera inconsistências na base de dados!"
    },
    {
        "speaker": "Carol",
        "text": "Sensacional! E tem mais duas regras de ouro: o usuário não pode abrir um segundo pedido de alteração enquanto houver uma solicitação em análise pelo administrador. E a foto de perfil? Ela também precisa de aprovação?"
    },
    {
        "speaker": "Lucas",
        "text": "Não, e essa foi uma decisão de design excelente! A foto é de livre escolha do colaborador. Ele pode trocar, adicionar ou remover sua foto a qualquer momento, e a atualização acontece instantaneamente em tempo real. Para não sobrecarregar o banco Cloudflare D1, criamos um algoritmo no navegador que redimensiona e comprime a foto em um elemento Canvas 2D antes do envio, garantindo que o arquivo fique minúsculo, com menos de trinta kilobytes!"
    },
    {
        "speaker": "Carol",
        "text": "Que elegância de engenharia, Lucas! E sobre a tela de Configurações? O que mudou nos alertas de relatórios?"
    },
    {
        "speaker": "Lucas",
        "text": "Na tela de Configurações, atendemos ao pedido de simplificação total. Primeiro: por padrão, ninguém recebe alertas sem solicitar, tudo vem desmarcado. Segundo: implementamos uma regra de exclusão mútua inteligente. Se o colaborador marcar que deseja receber alertas de todos os relatórios que possui acesso, o sistema desmarca automaticamente todos os relatórios individuais. E se ele marcar qualquer relatório específico da lista, desmarca imediatamente a opção de todos. Ficou super intuitivo e livre de ambiguidades!"
    },
    {
        "speaker": "Carol",
        "text": "E agora o formulário de Informar Erro ou Fazer Comentário envia mensagens curtas ou longas sem qualquer falha, além de termos corrigido os botões de fechar e a tecla Escape, que agora fecham os modais com total suavidade."
    },
    {
        "speaker": "Lucas",
        "text": "Exatamente! Corrigimos o conflito de CSS que prendia a exibição dos modais e adicionamos a coluna de atualização cadastral no banco de dados SQLite do D1. Isso eliminou de vez aquele erro de tela que ocorria ao aprovar solicitações antigas ou salvar preferências."
    },
    {
        "speaker": "Carol",
        "text": "Lucas, e sobre a nova Central de Notificações no topo da página? Como ela funciona para o usuário comum e para o administrador?"
    },
    {
        "speaker": "Lucas",
        "text": "A Central de Notificações é outro destaque brilhante! No cabeçalho, ao lado do profile, temos um ícone de sino corporativo com badge numérico em vermelho escuro indicando comunicados não lidos. Ao clicar, abre-se uma gaveta com abas para Todas as notificações e Não Lidas. O administrador possui um painel exclusivo onde pode publicar novos avisos, direcionar para setores específicos ou disparar alertas comemorativos e de manutenção."
    },
    {
        "speaker": "Carol",
        "text": "E não podemos deixar de destacar o novo painel analítico que acaba de ser integrado ao ecossistema: o Painel de Evolução de Carteira! O que esse novo relatório traz para a gestão estratégica da Claro na Regional Norte?"
    },
    {
        "speaker": "Lucas",
        "text": "O painel de Evolução de Carteira é fundamental, Carol! Ele monitora a movimentação líquida da base de clientes mês a mês, segregando adições brutas, desconexões voluntárias, churn involuntário e migrações entre planos em todos os cinco estados. Ele se junta aos nossos painéis consagrados de Churn Safra D cento e vinte, FPD, Banda Larga Total, PME, Market Share Anatel e Taxa de Aprovação de Crédito, formando a suíte analítica mais completa e rápida do setor de telecomunicações!"
    },
    {
        "speaker": "Carol",
        "text": "Que trabalho espetacular de toda a equipe de engenharia e inteligência da Regional Norte! Todos os oito gates do Release Gate foram aprovados com nota máxima A+, garantindo zero dependências externas, segurança bancária e altíssima velocidade de resposta."
    },
    {
        "speaker": "Lucas",
        "text": "Com certeza, Carol! O PEP HUB continua provando que simplicidade de código, foco no usuário de campo e disciplina de engenharia constroem produtos digitais extraordinários. Parabéns a todos os envolvidos!"
    },
    {
        "speaker": "Carol",
        "text": "É isso aí! Continuem aproveitando todas as ferramentas em pephub ponto cloud. Um grande abraço a todos e até a próxima edição!"
    },
    {
        "speaker": "Lucas",
        "text": "Até mais, pessoal! Forte abraço!"
    }
]

def chunk_text(text, max_len=180):
    sentences = re.split(r'([.?!,;:\n]+)', text)
    chunks = []
    curr = ''
    for i in range(0, len(sentences), 2):
        part = sentences[i]
        punct = sentences[i+1] if i+1 < len(sentences) else ''
        piece = (part + punct).strip()
        if not piece:
            continue
        if len(curr) + len(piece) + 1 <= max_len:
            curr = (curr + ' ' + piece).strip()
        else:
            if curr:
                chunks.append(curr)
            curr = piece
    if curr:
        chunks.append(curr)
    return chunks

def generate_segment_audio(text, speaker, idx, temp_dir):
    filename = os.path.join(temp_dir, f"segment_{idx:03d}_{speaker}.mp3")
    if os.path.exists(filename) and os.path.getsize(filename) > 3000:
        print(f"[{idx+1}/{len(DIALOGUE)}] Segmento {speaker} já pronto ({os.path.getsize(filename)} bytes). Pulando...", flush=True)
        return filename

    chunks = chunk_text(text)
    print(f"[{idx+1}/{len(DIALOGUE)}] Sintetizando fala de {speaker} ({len(chunks)} trechos)...", flush=True)
    
    with open(filename, 'wb') as outfile:
        for c_idx, c in enumerate(chunks):
            encoded = urllib.parse.quote(c)
            url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={encoded}&tl=pt-BR&client=tw-ob"
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
            })
            for attempt in range(1, 4):
                try:
                    with urllib.request.urlopen(req, context=SSL_CTX, timeout=15) as resp:
                        outfile.write(resp.read())
                    break
                except Exception as e:
                    if attempt == 3:
                        raise e
                    time.sleep(0.5 * attempt)
            time.sleep(0.12)
            
    return filename

def main():
    print("=" * 70, flush=True)
    print("🎙️ INICIANDO GERADOR DE PODCAST: NOVIDADES & GOVERNANÇA PEP HUB v3.0", flush=True)
    print("=" * 70, flush=True)
    
    temp_dir = os.path.join("public", "podcast", "temp_segments_novidades")
    os.makedirs(temp_dir, exist_ok=True)
    
    segment_files = []
    for idx, item in enumerate(DIALOGUE):
        f = generate_segment_audio(item["text"], item["speaker"], idx, temp_dir)
        segment_files.append(f)
    
    output_mp3 = os.path.join("public", "podcast", "pephub_novidades_governanca_podcast.mp3")
    
    print("\n📦 Concatenando segmentos de áudio em arquivo único...", flush=True)
    with open(output_mp3, "wb") as outfile:
        for f in segment_files:
            with open(f, "rb") as infile:
                outfile.write(infile.read())
                
    transcript_file = os.path.join("public", "podcast", "transcript_novidades.json")
    with open(transcript_file, "w", encoding="utf-8") as f:
        json.dump(DIALOGUE, f, ensure_ascii=False, indent=2)
        
    size_mb = os.path.getsize(output_mp3) / (1024 * 1024)
    print(f"✅ Podcast de Novidades & Governança gerado com sucesso!", flush=True)
    print(f"📁 Caminho: {output_mp3} ({size_mb:.2f} MB)", flush=True)
    print(f"📝 Transcrição atualizada: {transcript_file}", flush=True)
    print("=" * 70, flush=True)

if __name__ == "__main__":
    main()
