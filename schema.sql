-- =====================================================================
-- PEPHUB CLOUD - SCHEMA OFICIAL CLOUDFLARE D1
-- Arquitetura: Autenticação, Carteirização, Fatos Analíticos e Semantic RAG
-- Regional Norte: AM, PA, MA, AP, RR
-- =====================================================================

-- 1. USUÁRIOS E SEGURANÇA BÁSICA
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    login_claro TEXT UNIQUE NOT NULL,
    email_claro TEXT UNIQUE NOT NULL,
    nome_completo TEXT NOT NULL,
    senha_hash TEXT NOT NULL,
    senha_salt TEXT NOT NULL,
    area TEXT NOT NULL,
    funcao TEXT NOT NULL,
    telefone TEXT,
    status TEXT NOT NULL DEFAULT 'pendente',
    is_admin INTEGER NOT NULL DEFAULT 0,
    must_change_password INTEGER NOT NULL DEFAULT 0,
    modules_allowed TEXT DEFAULT 'churn,fpd,churn-bl-total,churn-bl-pme,divulgacao,tv,panorama-market-share,aprovacao-credito',
    profile_metadata TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME
);

CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    token TEXT UNIQUE NOT NULL,
    expires_at TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS login_attempts (
    ip TEXT NOT NULL,
    login TEXT NOT NULL,
    fail_count INTEGER NOT NULL DEFAULT 1,
    last_attempt TEXT NOT NULL,
    locked_until TEXT,
    PRIMARY KEY (ip, login)
);

CREATE TABLE IF NOT EXISTS access_logs (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    login_claro TEXT,
    email_claro TEXT,
    nome_completo TEXT,
    area TEXT,
    funcao TEXT,
    recurso TEXT,
    ip TEXT,
    cidade TEXT,
    estado TEXT,
    pais TEXT,
    localizacao TEXT,
    user_agent TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS system_controls (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    label TEXT NOT NULL,
    description TEXT NOT NULL,
    updated_at TEXT,
    updated_by TEXT
);

CREATE TABLE IF NOT EXISTS system_modules (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    short_name TEXT NOT NULL,
    section TEXT NOT NULL,
    description TEXT,
    route TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'ativo',
    sort_order INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME
);

-- =====================================================================
-- 2. CARTEIRIZAÇÃO & CONTROLE DE ESCOPO ANALÍTICO DO WHATSAPP
-- =====================================================================
CREATE TABLE IF NOT EXISTS dim_carteirizacao (
    id TEXT PRIMARY KEY,
    telefone TEXT NOT NULL UNIQUE,
    user_id TEXT,
    nome TEXT NOT NULL,
    regional TEXT DEFAULT 'REGIONAL NORTE',
    canal TEXT DEFAULT 'TODOS',
    cidade TEXT DEFAULT 'TODAS',
    permissao_total INTEGER NOT NULL DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- =====================================================================
-- 3. TABELAS DE FATOS ANALÍTICOS (TEXT-TO-SQL)
-- =====================================================================

-- 3.1. Fato Indicadores Mensais (Churn Banda Larga Total e PME)
CREATE TABLE IF NOT EXISTS fato_indicadores_mensais (
    id TEXT PRIMARY KEY,
    segmento TEXT NOT NULL,               -- 'Banda Larga Total' | 'Banda Larga PME'
    mes_referencia TEXT NOT NULL,         -- '2026-09' ou 'Setembro / 2026'
    tipo_visao TEXT NOT NULL,             -- 'TOTAL' | 'VOLUNTARIO' | 'INVOLUNTARIO'
    cidade TEXT NOT NULL,                 -- 'Regional Norte', 'Belém', 'Manaus', etc.
    uf TEXT NOT NULL,                     -- 'RNO', 'PA', 'AM', 'MA', 'AP', 'RR'
    vol_real REAL DEFAULT 0,
    vol_orc REAL DEFAULT 0,
    rxo_delta REAL DEFAULT 0,
    rxo_pct REAL DEFAULT 0,
    mom_delta REAL DEFAULT 0,
    mom_pct REAL DEFAULT 0,
    yoy_delta REAL DEFAULT 0,
    yoy_pct REAL DEFAULT 0,
    base_real REAL DEFAULT 0,
    base_orc REAL DEFAULT 0,
    taxa_real REAL DEFAULT 0,
    taxa_orc REAL DEFAULT 0,
    taxa_delta_pp REAL DEFAULT 0,
    tendencia_t1 REAL DEFAULT 0,
    tendencia_t2 REAL DEFAULT 0,
    tendencia_t3 REAL DEFAULT 0,
    tendencia_t4 REAL DEFAULT 0,
    ytd_real REAL DEFAULT 0,
    ytd_orc REAL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 3.2. Fato Churn Safra D120 (Sobrevivência, Inadimplência e Fraude)
CREATE TABLE IF NOT EXISTS fato_churn_safra (
    id TEXT PRIMARY KEY,
    safra TEXT NOT NULL,                  -- 'set/25', 'out/25', ..., 'mai/26', 'ago/26'
    safra_ord TEXT,                       -- '2025-09' ... '2026-09' (Ordenação Cronológica)
    visao TEXT NOT NULL,                  -- 'REGIONAL' | 'CIDADE' | 'PARCEIRO' | 'OPERACAO'
    entidade_nome TEXT NOT NULL,          -- 'Regional Norte', 'Belém', 'TOP CONNECT', etc.
    cidade TEXT,
    uf TEXT,
    instalacoes INTEGER DEFAULT 0,
    churn_d30 INTEGER DEFAULT 0,
    churn_d60 INTEGER DEFAULT 0,
    churn_d90 INTEGER DEFAULT 0,
    churn_d120 INTEGER DEFAULT 0,
    np120 INTEGER DEFAULT 0,
    taxa_d30 REAL DEFAULT 0,
    taxa_d60 REAL DEFAULT 0,
    taxa_d90 REAL DEFAULT 0,
    taxa_d120 REAL DEFAULT 0,
    taxa_np120 REAL DEFAULT 0,
    inadimplencia INTEGER DEFAULT 0,
    fraude INTEGER DEFAULT 0,
    status_safra TEXT DEFAULT 'MADURA',   -- 'MADURA' | 'EM_ABERTO'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 3.3. Fato FPD (First Payment Default - 30 e 60 dias)
CREATE TABLE IF NOT EXISTS fato_fpd (
    id TEXT PRIMARY KEY,
    safra TEXT NOT NULL,                  -- 'jan/26', 'fev/26', ..., 'mai/26'
    safra_ord TEXT,                       -- '2026-01' ... '2026-05' (Ordenação Cronológica)
    cidade TEXT NOT NULL,
    uf TEXT NOT NULL,
    canal TEXT DEFAULT 'GERAL',           -- 'PAP', 'Lojas', 'Televendas', 'Digital'
    familia_produto TEXT DEFAULT 'Dados', -- 'Dados', 'Vídeo + Dados', etc.
    instalacoes INTEGER DEFAULT 0,
    fpd30 INTEGER DEFAULT 0,
    taxa_fpd30 REAL DEFAULT 0,
    fpd60 INTEGER DEFAULT 0,
    taxa_fpd60 REAL DEFAULT 0,
    cura INTEGER DEFAULT 0,
    taxa_cura REAL DEFAULT 0,
    faixa_risco TEXT DEFAULT 'MEDIO',     -- Faixa de Risco NV ou Score
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 3.4. Fato Aprovação de Crédito PF
CREATE TABLE IF NOT EXISTS fato_aprovacao_credito (
    id TEXT PRIMARY KEY,
    mes_referencia TEXT NOT NULL,         -- '2026-08', '2026-09'
    cidade TEXT NOT NULL,
    uf TEXT NOT NULL,
    canal TEXT DEFAULT 'TODOS',
    pdv_ou_parceiro TEXT,
    consultas INTEGER DEFAULT 0,
    aprovados INTEGER DEFAULT 0,
    taxa_aprovacao REAL DEFAULT 0,
    recusas_politica INTEGER DEFAULT 0,
    recusas_antifraude INTEGER DEFAULT 0,
    risco_alto INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 3.5. Fato Market Share (Anatel / Regional Norte)
CREATE TABLE IF NOT EXISTS fato_market_share (
    id TEXT PRIMARY KEY,
    mes_referencia TEXT NOT NULL,         -- '2026-08', '2026-09'
    cidade TEXT NOT NULL,
    uf TEXT NOT NULL,
    operadora TEXT NOT NULL,              -- 'Claro', 'Vivo', 'Oi', 'Competitivas/ISPs'
    acessos INTEGER DEFAULT 0,
    market_share_pct REAL DEFAULT 0,
    net_adds INTEGER DEFAULT 0,
    posicao_ranking INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================================
-- 4. BASE DE CONHECIMENTO SEMÂNTICO (SEMANTIC RAG)
-- =====================================================================
CREATE TABLE IF NOT EXISTS bot_knowledge_chunks (
    id TEXT PRIMARY KEY,
    modulo TEXT NOT NULL,                 -- 'churn-bl-total', 'churn-bl-pme', 'churn-safra', 'fpd', 'aprovacao-credito', 'market-share', 'regras-gerais'
    topico TEXT NOT NULL,                 -- ex: 'Definição de FPD 30 vs FPD 60', 'Regra de Churn Safra D120'
    pergunta_exemplo TEXT,                -- 'O que é FPD?', 'Como calcula o NP120?'
    conteudo TEXT NOT NULL,               -- Texto explicativo detalhado e regras oficiais
    palavras_chave TEXT,                  -- 'fpd, default, primeiro pagamento, aging30, aging60'
    regras_calculo TEXT,                  -- '(AGING30 == 1 AND AGING60 == 1) / instalacoes'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS bot_pending_sessions (
    phone TEXT PRIMARY KEY,
    query TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================================
-- 5. ÁREA CENTRALIZADA DE UPLOADS & INSUMOS DE RELATÓRIOS
-- =====================================================================
CREATE TABLE IF NOT EXISTS upload_delegations (
    id TEXT PRIMARY KEY,
    scope_type TEXT NOT NULL,             -- 'ALL', 'churn-safra', 'fpd', 'churn-bl-total', 'churn-bl-pme', 'panorama-market-share', 'aprovacao-credito', 'bot-knowledge'
    scope_value TEXT NOT NULL DEFAULT 'ALL',
    delegated_user_id TEXT NOT NULL,
    delegated_user_name TEXT NOT NULL,
    delegated_user_email TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    FOREIGN KEY(delegated_user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS report_uploads (
    id TEXT PRIMARY KEY,
    report_key TEXT NOT NULL,             -- 'churn-safra', 'fpd', 'churn-bl-total', 'churn-bl-pme', 'panorama-market-share', 'aprovacao-credito', 'bot-knowledge'
    filename TEXT NOT NULL,
    filesize INTEGER NOT NULL,
    filetype TEXT NOT NULL,
    uploader_id TEXT NOT NULL,
    uploader_name TEXT NOT NULL,
    uploader_email TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'completed',
    records_count INTEGER DEFAULT 0,
    summary_metadata TEXT,
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS upload_file_chunks (
    id TEXT PRIMARY KEY,
    upload_id TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    chunk_data TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(upload_id) REFERENCES report_uploads(id) ON DELETE CASCADE
);

-- =====================================================================
-- 6. ÍNDICES DE PERFORMANCE D1 (OTIMIZAÇÃO DE CONSULTAS E FILTROS)
-- =====================================================================
CREATE INDEX IF NOT EXISTS idx_carteirizacao_tel ON dim_carteirizacao(telefone);
CREATE INDEX IF NOT EXISTS idx_carteirizacao_user ON dim_carteirizacao(user_id);

CREATE INDEX IF NOT EXISTS idx_ind_seg_mes_cid ON fato_indicadores_mensais(segmento, mes_referencia, tipo_visao, cidade);
CREATE INDEX IF NOT EXISTS idx_ind_cidade_uf ON fato_indicadores_mensais(cidade, uf);

CREATE INDEX IF NOT EXISTS idx_safra_visao_ent ON fato_churn_safra(safra, visao, entidade_nome);
CREATE INDEX IF NOT EXISTS idx_safra_cidade ON fato_churn_safra(cidade, safra);
CREATE INDEX IF NOT EXISTS idx_safra_ord ON fato_churn_safra(safra_ord DESC);

CREATE INDEX IF NOT EXISTS idx_fpd_safra_cid ON fato_fpd(safra, cidade);
CREATE INDEX IF NOT EXISTS idx_fpd_safra_ord ON fato_fpd(safra_ord DESC);
CREATE INDEX IF NOT EXISTS idx_fpd_canal ON fato_fpd(canal);

CREATE INDEX IF NOT EXISTS idx_aprov_mes_cid ON fato_aprovacao_credito(mes_referencia, cidade);
CREATE INDEX IF NOT EXISTS idx_mkt_mes_cid_op ON fato_market_share(mes_referencia, cidade, operadora);

CREATE INDEX IF NOT EXISTS idx_knowledge_mod_topico ON bot_knowledge_chunks(modulo, topico);
CREATE INDEX IF NOT EXISTS idx_knowledge_keywords ON bot_knowledge_chunks(palavras_chave);

CREATE INDEX IF NOT EXISTS idx_upload_del_user ON upload_delegations(delegated_user_id);
CREATE INDEX IF NOT EXISTS idx_report_uploads_key ON report_uploads(report_key, created_at DESC);

-- =====================================================================
-- 7. NOTIFICAÇÕES CORPORATIVAS & PRESETS DO SISTEMA
-- =====================================================================
CREATE TABLE IF NOT EXISTS notifications (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    type TEXT NOT NULL DEFAULT 'info',         -- 'info', 'warning', 'success', 'update', 'security'
    preset TEXT NOT NULL DEFAULT 'custom',     -- 'custom', 'first_login', 'password_change', 'new_report', 'maintenance'
    target_audience TEXT NOT NULL DEFAULT 'ALL',-- 'ALL', 'regular', 'admin', ou área
    action_url TEXT,
    action_label TEXT,
    starts_at TEXT,
    expires_at TEXT,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_by TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_notifications_read (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    notification_id TEXT NOT NULL,
    read_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    dismissed INTEGER NOT NULL DEFAULT 0,
    UNIQUE(user_id, notification_id),
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY(notification_id) REFERENCES notifications(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_notifications_active ON notifications(is_active, starts_at, expires_at);
CREATE INDEX IF NOT EXISTS idx_user_notif_read_user ON user_notifications_read(user_id, notification_id);
