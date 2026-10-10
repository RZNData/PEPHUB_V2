-- Migration: Tabela de Acessos e Ajustes de Privilégios

CREATE TABLE IF NOT EXISTS access_logs (
  id TEXT PRIMARY KEY,
  user_id TEXT,
  login_claro TEXT,
  email_claro TEXT,
  nome_completo TEXT,
  recurso TEXT,
  ip TEXT,
  cidade TEXT,
  estado TEXT,
  pais TEXT,
  localizacao TEXT,
  user_agent TEXT,
  created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_access_logs_created ON access_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_access_logs_email ON access_logs(email_claro);
CREATE INDEX IF NOT EXISTS idx_access_logs_ip ON access_logs(ip);

-- Atualiza colunas na tabela users se não existirem
ALTER TABLE users ADD COLUMN must_change_password INTEGER NOT NULL DEFAULT 0;
ALTER TABLE users ADD COLUMN modules_allowed TEXT DEFAULT 'churn';

-- Inserir / Atualizar o usuário admin oficial (senha #a1d2m3i4n5)
INSERT INTO users (
  id, nome_completo, login_claro, email_claro, area, funcao,
  password_hash, salt, status, is_admin, notify_updates, created_at, approved_at, modules_allowed
) VALUES (
  'admin-master',
  'Administrador do Sistema',
  'admin',
  'admin@pephub.cloud',
  'DIRETORIA',
  'DIRETOR',
  '0b3a90ea7be5cb0088a4d6a6b265c0a3f456796cda17875b83afce4681227496',
  '63ec914a52da560bc5edb76e8428db56',
  'aprovado',
  1,
  1,
  datetime('now'),
  datetime('now'),
  'all'
) ON CONFLICT(email_claro) DO UPDATE SET
  password_hash = '0b3a90ea7be5cb0088a4d6a6b265c0a3f456796cda17875b83afce4681227496',
  salt = '63ec914a52da560bc5edb76e8428db56',
  is_admin = 1,
  status = 'aprovado',
  login_claro = 'admin';

-- Também atualizar a conta de Arthur Rezende com a mesma senha de admin
UPDATE users SET 
  password_hash = '0b3a90ea7be5cb0088a4d6a6b265c0a3f456796cda17875b83afce4681227496',
  salt = '63ec914a52da560bc5edb76e8428db56',
  is_admin = 1,
  status = 'aprovado',
  modules_allowed = 'all'
WHERE email_claro = 'arthur.rezende.analista@gmail.com';
