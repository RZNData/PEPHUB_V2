# 🏛️ Guia de Arquitetura e Modularização — Pephub Churn

> **Documento Explicativo para Gestão, Engenharia e Novos Desenvolvedores**  
> *Linguagem acessível, didática e estruturada segundo as melhores práticas de Engenharia de Software.*

---

## 1. Contexto e Motivação: Por que Refatorar?

### O Problema do "Arquivo Monolítico"
Anteriormente, o arquivo [`scripts/generate_churn_reports.py`](file:///c:/Users/F138138/DEV/Churn_Safra/scripts/generate_churn_reports.py) acumulava **mais de 3.170 linhas de código** em um único bloco contínuo. 

Dentro de uma única função em Python, estavam misturados:
1. Todo o código visual e de estilização (**CSS**) com mais de 250 linhas;
2. Toda a estrutura de páginas (**HTML**) com mais de 650 linhas;
3. Toda a lógica de gráficos, filtros e tabelas (**JavaScript**) com mais de 2.200 linhas;
4. Todo o código de carregamento e gravação de arquivos (**Python**).

### Riscos que isso trazia para a Escalabilidade:
* **Efeito Dominó (Fragilidade):** Alterar uma linha de CSS corria o risco de quebrar o Python ou corromper o JavaScript por causa da necessidade de dobrar todas as chaves (`{{` e `}}`).
* **Lentidão em Ferramentas:** Editores de código e IDEs travavam ou perdiam o autocompletar e a checagem de erros.
* **Dificuldade de Crescimento:** Incluir novos segmentos (ex: Móvel, TV, Fibra) tornava o arquivo cada vez mais pesado e impossível de manter em equipe.

---

## 2. A Nova Arquitetura: O Padrão MVP (Model-View-Presenter)

Para resolver esse desafio e garantir escalabilidade de nível empresarial, adotamos o padrão **MVP (Model-View-Presenter)**, muito consagrado em frameworks modernos e no ecossistema web:

```
                      ┌────────────────────────┐
                      │      FONTE DE DADOS    │
                      │  (data.json / SQLite)  │
                      └───────────┬────────────┘
                                  │
                                  ▼
 ┌─────────────────────────────────────────────────────────────────┐
 │                            MODEL                                │
 │               (src/models/churn_dataset.py)                     │
 │   • Carrega e valida os dados brutos                            │
 │   • Garante integridade (evita dados nulos ou corrompidos)      │
 └────────────────────────────────┬────────────────────────────────┘
                                  │
                                  ▼
 ┌─────────────────────────────────────────────────────────────────┐
 │                          PRESENTER                              │
 │             (src/presenters/panel_presenter.py)                 │
 │   • O "Maestro": une os dados validados aos templates visuais   │
 │   • Compila e exporta os painéis finais prontos para uso        │
 └────────────────────────────────┬────────────────────────────────┘
                                  │
                                  ▼
 ┌─────────────────────────────────────────────────────────────────┐
 │                            VIEW                                 │
 │                 (templates/churn_panel/)                        │
 │   ├── styles.css   (Folha de estilos limpa, cores e layouts)   │
 │   ├── layout.html  (Estrutura semântica das páginas)            │
 │   └── app.js       (Inteligência no navegador: filtros/charts) │
 └─────────────────────────────────────────────────────────────────┘
```

---

## 3. A Analogia do Restaurante (Entendendo o MVP de Forma Simples)

Se o nosso projeto fosse um **restaurante executivo de alta gastronomia**, a divisão funcionaria assim:

1. **O MODEL é a Despensa e o Controle de Qualidade dos Ingredientes:**
   * Ele não sabe como arrumar a mesa nem que talheres usar.
   * Sua única função é garantir que os ingredientes (os dados de Churn de Manaus, Belém, etc.) estejam frescos, completos e validados. Se faltar a data ou o volume, o Model avisa imediatamente antes que o prato seja preparado.

2. **A VIEW é o Salão, a Louça Bonita e a Decoração:**
   * É o que o cliente (usuário) vê e toca.
   * O arquivo `styles.css` cuida das cores institucionais da Claro, dos contrastes e do alinhamento.
   * O arquivo `layout.html` define onde fica o cabeçalho, onde ficam os cartões de resumo e onde ficam as tabelas.
   * O arquivo `app.js` é a interatividade: ao clicar em uma cidade no menu ou no gráfico, o garçom traz apenas os dados daquela cidade sem recarregar a página.

3. **O PRESENTER é o Chef de Cozinha (O Maestro):**
   * Ele pega os ingredientes aprovados pelo **Model**, monta no prato definido pela **View** e entrega o relatório final quentinho e pronto na mesa.

---

## 4. O Mapa da Mina: O que Cada Módulo Faz

Aqui está o inventário de cada arquivo da nova estrutura e a sua exata responsabilidade:

### 📁 1. Camada de Apresentação e Telas (Views)
Localização: [`templates/churn_panel/`](file:///c:/Users/F138138/DEV/Churn_Safra/templates/churn_panel)

* **[`styles.css`](file:///c:/Users/F138138/DEV/Churn_Safra/templates/churn_panel/styles.css)**:
  * **O que faz:** Centraliza 100% da parte visual do painel.
  * **Do que cuida:** Variáveis de cores Claro (`--red`, `--amber`, `--green`), estilização de tabelas com linhas cinzas (`col-sep`), barras de rolagem customizadas, hovers e regras para popups fixáveis.
  * **Vantagem:** Designers e desenvolvedores front-end podem mexer no visual usando CSS puro, sem tocar em uma única linha de Python!

* **[`layout.html`](file:///c:/Users/F138138/DEV/Churn_Safra/templates/churn_panel/layout.html)**:
  * **O que faz:** O esqueleto semântico das páginas.
  * **Do que cuida:** Cabeçalho padrão, botões de ação (exportar, modo taxa, drawer de filtros), seções de cartões KPI, contêiner do gráfico de dispersão, tabela de acompanhamento analítico, painel de involuntário e área de Speech Analytics.
  * **Vantagem:** Utiliza marcações limpas como `{{TITLE_MAIN}}` e `{{SEGMENT_KEY}}`, eliminando emaranhados de código.

* **[`app.js`](file:///c:/Users/F138138/DEV/Churn_Safra/templates/churn_panel/app.js)**:
  * **O que faz:** Toda a inteligência dinâmica que roda no navegador do usuário.
  * **Do que cuida:**
    * Gráficos SVG interativos (evolução temporal, dispersão e ofensores);
    * Filtros dinâmicos (isolar cidade no gráfico de dispersão, alternar entre clusters GM e MD);
    * Modo Taxa % vs Volume Real (converte números para percentual e comparativos para `p.p.`);
    * Modais e popups detalhados com congelamento ao clique.
  * **Vantagem:** Código JavaScript puro, verificado e validado com checagem de sintaxe nativa.

---

### 📁 2. Camada de Modelos de Dados (Model)
Localização: [`src/models/`](file:///c:/Users/F138138/DEV/Churn_Safra/src/models)

* **[`churn_dataset.py`](file:///c:/Users/F138138/DEV/Churn_Safra/src/models/churn_dataset.py)**:
  * **O que faz:** Carrega os arquivos JSON consolidados (`public/churn-bl-total/data.json` e `public/churn-bl-pme/data.json`).
  * **Do que cuida:**
    * Valida se todas as chaves obrigatórias existem antes de compilar;
    * Impede que erros de digitação ou arquivos incompletos cheguem à tela do usuário;
    * Fornece métodos fáceis para ler cidades, modos (Total, Voluntário, Involuntário) e clusters.

---

### 📁 3. Camada de Orquestração (Presenter)
Localização: [`src/presenters/`](file:///c:/Users/F138138/DEV/Churn_Safra/src/presenters)

* **[`panel_presenter.py`](file:///c:/Users/F138138/DEV/Churn_Safra/src/presenters/panel_presenter.py)**:
  * **O que faz:** É o compilador do sistema.
  * **Do que cuida:**
    * Lê os templates de tela (`styles.css`, `layout.html`, `app.js`);
    * Solicita os dados limpos ao `ChurnDataset`;
    * Junta tudo em memória de forma ultrarrápida;
    * Grava os arquivos finais nos destinos corretos (`public/churn-bl-total/index.html`, etc.).

---

### 📁 4. Ponto de Entrada Simplificado (Entrypoint)
Localização: [`scripts/generate_churn_reports.py`](file:///c:/Users/F138138/DEV/Churn_Safra/scripts/generate_churn_reports.py)

* **Reduzido de 3.178 linhas para apenas 53 linhas!**
* **O que faz:** Serve como a "chave de ignição". Qualquer script, pipeline agendada ou tarefa automatizada continua chamando:
  ```bash
  python scripts/generate_churn_reports.py
  ```
  O script aciona o `PanelPresenter` e faz todo o trabalho sem que nada do legado precise ser alterado.

---

### 📁 5. Módulo do Bot de WhatsApp (Regional Norte)
Localização: [`whatsapp-bot/`](file:///c:/Users/F138138/DEV/Churn_Safra/whatsapp-bot)

Criado especificamente para permitir consultas em grupos do WhatsApp:
* **[`data_engine.py`](file:///c:/Users/F138138/DEV/Churn_Safra/whatsapp-bot/data_engine.py)**: Motor de busca e formatação com badges (`🟢`, `🔴`), siglas empresariais (`p.p.`, `MoM`, `YoY`) e números em formato brasileiro (`4.550,1`).
* **[`agent.py`](file:///c:/Users/F138138/DEV/Churn_Safra/whatsapp-bot/agent.py)**: Inteligência de compreensão de perguntas em português livre (cidades, rankings, perdas involuntárias, speech analytics do call center).
* **[`server.py`](file:///c:/Users/F138138/DEV/Churn_Safra/whatsapp-bot/server.py)**: Servidor de webhooks compatível com a Evolution API e Z-API.
* **[`simulator.html`](file:///c:/Users/F138138/DEV/Churn_Safra/whatsapp-bot/simulator.html)**: Simulador web interativo que roda em `http://localhost:8085/` para testar antes de ligar ao WhatsApp real.
* **[`evolution/`](file:///c:/Users/F138138/DEV/Churn_Safra/whatsapp-bot/evolution)**: Ambiente completo Docker, `.env`, cliente REST e script de 1 clique (`setup_instance.py`) para gerar o QR Code.

---

## 5. Como Isso Protege a Escalabilidade Futura?

| Cenário de Futuro | Como Era no Modelo Antigo | Como Ficou no Novo Modelo Modular |
| :--- | :--- | :--- |
| **Alterar o design de um gráfico** | Precisava caçar linhas específicas no meio de 3.170 linhas de Python com chaves dobradas `{{}}`. | Abre diretamente o [`templates/churn_panel/app.js`](file:///c:/Users/F138138/DEV/Churn_Safra/templates/churn_panel/app.js), altera com validação em tempo real e pronto. |
| **Ajustar as cores da marca Claro** | Mexer em strings de f-string com risco de quebrar a compilação. | Abre o [`templates/churn_panel/styles.css`](file:///c:/Users/F138138/DEV/Churn_Safra/templates/churn_panel/styles.css) e muda as variáveis `:root` em segundos. |
| **Adicionar novo segmento (ex: Móvel)** | Duplicar ou inchar ainda mais o script monolítico. | Cria uma nova chamada no `panel_presenter.py` apontando para o novo `data.json`. Todo o visual é reaproveitado automaticamente! |
| **Testes de Qualidade** | Impossível testar partes isoladas. | Podemos testar o Model separadamente da View e validar o JavaScript com ferramentas profissionais. |

---

## 6. Comandos Rápidos do Dia a Dia

### Gerar todos os relatórios compilados:
```powershell
python scripts/generate_churn_reports.py
```

### Rodar a bateria de validação dos 8 requisitos de negócio:
```powershell
node scripts/verify_all_user_requirements.js
node scripts/test_dynamic_filters.js
```

### Iniciar o simulador do Bot de WhatsApp:
```powershell
cd whatsapp-bot
python server.py
# Acesse no navegador: http://localhost:8085/
```

### Iniciar a Evolution API (via Docker):
```powershell
cd whatsapp-bot/evolution
docker compose up -d
python setup_instance.py
```
