const https = require('https');

// Ignorar verificação estrita temporária se necessário para testes locais
process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';

function request(options, data = null) {
  return new Promise((resolve, reject) => {
    const req = https.request(options, (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => resolve({
        statusCode: res.statusCode,
        headers: res.headers,
        body
      }));
    });
    req.on('error', reject);
    if (data) {
      req.write(typeof data === 'string' ? data : JSON.stringify(data));
    }
    req.end();
  });
}

async function run() {
  console.log('=== TESTE DE VALIDAÇÃO PEPHUB.CLOUD ===\n');

  // 1. Testar acesso não-autenticado a /churn/ (deve redirecionar 302 para /login/)
  console.log('1. Testando proteção de rota /churn/ (sem cookie):');
  const resChurnUnauth = await request({
    hostname: 'pephub.cloud',
    path: '/churn/',
    method: 'GET',
    headers: { 'User-Agent': 'TestClient/1.0' }
  });
  console.log(`Status: ${resChurnUnauth.statusCode} | Location: ${resChurnUnauth.headers.location || 'nenhum'}`);
  if (resChurnUnauth.statusCode === 302 && (resChurnUnauth.headers.location || '').includes('/login/')) {
    console.log('✅ Rota /churn/ protegida com sucesso! Redirecionamento 302 ativo.');
  } else {
    console.log('⚠️ Atenção no redirecionamento /churn/:', resChurnUnauth.statusCode);
  }

  // 2. Testar páginas públicas
  console.log('\n2. Testando páginas de autenticação pública:');
  for (const page of ['/login/', '/register/', '/forgot-password/']) {
    const res = await request({
      hostname: 'pephub.cloud',
      path: page,
      method: 'GET'
    });
    console.log(`${page}: Status ${res.statusCode} (${res.body.length} bytes)`);
  }

  // 3. Testar Login do Administrador Arthur Rezende
  console.log('\n3. Testando Login do Gestor (Arthur Rezende):');
  const loginRes = await request({
    hostname: 'pephub.cloud',
    path: '/api/auth/login',
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  }, {
    email_claro: 'arthur.rezende.analista@gmail.com',
    password: 'Claro#2026'
  });
  console.log(`Login Admin Status: ${loginRes.statusCode}`);
  const setCookie = loginRes.headers['set-cookie'];
  const sessionCookie = setCookie ? setCookie[0].split(';')[0] : null;
  console.log(`Cookie de Sessão: ${sessionCookie ? sessionCookie.substring(0, 35) + '...' : 'NÃO RECEBIDO'}`);

  if (sessionCookie) {
    // 4. Testar acesso ao /churn/ COM sessão válida
    console.log('\n4. Testando acesso ao /churn/ COM sessão válida:');
    const resChurnAuth = await request({
      hostname: 'pephub.cloud',
      path: '/churn/',
      method: 'GET',
      headers: {
        'Cookie': sessionCookie
      }
    });
    console.log(`Status /churn/ Autenticado: ${resChurnAuth.statusCode} | Tamanho: ${resChurnAuth.body.length} bytes`);
    if (resChurnAuth.statusCode === 200 && resChurnAuth.body.includes('churnUserWidget')) {
      console.log('✅ Painel /churn/ carregado com sucesso com Widget de Usuário!');
    }

    // 5. Testar rota de download direto do HTML (/churn/download)
    console.log('\n5. Testando download direto (/churn/download):');
    const resDownload = await request({
      hostname: 'pephub.cloud',
      path: '/churn/download',
      method: 'GET',
      headers: { 'Cookie': sessionCookie }
    });
    console.log(`Status Download: ${resDownload.statusCode} | Content-Disposition: ${resDownload.headers['content-disposition'] || 'nenhum'} | Tamanho: ${resDownload.body.length} bytes`);

    // 6. Testar /api/admin/users
    console.log('\n6. Testando listagem administrativa (/api/admin/users):');
    const resAdminUsers = await request({
      hostname: 'pephub.cloud',
      path: '/api/admin/users',
      method: 'GET',
      headers: { 'Cookie': sessionCookie }
    });
    console.log(`Status Admin Users: ${resAdminUsers.statusCode}`);
    if (resAdminUsers.statusCode === 200) {
      const users = JSON.parse(resAdminUsers.body);
      console.log(`Total de usuários cadastrados no D1: ${users.length}`);
      users.forEach(u => console.log(` - [${u.status.toUpperCase()}] ${u.nome_completo} (${u.email_claro}) - Área: ${u.area} / Função: ${u.funcao}`));
    }
  }

  console.log('\n=== TESTES CONCLUÍDOS ===');
}

run().catch(console.error);
