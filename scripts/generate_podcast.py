#!/usr/bin/env python3
"""
PEP HUB Audio Overview - Google NotebookLM Style Podcast Generator (Edição Especial Completa v3.0)
Gera o podcast executivo e técnico definitivo com 2 apresentadores (Carol e Lucas)
detalhando toda a plataforma PEP HUB da Regional Norte da Claro:
- O porquê da criação do sistema e comparação com ferramentas de mercado (PowerBI/Tableau)
- Filosofia de Engenharia: Zero dependências, Offline-First, SVG Puro, Canvas 2D e Typed Arrays
- Análise profunda dos 7 Painéis Analíticos:
  1. Churn Safra D120
  2. FPD isolado (30 e 60 dias)
  3. Banda Larga Total
  4. Banda Larga PME
  5. Panorama Market Share Anatel
  6. Taxa de Aprovação de Crédito
  7. Evolução de Carteira (Novo Painel Estratégico)
- Novo Profile Widget corporativo e Governança Cadastral
- Nova Central de Notificações no Header
- PeP Tools: Auxiliar de PPT (ex-Studio) e Gerador de Cards TV 16:9
- O cérebro do Bot WhatsApp com Arquitetura RAG Híbrida (Safe SQL no D1 contra alucinações de LLM)
- Central Unificada de Cargas no D1 e Delegação RBAC
- Segurança de padrão bancário (PBKDF2, CSP, D1 Prepared Statements) e aprovação no Release Gate
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
        "text": "Olá a todos! Sejam muito bem-vindos a esta edição especial e definitiva do Deep Dive do PEP HUB! Sabe aquela experiência fantástica do Google NotebookLM, onde relatórios densos, manuais de engenharia e decisões executivas viram uma conversa dinâmica e super agradável? Pois é! Hoje nós vamos fazer um mergulho completo na plataforma de inteligência e performance da Regional Norte da Claro, explicando de ponta a ponta o porquê de cada decisão técnica e operacional."
    },
    {
        "speaker": "Lucas",
        "text": "Que alegria estar com você, Carol! O PEP HUB da Regional Norte, que roda oficialmente em pephub ponto cloud, não é apenas mais um portal de dashboards corporativos. Ele representa uma quebra de paradigma na forma como uma grande operadora de telecomunicações gerencia seus dados de churn, qualidade, crédito e inteligência de mercado em cento e trinta e três cidades de cinco estados: Amazonas, Pará, Maranhão, Amapá e Roraima."
    },
    {
        "speaker": "Carol",
        "text": "Lucas, para começarmos pelo começo: por que a equipe decidiu construir uma plataforma proprietária em vez de usar soluções de mercado tradicionais, como o Power B I ou o Tableau? O que essas ferramentas não conseguiam entregar no dia a dia da Regional Norte?"
    },
    {
        "speaker": "Lucas",
        "text": "Carol, essa é a pergunta de um milhão de dólares! O Power B I e o Tableau são ferramentas conceituadas, mas no cenário operacional real da Regional Norte elas sofriam de três problemas crônicos. Primeiro: lentidão e peso excessivo. Um relatório pesado de Power B I leva de quinze a trinta segundos para carregar no navegador, baixando megabytes de código desnecessário. Quando um consultor comercial ou supervisor de campo está no interior do Pará ou do Maranhão, em uma rede três G ou quatro G intermitente, o painel simplesmente não abria ou travava o celular!"
    },
    {
        "speaker": "Carol",
        "text": "E para quem está na rua negociando com parceiros credenciados, esperar meio minuto por um número é impensável!"
    },
    {
        "speaker": "Lucas",
        "text": "Exatamente! Segundo: o funcionamento offline. Se o diretor ou analista viaja de avião ou vai a uma área remota sem sinal de internet, o Power B I para de funcionar. Já o PEP HUB foi projetado com arquitetura offline-first. Cada relatório analítico pode ser baixado em um único arquivo H T M L autocontido, que abre instantaneamente em qualquer computador ou tablet, sem precisar de internet nenhuma. E terceiro: os custos exorbitantes de licenciamento por usuário, que no PEP HUB foram reduzidos a zero, aproveitando a rede de borda da Cloudflare."
    },
    {
        "speaker": "Carol",
        "text": "Nossa Lucas, que diferença brutal! E como é que a equipe conseguiu fazer um sistema tão rápido e leve, que carrega em menos de trezentos milissegundos? Qual é o segredo de engenharia por trás do código?"
    },
    {
        "speaker": "Lucas",
        "text": "O grande pilar é o princípio de Zero Dependências Externas. Nós banimos frameworks pesados como React, Angular, Vue, Tailwind e bibliotecas de gráficos prontas como Chart ponto js ou D três. O frontend do PEP HUB foi escrito cem por cento em JavaScript moderno nativo, H T M L cinco semântico e C S S puro. Todos os gráficos são desenhados diretamente em S V G vetorial paramétrico, que se adapta com nitidez cristalina a qualquer tamanho de tela, de um smartphone a uma televisão gigante de sessenta e cinco polegadas na sala da Diretoria."
    },
    {
        "speaker": "Carol",
        "text": "E os mapas geoespaciais com milhares de clientes e pontos de rede? Como eles rodam tão lisos sem bibliotecas de mapas pesadas como Mapbox ou Google Maps?"
    },
    {
        "speaker": "Lucas",
        "text": "Eles foram programados em H T M L cinco Canvas dois D com projeção matemática pura de Web Mercator! O usuário pode dar zoom, mover o mapa com fluidez e desenhar um laço livre com o mouse para filtrar clientes de um quarteirão específico. Além disso, os dados brutos são comprimidos com o algoritmo Deflate e descompactados em tempo real pela A P I nativa do navegador, sendo guardados em vetores tipados na memória, como Uint trinta e dois Array. Isso reduz o consumo de memória R A M em mais de oitenta por cento!"
    },
    {
        "speaker": "Carol",
        "text": "É engenharia de software de altíssimo nível, Lucas! Agora vamos falar dos relatórios analíticos fundamentais da plataforma. O primeiro deles é o famoso Painel Churn Safra D cento e vinte. O que ele monitora e por que a janela oficial é de cento e vinte dias?"
    },
    {
        "speaker": "Lucas",
        "text": "Carol, o Churn Safra acompanha a desconexão definitiva dos contratos ao longo do tempo. Uma venda recém-instalada passa por um período crítico de maturação. Na Claro, o marco oficial é o D cento e vinte, que são os primeiros quatro meses do contrato. É nessa janela que é apurada a responsabilidade direta do canal de vendas e do parceiro credenciado. O painel rastreia o cancelamento voluntário, o involuntário por corte de inadimplência e o indicador de Nunca Pagou, que revela instalações que não pagaram sequer a primeira mensalidade."
    },
    {
        "speaker": "Carol",
        "text": "E isso nos leva direto ao segundo relatório: o Painel de F P D, o First Payment Default. Eu lembro que no passado houve uma tentativa de misturar os dados de F P D com as bases de Churn Safra, e isso causou uma confusão tremenda de colunas e métricas. Como isso foi consertado de vez?"
    },
    {
        "speaker": "Lucas",
        "text": "Carol, essa foi uma regra de ouro estabelecida pela Diretoria: segregação total e absoluta! O F P D mede inadimplência na primeira fatura, que é um sintoma de qualidade de onboarding e esteira de crédito, enquanto o Churn Safra mede desconexão física do modem. Misturar os dois distorcia a responsabilidade dos vendedores. Nós isolamos o painel de F P D em uma base exclusiva, a Base F P D de treze safras da Regional Norte. O painel apresenta com clareza o F P D trinta dias pró-rata e o F P D sessenta dias de ciclo cheio oficial, além da análise de risco por faixas de score de crédito."
    },
    {
        "speaker": "Carol",
        "text": "Que clareza necessária! E o terceiro e quarto relatórios, que cobrem a Banda Larga Total e o segmento corporativo P M E? O que eles trazem de inteligência preditiva?"
    },
    {
        "speaker": "Lucas",
        "text": "Eles trazem o monitoramento das quatro Tendências semanais, de T um a T quatro, confrontando o realizado com a meta orçada da companhia. Mas o grande destaque no segmento P M E foi uma descoberta empírica fantástica da nossa equipe: setenta e oito vírgula dois por cento dos cancelamentos de empresas ocorrem após o décimo segundo mês, exatamente quando termina a carência contratual da fidelidade! Por isso, o painel instituiu a Janela Crítica de Renegociação Proativa no Mês onze, orientando os consultores a procurarem o cliente trinta dias antes do contrato vencer para proteger a receita."
    },
    {
        "speaker": "Carol",
        "text": "Isso é pura geração de valor financeiro! E no relatório de Panorama Market Share da Anatel e no de Taxa de Aprovação de Crédito, o que temos de inteligência comercial?"
    },
    {
        "speaker": "Lucas",
        "text": "No Market Share, acompanhamos município a município o saldo do líder, adições líquidas e a pressão competitiva dos provedores regionais em toda a Regional Norte. E na Taxa de Aprovação de Crédito, analisamos a eficiência da esteira comercial por ponto de venda, lojas próprias e agentes autorizados, com ordenação nativa por volume e visões sem atrito."
    },
    {
        "speaker": "Carol",
        "text": "E agora temos o novíssimo Painel de Evolução de Carteira! Como ele complementa a visão da liderança?"
    },
    {
        "speaker": "Lucas",
        "text": "O painel de Evolução de Carteira fecha o ciclo com chave de ouro! Ele monitora a movimentação líquida da base de clientes mês a mês, segregando adições brutas, desconexões voluntárias, churn involuntário e migrações entre planos em todos os cinco estados. Ele permite aos diretores e gerentes enxergar exatamente onde a carteira está crescendo e onde precisamos reforçar a retenção."
    },
    {
        "speaker": "Carol",
        "text": "E na usabilidade do dia a dia, todos os relatórios contam agora com o novo botão corporativo de perfil no cabeçalho e a central de notificações em tempo real!"
    },
    {
        "speaker": "Lucas",
        "text": "Exatamente! Substituímos os antigos botões soltos pelo Profile Widget. O colaborador acessa seus dados, adiciona foto de perfil instantânea comprimida em canvas e pode solicitar alteração de Nome, Setor, Função ou Telefone, que vai direto para aprovação do administrador por e-mail com seletores oficiais padronizados. E a central de notificações avisa a equipe sobre novas safras e manutenções com contador dinâmico de avisos não lidos."
    },
    {
        "speaker": "Carol",
        "text": "Espetacular! E temos também o ecossistema PeP Tools, com o Auxiliar de P P T e o Gerador de Cards de Aniversário para as televisões dos prédios da Regional Norte. Me conta sobre eles!"
    },
    {
        "speaker": "Lucas",
        "text": "O Auxiliar de P P T, que antes era chamado de Market Share Studio, agora é uma central completa de produtividade executiva! O analista pode colar dados de uma planilha Excel e gerar gráficos de rosca, pizza, barras e organogramas prontos para apresentações da Diretoria, podendo copiar em S V G vetorial ou P N G em alta resolução com um clique só. E o Gerador de Cards de Aniversário foi ajustado com enquadramento matemático perfeito em formato dezesseis por nove, sem cortar a imagem em nenhum monitor ou televisor dos prédios operacionais."
    },
    {
        "speaker": "Carol",
        "text": "Agora Lucas, vamos para o robô de inteligência artificial no WhatsApp! Como a Arquitetura R A G Híbrida garante respostas com precisão matemática absoluta?"
    },
    {
        "speaker": "Lucas",
        "text": "Criamos uma rodovia de duas pistas estritamente separadas! Quando a pergunta chega no WhatsApp, um roteador identifica a intenção. Se for uma pergunta analítica com números, a I A não faz a conta: ela gera uma consulta S Q L segura e consulta diretamente o banco relacional Cloudflare D um! O banco devolve o número exato, por exemplo, dois vírgula trinta e quatro por cento. A I A apenas formata a mensagem com educação corporativa. Precisão de cem por cento, zero alucinações matemáticas! E se a dúvida for conceitual, a segunda pista resgata as regras de negócio homologadas."
    },
    {
        "speaker": "Carol",
        "text": "E com carteirização por telefone para proteger a privacidade dos dados das cidades! E me fala sobre a Central de Cargas: como ela empodera os analistas?"
    },
    {
        "speaker": "Lucas",
        "text": "A Central de Cargas permite subir qualquer base arrastando o arquivo no navegador, que fatia em chunks de quinhentos kilobytes e grava direto no Cloudflare D um com barra de progresso. E o gestor pode delegar uma carga específica para um analista via R B A C, sem dar acesso administrativo ao resto do sistema."
    },
    {
        "speaker": "Carol",
        "text": "Lucas, que aula de engenharia e governança corporativa! O PEP HUB foi submetido a todos os testes do Release Gate corporativo e obteve nota máxima A mais em todos os oito pilares de qualidade, segurança e arquitetura. Tudo rodando com perfeição em pephub ponto cloud!"
    },
    {
        "speaker": "Lucas",
        "text": "É o orgulho da Regional Norte da Claro! Uma plataforma veloz, segura, offline-first e que entrega a melhor inteligência analítica na palma da mão da nossa equipe."
    },
    {
        "speaker": "Carol",
        "text": "Sensacional! Esse foi o nosso episódio definitivo do PEP HUB. Parabéns a todos e até a próxima!"
    },
    {
        "speaker": "Lucas",
        "text": "Um grande abraço e até lá, pessoal!"
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
        for c in chunks:
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
    print("🎙️ INICIANDO GERADOR DE PODCAST: TREINAMENTO & FUNCIONALIDADES PEP HUB v3.0", flush=True)
    print("=" * 70, flush=True)
    
    temp_dir = os.path.join("public", "podcast", "temp_segments_training")
    os.makedirs(temp_dir, exist_ok=True)
    
    segment_files = []
    for idx, item in enumerate(DIALOGUE):
        f = generate_segment_audio(item["text"], item["speaker"], idx, temp_dir)
        segment_files.append(f)
    
    output_mp3 = os.path.join("public", "podcast", "pephub_deepdive_podcast.mp3")
    root_mp3 = "pephub_podcast.mp3"
    
    print("\n📦 Concatenando segmentos de áudio em arquivo único...", flush=True)
    with open(output_mp3, "wb") as outfile:
        for f in segment_files:
            with open(f, "rb") as infile:
                outfile.write(infile.read())
                
    with open(root_mp3, "wb") as outfile:
        with open(output_mp3, "rb") as infile:
            outfile.write(infile.read())
            
    transcript_file = os.path.join("public", "podcast", "transcript.json")
    with open(transcript_file, "w", encoding="utf-8") as f:
        json.dump(DIALOGUE, f, ensure_ascii=False, indent=2)
        
    size_mb = os.path.getsize(output_mp3) / (1024 * 1024)
    print(f"✅ Podcast de Treinamento e Funcionalidades gerado com sucesso!", flush=True)
    print(f"📁 Caminho: {output_mp3} ({size_mb:.2f} MB)", flush=True)
    print(f"📁 Cópia raiz: {root_mp3}", flush=True)
    print(f"📝 Transcrição atualizada: {transcript_file}", flush=True)
    print("=" * 70, flush=True)

if __name__ == "__main__":
    main()
