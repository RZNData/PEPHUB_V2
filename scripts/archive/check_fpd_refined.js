const fs = require('fs');
const c = fs.readFileSync('Painel_FPD_Regional_Norte.html', 'utf8');

console.log('1. Tamanho do HTML:', c.length, 'bytes');

const fpdKpiTerms = [
  'Taxa FPD 60 (Oficial)',
  'Taxa FPD 30 (Pré-FPD)',
  'Taxa FPD 90 (Pré-Churn)',
  'Variação MoM (FPD 60)',
  'Benchmark YTD (Acumulado)',
  'Regularização Pré-FPD',
  'Adimplência 1ª Fatura',
  'Nunca Pagou (FPD 30 & 60)'
];

console.log('\n2. Verificação dos Novos Cards FPD:');
fpdKpiTerms.forEach(t => {
  const found = c.includes(t);
  console.log(` - ${t.padEnd(30)}: ${found ? 'OK' : 'FALTOU'}`);
});

console.log('\n3. Verificação de Safra Foco e Métricas:');
console.log(' - Safra Foco padrão mai/26:', c.includes("let safraFoco='mai/26';"));
console.log(' - Seletor Mapa padrão FPD 60:', c.includes('value="c60" selected'));
console.log(' - Tabela de Ranking FPD 60:', c.includes('% FPD 60 (Oficial)'));
console.log(' - Tabela de Ranking FPD 30:', c.includes('% FPD 30 (Pré-FPD)'));
console.log(' - Tabela de Ranking FPD 90:', c.includes('% FPD 90 (Pré-Churn)'));
console.log('\nVALIDAÇÃO CONCLUÍDA!');
