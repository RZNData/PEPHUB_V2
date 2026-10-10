const fs = require('fs');

const html = fs.readFileSync('public_staging/aprovacao-credito/index.html', 'utf-8');

// Simple DOM mock for headless Node execution
class ElementMock {
  constructor(tag, id = '') {
    this.tagName = (tag || 'div').toUpperCase();
    this.id = id;
    this.className = '';
    this.classList = {
      classes: new Set(),
      add: (c) => this.classList.classes.add(c),
      remove: (c) => this.classList.classes.delete(c),
      toggle: (c, force) => {
        if (force === undefined) {
          if (this.classList.classes.has(c)) this.classList.classes.delete(c);
          else this.classList.classes.add(c);
        } else if (force) {
          this.classList.classes.add(c);
        } else {
          this.classList.classes.delete(c);
        }
      },
      contains: (c) => this.classList.classes.has(c)
    };
    this.style = {};
    this.dataset = {};
    this.childNodes = [{ nodeValue: '' }];
    this.textContent = '';
    this.innerHTML = '';
  }
  addEventListener() {}
  removeEventListener() {}
  focus() {}
  querySelector() { return new ElementMock('div'); }
  querySelectorAll() { return [new ElementMock('div')]; }
  closest() { return this; }
  getBoundingClientRect() { return { left: 0, top: 0, bottom: 0, right: 0, width: 100, height: 100 }; }
  appendChild(c) { return c; }
  remove() {}
}

const elementsById = {
  ttl: new ElementMock('h3', 'ttl'),
  tsub: new ElementMock('small', 'tsub'),
  viewNote: new ElementMock('span', 'viewNote'),
  modeToggle: new ElementMock('div', 'modeToggle'),
  content: new ElementMock('div', 'content'),
  nav: new ElementMock('nav', 'nav'),
  btnDrawer: new ElementMock('button', 'btnDrawer'),
  drawerIco: new ElementMock('span', 'drawerIco'),
  userWidget: new ElementMock('div', 'userWidget'),
  helpModal: new ElementMock('div', 'helpModal'),
  helpTitle: new ElementMock('h3', 'helpTitle'),
  helpBody: new ElementMock('div', 'helpBody')
};

global.window = {
  scrollTo: () => {},
  addEventListener: () => {},
  removeEventListener: () => {},
  location: { href: '' }
};
global.document = {
  getElementById: (id) => elementsById[id] || new ElementMock('div', id),
  querySelector: (sel) => new ElementMock('div'),
  querySelectorAll: (sel) => [new ElementMock('div'), new ElementMock('div')],
  createElement: (tag) => new ElementMock(tag),
  body: new ElementMock('body'),
  addEventListener: () => {}
};
global.fetch = () => Promise.resolve({ ok: false });
global.URL = { createObjectURL: () => 'blob:mock' };
global.Blob = class {};
global.Image = class { constructor() { setTimeout(() => this.onload && this.onload(), 10); } };

// Extract and execute scripts
const scriptRegex = /<script>([\s\S]*?)<\/script>/gi;
let match;
let scriptIndex = 0;
const vm = require('vm');
while ((match = scriptRegex.exec(html)) !== null) {
  const code = match[1];
  console.log(`Executing script ${scriptIndex} (length: ${code.length})...`);
  try {
    vm.runInThisContext(code);
    console.log(`Script ${scriptIndex} executed successfully!`);
  } catch (err) {
    console.error(`Error in script ${scriptIndex}:`, err);
    process.exit(1);
  }
  scriptIndex++;
}

console.log("\n=== Testing all views ===");
const views = ['v1', 'v2', 'v3', 'v4', 'cart', 'v5', 'sum', 'imp'];
for (const v of views) {
  try {
    go(v);
    console.log(`View '${v}' rendered successfully! HTML length: ${elementsById.content.innerHTML.length}`);
  } catch (err) {
    console.error(`Error rendering view '${v}':`, err);
    process.exit(1);
  }
}

console.log("\nALL 8 VIEWS RENDERED PERFECTLY HEADLESSLY WITH ZERO ERRORS!");
