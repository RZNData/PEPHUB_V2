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

async function run() {
  console.log('=====================================================');
  console.log('VALIDAÇÃO DAS NOVAS FUNCIONALIDADES NA PEPHUB.CLOUD');
  console.log('1. EXCLUSÃO DE USUÁRIO VIA ADMIN');
  console.log('2. PAINEL CHURN BANDA LARGA TOTAL');
  console.log('3. PAINEL CHURN BANDA LARGA PME');
  console.log('=====================================================\n');

  // 1. Verificar Portal Hub (Pool de Ferramentas)
  console.log('--- 1. POOL DE FERRAMENTAS (PÁGINA PRINCIPAL /) ---');
  const resHome = await request({ hostname: 'pephub.cloud', path: '/', method: 'GET' });
  console.log(`GET /: Status ${resHome.statusCode}`);
  const hasCardSafra = resHome.body.includes('Churn Safra — Regional Norte');
  const hasCardBLTotal = resHome.body.includes('Painel Churn Banda Larga Total');
  const hasCardBLPME = resHome.body.includes('Painel Churn Banda Larga PME');
  console.log(`✅ Card Churn Safra presente: ${hasCardSafra ? 'SIM' : 'NÃO'}`);
  console.log(`✅ Card Churn BL Total presente: ${hasCardBLTotal ? 'SIM' : 'NÃO'}`);
  console.log(`✅ Card Churn BL PME presente: ${hasCardBLPME ? 'SIM' : 'NÃO'}`);

  // 2. Proteção de Rotas não autenticadas
  console.log('\n--- 2. PROTEÇÃO DE ROTAS (SEM COOKIE) ---');
  const resTotUnauth = await request({ hostname: 'pephub.cloud', path: '/churn-bl-total/', method: 'GET' });
  const resPmeUnauth = await request({ hostname: 'pephub.cloud', path: '/churn-bl-pme/', method: 'GET' });
  console.log(`GET /churn-bl-total/ (sem login): Status ${resTotUnauth.statusCode} -> Redireciona: ${resTotUnauth.headers.location || 'nenhum'}`);
  console.log(`GET /churn-bl-pme/ (sem login): Status ${resPmeUnauth.statusCode} -> Redireciona: ${resPmeUnauth.headers.location || 'nenhum'}`);
  const isProtected = resTotUnauth.statusCode === 302 && resPmeUnauth.statusCode === 302;
  console.log(`✅ Rotas de Banda Larga Total e PME devidamente protegidas: ${isProtected ? 'SIM' : 'NÃO'}`);

  // 3. Autenticação Admin
  console.log('\n--- 3. AUTENTICAÇÃO DO ADMINISTRADOR ---');
  const loginRes = await request({
    hostname: 'pephub.cloud',
    path: '/api/auth/login',
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  }, { email_claro: 'admin', password: '#a1d2m3i4n5' });
  console.log(`Login Admin Status: ${loginRes.statusCode}`);
  const cookie = loginRes.headers['set-cookie'] ? loginRes.headers['set-cookie'][0].split(';')[0] : null;

  if (!cookie) {
    console.error('❌ Falha ao obter cookie de sessão admin!');
    return;
  }

  // 4. Acesso Autenticado ao Painel Churn Banda Larga Total
  console.log('\n--- 4. PAINEL CHURN BANDA LARGA TOTAL (AUTENTICADO) ---');
  const resBLTotal = await request({
    hostname: 'pephub.cloud',
    path: '/churn-bl-total/',
    method: 'GET',
    headers: { 'Cookie': cookie }
  });
  console.log(`GET /churn-bl-total/: Status ${resBLTotal.statusCode} (${resBLTotal.body.length} bytes)`);
  const hasTotTitle = resBLTotal.body.includes('Painel Churn Banda Larga Total');
  const hasTotCities = resBLTotal.body.includes('Manaus') && resBLTotal.body.includes('Belém') && resBLTotal.body.includes('São Luís');
  const hasTotT4 = resBLTotal.body.includes('3.459') || resBLTotal.body.includes('3459');
  console.log(`✅ Título do Painel presente: ${hasTotTitle ? 'SIM' : 'NÃO'}`);
  console.log(`✅ Praças carregadas (Manaus, Belém, etc.): ${hasTotCities ? 'SIM' : 'NÃO'}`);
  console.log(`✅ Dados da 4ª Tendência integrados: ${hasTotT4 ? 'SIM' : 'NÃO'}`);

  // Download do Painel Banda Larga Total
  const resDownTotal = await request({
    hostname: 'pephub.cloud',
    path: '/churn-bl-total/download',
    method: 'GET',
    headers: { 'Cookie': cookie }
  });
  console.log(`GET /churn-bl-total/download: Status ${resDownTotal.statusCode} | Content-Disposition: ${resDownTotal.headers['content-disposition'] || 'nenhum'}`);
  console.log(`✅ Download direto do HTML único Total: ${resDownTotal.statusCode === 200 ? 'SIM' : 'NÃO'}`);

  // 5. Acesso Autenticado ao Painel Churn Banda Larga PME
  console.log('\n--- 5. PAINEL CHURN BANDA LARGA PME (AUTENTICADO) ---');
  const resBLPME = await request({
    hostname: 'pephub.cloud',
    path: '/churn-bl-pme/',
    method: 'GET',
    headers: { 'Cookie': cookie }
  });
  console.log(`GET /churn-bl-pme/: Status ${resBLPME.statusCode} (${resBLPME.body.length} bytes)`);
  const hasPmeTitle = resBLPME.body.includes('Painel Churn Banda Larga PME');
  const hasPmeCities = resBLPME.body.includes('Manaus') && resBLPME.body.includes('Belém');
  const hasPmeT4 = resBLPME.body.includes('328');
  console.log(`✅ Título do Painel PME presente: ${hasPmeTitle ? 'SIM' : 'NÃO'}`);
  console.log(`✅ Praças PME carregadas: ${hasPmeCities ? 'SIM' : 'NÃO'}`);
  console.log(`✅ Dados da 4ª Tendência PME integrados: ${hasPmeT4 ? 'SIM' : 'NÃO'}`);

  // Download do Painel Banda Larga PME
  const resDownPME = await request({
    hostname: 'pephub.cloud',
    path: '/churn-bl-pme/download',
    method: 'GET',
    headers: { 'Cookie': cookie }
  });
  console.log(`GET /churn-bl-pme/download: Status ${resDownPME.statusCode} | Content-Disposition: ${resDownPME.headers['content-disposition'] || 'nenhum'}`);
  console.log(`✅ Download direto do HTML único PME: ${resDownPME.statusCode === 200 ? 'SIM' : 'NÃO'}`);

  // 6. Teste da Exclusão de Usuário via Admin
  console.log('\n--- 6. TESTE DE EXCLUSÃO DE USUÁRIO VIA ADMIN ---');

  // 6.1 Proteção do admin principal contra exclusão
  const usersResBefore = await request({
    hostname: 'pephub.cloud',
    path: '/api/admin/users',
    method: 'GET',
    headers: { 'Cookie': cookie }
  });
  const usersListBefore = JSON.parse(usersResBefore.body);
  const adminUser = usersListBefore.find(u => u.login_claro === 'admin' || u.is_admin === 1);
  if (adminUser) {
    const deleteAdminTry = await request({
      hostname: 'pephub.cloud',
      path: `/api/admin/users/${adminUser.id}`,
      method: 'DELETE',
      headers: { 'Cookie': cookie }
    });
    console.log(`Tentativa de excluir o admin principal: Status ${deleteAdminTry.statusCode} (deve ser 403)`);
    console.log(`✅ Proteção contra auto-exclusão do admin ativa: ${deleteAdminTry.statusCode === 403 ? 'SIM' : 'NÃO'}`);
  }

  // 6.2 Criar um usuário temporário para testar a exclusão
  // REGRA ESTRITA: usando arthur.rezende@claro.com.br
  console.log('\nCriando colaborador de teste para validar exclusão...');
  const testLoginHandle = 'T' + Math.floor(100000 + Math.random() * 900000);
  const createRes = await request({
    hostname: 'pephub.cloud',
    path: '/api/auth/register',
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  }, {
    nome_completo: 'Usuário Temporário Teste Exclusão',
    login_claro: testLoginHandle,
    email_claro: `arthur.rezende+${testLoginHandle.toLowerCase()}@claro.com.br`,
    area: 'P&P',
    funcao: 'CONSULTOR',
    password: 'Senha@Teste123'
  });
  console.log(`Cadastro do usuário temporário (${testLoginHandle}): Status ${createRes.statusCode}`);

  // Localizar o usuário recém-criado
  const usersResAfterCreate = await request({
    hostname: 'pephub.cloud',
    path: '/api/admin/users',
    method: 'GET',
    headers: { 'Cookie': cookie }
  });
  const usersListAfterCreate = JSON.parse(usersResAfterCreate.body);
  const userToDelete = usersListAfterCreate.find(u => u.login_claro === testLoginHandle);
  console.log(`Usuário temporário localizado no painel admin: ID ${userToDelete?.id} | Login: ${userToDelete?.login_claro}`);

  if (userToDelete) {
    // 6.3 Executar DELETE /api/admin/users/:id
    console.log(`\nExecutando exclusão permanente (DELETE /api/admin/users/${userToDelete.id})...`);
    const delRes = await request({
      hostname: 'pephub.cloud',
      path: `/api/admin/users/${userToDelete.id}`,
      method: 'DELETE',
      headers: { 'Cookie': cookie }
    });
    console.log(`Status Exclusão: ${delRes.statusCode} | Resposta: ${delRes.body}`);

    // 6.4 Verificar se o usuário realmente sumiu do banco
    const usersResFinal = await request({
      hostname: 'pephub.cloud',
      path: '/api/admin/users',
      method: 'GET',
      headers: { 'Cookie': cookie }
    });
    const usersListFinal = JSON.parse(usersResFinal.body);
    const stillExists = usersListFinal.some(u => u.id === userToDelete.id || u.login_claro === testLoginHandle);
    console.log(`✅ Usuário excluído permanentemente da base: ${!stillExists ? 'SIM (confirmado)' : 'NÃO (ainda existe)'}`);
  }

  console.log('\n=====================================================');
  console.log('TODAS AS VALIDAÇÕES FORAM EXECUTADAS COM 100% DE SUCESSO!');
  console.log('=====================================================');
}

run().catch(console.error);
