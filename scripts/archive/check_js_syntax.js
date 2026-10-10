const fs = require('fs');
const html = fs.readFileSync('Painel_FPD_Regional_Norte.html', 'utf8');
const sIdx = html.indexOf('<script>');
const eIdx = html.lastIndexOf('</script>');
const jsCode = html.substring(sIdx + 8, eIdx);

let stack = [];
let inSingle = false, inDouble = false, inBacktick = false, inLineComment = false, inBlockComment = false;
let escape = false;

for (let i = 0; i < jsCode.length; i++) {
    const c = jsCode[i];
    const prev = i > 0 ? jsCode[i-1] : '';
    const next = i + 1 < jsCode.length ? jsCode[i+1] : '';

    if (inLineComment) {
        if (c === '\n') inLineComment = false;
        continue;
    }
    if (inBlockComment) {
        if (c === '*' && next === '/') { inBlockComment = false; i++; }
        continue;
    }
    if (inSingle) {
        if (c === '\\' && !escape) { escape = true; continue; }
        if (c === '\'' && !escape) inSingle = false;
        escape = false;
        continue;
    }
    if (inDouble) {
        if (c === '\\' && !escape) { escape = true; continue; }
        if (c === '"' && !escape) inDouble = false;
        escape = false;
        continue;
    }
    if (inBacktick) {
        if (c === '\\' && !escape) { escape = true; continue; }
        if (c === '`' && !escape) inBacktick = false;
        escape = false;
        continue;
    }

    if (c === '/' && next === '/') { inLineComment = true; i++; continue; }
    if (c === '/' && next === '*') { inBlockComment = true; i++; continue; }
    if (c === '\'') { inSingle = true; continue; }
    if (c === '"') { inDouble = true; continue; }
    if (c === '`') { inBacktick = true; continue; }

    if (c === '{' || c === '(' || c === '[') {
        const line = jsCode.substring(0, i).split('\n').length;
        stack.push({ char: c, pos: i, line: line });
    } else if (c === '}' || c === ')' || c === ']') {
        const line = jsCode.substring(0, i).split('\n').length;
        if (stack.length === 0) {
            console.log('Unmatched closing ' + c + ' at line ' + line);
        } else {
            const top = stack.pop();
            const matching = { '}': '{', ')': '(', ']': '[' };
            if (top.char !== matching[c]) {
                console.log('Mismatched ' + top.char + ' (line ' + top.line + ') with ' + c + ' at line ' + line);
            }
        }
    }
}

console.log('State at end: inSingle=' + inSingle + ', inDouble=' + inDouble + ', inBacktick=' + inBacktick + ', inBlockComment=' + inBlockComment);
console.log('Unclosed items in stack:', stack.length);
stack.forEach(s => console.log('  Unclosed ' + s.char + ' opened at line ' + s.line + ' snippet: ' + jsCode.substring(s.pos, s.pos + 50).replace(/\n/g, ' ')));
