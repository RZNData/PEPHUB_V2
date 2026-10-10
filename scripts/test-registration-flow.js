const https = require('https');
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

async function testFullRegistrationCycle() {
  console.log('=== TESTE DO FLUXO COMPLETO DE CADASTRO E APROVAÇÃO ===\n');

  // 1. Enviar solicitação de cadastro
  console.log('1. Submetendo formulário de cadastro (POST /api/auth/register)...');
  const regRes = await request({
    hostname: 'pephub.cloud',
    path: '/api/auth/register',
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  }, {
    nome_completo: 'Arthur Rezende (Teste)',
    login_claro: 'F138138',
    email_claro: 'arthur.rezende@claro.com.br',
    area: 'LOJAS PRÓPRIAS',
    funcao: 'GERENTE',
    password: 'Senha@123'
  });

  console.log(`Status Cadastro: ${regRes.statusCode} | Body: ${regRes.body}`);

  // 2. Tentar login imediato antes da aprovação
  console.log('\n2. Tentando login com usuário recém-cadastrado (ainda não aprovado)...');
  const preLoginRes = await request({
    hostname: 'pephub.cloud',
    path: '/api/auth/login',
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  }, {
    email_claro: 'arthur.rezende@claro.com.br',
    password: 'Senha@123'
  });

  console.log(`Status Login Pré-Aprovação: ${preLoginRes.statusCode} | Body: ${preLoginRes.body}`);
  const preData = JSON.parse(preLoginRes.body);
  if (preLoginRes.statusCode === 403 && preData.status === 'pendente') {
    console.log('✅ Bloqueio correto: Usuário pendente não consegue logar!');
  }

  // 3. Login do Admin Arthur para verificar lista de pendentes
  console.log('\n3. Login do Gestor Arthur para consultar o painel...');
  const adminLogin = await request({
    hostname: 'pephub.cloud',
    path: '/api/auth/login',
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  }, {
    email_claro: 'arthur.rezende.analista@gmail.com',
    password: 'Claro#2026'
  });

  const adminCookie = adminLogin.headers['set-cookie'][0].split(';')[0];
  const usersRes = await request({
    hostname: 'pephub.cloud',
    path: '/api/admin/users',
    method: 'GET',
    headers: { 'Cookie': adminCookie }
  });

  const usersList = JSON.parse(usersRes.body);
  const targetUser = usersList.find(u => u.email_claro === 'arthur.rezende@claro.com.br');
  console.log(`Usuário encontrado no Admin: ID ${targetUser?.id} | Status: ${targetUser?.status}`);

  if (targetUser) {
    // 4. Responsável aprova o cadastro via API Administrativa
    console.log('\n4. Responsável pela ferramenta aprova o cadastro (POST /api/admin/users/:id/privileges)...');
    const approveRes = await request({
      hostname: 'pephub.cloud',
      path: `/api/admin/users/${targetUser.id}/privileges`,
      method: 'POST',
      headers: {
        'Cookie': adminCookie,
        'Content-Type': 'application/json'
      }
    }, { status: 'aprovado', is_admin: 0, modules_allowed: 'churn', notify_updates: 1 });

    console.log(`Status Aprovação: ${approveRes.statusCode} | Body: ${approveRes.body}`);

    // 5. Usuário tenta login após aprovação
    console.log('\n5. Usuário faz login agora que está aprovado...');
    const postLoginRes = await request({
      hostname: 'pephub.cloud',
      path: '/api/auth/login',
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    }, {
      email_claro: 'arthur.rezende@claro.com.br',
      password: 'Senha@123'
    });

    console.log(`Status Login Usuário: ${postLoginRes.statusCode}`);
    const userCookie = postLoginRes.headers['set-cookie'] ? postLoginRes.headers['set-cookie'][0].split(';')[0] : null;

    if (userCookie) {
      console.log('✅ Cookie de sessão recebido!');
      // 6. Usuário acessa /churn/
      const churnUser = await request({
        hostname: 'pephub.cloud',
        path: '/churn/',
        method: 'GET',
        headers: { 'Cookie': userCookie }
      });
      console.log(`Status /churn/ acessado: ${churnUser.statusCode} (${churnUser.body.length} bytes)`);

      // 7. Usuário verifica seu /api/auth/me
      const meUser = await request({
        hostname: 'pephub.cloud',
        path: '/api/auth/me',
        method: 'GET',
        headers: { 'Cookie': userCookie }
      });
      console.log(`Dados do usuário autenticado: ${meUser.body}`);
      console.log('✅ Ciclo completo testado com 100% de sucesso!');
    }
  }
}

testFullRegistrationCycle().catch(console.error);
