const fs = require('fs');
const path = require('path');

const filePath = path.join(__dirname, '..', 'public', 'churn', 'index.html');
let content = fs.readFileSync(filePath, 'utf8');

const regex = /(<h1><b>Churn Safra<\/b>\s*<span>Regional Norte<\/span><\/h1>)[\s\S]*?(<a\s+href="\/churn\/download"[^>]*>[\s\S]*?Exportar para E-mail \(\.html\)[\s\S]*?<\/a>)/i;

if (regex.test(content)) {
  content = content.replace(regex, `$1
    <div style="margin-left:auto;display:flex;align-items:center;gap:10px;flex-wrap:wrap">
      $2
      <div id="churnUserWidget" style="display:flex;align-items:center;gap:8px"></div>
    </div>`);
  console.log('Header successfully updated with regex in public/churn/index.html');
} else {
  console.log('Regex still not matched, checking snippet...');
  const idx = content.indexOf('Churn Safra');
  console.log('Snippet around Churn Safra:', JSON.stringify(content.substring(idx - 20, idx + 250)));
}

fs.writeFileSync(filePath, content, 'utf8');
console.log('File successfully updated!');
