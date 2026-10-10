const fs = require('fs');
const html = fs.readFileSync('Painel_Churn_Safra 28.html', 'utf8');

const titles = [
  'Churn safra por safra',
  'Curva de maturação',
  'Mapa de concentração',
  'Cidades — visão geográfica IBGE',
  'Nunca pagou × churn',
  'Motivo da desconexão',
  'Matriz de safra — responsabilidade do parceiro',
  'Esteira de instalações × desconexões',
  'Ranking por dimensão'
];

titles.forEach(t => {
  const idx = html.indexOf(t);
  if (idx !== -1) {
    const pStart = html.lastIndexOf('<div class="panel"', idx);
    console.log(`\n=== PANEL: ${t} === (pStart=${pStart})`);
    console.log(html.substring(pStart, pStart + 350));
  } else {
    console.log(`\n=== PANEL NOT FOUND: ${t} ===`);
  }
});
