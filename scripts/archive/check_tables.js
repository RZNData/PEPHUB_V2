const fs = require('fs');
const html = fs.readFileSync('Painel_FPD_Regional_Norte.html', 'utf8');
const tables = html.match(/<table[\s\S]*?<\/table>/gi) || [];
console.log('Total de tabelas estáticas no HTML:', tables.length);
tables.forEach((t, i) => {
  const idMatch = t.match(/id=['"](.*?)['"]/);
  const id = idMatch ? idMatch[1] : 'sem-id';
  const ths = (t.match(/<th[\s\S]*?<\/th>/gi) || []).map(h => h.replace(/<[^>]+>/g, '').trim());
  console.log(`Tabela ${i} (id=${id}):`, ths);
});

// Procurar também tabelas populadas via JavaScript (ex: innerHTML = '<thead>...')
console.log('\n--- Buscando tabelas geradas dinamicamente via JS ---');
const theads = html.match(/<thead>[\s\S]*?<\/thead>/gi) || [];
theads.forEach((th, i) => {
  const headers = (th.match(/<th[\s\S]*?<\/th>/gi) || []).map(h => h.replace(/<[^>]+>/g, '').trim());
  console.log(`Thead JS ${i}:`, headers);
});
