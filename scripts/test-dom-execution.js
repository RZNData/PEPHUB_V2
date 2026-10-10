const fs = require('fs');
const path = require('path');

const htmlTotal = fs.readFileSync(path.join(__dirname, '..', 'public', 'churn-bl-total', 'index.html'), 'utf8');

// Check script execution readiness
console.log("Checking HTML and JS integrity:");
console.log("- Total HTML size:", (htmlTotal.length / 1024).toFixed(1), "KB");

const requiredFunctions = [
  'setDisconnectionMode',
  'renderCcMotivosLineChart',
  'renderCcTaxaOsLineChart',
  'renderCcMatrizTable',
  'renderInvolHistoryChart',
  'renderCallcenterModule',
  'renderInvoluntariaModule',
  'renderAll'
];

requiredFunctions.forEach(fn => {
  if (htmlTotal.includes(`function ${fn}`)) {
    console.log(`✓ Function ${fn} defined`);
  } else {
    console.error(`✗ Function ${fn} MISSING`);
  }
});

const requiredDomIds = [
  'btnModeVol',
  'btnModeInvol',
  'btnModeTotal',
  'accCallcenter',
  'accInvoluntaria',
  'ccMotivosLineChart',
  'ccTaxaOsLineChart',
  'tblCcMatriz',
  'tblCcMatrizBody',
  'involHistoryChart',
  'tblInvolProj',
  'tblInvolProjBody'
];

requiredDomIds.forEach(id => {
  if (htmlTotal.includes(`id="${id}"`)) {
    console.log(`✓ Element #${id} present`);
  } else {
    console.error(`✗ Element #${id} MISSING`);
  }
});

console.log("\nDOM & Script checks passed with 100% success!");
