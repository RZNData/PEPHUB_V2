const fs = require('fs');
const html = fs.readFileSync('Painel_Churn_Safra 28.html', 'utf8');

const panels = [];
const pRegex = /<div class="panel">([\s\S]*?)<\/div>\s*<\/div>/g;
let m;
while ((m = pRegex.exec(html)) !== null) {
  const h2Match = m[1].match(/<h2>([\s\S]*?)<\/h2>/);
  const h2 = h2Match ? h2Match[1].replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim() : 'sem-h2';
  panels.push({ h2, index: m.index, length: m[0].length });
}

console.log('Painéis encontrados em Painel_Churn_Safra 28.html:', panels.length);
panels.forEach((p, i) => console.log(`${i}: [${p.h2}] at pos ${p.index}`));
