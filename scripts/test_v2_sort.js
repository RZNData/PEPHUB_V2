const fs = require('fs');
const vm = require('vm');
const html = fs.readFileSync('public_staging/aprovacao-credito/index.html', 'utf-8');

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

const scriptRegex = /<script>([\s\S]*?)<\/script>/gi;
let match;
while ((match = scriptRegex.exec(html)) !== null) {
  vm.runInThisContext(match[1]);
}

S.view = 'v2';
const st = tget('t_v2');

function getGroups(htmlStr) {
  const grps = [];
  const regex = /<tr class="rowgrp[^"]*" data-lvl="g"[^>]*><td[^>]*><b>(.*?)<\/b><\/td>/g;
  let m;
  while ((m = regex.exec(htmlStr)) !== null) {
    grps.push(m[1].trim());
  }
  return grps;
}

function getChannels(htmlStr) {
  const chs = [];
  const regex = /<tr class="rowchild rowgrp rowsub[^"]*"[^>]*><td[^>]*><b>(.*?)<\/b><\/td>/g;
  let m;
  while ((m = regex.exec(htmlStr)) !== null) {
    chs.push(m[1].trim());
  }
  return chs;
}

// 1. Default (no sortCol) -> should start with highest volume descending
st.sortCol = null;
const defHtml = v2View();
console.log('1. Default Groups:', getGroups(defHtml));
console.log('1. Default Top 4 Channels:', getChannels(defHtml).slice(0, 4));

// 2. Sort by 'cons' DESC (maior pro menor)
st.sortCol = 'cons';
st.sortDir = -1;
const descHtml = v2View();
console.log('\n2. Sort Consultas DESC (maior pro menor):');
console.log('   Groups:', getGroups(descHtml));
console.log('   Top 4 Channels:', getChannels(descHtml).slice(0, 4));

// 3. Sort by 'cons' ASC (menor pro maior)
st.sortCol = 'cons';
st.sortDir = 1;
const ascHtml = v2View();
console.log('\n3. Sort Consultas ASC (menor pro maior):');
console.log('   Groups:', getGroups(ascHtml));
console.log('   First 4 Channels:', getChannels(ascHtml).slice(0, 4));

// Verify that reverse sorting reversed the order!
const descChs = getChannels(descHtml);
const ascChs = getChannels(ascHtml);
console.log('\nFirst channel in DESC:', descChs[0]);
console.log('First channel in ASC:', ascChs[0]);
console.log('Did order flip between DESC and ASC?', descChs[0] !== ascChs[0]);
