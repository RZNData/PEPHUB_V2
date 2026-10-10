const fs = require('fs');
const path = require('path');

const filePath = path.join(__dirname, '..', 'public', 'churn', 'index.html');
let content = fs.readFileSync(filePath, 'utf8');

// Remover emoji 👤
content = content.replace(/👤\s*/g, '');

fs.writeFileSync(filePath, content, 'utf8');
console.log('public/churn/index.html cleaned of emojis!');
