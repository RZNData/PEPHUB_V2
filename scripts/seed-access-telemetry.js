const fs = require('fs');

// Gerador de telemetria realista da Regional Norte para o Dashboard de Acessos
// Cobre 30 dias com distribuição realista de dias da semana (picos ter/qui), horários comerciais e canais

const channels = [
  { area: 'LOJAS PRÓPRIAS', funcao: 'GERENTE', weight: 28 },
  { area: 'P&P', funcao: 'SUPERVISOR', weight: 26 },
  { area: 'VAREJO', funcao: 'CONSULTOR', weight: 18 },
  { area: 'AGENTE AUTORIZADO', funcao: 'EXECUTIVO/GN', weight: 14 },
  { area: 'PME', funcao: 'CONSULTOR', weight: 8 },
  { area: 'DIRETORIA', funcao: 'DIRETOR', weight: 4 },
  { area: 'MARKETING', funcao: 'ESPECIALISTA/COORDENADOR', weight: 2 }
];

const locations = [
  { cidade: 'Manaus', estado: 'AM', ip: '187.64.120.45', weight: 38 },
  { cidade: 'Belém', estado: 'PA', ip: '177.136.88.92', weight: 32 },
  { cidade: 'São Luís', estado: 'MA', ip: '189.40.15.22', weight: 14 },
  { cidade: 'Ananindeua', estado: 'PA', ip: '177.136.90.14', weight: 7 },
  { cidade: 'Macapá', estado: 'AP', ip: '179.184.210.66', weight: 5 },
  { cidade: 'Santarém', estado: 'PA', ip: '177.136.95.80', weight: 2 },
  { cidade: 'Boa Vista', estado: 'RR', ip: '179.184.230.12', weight: 2 }
];

const users = [
  { nome: 'Arthur Rezende', login: 'F138138', email: 'arthur.rezende@claro.com.br', area: 'DIRETORIA', funcao: 'ESPECIALISTA/COORDENADOR' },
  { nome: 'Operação Comercial Manaus', login: 'M991020', email: 'op.manaus@pephub.cloud', area: 'LOJAS PRÓPRIAS', funcao: 'GERENTE' },
  { nome: 'Coordenação P&P Pará', login: 'P883010', email: 'coord.pep.pa@pephub.cloud', area: 'P&P', funcao: 'SUPERVISOR' },
  { nome: 'Gestão Varejo Belém', login: 'V774020', email: 'gestao.varejo@pephub.cloud', area: 'VAREJO', funcao: 'GERENTE' },
  { nome: 'Supervisão Agentes AM', login: 'A665030', email: 'agentes.am@pephub.cloud', area: 'AGENTE AUTORIZADO', funcao: 'SUPERVISOR' },
  { nome: 'Consultoria PME Maranhão', login: 'P556040', email: 'pme.ma@pephub.cloud', area: 'PME', funcao: 'CONSULTOR' },
  { nome: 'Planejamento Regional', login: 'F138138', email: 'arthur.rezende@claro.com.br', area: 'MARKETING', funcao: 'ESPECIALISTA/COORDENADOR' },
  { nome: 'Diretoria Regional Norte', login: 'D100010', email: 'diretoria.norte@pephub.cloud', area: 'DIRETORIA', funcao: 'DIRETOR' },
  { nome: 'Equipe P&P Manaus', login: 'P883015', email: 'pep.manaus@pephub.cloud', area: 'P&P', funcao: 'SUPERVISOR' },
  { nome: 'Lojas Belém Metrópole', login: 'M991025', email: 'lojas.belem@pephub.cloud', area: 'LOJAS PRÓPRIAS', funcao: 'GERENTE' }
];

const resources = [
  { recurso: 'CHURN_SAFRA', weight: 58 },
  { recurso: 'CHURN_DOWNLOAD', weight: 16 },
  { recurso: 'PORTAL_HOME', weight: 14 },
  { recurso: 'LOGIN', weight: 12 }
];

function pick(arr) {
  const total = arr.reduce((acc, it) => acc + (it.weight || 1), 0);
  let rnd = Math.random() * total;
  for (const it of arr) {
    rnd -= (it.weight || 1);
    if (rnd <= 0) return it;
  }
  return arr[0];
}

const queries = [];
const now = new Date('2026-09-29T17:30:00Z');

for (let d = 28; d >= 0; d--) {
  // Mais acessos em dias de semana (seg-sex) que fim de semana
  const date = new Date(now.getTime() - d * 24 * 60 * 60 * 1000);
  const dayOfWeek = date.getUTCDay();
  const isWeekend = dayOfWeek === 0 || dayOfWeek === 6;
  const baseCount = isWeekend ? Math.floor(Math.random() * 6) + 3 : Math.floor(Math.random() * 18) + 14;

  for (let i = 0; i < baseCount; i++) {
    const u = users[Math.floor(Math.random() * users.length)];
    const loc = pick(locations);
    const res = pick(resources);

    // Horários comerciais com pico 09h-11h e 14h-17h
    let hour = Math.floor(Math.random() * 10) + 8; // 8h às 18h
    if (Math.random() < 0.2) hour = Math.floor(Math.random() * 4) + 19; // plantão noite

    const min = Math.floor(Math.random() * 60);
    const sec = Math.floor(Math.random() * 60);
    date.setUTCHours(hour, min, sec);

    const dateStr = date.toISOString().replace('T', ' ').substring(0, 19);
    const id = `telemetry-${d}-${i}-${Math.random().toString(36).substring(2, 7)}`;
    const localizacao = `${loc.cidade} - ${loc.estado}, BR`;

    queries.push(`INSERT INTO access_logs (id, user_id, login_claro, email_claro, nome_completo, area, funcao, recurso, ip, cidade, estado, pais, localizacao, user_agent, created_at) VALUES ('${id}', 'seed-user', '${u.login}', '${u.email}', '${u.nome}', '${u.area}', '${u.funcao}', '${res.recurso}', '${loc.ip}', '${loc.cidade}', '${loc.estado}', 'BR', '${localizacao}', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/128.0', '${dateStr}');`);
  }
}

fs.writeFileSync('seed_telemetry.sql', queries.join('\n'), 'utf8');
console.log(`Geradas ${queries.length} entradas de telemetria em seed_telemetry.sql`);
