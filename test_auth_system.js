const https = require('https');

function request(options, postData = null) {
  return new Promise((resolve, reject) => {
    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve({
        statusCode: res.statusCode,
        headers: res.headers,
        body: data
      }));
    });
    req.on('error', reject);
    if (postData) req.write(postData);
    req.end();
  });
}

async function testAll() {
  console.log('--- 1. TESTANDO PÁGINAS PÚBLICAS ---');
  const loginPage = await request({ hostname: 'pephub.cloud', path: '/login/' });
  console.log('/login/:', loginPage.statusCode);

  const registerPage = await request({ hostname: 'pephub.cloud', path: '/register/' });
  console.log('/register/:', registerPage.statusCode);

  const forgotPage = await request({ hostname: 'pephub.cloud', path: '/forgot-password/' });
  console.log('/forgot-password/:', forgotPage.statusCode);

  console.log('--- 2. TESTANDO PROTEÇÃO DO CHURN (SEM SESSÃO) ---');
  const churnUnauth = await request({ hostname: 'pephub.cloud', path: '/churn/' });
  console.log('/churn/ sem sessão:', churnUnauth.statusCode, '-> Redirect:', churnUnauth.headers.location);

  console.log('--- 3. TESTANDO LOGIN DO ADMIN ARTHUR ---');
  const loginPayload = JSON.stringify({
    email_claro: 'arthur.rezende.analista@gmail.com',
    password: 'Claro#2026'
  });
  const loginRes = await request({
    hostname: 'pephub.cloud',
    path: '/api/auth/login',
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Content-Length': Buffer.byteLength(loginPayload)
    }
  }, loginPayload);
  console.log('Login Arthur:', loginRes.statusCode, loginRes.body);
  const cookie = loginRes.headers['set-cookie'];
  console.log('Cookie recebido:', cookie ? cookie[0].slice(0, 45) + '...' : 'Nenhum');

  if (cookie) {
    console.log('--- 4. TESTANDO ACESSO AO CHURN COM COOKIE VÁLIDO ---');
    const churnAuth = await request({
      hostname: 'pephub.cloud',
      path: '/churn/',
      headers: { 'Cookie': cookie[0] }
    });
    console.log('/churn/ autenticado:', churnAuth.statusCode, 'Tamanho:', churnAuth.body.length, 'bytes');

    console.log('--- 5. TESTANDO /api/auth/me COM COOKIE ---');
    const meRes = await request({
      hostname: 'pephub.cloud',
      path: '/api/auth/me',
      headers: { 'Cookie': cookie[0] }
    });
    console.log('/api/auth/me:', meRes.statusCode, meRes.body);

    console.log('--- 6. TESTANDO ACESSO AO ADMIN COM COOKIE ---');
    const adminRes = await request({
      hostname: 'pephub.cloud',
      path: '/admin/',
      headers: { 'Cookie': cookie[0] }
    });
    console.log('/admin/ autenticado:', adminRes.statusCode, 'Tamanho:', adminRes.body.length, 'bytes');
  }
}

testAll().catch(console.error);
