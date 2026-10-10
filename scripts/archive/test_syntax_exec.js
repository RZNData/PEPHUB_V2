const fs = require('fs');
const zlib = require('zlib');
const vm = require('vm');

const html = fs.readFileSync('Painel_FPD_Regional_Norte.html', 'utf8');

// Extrair JS
const sIdx = html.indexOf('<script>');
const eIdx = html.lastIndexOf('</script>');
let jsCode = html.substring(sIdx + 8, eIdx);

const pStart = html.indexOf('const PAYLOAD = ') + 'const PAYLOAD = '.length;
const pEnd = html.indexOf('/* ============ decodificação ============ */');
const payloadJson = html.substring(pStart, pEnd).trim().replace(/;$/, '');
const PAYLOAD = JSON.parse(payloadJson);

const C = {};
for (const k in PAYLOAD.cols) {
  const c = PAYLOAD.cols[k];
  const buf = Buffer.from(c.b, 'base64');
  const ab = zlib.inflateSync(buf);
  C[k] = c.t === 'u8' ? new Uint8Array(ab.buffer, ab.byteOffset, ab.byteLength) :
        (c.t === 'u32' ? new Uint32Array(ab.buffer, ab.byteOffset, ab.byteLength / 4) :
         new Uint16Array(ab.buffer, ab.byteOffset, ab.byteLength / 2));
}

console.log('Payload carregado. Configurando sandbox DOM...');

const domElements = {};
function getEl(id) {
  if (!domElements[id]) {
    domElements[id] = {
      id,
      value: '',
      innerHTML: '',
      textContent: '',
      style: {},
      dataset: {},
      options: [],
      classList: {
        add: () => {},
        remove: () => {},
        toggle: () => {},
        contains: () => false
      },
      appendChild: (c) => c,
      querySelector: (sel) => getEl('mock_' + sel),
      querySelectorAll: (sel) => [],
      addEventListener: () => {},
      getContext: () => ({
        fillRect: () => {},
        clearRect: () => {},
        beginPath: () => {},
        arc: () => {},
        fill: () => {},
        stroke: () => {}
      })
    };
  }
  return domElements[id];
}

const mockDoc = {
  getElementById: (id) => getEl(id),
  querySelector: (s) => getEl('mock_' + s),
  querySelectorAll: (s) => [],
  createElement: (tag) => getEl('mock_tag_' + tag),
  createElementNS: (ns, tag) => getEl('mock_svg_' + tag),
  addEventListener: () => {}
};

// Mock DecompressionStream e Response/Blob para o boot() rodar
class MockDecompressionStream {
  constructor(format) {}
}

const sandbox = {
  document: mockDoc,
  window: {
    addEventListener: () => {},
    innerWidth: 1920,
    innerHeight: 945,
    devicePixelRatio: 1
  },
  console: console,
  setTimeout: (fn) => setTimeout(fn, 1),
  clearTimeout: () => {},
  Math: Math,
  Date: Date,
  Set: Set,
  Map: Map,
  Int32Array: Int32Array,
  Uint8Array: Uint8Array,
  Uint16Array: Uint16Array,
  Uint32Array: Uint32Array,
  Float32Array: Float32Array,
  Array: Array,
  Object: Object,
  String: String,
  Number: Number,
  RegExp: RegExp,
  JSON: JSON,
  atob: (s) => Buffer.from(s, 'base64').toString('binary'),
  btoa: (s) => Buffer.from(s, 'binary').toString('base64'),
  DecompressionStream: MockDecompressionStream,
  Blob: class MockBlob {
    constructor(parts) { this.parts = parts; }
    stream() {
      return {
        pipeThrough: () => ({})
      };
    }
  },
  Response: class MockResponse {
    constructor(stream) {}
    async arrayBuffer() {
      // Como o boot chama inflate(B64(c.b)), vamos retornar o arraybuffer já descomprimido
      return new ArrayBuffer(0);
    }
  }
};

// Vamos verificar se o arquivo tem erros de sintaxe ou de execução
try {
  vm.createContext(sandbox);
  // Testar sintaxe primeiro
  new vm.Script(jsCode);
  console.log("Sintaxe JavaScript OK!");
} catch (err) {
  console.error("ERRO DE SINTAXE JS:", err);
}
