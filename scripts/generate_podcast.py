#!/usr/bin/env python3
"""
PEP HUB Audio Overview - Google NotebookLM Style Podcast Generator (Edição Especial Completa v2.5)
Gera o podcast executivo e técnico definitivo com 2 apresentadores neurais (Carol e Lucas)
detalhando toda a plataforma PEP HUB da Regional Norte da Claro:
- O porquê da criação do sistema e comparação com ferramentas de mercado (PowerBI/Tableau)
- Filosofia de Engenharia: Zero dependências, Offline-First, SVG Puro, Canvas 2D e Typed Arrays
- Análise profunda dos 6 Painéis Analíticos (Safra, FPD isolado, BL Total, PME, Market Share e Aprovação)
- PeP Tools: Auxiliar de PPT (ex-Studio) e Gerador de Cards TV 16:9 sem corte
- O cérebro do Bot WhatsApp com Arquitetura RAG Híbrida (Safe SQL no D1 contra alucinações de LLM)
- Central Unificada de Cargas em Chunks no D1 e Delegação RBAC
- Segurança de padrão bancário (PBKDF2, CSP, D1 Prepared Statements) e aprovação no Release Gate
"""

import os
import sys
import ssl
import json
import asyncio

# Ensure UTF-8 output on Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

import edge_tts

# Patch SSL context for corporate proxy environments
ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE
edge_tts.voices._SSL_CTX = ssl_ctx
edge_tts.communicate._SSL_CTX = ssl_ctx

# Voice configurations
# Carol: Francisca Neural (expressive, lively, engaging female host)
# Lucas: Antonio Neural (clear, knowledgeable, warm male host)
VOICE_CAROL = "pt-BR-FranciscaNeural"
VOICE_LUCAS = "pt-BR-AntonioNeural"

DIALOGUE = [
    {
        "speaker": "Carol",
        "voice": VOICE_CAROL,
        "text": "Olá a todos! Sejam muito bem-vindos a esta edição especial e definitiva do Deep Dive do PEP HUB! Sabe aquela experiência fantástica do Google NotebookLM, onde relatórios densos, manuais de engenharia e decisões executivas viram uma conversa dinâmica e super agradável? Pois é! Hoje nós vamos fazer um mergulho completo na plataforma de inteligência e performance da Regional Norte da Claro, explicando de ponta a ponta o porquê de cada decisão técnica e operacional."
    },
    {
        "speaker": "Lucas",
        "voice": VOICE_LUCAS,
        "text": "Que alegria estar com você, Carol! O PEP HUB da Regional Norte, que roda oficialmente em pephub ponto cloud, não é apenas mais um portal de dashboards corporativos. Ele representa uma quebra de paradigma na forma como uma grande operadora de telecomunicações gerencia seus dados de churn, qualidade, crédito e inteligência de mercado em cento e trinta e três cidades de cinco estados: Amazonas, Pará, Maranhão, Amapá e Roraima."
    },
    {
        "speaker": "Carol",
        "voice": VOICE_CAROL,
        "text": "Lucas, para começarmos pelo começo: por que a equipe decidiu construir uma plataforma proprietária em vez de usar soluções de mercado tradicionais, como o Power B I ou o Tableau? O que essas ferramentas não conseguiam entregar no dia a dia da Regional Norte?"
    },
    {
        "speaker": "Lucas",
        "voice": VOICE_LUCAS,
        "text": "Carol, essa é a pergunta de um milhão de dólares! O Power B I e o Tableau são ferramentas conceituadas, mas no cenário operacional real da Regional Norte elas sofriam de três problemas crônicos. Primeiro: lentidão e peso excessivo. Um relatório pesado de Power B I leva de quinze a trinta segundos para carregar no navegador, baixando megabytes de código desnecessário. Quando um consultor comercial ou supervisor de campo está no interior do Pará ou do Maranhão, em uma rede três G ou quatro G intermitente, o painel simplesmente não abria ou travava o celular!"
    },
    {
        "speaker": "Carol",
        "voice": VOICE_CAROL,
        "text": "E para quem está na rua negociando com parceiros credenciados, esperar meio minuto por um número é impensável!"
    },
    {
        "speaker": "Lucas",
        "voice": VOICE_LUCAS,
        "text": "Exatamente! Segundo: o funcionamento offline. Se o diretor ou analista viaja de avião ou vai a uma área remota sem sinal de internet, o Power B I para de funcionar. Já o PEP HUB foi projetado com arquitetura offline-first. Cada relatório analítico pode ser baixado em um único arquivo H T M L autocontido, que abre instantaneamente em qualquer computador ou tablet, sem precisar de internet nenhuma. E terceiro: os custos exorbitantes de licenciamento por usuário, que no PEP HUB foram reduzidos a zero, aproveitando a rede de borda da Cloudflare."
    },
    {
        "speaker": "Carol",
        "voice": VOICE_CAROL,
        "text": "Nossa Lucas, que diferença brutal! E como é que a equipe conseguiu fazer um sistema tão rápido e leve, que carrega em menos de trezentos milissegundos? Qual é o segredo de engenharia por trás do código?"
    },
    {
        "speaker": "Lucas",
        "voice": VOICE_LUCAS,
        "text": "O grande pilar é o princípio de Zero Dependências Externas. Nós banimos frameworks pesados como React, Angular, Vue, Tailwind e bibliotecas de gráficos prontas como Chart ponto js ou D três. O frontend do PEP HUB foi escrito cem por cento em JavaScript moderno nativo, H T M L cinco semântico e C S S puro. Todos os gráficos são desenhados diretamente em S V G vetorial paramétrico, que se adapta com nitidez cristalina a qualquer tamanho de tela, de um smartphone a uma televisão gigante de sessenta e cinco polegadas na sala da Diretoria."
    },
    {
        "speaker": "Carol",
        "voice": VOICE_CAROL,
        "text": "E os mapas geoespaciais com milhares de clientes e pontos de rede? Como eles rodam tão lisos sem bibliotecas de mapas pesadas como Mapbox ou Google Maps?"
    },
    {
        "speaker": "Lucas",
        "voice": VOICE_LUCAS,
        "text": "Eles foram programados em H T M L cinco Canvas dois D com projeção matemática pura de Web Mercator! O usuário pode dar zoom, mover o mapa com fluidez e desenhar um laço livre com o mouse para filtrar clientes de um quarteirão específico. Além disso, os dados brutos são comprimidos com o algoritmo Deflate e descompactados em tempo real pela A P I nativa do navegador, sendo guardados em vetores tipados na memória, como Uint trinta e dois Array. Isso reduz o consumo de memória R A M em mais de oitenta por cento!"
    },
    {
        "speaker": "Carol",
        "voice": VOICE_CAROL,
        "text": "É engenharia de software de altíssimo nível, Lucas! Agora vamos falar dos seis relatórios analíticos fundamentais da plataforma. O primeiro deles é o famoso Painel Churn Safra D cento e vinte. O que ele monitora e por que a janela oficial é de cento e vinte dias?"
    },
    {
        "speaker": "Lucas",
        "voice": VOICE_LUCAS,
        "text": "Carol, o Churn Safra acompanha a desconexão definitiva dos contratos ao longo do tempo. Uma venda recém-instalada passa por um período crítico de maturação. Na Claro, o marco oficial é o D cento e vinte, que são os primeiros quatro meses do contrato. É nessa janela que é apurada a responsabilidade direta do canal de vendas e do parceiro credenciado. O painel rastreia o cancelamento voluntário, o involuntário por corte de inadimplência e o indicador de Nunca Pagou, que revela instalações que não pagaram sequer a primeira mensalidade."
    },
    {
        "speaker": "Carol",
        "voice": VOICE_CAROL,
        "text": "E isso nos leva direto ao segundo relatório: o Painel de F P D, o First Payment Default. Eu lembro que no passado houve uma tentativa de misturar os dados de F P D com as bases de Churn Safra, e isso causou uma confusão tremenda de colunas e métricas. Como isso foi consertado de vez?"
    },
    {
        "speaker": "Lucas",
        "voice": VOICE_LUCAS,
        "text": "Carol, essa foi uma regra de ouro estabelecida pela Diretoria: segregação total e absoluta! O F P D mede inadimplência na primeira fatura, que é um sintoma de qualidade de onboarding e esteira de crédito, enquanto o Churn Safra mede desconexão física do modem. Misturar os dois distorcia a responsabilidade dos vendedores. Nós isolamos o painel de F P D em uma base exclusiva, a Base F P D de treze safras da Regional Norte. O painel apresenta com clareza o F P D trinta dias pró-rata e o F P D sessenta dias de ciclo cheio oficial, além da análise de risco por faixas de score de crédito."
    },
    {
        "speaker": "Carol",
        "voice": VOICE_CAROL,
        "text": "Que clareza necessária! E o terceiro e quarto relatórios, que cobrem a Banda Larga Total e o segmento corporativo P M E? O que eles trazem de inteligência preditiva?"
    },
    {
        "speaker": "Lucas",
        "voice": VOICE_LUCAS,
        "text": "Eles trazem o monitoramento das quatro Tendências semanais, de T um a T quatro, confrontando o realizado com a meta orçada da companhia. Mas o grande destaque no segmento P M E foi uma descoberta empírica fantástica da nossa equipe: setenta e oito vírgula dois por cento dos cancelamentos de empresas ocorrem após o décimo segundo mês, exatamente quando termina a carência contratual da fidelidade! Por isso, o painel instituiu a Janela Crítica de Renegociação Proativa no Mês onze, orientando os consultores a procurarem o cliente trinta dias antes do contrato vencer para proteger a receita."
    },
    {
        "speaker": "Carol",
        "voice": VOICE_CAROL,
        "text": "Isso é pura geração de valor financeiro! E no relatório de Panorama Market Share da Anatel e no de Taxa de Aprovação de Crédito, que passaram por melhorias recentes, o que mudou na usabilidade?"
    },
    {
        "speaker": "Lucas",
        "voice": VOICE_LUCAS,
        "text": "No Market Share, nós reconstruímos o painel inteiro dentro do padrão visual elegante da Claro, com navegação rápida no topo para todos os outros módulos e acompanhamento preciso de saldo do líder, adições líquidas e provedores locais em cada município. E na Taxa de Aprovação de Crédito, nós jogamos fora aquela capa decorativa inútil para o diretor entrar direto nos dados executivos, ordenamos a tabela de lojas pelo maior volume de consultas e travamos nomes corporativos gigantes em até trinta caracteres com balõezinhos explicativos para não estourar a largura da tela."
    },
    {
        "speaker": "Carol",
        "voice": VOICE_CAROL,
        "text": "Espetacular! E temos também o ecossistema PeP Tools, com o Auxiliar de P P T e o Gerador de Cards de Aniversário para as televisões dos prédios da Regional Norte. Me conta sobre eles!"
    },
    {
        "speaker": "Lucas",
        "voice": VOICE_LUCAS,
        "text": "O Auxiliar de P P T, que antes era chamado de Market Share Studio, agora é uma central completa de produtividade executiva! O analista pode colar dados de uma planilha Excel e gerar gráficos de rosca, pizza, barras e organogramas prontos para apresentações da Diretoria, podendo copiar em S V G vetorial ou P N G em alta resolução com um clique só. E o Gerador de Cards de Aniversário foi ajustado com enquadramento matemático perfeito em formato dezesseis por nove, sem cortar a imagem em nenhum monitor ou televisor dos prédios operacionais."
    },
    {
        "speaker": "Carol",
        "voice": VOICE_CAROL,
        "text": "Agora Lucas, vamos para o tema que mais encanta todo mundo que conhece o PEP HUB: o robô de inteligência artificial no WhatsApp! Por que vocês criaram a tal da Arquitetura R A G Híbrida e não deixaram a inteligência artificial responder as perguntas matemáticas sozinha?"
    },
    {
        "speaker": "Lucas",
        "voice": VOICE_LUCAS,
        "text": "Carol, esse é o maior aprendizado que qualquer empresa moderna precisa entender sobre I A generativa! Modelos de linguagem como o Chat G P T ou o Gemini são excelentes para redigir textos e resumir conversas, mas são péssimos em matemática pura. Eles trabalham prevendo palavras estatisticamente. Se um gerente perguntar no WhatsApp: 'Qual foi o churn de Manaus em agosto?', e você deixar a I A calcular na memória, ela alucina: erra a soma, inventa casas decimais e passa um dado falso para a reunião de diretoria!"
    },
    {
        "speaker": "Carol",
        "voice": VOICE_CAROL,
        "text": "E em uma reunião de resultados, um número incorreto destrói a credibilidade da operação! Como o robô do PEP HUB resolveu isso?"
    },
    {
        "speaker": "Lucas",
        "voice": VOICE_LUCAS,
        "text": "Criamos uma rodovia de duas pistas estritamente separadas! Quando a pergunta chega no WhatsApp, um roteador identifica a intenção. Se for uma pergunta analítica com números, a I A não faz a conta: ela gera uma consulta S Q L segura e consulta diretamente o banco relacional Cloudflare D um! O banco devolve o número exato, por exemplo, dois vírgula trinta e quatro por cento. A I A apenas formata a mensagem com educação corporativa. Precisão de cem por cento, zero alucinações matemáticas! E se a dúvida for conceitual, como 'O que é F P D?', aí sim a segunda pista resgata as regras de negócio homologadas no banco."
    },
    {
        "speaker": "Carol",
        "voice": VOICE_CAROL,
        "text": "E ainda tem a checagem de carteirização pelo número de telefone do colaborador para garantir que ele só veja as cidades autorizadas! É uma segurança impecável. E me fala sobre a nova Central de Carga de Insumos no painel administrativo: como funciona a atualização das bases agora?"
    },
    {
        "speaker": "Lucas",
        "voice": VOICE_LUCAS,
        "text": "Essa foi a grande emancipação da equipe! Antes, qualquer nova safra exigia que um desenvolvedor rodasse scripts locais no computador. Agora, nós criamos uma aba central de Cargas com os sete insumos oficiais da Regional Norte. O administrador pode arrastar o arquivo na tela e o próprio navegador fatia o arquivo em pequenos blocos de quinhentos kilobytes, gravando direto no Cloudflare D um com barra de progresso em tempo real, sem gastar nem um centavo com armazenamentos caros como o Amazon S três."
    },
    {
        "speaker": "Carol",
        "voice": VOICE_CAROL,
        "text": "E com controle granular de delegação, certo? O gestor pode delegar a carga de um relatório para um analista sem dar acesso administrativo ao resto do sistema!"
    },
    {
        "speaker": "Lucas",
        "voice": VOICE_LUCAS,
        "text": "Exatamente! Se o administrador autorizar um estagiário ou analista a subir apenas a base de Market Share, quando esse colaborador faz login, as abas de usuários, travas do sistema e auditoria somem automaticamente. Ele vê apenas o card que foi delegado. Segurança por design com controle de acesso baseado em funções, o famoso R B A C."
    },
    {
        "speaker": "Carol",
        "voice": VOICE_CAROL,
        "text": "Lucas, que aula de arquitetura, segurança e governança corporativa! O PEP HUB foi submetido a todos os testes do Release Gate corporativo e obteve nota máxima A mais em Layout, A mais em Segurança de Aplicação e A mais em Arquitetura de Código. Tudo rodando com perfeição e pronto para o uso diário em produção no domínio pephub ponto cloud."
    },
    {
        "speaker": "Lucas",
        "voice": VOICE_LUCAS,
        "text": "É o orgulho da engenharia da Regional Norte da Claro! Uma plataforma veloz, à prova de falhas, offline-first e que coloca a melhor inteligência analítica na palma da mão dos nossos líderes e colaboradores."
    },
    {
        "speaker": "Carol",
        "voice": VOICE_CAROL,
        "text": "Sensacional! Esse foi o nosso episódio especial do Deep Dive do PEP HUB. Agradecemos a todos que nos ouviram e até a próxima edição!"
    },
    {
        "speaker": "Lucas",
        "voice": VOICE_LUCAS,
        "text": "Um grande abraço e até lá, pessoal!"
    },
    {
        "speaker": "Carol",
        "voice": VOICE_CAROL,
        "text": "Tchau tchau!"
    }
]

async def generate_segment(item, idx, temp_dir):
    filename = os.path.join(temp_dir, f"segment_{idx:03d}_{item['speaker']}.mp3")
    
    # Check if already generated and valid
    if os.path.exists(filename) and os.path.getsize(filename) > 2000:
        print(f"[{idx+1}/{len(DIALOGUE)}] Segmento {item['speaker']} já pronto ({os.path.getsize(filename)} bytes). Pulando...", flush=True)
        return filename

    if os.path.exists(filename):
        try:
            os.remove(filename)
        except Exception:
            pass

    max_retries = 4
    for attempt in range(1, max_retries + 1):
        try:
            print(f"[{idx+1}/{len(DIALOGUE)}] Gerando áudio de {item['speaker']} (tentativa {attempt}/{max_retries})...", flush=True)
            communicate = edge_tts.Communicate(item["text"], item["voice"], rate="+3%")
            await asyncio.wait_for(communicate.save(filename), timeout=35.0)
            
            if os.path.exists(filename) and os.path.getsize(filename) > 1000:
                print(f"[{idx+1}/{len(DIALOGUE)}] Segmento {item['speaker']} gravado com sucesso! ({os.path.getsize(filename)} bytes)", flush=True)
                await asyncio.sleep(0.4)
                return filename
        except Exception as e:
            print(f"⚠️ Alerta na tentativa {attempt} para {item['speaker']}: {e}", flush=True)
            if os.path.exists(filename):
                try:
                    os.remove(filename)
                except Exception:
                    pass
            await asyncio.sleep(1.5 * attempt)
            
    raise RuntimeError(f"Falha ao gerar segmento {idx} ({item['speaker']}) após {max_retries} tentativas.")

async def main():
    print("=" * 70, flush=True)
    print("🎙️ INICIANDO GERADOR DE PODCAST PEP HUB — EDIÇÃO ESPECIAL COMPLETA", flush=True)
    print("=" * 70, flush=True)
    
    temp_dir = os.path.join("public", "podcast", "temp_segments_full")
    os.makedirs(temp_dir, exist_ok=True)
    
    segment_files = []
    for idx, item in enumerate(DIALOGUE):
        f = await generate_segment(item, idx, temp_dir)
        segment_files.append(f)
    
    output_mp3 = os.path.join("public", "podcast", "pephub_deepdive_podcast.mp3")
    root_mp3 = "pephub_podcast.mp3"
    staging_mp3 = os.path.join("public_staging", "podcast", "pephub_deepdive_podcast.mp3")
    
    print("\n📦 Concatenando segmentos de áudio em arquivo único...", flush=True)
    with open(output_mp3, "wb") as outfile:
        for f in segment_files:
            with open(f, "rb") as infile:
                outfile.write(infile.read())
                
    # Copy to root and staging as well
    with open(root_mp3, "wb") as outfile:
        with open(output_mp3, "rb") as infile:
            outfile.write(infile.read())

    if os.path.exists(os.path.dirname(staging_mp3)):
        os.makedirs(os.path.dirname(staging_mp3), exist_ok=True)
        with open(staging_mp3, "wb") as outfile:
            with open(output_mp3, "rb") as infile:
                outfile.write(infile.read())
            
    # Also update transcript.json in public/podcast/
    transcript_file = os.path.join("public", "podcast", "transcript.json")
    with open(transcript_file, "w", encoding="utf-8") as f:
        json.dump(DIALOGUE, f, ensure_ascii=False, indent=2)
        
    size_mb = os.path.getsize(output_mp3) / (1024 * 1024)
    print(f"✅ Podcast definitivo gerado com sucesso!", flush=True)
    print(f"📁 Caminho: {output_mp3} ({size_mb:.2f} MB)", flush=True)
    print(f"📁 Cópia raiz: {root_mp3}", flush=True)
    print(f"📝 Transcrição atualizada: {transcript_file}", flush=True)
    print("=" * 70, flush=True)

if __name__ == "__main__":
    asyncio.run(main())
