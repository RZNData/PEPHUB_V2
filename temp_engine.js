
/* ============ STATE ============ */
let DD=DASH_DATA; // live data (replaceable via import)
try{const ls=localStorage.getItem('RNO_DASH');if(ls){DD=JSON.parse(ls);}}catch(e){}
function cidGroups(){return DD.cidades;}
function allCidades(){return [].concat(...Object.values(DD.cidades));}
const ALLPROD=['BANDA LARGA','CLARO BOX','TV TRADICIONAL'];
const PLAB={'BANDA LARGA':'Banda Larga','CLARO BOX':'Box','TV TRADICIONAL':'TV Tradicional'};
const S={view:'v1',mode:'pct',prod:new Set(ALLPROD),canais:new Set(DD.canais_norm),
  cidades:new Set(allCidades()),v4crit:'credito',pdvSearch:'',openDD:new Set(),v2search:'',v2sel:new Set(),v3weeks:null,insLabels:false,zoomChart:null,
  zoomMode:'lines',zoomTopN:5,v3mode:'tabela',sidebarCollapsed:true,
  execs:new Set(DD.carteira_meta.execs),gns:new Set(DD.carteira_meta.gns),gfils:new Set(DD.carteira_meta.gfils||[]),gers:new Set(DD.carteira_meta.gers),cartLevel:3,cartSearch:''};
let PRES=DD.canal_grupos['Canais Presenciais'], REM=DD.canal_grupos['Canais Remotos'];
let SAF=DD.safras;
const NC='Não carteirizado';
function refreshRefs(){PRES=DD.canal_grupos['Canais Presenciais'];REM=DD.canal_grupos['Canais Remotos'];SAF=DD.safras;
  S.prod=new Set(ALLPROD);S.canais=new Set(DD.canais_norm);S.cidades=new Set(allCidades());if(typeof invalidatePdvCache==='function')invalidatePdvCache();}
const fmtN=n=>Math.round(n||0).toLocaleString('pt-BR');
const fmtP=p=>isFinite(p)?(p*100).toFixed(1).replace('.',',')+'%':'–';
const fmtPP=p=>(p>=0?'+':'')+(p*100).toFixed(1).replace('.',',')+' p.p.';
const fmtD=n=>(n>=0?'+':'')+fmtN(n);
const fmtGrow=g=>isFinite(g)?(g>=0?'+':'')+(g*100).toFixed(1).replace('.',',')+'%':'–';
function outros(){return DD.canais_norm.filter(c=>!PRES.includes(c)&&!REM.includes(c));}
function canalGrupo(cn){return PRES.includes(cn)?'Canais Presenciais':REM.includes(cn)?'Canais Remotos':'Outros Canais';}
function segOf(cid){for(const[g,arr]of Object.entries(DD.cidades))if(arr.includes(cid))return g;return 'Sem Cabo';}

/* ===== SVG charts ===== */
function svgEl(w,h){return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${w} ${h}" width="100%" height="100%" preserveAspectRatio="xMidYMid meet" font-family="Segoe UI,Arial">`;}
function groupedBar(el,labels,series,opt){
  opt=opt||{};const W=560,H=300,pl=48,pr=14,pt=18,pb=46;const iw=W-pl-pr,ih=H-pt-pb;
  const max=opt.max||Math.ceil(Math.max(...series.flatMap(s=>s.data),1)/10)*10;
  let s=svgEl(W,H);
  for(let g=0;g<=5;g++){const y=pt+ih-ih*g/5;const v=(max*g/5);s+=`<line x1="${pl}" y1="${y}" x2="${W-pr}" y2="${y}" stroke="#EEF1F7"/><text x="${pl-6}" y="${y+3}" font-size="9" fill="#9AA6C2" text-anchor="end">${v.toFixed(0)}${opt.suffix||''}</text>`;}
  const gw=iw/labels.length,bw=Math.min(46,gw/(series.length+1));
  labels.forEach((lb,i)=>{const gx=pl+gw*i;
    series.forEach((se,j)=>{const v=se.data[i];const bh=ih*v/max;const x=gx+gw/2-(series.length*bw)/2+j*bw+2;const y=pt+ih-bh;
      s+=`<rect x="${x}" y="${y}" width="${bw-3}" height="${bh}" rx="3" fill="${se.color}"><title>${se.name}: ${v}${opt.suffix||''}</title></rect>`;
      s+=`<text x="${x+(bw-3)/2}" y="${y-4}" font-size="9" font-weight="700" fill="#444" text-anchor="middle">${v}${opt.suffix||''}</text>`;});
    s+=`<text x="${gx+gw/2}" y="${H-pb+16}" font-size="10" fill="#555" text-anchor="middle">${lb}</text>`;});
  s+='</svg>';
  let lg='<div class="legend-mini" style="text-align:center">'+series.map(se=>`<span style="display:inline-block;margin:0 8px"><span style="display:inline-block;width:10px;height:10px;border-radius:2px;background:${se.color};vertical-align:middle"></span> ${se.name}</span>`).join('')+'</div>';
  document.getElementById(el).innerHTML=s+lg;
}
function hBar(el,labels,data,colors,opt){
  opt=opt||{};const W=560,rowH=40,pt=10,pl=140,pr=54;const H=pt*2+labels.length*rowH;const iw=W-pl-pr;
  const max=opt.max||Math.max(...data,1)*1.1;let s=svgEl(W,H);
  labels.forEach((lb,i)=>{const y=pt+i*rowH+6;const bw=iw*data[i]/max;
    s+=`<text x="${pl-8}" y="${y+16}" font-size="10.5" fill="#444" text-anchor="end">${lb}</text>`;
    s+=`<rect x="${pl}" y="${y}" width="${iw}" height="22" rx="4" fill="#EEF1F7"/>`;
    s+=`<rect x="${pl}" y="${y}" width="${Math.max(0,bw)}" height="22" rx="4" fill="${colors[i]}"/>`;
    s+=`<text x="${pl+Math.max(0,bw)+6}" y="${y+16}" font-size="10.5" font-weight="700" fill="#333">${data[i].toFixed(1)}${opt.suffix||''}</text>`;});
  s+='</svg>';document.getElementById(el).innerHTML=s;
}
function donut(el,labels,data,colors,opt){
  opt=opt||{};const W=560,H=300,cx=155,cy=150,r=100,rin=60;const tot=data.reduce((a,b)=>a+b,0)||1;
  let s=svgEl(W,H);let ang=-Math.PI/2;
  data.forEach((v,i)=>{if(v<=0)return;const a2=ang+2*Math.PI*v/tot;const x1=cx+r*Math.cos(ang),y1=cy+r*Math.sin(ang),x2=cx+r*Math.cos(a2),y2=cy+r*Math.sin(a2);
    const xi1=cx+rin*Math.cos(a2),yi1=cy+rin*Math.sin(a2),xi2=cx+rin*Math.cos(ang),yi2=cy+rin*Math.sin(ang);
    const large=(a2-ang)>Math.PI?1:0;
    s+=`<path d="M${x1} ${y1} A${r} ${r} 0 ${large} 1 ${x2} ${y2} L${xi1} ${yi1} A${rin} ${rin} 0 ${large} 0 ${xi2} ${yi2} Z" fill="${colors[i]}"><title>${labels[i]}: ${Math.round(v)} (${(v/tot*100).toFixed(1)}%)</title></path>`;ang=a2;});
  s+=`<text x="${cx}" y="${cy-4}" font-size="12" fill="#6B7280" text-anchor="middle">Recusas</text><text x="${cx}" y="${cy+16}" font-size="17" font-weight="800" fill="#1F2937" text-anchor="middle">${fmtN(tot)}</text>`;
  labels.forEach((lb,i)=>{const y=60+i*30;s+=`<rect x="320" y="${y}" width="12" height="12" rx="2" fill="${colors[i]}"/><text x="340" y="${y+11}" font-size="12" fill="#444">${lb}</text><text x="${W-10}" y="${y+11}" font-size="12" font-weight="700" fill="#333" text-anchor="end">${opt.pct?(data[i]/tot*100).toFixed(1)+'%':fmtN(data[i])}</text>`;});
  s+='</svg>';document.getElementById(el).innerHTML=s;
}
function lineChart(el,labels,series,opt){
  opt=opt||{};const W=680,H=300,pl=44,pr=16,pt=18,pb=40;const iw=W-pl-pr,ih=H-pt-pb;
  const allv=series.flatMap(s=>s.data);const min=opt.min!=null?opt.min:Math.floor(Math.min(...allv)/5)*5;const max=opt.max!=null?opt.max:Math.ceil(Math.max(...allv)/5)*5;
  const X=i=>pl+iw*i/(labels.length-1||1);const Y=v=>pt+ih-ih*(v-min)/((max-min)||1);
  let s=svgEl(W,H);
  for(let g=0;g<=5;g++){const v=min+(max-min)*g/5;const y=Y(v);s+=`<line x1="${pl}" y1="${y}" x2="${W-pr}" y2="${y}" stroke="#EEF1F7"/><text x="${pl-6}" y="${y+3}" font-size="9" fill="#9AA6C2" text-anchor="end">${v.toFixed(0)}${opt.suffix||''}</text>`;}
  labels.forEach((lb,i)=>{s+=`<text x="${X(i)}" y="${H-pb+16}" font-size="8.5" fill="#777" text-anchor="middle">${lb}</text>`;});
  series.forEach((se,si)=>{let d='';se.data.forEach((v,i)=>{d+=(i?'L':'M')+X(i)+' '+Y(v)+' ';});
    s+=`<path d="${d}" fill="none" stroke="${se.color}" stroke-width="2.4" stroke-linejoin="round"/>`;
    se.data.forEach((v,i)=>{s+=`<circle cx="${X(i)}" cy="${Y(v)}" r="3" fill="#fff" stroke="${se.color}" stroke-width="2"><title>${se.name} ${labels[i]}: ${v}${opt.suffix||''}</title></circle>`;
      // data label on every point (offset above for first series, below for others to reduce overlap)
      const dy=si===0?-7:12;s+=`<text x="${X(i)}" y="${Y(v)+dy}" font-size="8" font-weight="700" fill="${se.color}" text-anchor="middle">${(+v).toFixed(1).replace('.',',')}${opt.suffix||''}</text>`;});});
  s+='</svg>';
  let lg='<div class="legend-mini" style="text-align:center">'+series.map(se=>`<span style="display:inline-block;margin:0 8px"><span style="display:inline-block;width:14px;height:3px;border-radius:2px;background:${se.color};vertical-align:middle"></span> ${se.name}</span>`).join('')+'</div>';
  document.getElementById(el).innerHTML=s+lg;
}
function stackedBar(el,labels,segs,opt){ // segs:[{name,color,data:[per label]}], values summed per label
  opt=opt||{};const W=680,H=320,pl=44,pr=16,pt=18,pb=56;const iw=W-pl-pr,ih=H-pt-pb;
  const totals=labels.map((_,i)=>segs.reduce((a,se)=>a+se.data[i],0));
  const max=opt.pct?100:Math.ceil(Math.max(...totals,1)/10)*10;
  let s=svgEl(W,H);
  for(let g=0;g<=5;g++){const v=max*g/5;const y=pt+ih-ih*g/5;s+=`<line x1="${pl}" y1="${y}" x2="${W-pr}" y2="${y}" stroke="#EEF1F7"/><text x="${pl-6}" y="${y+3}" font-size="9" fill="#9AA6C2" text-anchor="end">${v.toFixed(0)}${opt.pct?'%':''}</text>`;}
  const bw=Math.min(30,iw/labels.length*0.7);
  labels.forEach((lb,i)=>{const x=pl+iw*(i+0.5)/labels.length-bw/2;let acc=0;const tot=totals[i]||1;
    segs.forEach(se=>{const val=se.data[i];const disp=opt.pct?(val/tot*100):val;const h=ih*disp/max;const y=pt+ih-ih*acc/max - h;
      if(disp>0){s+=`<rect x="${x}" y="${y}" width="${bw}" height="${h}" fill="${se.color}"><title>${se.name} ${lb}: ${opt.pct?(val/tot*100).toFixed(1)+'%':val}</title></rect>`;
        // in-segment label if tall enough
        if(h>=14){const txt=opt.pct?(val/tot*100).toFixed(0)+'%':fmtN(val);s+=`<text x="${x+bw/2}" y="${y+h/2+3}" font-size="7.5" font-weight="700" fill="#fff" text-anchor="middle">${txt}</text>`;}}
      acc+=disp;});
    // total label on top (absolute mode)
    if(!opt.pct){const topY=pt+ih-ih*acc/max;s+=`<text x="${x+bw/2}" y="${topY-3}" font-size="7.5" font-weight="700" fill="#444" text-anchor="middle">${fmtN(tot)}</text>`;}
    s+=`<text x="${x+bw/2}" y="${H-pb+14}" font-size="8.5" fill="#777" text-anchor="middle">${lb}</text>`;});
  s+='</svg>';
  let lg='<div class="legend-mini" style="text-align:center">'+segs.map(se=>`<span style="display:inline-block;margin:0 7px"><span style="display:inline-block;width:10px;height:10px;border-radius:2px;background:${se.color};vertical-align:middle"></span> ${se.name}</span>`).join('')+'</div>';
  document.getElementById(el).innerHTML=s+lg;
}
// build scatter SVG string.
// opt.labelMode: 'off' | 'lines' (leader-line callouts) | 'numbers' (number badge on each point + side legend)
// opt.labelTop: N (top offenders to label). opt.offenderScore(p)->higher=worse
function scatterSVG(points,opt,big){
  opt=opt||{};
  const labelMode=opt.labelMode||(opt.labelTop?'lines':'off');
  const labelTop=(labelMode!=='off')?(opt.labelTop||5):0;
  const legendW=labelTop?180:0;
  const W=(big?760:560)+legendW,H=big?540:380,pl=52,pr=18+legendW,pt=20,pb=46;const iw=W-pl-pr,ih=H-pt-pb;
  const xs=points.map(p=>p.x),ys=points.map(p=>p.y);
  let xmin=opt.xmin!=null?opt.xmin:Math.min(...xs),xmax=opt.xmax!=null?opt.xmax:Math.max(...xs);
  let ymin=opt.ymin!=null?opt.ymin:Math.min(...ys),ymax=opt.ymax!=null?opt.ymax:Math.max(...ys);
  if(!isFinite(xmin)){xmin=0;xmax=1;}if(!isFinite(ymin)){ymin=0;ymax=1;}
  if(xmin===xmax){xmin-=1;xmax+=1;}if(ymin===ymax){ymin-=1;ymax+=1;}
  const padx=(xmax-xmin)*0.1,pady=(ymax-ymin)*0.12;xmin-=padx;xmax+=padx;ymin-=pady;ymax+=pady;
  const X=v=>pl+iw*(v-xmin)/((xmax-xmin)||1);const Y=v=>pt+ih-ih*(v-ymin)/((ymax-ymin)||1);
  let s=svgEl(W,H);
  s+=`<rect x="0" y="0" width="${W}" height="${H}" fill="#ffffff" fill-opacity="0"/>`;
  for(let g=0;g<=4;g++){const yy=pt+ih*g/4;s+=`<line x1="${pl}" y1="${yy}" x2="${W-pr}" y2="${yy}" stroke="#F1F4F9"/>`;const xx=pl+iw*g/4;s+=`<line x1="${xx}" y1="${pt}" x2="${xx}" y2="${pt+ih}" stroke="#F1F4F9"/>`;}
  const x0=opt.x0!=null?opt.x0:0,y0=opt.y0!=null?opt.y0:0;
  if(x0>=xmin&&x0<=xmax)s+=`<line x1="${X(x0)}" y1="${pt}" x2="${X(x0)}" y2="${pt+ih}" stroke="#94A3B8" stroke-width="1.4" stroke-dasharray="4 3"/>`;
  if(y0>=ymin&&y0<=ymax)s+=`<line x1="${pl}" y1="${Y(y0)}" x2="${W-pr}" y2="${Y(y0)}" stroke="#94A3B8" stroke-width="1.4" stroke-dasharray="4 3"/>`;
  if(opt.qlabels){const ql=opt.qlabels;const midX0=(X(xmin)+X(x0))/2,midX1=(X(x0)+X(xmax))/2;
    s+=`<text x="${midX1}" y="${pt+12}" font-size="9" fill="#B0B8C8" text-anchor="middle">${ql.tr||''}</text>`;
    s+=`<text x="${midX0}" y="${pt+12}" font-size="9" fill="#B0B8C8" text-anchor="middle">${ql.tl||''}</text>`;
    s+=`<text x="${midX1}" y="${pt+ih-4}" font-size="9" fill="#B0B8C8" text-anchor="middle">${ql.br||''}</text>`;
    s+=`<text x="${midX0}" y="${pt+ih-4}" font-size="9" fill="#B0B8C8" text-anchor="middle">${ql.bl||''}</text>`;}
  s+=`<text x="${pl+iw/2}" y="${H-6}" font-size="10" fill="#555" text-anchor="middle">${opt.xlabel||''}</text>`;
  s+=`<text x="14" y="${pt+ih/2}" font-size="10" fill="#555" text-anchor="middle" transform="rotate(-90 14 ${pt+ih/2})">${opt.ylabel||''}</text>`;
  for(let g=0;g<=4;g++){const vx=xmin+(xmax-xmin)*g/4;s+=`<text x="${pl+iw*g/4}" y="${pt+ih+14}" font-size="8" fill="#9AA6C2" text-anchor="middle">${vx.toFixed(0)}${opt.xsuffix||''}</text>`;const vy=ymin+(ymax-ymin)*g/4;s+=`<text x="${pl-6}" y="${Y(vy)+3}" font-size="8" fill="#9AA6C2" text-anchor="end">${vy.toFixed(0)}${opt.ysuffix||''}</text>`;}
  // determine top offenders
  let tops=[];
  if(labelTop&&opt.offenderScore){tops=points.slice().sort((a,b)=>opt.offenderScore(b)-opt.offenderScore(a)).slice(0,labelTop);}
  const topIdx=new Map();tops.forEach((p,i)=>topIdx.set(p,i+1));
  // points
  points.forEach(p=>{const isTop=topIdx.has(p);s+=`<circle cx="${X(p.x)}" cy="${Y(p.y)}" r="${p.r||5}" fill="${p.color||'#E4002B'}" fill-opacity="${isTop?0.95:0.62}" stroke="${isTop?'#111':'#fff'}" stroke-width="${isTop?1.5:1}"><title>${p.label}\n${opt.xlabel}: ${p.x.toFixed(1)}${opt.xsuffix||''}\n${opt.ylabel}: ${p.y.toFixed(1)}${opt.ysuffix||''}</title></circle>`;
    if(labelMode==='off'&&p.text)s+=`<text x="${X(p.x)+(p.r||5)+2}" y="${Y(p.y)+3}" font-size="8.5" fill="#333">${p.text}</text>`;});
  if(labelTop&&tops.length){
    const lx=W-legendW+8;let ly=pt+8;
    if(labelMode==='lines'){
      // number ring on point + leader line to side list
      tops.forEach(p=>{const n=topIdx.get(p);s+=`<circle cx="${X(p.x)}" cy="${Y(p.y)}" r="9" fill="none" stroke="#111" stroke-width="1"/>`;s+=`<text x="${X(p.x)}" y="${Y(p.y)-11}" font-size="9" font-weight="800" fill="#111" text-anchor="middle">${n}</text>`;});
      s+=`<text x="${lx}" y="${ly}" font-size="10" font-weight="800" fill="#111">Top ${tops.length} ofensores</text>`;ly+=16;
      tops.forEach(p=>{const n=topIdx.get(p);const nm=p.label.length>22?p.label.slice(0,22)+'…':p.label;
        s+=`<line x1="${X(p.x)+9}" y1="${Y(p.y)}" x2="${lx-3}" y2="${ly-3}" stroke="#C0C6D4" stroke-width="0.8"/>`;
        s+=`<circle cx="${lx+3}" cy="${ly-4}" r="7" fill="${p.color}"/><text x="${lx+3}" y="${ly-1}" font-size="8" font-weight="800" fill="#fff" text-anchor="middle">${n}</text>`;
        s+=`<text x="${lx+14}" y="${ly-1}" font-size="9" fill="#333">${nm}</text>`;ly+=16;});
    } else if(labelMode==='numbers'){
      // just a number badge on each top point (no lines), plus numbered legend list
      tops.forEach(p=>{const n=topIdx.get(p);const rr=Math.max(p.r||5,7);
        s+=`<circle cx="${X(p.x)}" cy="${Y(p.y)}" r="${rr}" fill="${p.color}" fill-opacity="0.95" stroke="#111" stroke-width="1.2"/>`;
        s+=`<text x="${X(p.x)}" y="${Y(p.y)+3}" font-size="9" font-weight="800" fill="#fff" text-anchor="middle">${n}</text>`;});
      s+=`<text x="${lx}" y="${ly}" font-size="10" font-weight="800" fill="#111">Top ${tops.length} ofensores</text>`;ly+=16;
      tops.forEach(p=>{const n=topIdx.get(p);const nm=p.label.length>24?p.label.slice(0,24)+'…':p.label;
        s+=`<circle cx="${lx+3}" cy="${ly-4}" r="7" fill="${p.color}" stroke="#111" stroke-width="0.8"/><text x="${lx+3}" y="${ly-1}" font-size="8" font-weight="800" fill="#fff" text-anchor="middle">${n}</text>`;
        s+=`<text x="${lx+14}" y="${ly-1}" font-size="9" fill="#333">${nm}</text>`;ly+=16;});
    }
  }
  s+='</svg>';return s;
}
function scatter(el,points,opt){opt=opt||{};CHARTS[el]={points,opt};const mode=S.insLabels?'lines':'off';document.getElementById(el).innerHTML=scatterSVG(points,Object.assign({},opt,{labelMode:mode,labelTop:5}),false);}
const CHARTS={};
function vBars(el,labels,data,opt){
  opt=opt||{};const W=Math.max(560,labels.length*20),H=300,pl=34,pr=10,pt=16,pb=34;const iw=W-pl-pr,ih=H-pt-pb;
  const max=Math.max(...data,1);let s=svgEl(W,H);
  for(let g=0;g<=4;g++){const y=pt+ih-ih*g/4;s+=`<line x1="${pl}" y1="${y}" x2="${W-pr}" y2="${y}" stroke="#EEF1F7"/><text x="${pl-4}" y="${y+3}" font-size="8" fill="#9AA6C2" text-anchor="end">${Math.round(max*g/4)}</text>`;}
  const bw=iw/labels.length;
  labels.forEach((lb,i)=>{const bh=ih*data[i]/max;const x=pl+bw*i+2;const y=pt+ih-bh;
    s+=`<rect x="${x}" y="${y}" width="${bw-3}" height="${bh}" rx="2" fill="${opt.colors?opt.colors[i]:'#E4002B'}"><title>${lb}: ${data[i]}</title></rect>`;
    if(data[i]>0)s+=`<text x="${x+(bw-3)/2}" y="${y-2}" font-size="7.5" font-weight="700" fill="#555" text-anchor="middle">${data[i]}</text>`;
    s+=`<text x="${x+(bw-3)/2}" y="${H-pb+12}" font-size="7.5" fill="#888" text-anchor="middle">${lb}</text>`;});
  s+='</svg>';document.getElementById(el).innerHTML=s;
}

/* ============ AGGREGATION (returns triple rec/ant/ano) ============ */
function M0(){return {ttd:0,ap:0,rec_cred:0,rec_ext:0,rec_eleg:0,rec_anti:0,rec_cs:0,rec_bio:0,rec_ra:0,rec_rb:0,cons_ra:0,cons_rb:0};}
function accM(o,r){o.ttd+=r.ttd;o.ap+=r.ap;o.rec_cred+=r.rec_cred;o.rec_ext+=(r.rec_ext||0);o.rec_eleg+=r.rec_eleg;o.rec_anti+=r.rec_anti;o.rec_cs+=r.rec_cs;o.rec_bio+=r.rec_bio;o.rec_ra+=r.rec_ra;o.rec_rb+=r.rec_rb;o.cons_ra+=r.cons_ra;o.cons_rb+=r.cons_rb;}
function finM(o){o.rec=o.ttd-o.ap;o.tx=o.ttd?o.ap/o.ttd:0;return o;}
// generic pool aggregation into triple by predicate
// ===== carteira filter =====
function _dimActive(set,arr){return set&&set.size&&set.size!==arr.length;}
// cumulative quality level: a PDV is "effectively carteirizado" only if its CRANK <= S.cartLevel (1=Ident,2=+Semelhança,3=+Estimada)
function effCarteirized(r){return (r.CRANK||4)<=S.cartLevel;}
// effective hierarchy honoring the level (below level -> treated as não atribuído)
function effHier(r){
  if(effCarteirized(r))return {exec:r.EXEC,gn:r.GN,gfil:r.GFIL,ger:r.GER,fant:r.FANT,grupo:r.CGRP,rank:r.CRANK};
  return {exec:null,gn:null,gfil:null,ger:null,fant:null,grupo:'Não Identificada',rank:4};
}
function cartActive(){const cm=DD.carteira_meta;return _dimActive(S.execs,cm.execs)||_dimActive(S.gns,cm.gns)||_dimActive(S.gfils,cm.gfils||[])||_dimActive(S.gers,cm.gers);}
function fCart(r){
  if(!cartActive())return true;
  if(r.CGRP===undefined)return false; // rows without carteira dims (e.g. DD.rno) can't satisfy an active carteira filter
  const eh=effHier(r);const cm=DD.carteira_meta;
  if(_dimActive(S.execs,cm.execs)&&!S.execs.has(eh.exec))return false;
  if(_dimActive(S.gns,cm.gns)&&!S.gns.has(eh.gn))return false;
  if(_dimActive(S.gfils,cm.gfils||[])&&!S.gfils.has(eh.gfil))return false;
  if(_dimActive(S.gers,cm.gers)&&!S.gers.has(eh.ger))return false;
  return true;
}
// when a carteira filter is active and the caller passed DD.rno, transparently use DD.pdv (same metrics, carries carteira dims)
function srcSwap(pool){return (pool===DD.rno && cartActive())?DD.pdv:pool;}
function agg3(pool,pred){
  const usePool=srcSwap(pool);
  const t={rec:M0(),ant:M0(),ano:M0()};
  for(const r of usePool){
    if(!pred(r))continue;if(!fCart(r))continue;
    if(r.SAFRA===SAF.rec)accM(t.rec,r);
    else if(r.SAFRA===SAF.ant)accM(t.ant,r);
    else if(r.SAFRA===SAF.ano)accM(t.ano,r);
  }
  finM(t.rec);finM(t.ant);finM(t.ano);return t;
}
function fProd(r){return S.prod.has(r.PROD);}
function fCan(r){return S.canais.has(r.CN);}
function fCid(r){return S.cidades.has(r.CIDLAB);}
function rnoTriple(extra){return agg3(DD.rno,r=>fProd(r)&&fCan(r)&&fCid(r)&&(!extra||extra(r)));}
function brTriple(){return agg3(DD.br,r=>S.prod.has(r.PROD)&&S.canais.has(r.CN));}
// grouped triples by key function (over rno pool honoring filters)
function groupTriples(pool,keyFn,extra){
  const usePool=srcSwap(pool);
  const rec={},ant={},ano={};
  for(const r of usePool){
    if(extra&&!extra(r))continue;if(!fCart(r))continue;
    const k=keyFn(r);if(k==null)continue;
    const tgt=r.SAFRA===SAF.rec?rec:r.SAFRA===SAF.ant?ant:r.SAFRA===SAF.ano?ano:null;
    if(!tgt)continue;
    if(!tgt[k])tgt[k]=M0();accM(tgt[k],r);
  }
  const keys=new Set([...Object.keys(rec),...Object.keys(ant),...Object.keys(ano)]);
  const out={};
  keys.forEach(k=>{out[k]={rec:finM(rec[k]||M0()),ant:finM(ant[k]||M0()),ano:finM(ano[k]||M0())};});
  return out;
}

/* ============ GENERIC TABLE with sort + filter + per-field MoM/YoY ============ */
const TS={}; // table states
function tget(tid){if(!TS[tid])TS[tid]={sortCol:null,sortDir:1,filters:{}};return TS[tid];}
// column: {key,label,type:'text'|'count'|'part'|'rate',text?(row),num?(agg),den?(agg),pill?,hlneg?}
function cellFor(c,row){
  if(c.type==='text')return {sv:0};
  const nr=c.num(row.rec),na=c.num(row.ant),ny=c.num(row.ano);
  if(c.type==='rate'){
    const dr=c.den(row.rec),da=c.den(row.ant),dy=c.den(row.ano);
    const vr=dr?nr/dr:0,va=da?na/da:0,vy=dy?ny/dy:0;
    return {sv:vr,disp:fmtP(vr),pill:true,mom:{ok:da>0,v:vr-va,txt:fmtPP(vr-va)},yoy:{ok:dy>0,v:vr-vy,txt:fmtPP(vr-vy)}};
  }
  if(c.type==='part'){
    if(S.mode==='pct'){
      const dr=c.den(row.rec),da=c.den(row.ant),dy=c.den(row.ano);
      const vr=dr?nr/dr:0,va=da?na/da:0,vy=dy?ny/dy:0;
      return {sv:vr,disp:fmtP(vr),mom:{ok:da>0,v:vr-va,txt:fmtPP(vr-va)},yoy:{ok:dy>0,v:vr-vy,txt:fmtPP(vr-vy)}};
    }
    return {sv:nr,disp:fmtN(nr),mom:{ok:row.ant.ttd>0,v:nr-na,txt:fmtD(nr-na)},yoy:{ok:row.ano.ttd>0,v:nr-ny,txt:fmtD(nr-ny)}};
  }
  // count
  if(S.mode==='pct'){
    const gm=na?(nr-na)/na:null,gy=ny?(nr-ny)/ny:null;
    return {sv:nr,disp:fmtN(nr),mom:{ok:na>0,v:gm,txt:gm==null?'':fmtGrow(gm)},yoy:{ok:ny>0,v:gy,txt:gy==null?'':fmtGrow(gy)}};
  }
  return {sv:nr,disp:fmtN(nr),mom:{ok:row.ant.ttd>0,v:nr-na,txt:fmtD(nr-na)},yoy:{ok:row.ano.ttd>0,v:nr-ny,txt:fmtD(nr-ny)}};
}
function pillTx(tx){const c=tx>=0.7?'pg':tx>=0.55?'pa':'pr';return `<span class="pill ${c}">${fmtP(tx)}</span>`;}
function cellHTML(c,cell,showDelta){
  const val=(c.pill||c.type==='rate')?pillTx(cell.sv):`<span class="cv">${cell.disp}</span>`;
  if(showDelta===false)return `<div class="cellwrap">${val}</div>`;
  const dd=d=>d&&d.ok?`<span class="${d.v>=0?'up':'down'}">${d.txt}</span>`:'<span class="mut">n/d</span>';
  return `<div class="cellwrap">${val}<div class="delta">M ${dd(cell.mom)} · A ${dd(cell.yoy)}</div></div>`;
}
function renderTable(tid,cols,rows,opt){
  opt=opt||{};const st=tget(tid);
  const items=rows.map(r=>({row:r,cells:cols.map(c=>cellFor(c,r))}));
  // filter
  let fil=items.filter(it=>{
    for(let i=0;i<cols.length;i++){const c=cols[i];const f=st.filters[c.key];if(!f||f.val==null||f.val==='')continue;
      if(c.type==='text'){if(!String(c.text(it.row)).toLowerCase().includes(String(f.val).toLowerCase()))return false;}
      else{const scale=(c.type==='rate'||(c.type==='part'&&S.mode==='pct'))?100:1;const fv=parseFloat(String(f.val).replace(',','.'))/scale;if(isNaN(fv))continue;const v=it.cells[i].sv;if(f.op==='ge'&&!(v>=fv))return false;if(f.op==='le'&&!(v<=fv))return false;}
    }return true;});
  // sort
  if(st.sortCol!=null){const ci=cols.findIndex(c=>c.key===st.sortCol);if(ci>=0){const c=cols[ci];
    fil.sort((a,b)=>{if(c.type==='text'){const av=String(c.text(a.row)).toLowerCase(),bv=String(c.text(b.row)).toLowerCase();return st.sortDir*(av<bv?-1:av>bv?1:0);}return st.sortDir*(((a.cells[ci].sv)||0)-((b.cells[ci].sv)||0));});}}
  if(opt.limit)fil=fil.slice(0,opt.limit);
  const compact=opt.compact?' tbl-compact':'';
  let inner=`<table data-tid="${tid}" class="${compact.trim()}"><thead><tr>`;
  cols.forEach(c=>{const active=st.sortCol===c.key;const ar=active?(st.sortDir>0?'▲':'▼'):'⇅';const cc=c.cls?' '+c.cls:'';
    inner+=`<th class="sortable ${active?'sorton':''}${cc}" data-tid="${tid}" data-col="${c.key}">${c.label} <span class="sar">${ar}</span></th>`;});
  inner+='</tr><tr class="filterrow">';
  cols.forEach(c=>{const f=st.filters[c.key]||{op:'ge',val:''};const cc=c.cls?' class="'+c.cls+'"':'';
    if(c.type==='text')inner+=`<th${cc}><input class="fltxt" data-tid="${tid}" data-col="${c.key}" placeholder="buscar…" value="${(f.val||'').replace(/"/g,'&quot;')}"></th>`;
    else inner+=`<th${cc}><span class="fnum"><select class="flop" data-tid="${tid}" data-col="${c.key}"><option value="ge"${f.op==='ge'?' selected':''}>≥</option><option value="le"${f.op==='le'?' selected':''}>≤</option></select><input class="flval" data-tid="${tid}" data-col="${c.key}" placeholder="—" value="${f.val||''}"></span></th>`;});
  inner+='</tr></thead><tbody>';
  if(!fil.length)inner+=`<tr><td colspan="${cols.length}" style="text-align:center;color:#9AA6C2;padding:18px">Nenhum resultado com os filtros atuais.</td></tr>`;
  fil.forEach(it=>{const hl=opt.hl?opt.hl(it.row,it.cells):'';
    inner+=`<tr${hl?` style="background:${hl}"`:''}>`;
    cols.forEach((c,i)=>{const cc=c.cls?' class="'+c.cls+'"':'';if(c.type==='text'){inner+=`<td${cc}>${c.text(it.row)}</td>`;}else{inner+=`<td${cc}>${cellHTML(c,it.cells[i],opt.showDelta)}</td>`;}});
    inner+='</tr>';});
  inner+='</tbody></table>';
  if(opt.topscroll){
    // dual scrollbar: a top proxy scrollbar synced with the table's own scroll
    return `<div class="dualscroll" data-ds="${tid}"><div class="ds-top"><div class="ds-spacer"></div></div><div class="tablewrap ds-body">${inner}</div></div>`;
  }
  return `<div class="tablewrap">${inner}</div>`;
}

/* ============ MULTISELECT ============ */
function msDropdown(id,label,groups,selSet,allItems){
  const cnt=selSet.size, tot=allItems.length;
  const openAttr=S.openDD.has(id)?' open':'';
  let h=`<details class="msdd" data-dd="${id}"${openAttr}><summary><span>${label} <span class="cnt">${cnt}/${tot}</span></span><span class="car">▾</span></summary><div class="msbody">`;
  h+=`<input class="msearch" data-dd="${id}" placeholder="filtrar…">`;
  h+=`<div class="msquick"><button data-dd="${id}" data-act="all">Todos</button><button data-dd="${id}" data-act="none">Limpar</button></div>`;
  Object.entries(groups).forEach(([g,items])=>{
    if(!items.length)return;
    h+=`<div class="grp">${g}<a data-dd="${id}" data-grp="${g}">alternar</a></div>`;
    items.forEach(it=>{h+=`<label class="msitem" data-item="${it.toLowerCase()}"><input type="checkbox" class="mscheck" data-dd="${id}" data-val="${it.replace(/"/g,'&quot;')}"${selSet.has(it)?' checked':''}> ${it}</label>`;});
  });
  h+='</div></details>';
  return h;
}
/* ============ FILTER BAR ============ */
function filterBar(opts){
  opts=opts||{};let h='<div class="filters">';
  if(opts.prod!==false)
    h+=`<div class="fgroup"><label>Produto</label>${msDropdown('prod','Produto',{'Produtos':ALLPROD.map(p=>PLAB[p])},new Set([...S.prod].map(p=>PLAB[p])),ALLPROD.map(p=>PLAB[p]))}</div>`;
  if(opts.canal!==false){
    const groups={'Canais Presenciais':PRES,'Canais Remotos':REM,'Outros Canais':outros()};
    h+=`<div class="fgroup"><label>Canal (individual ou combinação)</label>${msDropdown('canal','Canal',groups,S.canais,DD.canais_norm)}</div>`;
  }
  if(opts.city!==false){
    h+=`<div class="fgroup"><label>Cidade / Município (OPERADORA)</label>${msDropdown('cid','Cidade',DD.cidades,S.cidades,allCidades())}</div>`;
  }
  if(opts.cart!==false){
    const cm=DD.carteira_meta;
    h+=`<div class="fgroup"><label>Nível de qualificação (cumulativo)</label>${cartLevelSlider()}</div>`;
    h+=`<div class="fgroup"><label>Gerente Regional</label>${msDropdown('ger','Gerente',{'Gerentes':cm.gers},S.gers,cm.gers)}</div>`;
    h+=`<div class="fgroup"><label>Gerente de Filial</label>${msDropdown('gfil','Filial',{'Gerentes de Filial':cm.gfils||[]},S.gfils,cm.gfils||[])}</div>`;
    h+=`<div class="fgroup"><label>GN / Coordenador</label>${msDropdown('gn','GN',{'Coordenadores':cm.gns},S.gns,cm.gns)}</div>`;
    h+=`<div class="fgroup"><label>Executivo (carteira)</label>${msDropdown('exec','Executivo',{'Executivos':cm.execs},S.execs,cm.execs)}</div>`;
  }
  h+='</div>';
  return h;
}
// map product labels back
function prodFromLabel(l){return Object.keys(PLAB).find(k=>PLAB[k]===l);}
// cumulative quality slider: 1=Identificada, 2=+Semelhança, 3=+Estimada
const LEVELNAMES=['','Somente Identificada','Identificada + Semelhança','Identificada + Semelhança + Estimada'];
function cartLevelSlider(){
  const lv=S.cartLevel;
  let h='<div class="qslider">';
  h+='<input type="range" min="1" max="3" step="1" value="'+lv+'" id="qslider" class="qsl-range">';
  h+='<div class="qsl-ticks">';
  [['1','Identificada','on'],['2','+ Semelhança',''],['3','+ Estimada','']].forEach(([n,nm],i)=>{
    const active=(i+1)<=lv;const cur=(i+1)===lv;
    h+=`<span class="qsl-tick ${active?'act':''} ${cur?'cur':''}" data-lv="${i+1}"><span class="qsl-dot"></span><span class="qsl-lbl">${nm}</span></span>`;
  });
  h+='</div></div>';
  return h;
}

/* ===== FILTER STATUS TAGS (req 1) ===== */
// abbreviate a list of selected options: show first 2, then "+N"; if all selected -> "Todos"
function abbrevSel(items,allWord){
  if(!items.length)return allWord;
  if(items.length<=2)return items.join(', ');
  return items.slice(0,2).join(', ')+' +'+(items.length-2);
}
function filterState(){
  const prodAll=S.prod.size===ALLPROD.length;
  const canAll=S.canais.size===DD.canais_norm.length;
  const cidAll=S.cidades.size===allCidades().length;
  const prodItems=ALLPROD.filter(p=>S.prod.has(p)).map(p=>PLAB[p]);
  const canItems=DD.canais_norm.filter(c=>S.canais.has(c));
  const cidItems=allCidades().filter(c=>S.cidades.has(c));
  const cm=DD.carteira_meta;const gfilsArr=cm.gfils||[];
  const eAll=S.execs.size===cm.execs.length,gAll=S.gns.size===cm.gns.length,fAll=S.gfils.size===gfilsArr.length,rAll=S.gers.size===cm.gers.length;
  const eItems=cm.execs.filter(x=>S.execs.has(x)),gItems=cm.gns.filter(x=>S.gns.has(x)),fItems=gfilsArr.filter(x=>S.gfils.has(x)),rItems=cm.gers.filter(x=>S.gers.has(x));
  return {
    grupo:{active:S.cartLevel<3, txt:LEVELNAMES[S.cartLevel], label:'Nível: '+LEVELNAMES[S.cartLevel]},
    prod:{active:!prodAll, n:S.prod.size, tot:ALLPROD.length, txt:prodAll?'Todos':abbrevSel(prodItems,'Todos'), label:'Produto: '+(prodAll?'Todos':abbrevSel(prodItems,'Todos'))},
    canal:{active:!canAll, n:S.canais.size, tot:DD.canais_norm.length, txt:canAll?'Todos':abbrevSel(canItems,'Todos'), label:'Canal: '+(canAll?'Todos':abbrevSel(canItems,'Todos'))},
    cid:{active:!cidAll, n:S.cidades.size, tot:allCidades().length, txt:cidAll?'Todas':abbrevSel(cidItems,'Todas'), label:'Cidade: '+(cidAll?'Todas':abbrevSel(cidItems,'Todas'))},
    exec:{active:!eAll, txt:eAll?'Todos':abbrevSel(eItems,'Todos'), label:'Executivo: '+(eAll?'Todos':abbrevSel(eItems,'Todos'))},
    gn:{active:!gAll, txt:gAll?'Todos':abbrevSel(gItems,'Todos'), label:'GN: '+(gAll?'Todos':abbrevSel(gItems,'Todos'))},
    gfil:{active:!fAll, txt:fAll?'Todos':abbrevSel(fItems,'Todos'), label:'Gerente Filial: '+(fAll?'Todos':abbrevSel(fItems,'Todos'))},
    ger:{active:!rAll, txt:rAll?'Todos':abbrevSel(rItems,'Todos'), label:'Gerente Regional: '+(rAll?'Todos':abbrevSel(rItems,'Todos'))}
  };
}
function filterTags(){
  const f=filterState();const any=f.prod.active||f.canal.active||f.cid.active||f.exec.active||f.gn.active||f.gfil.active||f.ger.active||(f.grupo&&f.grupo.active);
  let h='<div class="filtbar">';
  if(!any){h+='<span class="ftag none">Sem filtros ativos — exibindo tudo</span>';}
  else{h+='<span class="ftag act" style="background:#FCE9EC;color:#a01829;border-color:#F3C4CC">Filtros ativos</span>';
    if(f.prod.active)h+=`<span class="ftag act"><span class="fk">Produto</span> ${f.prod.txt} <span class="fclr" data-clr="prod" title="Limpar">✕</span></span>`;
    if(f.canal.active)h+=`<span class="ftag act"><span class="fk">Canal</span> ${f.canal.txt} <span class="fclr" data-clr="canal" title="Limpar">✕</span></span>`;
    if(f.cid.active)h+=`<span class="ftag act"><span class="fk">Cidade</span> ${f.cid.txt} <span class="fclr" data-clr="cid" title="Limpar">✕</span></span>`;
    if(f.grupo&&f.grupo.active)h+=`<span class="ftag act"><span class="fk">Qualificação</span> ${f.grupo.txt} <span class="fclr" data-clr="grupo" title="Restaurar nível máximo">✕</span></span>`;
    if(f.ger.active)h+=`<span class="ftag act"><span class="fk">Ger. Regional</span> ${f.ger.txt} <span class="fclr" data-clr="ger" title="Limpar">✕</span></span>`;
    if(f.gfil.active)h+=`<span class="ftag act"><span class="fk">Ger. Filial</span> ${f.gfil.txt} <span class="fclr" data-clr="gfil" title="Limpar">✕</span></span>`;
    if(f.gn.active)h+=`<span class="ftag act"><span class="fk">GN</span> ${f.gn.txt} <span class="fclr" data-clr="gn" title="Limpar">✕</span></span>`;
    if(f.exec.active)h+=`<span class="ftag act"><span class="fk">Executivo</span> ${f.exec.txt} <span class="fclr" data-clr="exec" title="Limpar">✕</span></span>`;
    h+='<span class="ftag act" style="cursor:pointer" data-clr="all"><span class="fk">↺</span> Limpar todos</span>';
  }
  h+='</div>';
  return h;
}
// per-card badge. dims: filters the card RESPECTS; ignored: filters it deliberately ignores.
// Default shows the filter name + chosen options: "Produto: Banda Larga, TV Box +1" / "Cidade: Todos".
function scopeBadge(dims,ignored){
  const f=filterState();dims=dims||[];ignored=ignored||[];
  let out='';
  // respected dims: always show their current selection label (active in red, all-selected in muted)
  dims.forEach(d=>{const cls=f[d].active?'on':'off';out+=`<span class="scopebadge ${cls}" title="Reflete este filtro">${f[d].label}</span>`;});
  // ignored dims: only warn when the user actually has that filter active
  ignored.forEach(d=>{if(f[d].active)out+=`<span class="scopebadge warn" title="Este gráfico/tabela ignora o filtro de ${d==='prod'?'produto':d==='canal'?'canal':'cidade'} de propósito">⚠ ${f[d].label} (ignorado)</span>`;});
  return out;
}

/* ============ RENDER / NAV ============ */
const TITLES={v1:['Visão Geral','Consultas, recusas e perfil — RNO vs Brasil e por cidade'],
 v2:['Canais & PDVs','Abertura canal a canal e por PDV (expansível)'],
 v3:['Visão Diária','Motivo de recusa dia a dia e agrupado a cada 7 dias'],
 v4:['PDVs — DV_EQUIPE_VENDA','Ranking e filtros de risco por ponto de venda'],
 cart:['Carteira / Hierarquia comercial','Drilldown Canal → Gerente Regional → Filial → Coordenador → Executivo → PDV'],
 v5:['Insights','Achados que se adaptam aos filtros'],
 sum:['Resumo','Síntese pronta para envio — canais e PDVs ofensores em performance, fraude e mix de risco'],
 imp:['Importar dados','Atualize a base e o relatório para recalcular tudo']};
function render(){
  const ttlEl = document.getElementById('ttl');
  if (ttlEl && ttlEl.childNodes.length > 0 && TITLES[S.view]) ttlEl.childNodes[0].nodeValue = TITLES[S.view][0];
  const tsubEl = document.getElementById('tsub');
  if (tsubEl && TITLES[S.view]) tsubEl.textContent = TITLES[S.view][1];
  const vNote = document.getElementById('viewNote');
  if (vNote && TITLES[S.view]) vNote.textContent = TITLES[S.view][1] || '';
  const mt = document.getElementById('modeToggle');
  if (mt) mt.style.display = S.view === 'imp' ? 'none' : 'inline-flex';
  document.querySelectorAll('#modeToggle button').forEach(b=>b.classList.toggle('on',b.dataset.m===S.mode));
  const c=document.getElementById('content');
  // aba Importar é restrita: mostra tela de desbloqueio se este navegador não estiver autorizado
  if(S.view==='imp'&&!impUnlocked()){c.innerHTML=vImportLocked();bindImportLock();document.querySelectorAll('#nav a').forEach(a=>a.classList.toggle('locked',a.dataset.v==='imp'));return;}
  c.innerHTML=({v1:v1View,v2:v2View,v3:v3View,v4:v4View,v5:v5View,cart:vCarteira,sum:vResumo,imp:vImport})[S.view]();
  document.querySelectorAll('#nav a').forEach(a=>a.classList.toggle('locked',a.dataset.v==='imp'&&!impUnlocked()));
  if(S.view==='v1'){drawV1();bindGroups();}
  if(S.view==='v2'){bindGroups();bindV2Tools();}
  if(S.view==='v3'){drawV3();if(S.v3mode==='linha')drawV3Lines();bindGroups();bindV3Week();}
  if(S.view==='v4'){bindV4();restorePdvFocus();}
  if(S.view==='v5'){drawV5();bindV5Tools();}
  if(S.view==='cart'){bindCarteira();}
  if(S.view==='sum'){bindSumTools();}
  
  // Drawer filter visibility sync
  const fEl = document.querySelector('.filters');
  if (fEl && S.filtersHidden) fEl.style.display = 'none';
  const btnD = document.getElementById('btnDrawer');
  if (btnD) btnD.classList.toggle('open', !S.filtersHidden);
  const icoD = document.getElementById('drawerIco');
  if (icoD) icoD.textContent = S.filtersHidden ? '▸' : '▾';
// Onboarding popup eliminated
}
/* ================= ONBOARDING / DISCLAIMER (1x por sessão) ================= */
let _obShown=false;
function showOnboarding(){ /* disabled */ }catch(e){}}bg.remove();};
  bg.querySelector('#obOk').onclick=close;
  bg.querySelector('#obPdv').onclick=()=>{close();go('v4');};
  bg.onclick=e=>{if(e.target===bg)close();};
  document.addEventListener('keydown',function esc(ev){if(ev.key==='Escape'){close();document.removeEventListener('keydown',esc);}});
}
function maybeOnboard(view){
  if(view==='capa')return;                       // capa não dispara
  if(_obShown)return;                            // só 1x por carregamento
  try{if(localStorage.getItem('RNO_OB_HIDE')==='1')return;}catch(e){}
  showOnboarding();
}
/* ================= ACESSO RESTRITO — ABA IMPORTAR ================= */
// Um HTML local não consegue ler usuário do Windows / hostname / IP da rede (bloqueio de segurança do navegador).
// Então usamos: (a) tentativa de auto-detecção do IP local via WebRTC e (b) chave de acesso (matrícula/hostname), memorizada neste navegador.
const IMP_ALLOW={users:['F138138'],hosts:['CLR0AN001242041'],ips:['192.168.0.12','10.56.204.189']};
function impNorm(s){return String(s||'').trim().toUpperCase().replace(/\s+/g,'');}
function impKeyValid(v){const k=impNorm(v);
  return IMP_ALLOW.users.map(impNorm).includes(k)||IMP_ALLOW.hosts.map(impNorm).includes(k)||IMP_ALLOW.ips.includes(String(v||'').trim());}
function impUnlocked(){try{return localStorage.getItem('RNO_IMP_OK')==='1';}catch(e){return false;}}
function impUnlock(){try{localStorage.setItem('RNO_IMP_OK','1');}catch(e){}}
// tenta descobrir IP local (funciona em navegadores/políticas que não usam mDNS)
function impTryAutoIP(cb){
  try{
    const pc=new RTCPeerConnection({iceServers:[]});pc.createDataChannel('x');
    const found=new Set();
    pc.onicecandidate=e=>{
      if(!e.candidate){pc.close();cb([...found]);return;}
      const m=/([0-9]{1,3}(?:\.[0-9]{1,3}){3})/.exec(e.candidate.candidate||'');
      if(m)found.add(m[1]);
    };
    pc.createOffer().then(o=>pc.setLocalDescription(o)).catch(()=>cb([]));
    setTimeout(()=>{try{pc.close();}catch(e){}cb([...found]);},1200);
  }catch(e){cb([]);}
}
function vImportLocked(){
  return `<h2 class="vtitle">Importar dados</h2><div class="vdesc">Área restrita.</div>
  <div class="lockbox">
    <div class="lk">▲</div>
    <h3>Acesso restrito</h3>
    <p>Esta aba atualiza a base de todo o painel e está liberada apenas para o responsável pela ferramenta.<br>Informe sua <b>matrícula</b> ou o <b>hostname</b> da máquina autorizada para desbloquear neste navegador.</p>
    <div><input id="impKey" placeholder="Matrícula ou hostname" autocomplete="off"></div>
    <div style="margin-top:12px"><button class="ob-btn" id="impGo">Desbloquear</button></div>
    <div id="impErr" class="err" style="display:none">Credencial não autorizada.</div>
    <p style="margin-top:16px;font-size:11.5px">Depois de desbloquear, este navegador lembra o acesso. Se precisar liberar em outra máquina, use a mesma credencial.</p>
  </div>`;
}
function bindImportLock(){
  const btn=document.getElementById('impGo'),inp=document.getElementById('impKey'),err=document.getElementById('impErr');
  if(!btn)return;
  const attempt=()=>{if(impKeyValid(inp.value)){impUnlock();render();}else{err.style.display='block';inp.select();}};
  btn.onclick=attempt;
  inp.onkeydown=e=>{if(e.key==='Enter')attempt();};
  inp.focus();
  // auto-desbloqueio se o IP local for autorizado
  impTryAutoIP(ips=>{if(ips.some(ip=>IMP_ALLOW.ips.includes(ip))){impUnlock();render();}});
}
function applySidebar(){document.body.classList.toggle('side-collapsed',!!S.sidebarCollapsed);const t=document.getElementById('sideToggle');if(t)t.textContent=S.sidebarCollapsed?'›':'‹';}
function setSidebar(collapsed){S.sidebarCollapsed=collapsed;applySidebar();}
function go(v){
  S.view = v;
  document.querySelectorAll('#nav a').forEach(a => {
    a.classList.toggle('active', a.dataset.v === v);
    a.classList.toggle('on', a.dataset.v === v);
  });
  render();
  window.scrollTo(0,0);
}

/* KPI with per-field MoM/YoY.
   kind: 'count' | 'part' | 'rate'
   t = triple {rec,ant,ano}; k = metric key; dk = denominator key (for part/rate) */
function kpi(cls,label,t,kind,k,dk,sub){
  let val,momv,momt,yoyv,yoyt,momok=true,yoyok=true;
  const nr=t.rec[k],na=t.ant[k],ny=t.ano[k];
  if(kind==='rate'){
    const vr=t.rec[dk]?nr/t.rec[dk]:0,va=t.ant[dk]?na/t.ant[dk]:0,vy=t.ano[dk]?ny/t.ano[dk]:0;
    val=fmtP(vr);momv=vr-va;momt=fmtPP(momv);yoyv=vr-vy;yoyt=fmtPP(yoyv);momok=t.ant[dk]>0;yoyok=t.ano[dk]>0;
  }else if(kind==='part'){
    if(S.mode==='pct'){const vr=t.rec[dk]?nr/t.rec[dk]:0,va=t.ant[dk]?na/t.ant[dk]:0,vy=t.ano[dk]?ny/t.ano[dk]:0;val=fmtP(vr);momv=vr-va;momt=fmtPP(momv);yoyv=vr-vy;yoyt=fmtPP(yoyv);momok=t.ant[dk]>0;yoyok=t.ano[dk]>0;}
    else{val=fmtN(nr);momv=nr-na;momt=fmtD(momv);yoyv=nr-ny;yoyt=fmtD(yoyv);momok=t.ant.ttd>0;yoyok=t.ano.ttd>0;}
  }else{ // count
    val=fmtN(nr);
    if(S.mode==='pct'){momok=na>0;yoyok=ny>0;const gm=na?(nr-na)/na:0,gy=ny?(nr-ny)/ny:0;momv=gm;momt=fmtGrow(gm);yoyv=gy;yoyt=fmtGrow(gy);}
    else{momok=t.ant.ttd>0;yoyok=t.ano.ttd>0;momv=nr-na;momt=fmtD(momv);yoyv=nr-ny;yoyt=fmtD(yoyv);}
  }
  const dd=(ok,v,txt)=>ok?`<span class="${v>=0?'up':'down'}">${txt}</span>`:'<span class="mut">n/d</span>';
  return `<div class="kpi ${cls}"><div class="lab">${label}</div><div class="val">${val}</div>${sub?`<div class="sub">${sub}</div>`:''}<div class="dl">MoM ${dd(momok,momv,momt)} · YoY ${dd(yoyok,yoyv,yoyt)}</div></div>`;
}

/* ---------- CAPA (executiva) ---------- */
function vCapa(){
  const rno=agg3(DD.rno,r=>true),br=brTripleAll();
  const cidT=groupTriples(DD.rno,r=>r.CIDLAB);
  const arr=Object.entries(cidT).filter(([k,v])=>v.rec.ttd>50).sort((a,b)=>b[1].rec.tx-a[1].rec.tx);
  const best=arr[0],worst=arr[arr.length-1];
  // praças CABEADAS = Grandes Mercados + Mercados em Desenvolvimento (independe do volume do mês parcial)
  const nCabeadas=(DD.cidades['Grandes Mercados']||[]).length+(DD.cidades['Mercados em Desenvolvimento']||[]).length;
  const r=rno.rec,ra=rno.ano;const gap=r.tx-br.rec.tx;
  const momTx=r.tx-rno.ant.tx, yoyTx=r.tx-ra.tx;
  const csYoY=r.rec_cs-ra.rec_cs;
  // overall semaphore: gap large + fraud rising -> amber/red
  const sem = (gap<-0.08||csYoY>0)? 'r' : (momTx<0? 'a':'g');
  const semTxt = sem==='r'?'Atenção — abaixo do Brasil e fraude em alta':(sem==='a'?'Estável, porém abaixo do Brasil':'Saudável');
  const chip=(ok,txt)=>`<span class="chip chip-${ok?'g':'r'}">${txt}</span>`;
  const trend=heroTrend(DD.monthly_rno.map(m=>m.tx*100),DD.monthly_br.map(m=>m.tx*100));
  const hoje=new Date().toLocaleDateString('pt-BR',{day:'2-digit',month:'long',year:'numeric'});
  // ===== destaques operacionais (dinâmicos) =====
  const chanT=groupTriples(DD.rno,x=>x.CN);
  const chanArr=Object.entries(chanT).map(([cn,v])=>({cn,cg:canalGrupo(cn),rec:v.rec})).filter(x=>x.rec.ttd>=200);
  const worstChan=chanArr.slice().sort((a,b)=>a.rec.tx-b.rec.tx)[0];
  const csPdv=pdvAggAll().filter(p=>p.rec.rec_cs>0).sort((a,b)=>b.rec.rec_cs-a.rec.rec_cs)[0];
  const hl=`<div class="hlstrip">
    <div class="hlcard r"><div class="ic" style="color:#a01829;font-weight:800;font-size:15px">▼</div><div><div class="k">Canal mais ofensor (taxa)</div><div class="v">${worstChan?worstChan.cn:'–'}</div><div class="d">${worstChan?fmtP(worstChan.rec.tx)+' de aprovação · '+fmtN(worstChan.rec.ttd)+' consultas · '+worstChan.cg:'sem dados'}</div></div></div>
    <div class="hlcard a"><div class="ic" style="color:#8a6400;font-weight:800;font-size:15px">!</div><div><div class="k">Maior foco de ClearSale (PDV)</div><div class="v">${csPdv?csPdv.PDV:'–'}</div><div class="d">${csPdv?fmtN(csPdv.rec.rec_cs)+' flags ClearSale · '+csPdv.city+' · '+csPdv.cn:'sem dados'}</div></div></div>
    <div class="hlcard g"><div class="ic" style="color:#12723f;font-weight:800;font-size:15px">▲</div><div><div class="k">Melhor vs Pior praça</div><div class="v">${best?best[0]:'–'} ${best?fmtP(best[1].rec.tx):''}</div><div class="d">Pior: ${worst?worst[0]+' '+fmtP(worst[1].rec.tx):'–'} · ${arr.length} praças cobertas</div></div></div>
  </div>`;
  const mn=(n,t,tgt)=>`<span class="mn" onclick="go('${tgt||'v'+n}')"><b>${n}</b> ${t}</span>`;
  return `
  <div class="cov-mast">
    <div class="brandblk"><div class="accent"></div><div class="ttl">Aprovação de Crédito PF · Regional Norte<small>Relatório executivo · ${safraLabel(SAF.rec)} (parcial) · Uso Interno</small></div></div>
    <div class="mast-nav">
      ${mn('1','Geral')}${mn('2','Canais/PDVs')}${mn('3','Diária')}${mn('4','PDVs')}${mn('5','Carteira','cart')}${mn('6','Insights','v5')}
      <span class="mn cta" onclick="go('sum')"><b></b> Resumo</span>
    </div>
  </div>
  <div class="chero">
    <div class="inner">
      <div>
        <div class="eyebrow">Regional Norte · Crédito PF Fixa</div>
        <h2>Aprovação de crédito da RNO em <span class="hl">${fmtP(r.tx)}</span>, <span class="hl">${fmtPP(gap)}</span> frente ao Brasil</h2>
        <div class="lead">${fmtN(r.ttd)} consultas no mês · ${fmtN(r.ap)} aprovadas · ${fmtN(r.rec)} recusadas. Antifraude (Biometria + ClearSale) responde por ${fmtP(r.rec_anti/r.rec)} das recusas.</div>
        <div class="verdict"><span class="sem sem-${sem}"></span> ${semTxt}</div>
      </div>
      <div class="figblk">
        <div class="figlab">Taxa de Aprovação — RNO</div>
        <div class="fignum">${fmtP(r.tx)}</div>
        <div class="figsub">Brasil ${fmtP(br.rec.tx)} · gap ${fmtPP(gap)}</div>
        <div class="figdeltas"><span class="fchip ${momTx>=0?'up':'down'}">MoM ${fmtPP(momTx)}</span><span class="fchip ${yoyTx>=0?'up':'down'}">YoY ${fmtPP(yoyTx)}</span></div>
        <div class="trendwrap">${trend}</div>
        <div style="font-size:9.5px;color:#8FA0C6;margin-top:3px">Histórico 13 meses · RNO (—) × Brasil (··)</div>
      </div>
    </div>
  </div>
  <div class="xkpis">
    ${xkpi('Consultas no mês',fmtN(r.ttd),`Aprov ${fmtN(r.ap)} · Recusas ${fmtN(r.rec)}`,[['MoM',r.ttd>=rno.ant.ttd,fmtD(r.ttd-rno.ant.ttd)],['YoY',r.ttd>=ra.ttd,fmtD(r.ttd-ra.ttd)]])}
    ${xkpi('Recusas Antifraude',fmtN(r.rec_anti),`Biometria ${fmtN(r.rec_bio)} · ClearSale ${fmtN(r.rec_cs)}`,[['MoM',r.rec_anti<=rno.ant.rec_anti,fmtD(r.rec_anti-rno.ant.rec_anti)],['YoY',r.rec_anti<=ra.rec_anti,fmtD(r.rec_anti-ra.rec_anti)]])}
    ${xkpi('Mix de risco alto',fmtP(r.cons_ra/r.ttd),`${fmtN(r.cons_ra)} consultas de risco alto`,[['MoM',(r.cons_ra/r.ttd)<=(rno.ant.ttd?rno.ant.cons_ra/rno.ant.ttd:0),fmtPP((r.cons_ra/r.ttd)-(rno.ant.ttd?rno.ant.cons_ra/rno.ant.ttd:0))]])}
    ${xkpi('Praças cabeadas',nCabeadas+' cidades',`Melhor: ${best?best[0]+' '+fmtP(best[1].rec.tx):'–'} · Pior: ${worst?worst[0]+' '+fmtP(worst[1].rec.tx):'–'}`,[['Grandes+Desenv.',true,'segmentadas']])}
  </div>
  <div style="font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:.6px;color:var(--muted);margin:4px 0 8px">Destaques operacionais</div>
  ${hl}
  <div class="cta-bar">
    <div class="txt"><h4> Resumo</h4><p>Síntese pronta para envio: canais e PDVs ofensores em performance e antifraude, e mix de risco por PDV — com MoM e YoY.</p></div>
    <div class="acts"><button class="goact" onclick="go('sum')">Abrir Resumo</button><button class="goalt" onclick="go('v1')">Explorar Visão Geral →</button></div>
  </div>
  <div class="foot-credit">Elaborado por Arthur Rezende · Planejamento e Performance RNO · Fonte: BASE_ATUAL.xlsx (RNO, 360k linhas) · 08092026 - TAXA DE APROVAÇÃO FIXA PF.xlsx</div>`;
}
function navChip(n,t,d){return `<div class="navchip" onclick="go('${n==='imp'?'imp':'v'+n}')"><div class="nn">${n==='imp'?'':n}</div><div><div class="nt">${t}</div><div class="nd">${d}</div></div></div>`;}
// hero trend: two lines (RNO red, Brasil light) with gradient fill under RNO
function heroTrend(rnoVals,brVals){
  // wide viewBox matched to the container (fills the figure column without stretching)
  const W=420,H=90,pl=6,pr=6,pt=12,pb=16;const iw=W-pl-pr,ih=H-pt-pb;
  const all=rnoVals.concat(brVals);const mn=Math.floor(Math.min(...all)/5)*5,mx=Math.ceil(Math.max(...all)/5)*5;
  const X=i=>pl+iw*i/(rnoVals.length-1||1);const Y=v=>pt+ih-ih*(v-mn)/((mx-mn)||1);
  const path=vals=>{let d='';vals.forEach((v,i)=>d+=(i?'L':'M')+X(i).toFixed(1)+' '+Y(v).toFixed(1)+' ');return d;};
  const area=vals=>{let d='M'+X(0)+' '+Y(vals[0]);vals.forEach((v,i)=>d+='L'+X(i).toFixed(1)+' '+Y(v).toFixed(1));d+='L'+X(vals.length-1)+' '+(pt+ih)+'L'+X(0)+' '+(pt+ih)+'Z';return d;};
  const lastR=rnoVals[rnoVals.length-1],lastB=brVals[brVals.length-1];
  // preserveAspectRatio "none" here is intentional and safe: the wrapper (.trendwrap) fixes the height,
  // and the chart is a schematic sparkline (uniform axis), so horizontal fill reads correctly.
  return `<svg viewBox="0 0 ${W} ${H}" preserveAspectRatio="none" style="display:block;width:100%;height:100%">
    <defs><linearGradient id="hg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E4002B" stop-opacity="0.32"/><stop offset="1" stop-color="#E4002B" stop-opacity="0"/></linearGradient></defs>
    <path d="${area(rnoVals)}" fill="url(#hg)"/>
    <path d="${path(brVals)}" fill="none" stroke="rgba(255,255,255,.5)" stroke-width="1.4" stroke-dasharray="4 3" vector-effect="non-scaling-stroke"/>
    <path d="${path(rnoVals)}" fill="none" stroke="#FF6B82" stroke-width="2.2" vector-effect="non-scaling-stroke"/>
    <text x="${pl}" y="${H-3}" font-size="8" fill="#8FA0C6">${safraLabel(DD.monthly_rno[0].SAFRA)}</text>
    <text x="${W-pr}" y="${H-3}" font-size="8" fill="#8FA0C6" text-anchor="end">${safraLabel(SAF.rec)}</text>
    <text x="${W-pr}" y="${Y(lastR)-5}" font-size="8.5" font-weight="800" fill="#FF9BA8" text-anchor="end">RNO ${lastR.toFixed(0)}%</text>
    <text x="${W-pr}" y="${Y(lastB)+11}" font-size="8.5" font-weight="700" fill="rgba(255,255,255,.85)" text-anchor="end">BR ${lastB.toFixed(0)}%</text>
  </svg>`;
}
function xkpi(lab,big,sub,deltas,spark,invert){
  const dhtml=(deltas||[]).map(([k,ok,t])=>`<span class="chip chip-${ok?'g':'r'}">${k} ${t}</span>`).join(' ');
  return `<div class="xkpi"><div class="top"><span class="lab">${lab}</span></div><div class="big">${big}</div><div class="sub">${sub}</div><div style="margin-top:8px;display:flex;gap:6px;flex-wrap:wrap">${dhtml}</div>${spark?`<div class="spark">${spark}</div>`:''}</div>`;
}
function insCardX(cls,t,p){const tg={g:'Positivo',a:'Atenção',r:'Crítico'}[cls];return `<div class="ins ${cls} inscard"><span class="tag ${cls}">${tg}</span><b>${t}</b><p>${p}</p></div>`;}
function miniSpark(vals,color){const W=90,H=28,pad=3;const mn=Math.min(...vals),mx=Math.max(...vals);const X=i=>pad+(W-2*pad)*i/(vals.length-1);const Y=v=>H-pad-(H-2*pad)*(v-mn)/((mx-mn)||1);let d='';vals.forEach((v,i)=>d+=(i?'L':'M')+X(i).toFixed(1)+' '+Y(v).toFixed(1)+' ');return `<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}"><path d="${d}" fill="none" stroke="${color}" stroke-width="1.6"/><circle cx="${X(vals.length-1)}" cy="${Y(vals[vals.length-1])}" r="2.2" fill="${color}"/></svg>`;}
function brTripleAll(){return agg3(DD.br,r=>true);}
function navCard(n,t,d){return `<div class="navcard" onclick="go('${n==='imp'?'imp':'v'+n}')"><div class="ico">${n==='imp'?'':n}</div><h4>${t}</h4><p>${d}</p></div>`;}
function insHTML(cls,t,p){const tg={g:'Positivo',a:'Atenção',r:'Crítico'}[cls];return `<div class="ins ${cls}"><span class="tag ${cls}">${tg}</span><b>${t}</b><p>${p}</p></div>`;}

/* columns factory for scope/city/pdv tables */
function metricCols(labelCol){
  return [
    labelCol,
    {key:'cons',label:'Consultas',type:'count',num:a=>a.ttd},
    {key:'ap',label:'Aprovados',type:'count',num:a=>a.ap},
    {key:'tx',label:'Tx Aprov.',type:'rate',num:a=>a.ap,den:a=>a.ttd,pill:true},
    {key:'rec',label:'Recusas',type:'count',num:a=>a.rec},
    {key:'cred',label:S.mode==='pct'?'% Rest. Int.+Score':'Rest. Int.+Score',type:'part',num:a=>a.rec_cred,den:a=>a.rec},
    {key:'ext',label:S.mode==='pct'?'% Rest. Externa':'Rest. Externa',type:'part',num:a=>a.rec_ext,den:a=>a.rec},
    {key:'eleg',label:S.mode==='pct'?'% Elegib.':'Elegibilidade',type:'part',num:a=>a.rec_eleg,den:a=>a.rec},
    {key:'bio',label:S.mode==='pct'?'% Antif. Biometria':'Antif. Biometria',type:'part',num:a=>a.rec_bio,den:a=>a.rec},
    {key:'cs',label:S.mode==='pct'?'% Antif. ClearSale':'Antif. ClearSale',type:'part',num:a=>a.rec_cs,den:a=>a.rec},
    {key:'ra',label:S.mode==='pct'?'% Risco Alto':'Rec. Risco Alto',type:'part',num:a=>a.rec_ra,den:a=>a.rec},
    {key:'rb',label:S.mode==='pct'?'% Médio-Baixo':'Rec. Médio-Baixo',type:'part',num:a=>a.rec_rb,den:a=>a.rec},
  ];
}
/* ---------- VIEW 1 ---------- */
function v1View(){
  const proj=DD.proj.factor;
  const rno=rnoTriple(),br=brTriple();
  const r=rno.rec;
  let h=filterBar({})+filterTags();
  h+=`<h2 class="vtitle">Visão Geral — Regional Norte</h2><div class="vdesc">${safraLabel(SAF.rec)} (parcial) vs ${safraLabel(SAF.ant)} e ${safraLabel(SAF.ano)}. Projeção por dias úteis ×${proj.toFixed(2)}. Toggle alterna % ⇄ volume nos campos de participação; deltas MoM e YoY em cada indicador. Reflete todos os filtros.</div>`;
  h+='<div class="kpis">';
  h+=kpi('','Total de Consultas',rno,'count','ttd',null,`Proj. dias úteis: ${fmtN(r.ttd*proj)}`);
  h+=kpi('g','Taxa de Aprovação',rno,'rate','ap','ttd',`Aprovados: ${fmtN(r.ap)}`);
  h+=kpi('a','Total de Recusas',rno,'count','rec',null,`${fmtP(r.rec/r.ttd)} das consultas`);
  h+=kpi('r','Recusas Antifraude (total)',rno,'part','rec_anti','rec',`Biometria ${fmtN(r.rec_bio)} · ClearSale ${fmtN(r.rec_cs)}`);
  h+='</div><div class="kpis">';
  h+=kpi('b','Crédito (Rest. Interna + Score)',rno,'part','rec_cred','rec','Dívidas com a Claro / liberação');
  h+=kpi('b','Restrição Externa',rno,'part','rec_ext','rec','Dívidas externas / score em bureaus');
  h+=kpi('a','Elegibilidade',rno,'part','rec_eleg','rec','Outros casos não mapeados');
  h+=kpi('r','Antifraude (ClearSale)',rno,'part','rec_cs','rec','Flag da Serasa/ClearSale');
  h+='</div>';
  // Comparativo por escopo (Brasil, RNO, best/worst city)
  const cidT=groupTriples(DD.rno,x=>x.CIDLAB,x=>fProd(x)&&fCan(x)&&fCid(x));
  const arr=Object.entries(cidT).filter(([k,v])=>v.rec.ttd>30).sort((a,b)=>b[1].rec.tx-a[1].rec.tx);
  const best=arr[0],worst=arr[arr.length-1];
  const scopeRows=[{lab:'Brasil',rec:br.rec,ant:br.ant,ano:br.ano},{lab:'Regional Norte (RNO)',rec:rno.rec,ant:rno.ant,ano:rno.ano,hl:1}];
  if(best)scopeRows.push({lab:'Melhor cidade: '+best[0],rec:best[1].rec,ant:best[1].ant,ano:best[1].ano});
  if(worst)scopeRows.push({lab:'Pior cidade: '+worst[0],rec:worst[1].rec,ant:worst[1].ant,ano:worst[1].ano});
  const cols=metricCols({key:'lab',label:'Escopo',type:'text',text:r=>r.lab});
  h+=`<div class="card"><h3>Comparativo por escopo${scopeBadge(['prod','canal','cid'])}</h3><div class="csub">Brasil, RNO e melhor/pior cidade · cada campo com MoM e YoY · ordene/filtre nos cabeçalhos</div>`;
  h+=renderTable('t_scope',cols,scopeRows,{hl:r=>r.hl?'#FBE7EA':''});
  h+='</div>';
  // Ranking por cidade com grupos de segmento (req 5)
  h+=`<div class="card"><h3>Ranking por cidade (município) — por segmento${scopeBadge(['prod','canal'],['cid'])}</h3><div class="csub">Grupos: Grandes Mercados · Mercados em Desenvolvimento · Sem Cabo. Clique no grupo para expandir. Destaque nas 3 maiores praças. <b>Esta tabela lista todas as cidades</b> (não aplica o filtro de cidade, para permitir comparação).</div>`;
  h+=cityGroupedTable(cidT);
  h+='</div>';
  // Consultas por faixa de risco (req 2)
  h+=riskTable();
  // charts — respect filters (task 1): full 13-month history when unfiltered; 3-month comparison (Ago/25·Jul/26·Ago/26) when filtered
  const filt=anyFilterActive();
  const per=filt?('comparativo '+safraLabel(SAF.ano)+' · '+safraLabel(SAF.ant)+' · '+safraLabel(SAF.rec)):'histórico 13 meses';
  const perNote=filt?'<b>Reflete os filtros ativos</b> — 3 meses comparáveis (mês atual, anterior e ano anterior).':'<b>Histórico completo</b> — limpe os filtros para 13 meses; ao filtrar, mostra 3 meses comparáveis.';
  h+='<div class="card"><h3>Taxa de aprovação — '+per+' (RNO × Brasil)'+scopeBadge(['prod','canal','cid'])+'</h3><div class="csub">Série mensal (%). '+perNote+'</div><div class="chartbox" style="height:300px"><div id="c1a" style="width:100%;height:100%"></div></div></div>';
  h+='<div class="grid2">'+
     '<div class="card"><h3>Composição das recusas — RNO ('+per+')'+scopeBadge(['prod','canal','cid'])+'</h3><div class="csub">Colunas empilhadas · '+(S.mode==='pct'?'participação % das recusas':'volumes')+' · Crédito(Int.+Score) · Rest. Externa · Elegibilidade · Antif. Biometria · Antif. ClearSale</div><div class="chartbox" style="height:320px"><div id="c1b" style="width:100%;height:100%"></div></div></div>'+
     '<div class="card"><h3>Composição das recusas — Brasil ('+per+')'+scopeBadge(['prod','canal'],['cid'])+'</h3><div class="csub">Colunas empilhadas · '+(S.mode==='pct'?'participação % das recusas':'volumes')+'</div><div class="chartbox" style="height:320px"><div id="c1c" style="width:100%;height:100%"></div></div></div>'+
     '</div>';
  // Perfil de risco histórico (respeita filtros)
  h+='<h3 class="vtitle" style="margin:22px 0 4px">Perfil de risco — '+per+' (RNO)'+scopeBadge(['prod','canal','cid'])+'</h3><div class="vdesc">Grupos de risco por faixa (Crítico → Baixíssimo). Colunas empilhadas de demanda, aprovados e reprovados; e a taxa de aprovação de cada perfil. '+perNote+' Toggle alterna % ⇄ volume.</div>';
  h+='<div class="grid2">'+
     '<div class="card"><h3>Grupos de risco — Demanda (consultas)</h3><div class="csub">Colunas empilhadas por faixa de risco · '+(S.mode==='pct'?'participação %':'volumes')+'</div><div class="chartbox" style="height:320px"><div id="rh1" style="width:100%;height:100%"></div></div></div>'+
     '<div class="card"><h3>Grupos de risco — Aprovados</h3><div class="csub">Colunas empilhadas por faixa · '+(S.mode==='pct'?'participação %':'volumes')+'</div><div class="chartbox" style="height:320px"><div id="rh2" style="width:100%;height:100%"></div></div></div>'+
     '</div>';
  h+='<div class="grid2">'+
     '<div class="card"><h3>Grupos de risco — Reprovados</h3><div class="csub">Colunas empilhadas por faixa · '+(S.mode==='pct'?'participação %':'volumes')+'</div><div class="chartbox" style="height:320px"><div id="rh3" style="width:100%;height:100%"></div></div></div>'+
     '<div class="card"><h3>Taxa de aprovação por perfil de risco</h3><div class="csub">Linha por faixa (%) · demanda que passa em cada perfil ao longo dos meses</div><div class="chartbox" style="height:320px"><div id="rh4" style="width:100%;height:100%"></div></div></div>'+
     '</div>';
  return h;
}
function safraLabel(s){const mm=s%100;const yy=Math.floor(s/100)%100;const M=['','jan','fev','mar','abr','mai','jun','jul','ago','set','out','nov','dez'];return M[mm]+'/'+yy;}
// aggregate risk grain honoring filters, into per-faixa {rec,ant,ano} of {ttd,ap}
function riskTriples(){
  const rec={},ant={},ano={};
  for(const r of DD.risk){
    if(!S.prod.has(r.PROD))continue;if(!S.canais.has(r.CN))continue;if(!S.cidades.has(r.CIDLAB))continue;
    const tgt=r.SAFRA===SAF.rec?rec:r.SAFRA===SAF.ant?ant:r.SAFRA===SAF.ano?ano:null;if(!tgt)continue;
    if(!tgt[r.FX])tgt[r.FX]={ttd:0,ap:0};tgt[r.FX].ttd+=r.ttd;tgt[r.FX].ap+=r.ap;
  }
  return {rec,ant,ano};
}
function riskTable(){
  const t=riskTriples();const order=DD.fx_order;
  // build rows: one per faixa, cols: consultas, aprovadas, recusadas, tx, %do total consultas, %do total recusas
  const totRec={ttd:0,ap:0},totAnt={ttd:0,ap:0},totAno={ttd:0,ap:0};
  order.forEach(fx=>{if(t.rec[fx]){totRec.ttd+=t.rec[fx].ttd;totRec.ap+=t.rec[fx].ap;}if(t.ant[fx]){totAnt.ttd+=t.ant[fx].ttd;totAnt.ap+=t.ant[fx].ap;}if(t.ano[fx]){totAno.ttd+=t.ano[fx].ttd;totAno.ap+=t.ano[fx].ap;}});
  const mk=(o)=>({ttd:o?o.ttd:0,ap:o?o.ap:0,rec:(o?o.ttd-o.ap:0)});
  const rows=order.filter(fx=>{const o=t.rec[fx];return o&&o.ttd>0;}).map(fx=>({fx,rec:mk(t.rec[fx]),ant:mk(t.ant[fx]),ano:mk(t.ano[fx])}));
  const cols=[
    {key:'fx',label:'Faixa de Risco',type:'text',text:r=>r.fx},
    {key:'ttd',label:'Consultas',type:'count',num:a=>a.ttd},
    {key:'ap',label:'Aprovadas',type:'count',num:a=>a.ap},
    {key:'rec',label:'Recusadas',type:'count',num:a=>a.rec},
    {key:'tx',label:'Tx Aprov.',type:'rate',num:a=>a.ap,den:a=>a.ttd,pill:true},
    {key:'txrec',label:'% Recusada',type:'rate',num:a=>a.rec,den:a=>a.ttd},
    {key:'mixc',label:S.mode==='pct'?'% do total consultas':'Consultas',type:'part',num:a=>a.ttd,den:a=>totRec.ttd,denAnt:totAnt.ttd,denAno:totAno.ttd},
    {key:'mixr',label:S.mode==='pct'?'% do total recusas':'Recusas',type:'part',num:a=>a.rec,den:a=>totRec.rec!==undefined?totRec.rec:(totRec.ttd-totRec.ap)},
  ];
  // simpler: use metric-style custom render; build manual table for clarity with MoM/YoY per field
  let h=`<div class="card"><h3>Consultas por faixa de risco — o que passa e o que fica preso${scopeBadge(['prod','canal','cid'])}</h3><div class="csub">${safraLabel(SAF.rec)} · total de consultas, aprovadas e recusadas por faixa · taxa de aprovação e de recusa · participação no total · com MoM e YoY. Ordene/filtre nos cabeçalhos.</div>`;
  const rcols=[
    {key:'fx',label:'Faixa de Risco',type:'text',text:r=>r.fx},
    {key:'ttd',label:'Consultas',type:'count',num:a=>a.ttd},
    {key:'ap',label:'Aprovadas',type:'count',num:a=>a.ap},
    {key:'rec',label:'Recusadas',type:'count',num:a=>a.rec},
    {key:'tx',label:'Tx Aprov.',type:'rate',num:a=>a.ap,den:a=>a.ttd,pill:true},
    {key:'txrec',label:'% Recusada',type:'rate',num:a=>a.rec,den:a=>a.ttd},
    {key:'shc',label:S.mode==='pct'?'% das consultas':'Consultas',type:'part',num:a=>a.ttd,den:a=>a.ttd,_shareDen:'ttd'},
    {key:'shr',label:S.mode==='pct'?'% das recusas':'Recusas',type:'part',num:a=>a.rec,den:a=>a.rec,_shareDen:'rec'},
  ];
  // For share columns we override cellFor via denominator = total; implement custom render below
  h+=renderRiskTable('t_risk',rcols,rows,totRec,totAnt,totAno);
  // total row summary
  const txT=totRec.ttd?totRec.ap/totRec.ttd:0;
  h+=`<div class="csub" style="margin-top:8px">Total do recorte: <b>${fmtN(totRec.ttd)}</b> consultas · <b>${fmtN(totRec.ap)}</b> aprovadas (${fmtP(txT)}) · <b>${fmtN(totRec.ttd-totRec.ap)}</b> recusadas. Leitura: faixas de risco alto concentram a maior parte das recusas (o que fica preso); faixas Médio/Baixo passam quase integralmente.</div></div>`;
  return h;
}
function renderRiskTable(tid,cols,rows,totRec,totAnt,totAno){
  const st=tget(tid);
  const totals={rec:totRec,ant:totAnt,ano:totAno};
  // custom cellFor for share cols using totals
  function cf(c,row){
    if(c.type==='text')return {sv:0};
    if(c._shareDen){const denKey=c._shareDen;
      const nr=c.num(row.rec),na=c.num(row.ant),ny=c.num(row.ano);
      const dr=(denKey==='rec')?(totRec.ttd-totRec.ap):totRec.ttd;
      const da=(denKey==='rec')?(totAnt.ttd-totAnt.ap):totAnt.ttd;
      const dy=(denKey==='rec')?(totAno.ttd-totAno.ap):totAno.ttd;
      if(S.mode==='pct'){const vr=dr?nr/dr:0,va=da?na/da:0,vy=dy?ny/dy:0;return {sv:vr,disp:fmtP(vr),mom:{ok:da>0,v:vr-va,txt:fmtPP(vr-va)},yoy:{ok:dy>0,v:vr-vy,txt:fmtPP(vr-vy)}};}
      return {sv:nr,disp:fmtN(nr),mom:{ok:row.ant.ttd>0,v:nr-na,txt:fmtD(nr-na)},yoy:{ok:row.ano.ttd>0,v:nr-ny,txt:fmtD(nr-ny)}};
    }
    return cellFor(c,row);
  }
  let items=rows.map(r=>({row:r,cells:cols.map(c=>cf(c,r))}));
  // filter
  items=items.filter(it=>{for(let i=0;i<cols.length;i++){const c=cols[i];const f=st.filters[c.key];if(!f||f.val==null||f.val==='')continue;
    if(c.type==='text'){if(!String(c.text(it.row)).toLowerCase().includes(String(f.val).toLowerCase()))return false;}
    else{const scale=(c.type==='rate'||(c.type==='part'&&S.mode==='pct'))?100:1;const fv=parseFloat(String(f.val).replace(',','.'))/scale;if(isNaN(fv))continue;const v=it.cells[i].sv;if(f.op==='ge'&&!(v>=fv))return false;if(f.op==='le'&&!(v<=fv))return false;}}return true;});
  if(st.sortCol){const ci=cols.findIndex(c=>c.key===st.sortCol);if(ci>=0){const c=cols[ci];items.sort((a,b)=>{if(c.type==='text'){const av=String(c.text(a.row)).toLowerCase(),bv=String(c.text(b.row)).toLowerCase();return st.sortDir*(av<bv?-1:av>bv?1:0);}return st.sortDir*(((a.cells[ci].sv)||0)-((b.cells[ci].sv)||0));});}}
  let h=`<div class="tablewrap"><table data-tid="${tid}"><thead><tr>`;
  cols.forEach(c=>{const active=st.sortCol===c.key;const ar=active?(st.sortDir>0?'▲':'▼'):'⇅';h+=`<th class="sortable ${active?'sorton':''}" data-tid="${tid}" data-col="${c.key}">${c.label} <span class="sar">${ar}</span></th>`;});
  h+='</tr><tr class="filterrow">';
  cols.forEach(c=>{const f=st.filters[c.key]||{op:'ge',val:''};if(c.type==='text')h+=`<th><input class="fltxt" data-tid="${tid}" data-col="${c.key}" placeholder="buscar…" value="${(f.val||'').replace(/"/g,'&quot;')}"></th>`;else h+=`<th><span class="fnum"><select class="flop" data-tid="${tid}" data-col="${c.key}"><option value="ge"${f.op==='ge'?' selected':''}>≥</option><option value="le"${f.op==='le'?' selected':''}>≤</option></select><input class="flval" data-tid="${tid}" data-col="${c.key}" placeholder="—" value="${f.val||''}"></span></th>`;});
  h+='</tr></thead><tbody>';
  items.forEach(it=>{const alto=/Crítico|Altíssimo|Alto/.test(it.row.fx);h+=`<tr${alto?' style="background:#FEF3F4"':''}>`;cols.forEach((c,i)=>{if(c.type==='text')h+=`<td>${c.text(it.row)}</td>`;else h+=`<td>${cellHTML(c,it.cells[i])}</td>`;});h+='</tr>';});
  // total row
  const totRow={rec:{ttd:totRec.ttd,ap:totRec.ap,rec:totRec.ttd-totRec.ap},ant:{ttd:totAnt.ttd,ap:totAnt.ap,rec:totAnt.ttd-totAnt.ap},ano:{ttd:totAno.ttd,ap:totAno.ap,rec:totAno.ttd-totAno.ap}};
  h+=`<tr style="background:#F2F5FB;font-weight:800"><td>TOTAL</td>`;cols.slice(1).forEach(c=>{h+=`<td>${cellHTML(c,cf(c,totRow))}</td>`;});h+='</tr>';
  h+='</tbody></table></div>';return h;
}
// grouped city table with segment groups + expandable
function cityGroupedTable(cidT){
  const st=tget('t_city');
  const cols=metricCols({key:'lab',label:'Cidade',type:'text',text:r=>r.lab});
  const seg3=['Manaus','Belém','São Luís'];
  let h=`<div class="tablewrap"><table><thead><tr>`;
  cols.forEach(c=>{const active=st.sortCol===c.key;const ar=active?(st.sortDir>0?'▲':'▼'):'⇅';h+=`<th class="sortable ${active?'sorton':''}" data-tid="t_city" data-col="${c.key}">${c.label} <span class="sar">${ar}</span></th>`;});
  h+='</tr></thead><tbody>';
  const segs=['Grandes Mercados','Mercados em Desenvolvimento','Sem Cabo'];
  let gi=0;
  segs.forEach(seg=>{
    const cities=Object.entries(cidT).filter(([c,v])=>segOf(c)===seg&&v.rec.ttd>0);
    if(!cities.length){gi++;return;}
    // subtotal
    const sub={rec:M0(),ant:M0(),ano:M0()};
    cities.forEach(([c,v])=>{accAll(sub.rec,v.rec);accAll(sub.ant,v.ant);accAll(sub.ano,v.ano);});
    finM(sub.rec);finM(sub.ant);finM(sub.ano);
    const subRow={rec:sub.rec,ant:sub.ant,ano:sub.ano};
    h+=`<tr class="rowgrp" data-lvl="g" data-g="cg${gi}"><td>${seg}</td>`;
    cols.slice(1).forEach(c=>{h+=`<td>${cellHTML(c,cellFor(c,subRow))}</td>`;});
    h+='</tr>';
    // sort cities
    let cl=cities.slice();
    if(st.sortCol&&st.sortCol!=='lab'){const cc=cols.find(x=>x.key===st.sortCol);cl.sort((a,b)=>st.sortDir*((cellFor(cc,{rec:a[1].rec,ant:a[1].ant,ano:a[1].ano}).sv||0)-(cellFor(cc,{rec:b[1].rec,ant:b[1].ant,ano:b[1].ano}).sv||0)));}
    else if(st.sortCol==='lab'){cl.sort((a,b)=>st.sortDir*(a[0]<b[0]?-1:1));}
    else{cl.sort((a,b)=>b[1].rec.ttd-a[1].rec.ttd);}
    cl.forEach(([c,v])=>{const row={rec:v.rec,ant:v.ant,ano:v.ano};const hl=seg3.includes(c)?' style="background:#FFF7E6"':'';
      h+=`<tr class="rowchild rowsub" data-p="cg${gi}"${hl}><td>${c}</td>`;
      cols.slice(1).forEach(col=>{h+=`<td>${cellHTML(col,cellFor(col,row))}</td>`;});
      h+='</tr>';});
    gi++;
  });
  h+='</tbody></table></div>';
  return h;
}
function accAll(o,s){for(const k in s){if(k==='rec'||k==='tx')continue;o[k]=(o[k]||0)+s[k];}}
function anyFilterActive(){const f=filterState();return f.prod.active||f.canal.active||f.cid.active||cartActive();}
// filtered monthly series (3 safras Ago/25·Jul/26·Ago/26). Uses DD.pdv when carteira filter is active (carries exec dims).
function filteredMonthlyRno(){
  const safras=[SAF.ano,SAF.ant,SAF.rec];const by={};safras.forEach(s=>by[s]={ttd:0,ap:0,cred:0,ext:0,eleg:0,bio:0,cs:0});
  const pool=cartActive()?DD.pdv:DD.rno;
  for(const r of pool){if(!fProd(r)||!fCan(r)||!fCid(r)||!fCart(r))continue;const o=by[r.SAFRA];if(!o)continue;o.ttd+=r.ttd;o.ap+=r.ap;o.cred+=r.rec_cred;o.ext+=(r.rec_ext||0);o.eleg+=r.rec_eleg;o.bio+=r.rec_bio;o.cs+=r.rec_cs;}
  return safras.map(s=>{const o=by[s];return {SAFRA:s,ttd:o.ttd,ap:o.ap,cred:o.cred,ext:o.ext,eleg:o.eleg,bio:o.bio,cs:o.cs,tx:o.ttd?o.ap/o.ttd:0};});
}
// BR grain honors prod+canal (no city dimension)
function filteredMonthlyBr(){
  const safras=[SAF.ano,SAF.ant,SAF.rec];const by={};safras.forEach(s=>by[s]={ttd:0,ap:0,cred:0,ext:0,eleg:0,bio:0,cs:0});
  for(const r of DD.br){if(!S.prod.has(r.PROD)||!S.canais.has(r.CN))continue;const o=by[r.SAFRA];if(!o)continue;o.ttd+=r.ttd;o.ap+=r.ap;o.cred+=r.rec_cred;o.ext+=(r.rec_ext||0);o.eleg+=r.rec_eleg;o.bio+=r.rec_bio;o.cs+=r.rec_cs;}
  return safras.map(s=>{const o=by[s];return {SAFRA:s,ttd:o.ttd,ap:o.ap,cred:o.cred,ext:o.ext,eleg:o.eleg,bio:o.bio,cs:o.cs,tx:o.ttd?o.ap/o.ttd:0};});
}
// filtered risk monthly (3 safras) from risk grain, mapped to monthly_risk.order names
function filteredMonthlyRisk(){
  const order=DD.monthly_risk.order;const safras=[SAF.ano,SAF.ant,SAF.rec];
  const norm=fx=>String(fx).replace(/^\s*\d+(\.\d+)?\s*-\s*/,'').trim();
  const by={};safras.forEach(s=>{by[s]={};order.forEach(fx=>by[s][fx]={ttd:0,ap:0});});
  for(const r of DD.risk){if(!fProd(r)||!fCan(r)||!fCid(r))continue;const o=by[r.SAFRA];if(!o)continue;const fx=norm(r.FX);if(!o[fx])o[fx]={ttd:0,ap:0};o[fx].ttd+=r.ttd;o[fx].ap+=r.ap;}
  return {order,data:safras.map(s=>{const rec={SAFRA:s};order.forEach(fx=>rec[fx]=by[s][fx]);return rec;})};
}
function drawV1(){
  const filtered=anyFilterActive();
  const mr=filtered?filteredMonthlyRno():DD.monthly_rno;
  const mb=filtered?filteredMonthlyBr():DD.monthly_br;
  const labels=mr.map(m=>safraLabel(m.SAFRA));
  const rnoTx=mr.map(m=>+(m.tx*100).toFixed(1)),brTx=mb.map(m=>+(m.tx*100).toFixed(1));
  const allTx=rnoTx.concat(brTx);const lmin=Math.max(0,Math.floor(Math.min(...allTx)/5)*5-2),lmax=Math.min(100,Math.ceil(Math.max(...allTx)/5)*5+2);
  lineChart('c1a',labels,[
    {name:'RNO',color:'#E4002B',data:rnoTx},
    {name:'Brasil',color:'#2E5AAC',data:brTx}],{min:filtered?lmin:55,max:filtered?lmax:80,suffix:'%'});
  const pct=S.mode==='pct';
  const segCols=[{name:'Crédito (Rest.Int.+Score)',color:'#2E5AAC',key:'cred'},{name:'Restrição Externa',color:'#5B8FD9',key:'ext'},{name:'Elegibilidade',color:'#E8A200',key:'eleg'},{name:'Antifraude (Biometria)',color:'#B84AB0',key:'bio'},{name:'Antifraude (ClearSale)',color:'#D6293E',key:'cs'}];
  const mkSegs=arr=>segCols.map(sc=>({name:sc.name,color:sc.color,data:arr.map(m=>m[sc.key]||0)}));
  stackedBar('c1b',labels,mkSegs(mr),{pct});
  stackedBar('c1c',labels,mkSegs(mb),{pct});
  drawRiskHistory();
}
function drawRiskHistory(){
  const pct=S.mode==='pct';const filtered=anyFilterActive();
  const mrk=filtered?filteredMonthlyRisk():DD.monthly_risk;const order=mrk.order;const data=mrk.data;
  const labels=data.map(m=>safraLabel(m.SAFRA));
  const COL={'Crítico':'#8a1220','Altíssimo':'#D6293E','Alto':'#E8722A','Médio':'#E8A200','Baixo':'#5B9E4F','Baixíssimo':'#1E9E5A','Score 0/1':'#9AA6C2','Sem info':'#C0C6D4'};
  const segsFor=key=>order.map(fx=>({name:fx,color:COL[fx]||'#888',data:data.map(m=>m[fx]?m[fx][key]:0)}));
  if(document.getElementById('rh1'))stackedBar('rh1',labels,segsFor('ttd'),{pct});
  if(document.getElementById('rh2'))stackedBar('rh2',labels,segsFor('ap'),{pct});
  if(document.getElementById('rh3')){const rej=order.map(fx=>({name:fx,color:COL[fx]||'#888',data:data.map(m=>m[fx]?m[fx].ttd-m[fx].ap:0)}));stackedBar('rh3',labels,rej,{pct});}
  if(document.getElementById('rh4')){
    const series=order.filter(fx=>fx!=='Sem info'&&fx!=='Score 0/1').map(fx=>({name:fx,color:COL[fx]||'#888',data:data.map(m=>m[fx]&&m[fx].ttd?+(m[fx].ap/m[fx].ttd*100).toFixed(1):0)}));
    lineChart('rh4',labels,series,{min:0,max:100,suffix:'%'});
  }
}

/* name-similarity sort key: remove leading code prefix (e.g. C12345_) so equal/similar names sit together */
function pdvNameKey(pdv){return String(pdv||'').replace(/^\\?[\s\-]*C?\d+[_\-\s]*/i,'').replace(/^[_\-\s]+/,'').toUpperCase();}
// display label for a PDV aggregate (fantasia + code when carteirizado, else DV code)
function pdvDisp(p){return p&&p.fant?`${p.fant} <span class="mut" style="font-size:10px">· ${p.PDV}</span>`:(p?p.PDV:'');}
function pdvDispPlain(p){return p&&p.fant?`${p.fant} · ${p.PDV}`:(p?p.PDV:'');}
// small badge showing the carteirization criterion (quality group) — only when the PDV is carteirized
function cartBadge(p){
  const g=p&&p.grupo;if(!g||g==='Não Identificada')return '';
  const map={'Identificada':['ci','CNPJ','Carteira Identificada (casada por CNPJ)'],'Semelhança':['cs','Semelh.','Carteira por Semelhança de nome'],'Estimada':['ce','Estim.','Carteira Estimada (canal + município)']};
  const m=map[g];if(!m)return '';
  return `<span class="cbadge ${m[0]}" title="${m[2]}">${m[1]}</span>`;
}
/* ---------- VIEW 2 ---------- */
function v2View(){
  const st=tget('t_v2');
  let h=filterBar({})+filterTags();
  h+=`<h2 class="vtitle">Canais & PDVs — Regional Norte</h2><div class="vdesc">Aberta na dimensão de <b>canal</b> por padrão. Clique em um canal para ver seus PDVs (ordenados por semelhança de nome). Ordene/filtre nos cabeçalhos (≥/≤ e busca) ou use a busca geral. Cada campo traz MoM e YoY.</div>`;
  h+=`<div style="margin-bottom:10px;display:flex;gap:10px;flex-wrap:wrap;align-items:center"><input class="searchbox" id="v2search" placeholder="Buscar canal ou parceiro (PDV) por nome…" value="${(S.v2search||'').replace(/"/g,'&quot;')}">
      <span class="mut" style="font-size:11.5px">Dica: clique no + ao lado de um PDV para adicioná-lo à seleção e ver o subtotal.</span></div>`;
  // ===== PDV selection tags + subtotal (task 1) =====
  h+=v2SelectionBar();
  const cols=metricCols({key:'lab',label:'Canal / PDV',type:'text',text:r=>r.lab});
  const q=(S.v2search||'').trim().toLowerCase();
  const colFilterActive=cols.some(c=>{const f=st.filters[c.key];return f&&f.val!=null&&f.val!=='';});
  function passColFilters(row){for(let i=0;i<cols.length;i++){const c=cols[i];const f=st.filters[c.key];if(!f||f.val==null||f.val==='')continue;
    if(c.type==='text'){if(!String(row.lab||'').toLowerCase().includes(String(f.val).toLowerCase()))return false;}
    else{const cell=cellFor(c,row);const scale=(c.type==='rate'||(c.type==='part'&&S.mode==='pct'))?100:1;const fv=parseFloat(String(f.val).replace(',','.'))/scale;if(isNaN(fv))continue;if(f.op==='ge'&&!(cell.sv>=fv))return false;if(f.op==='le'&&!(cell.sv<=fv))return false;}}return true;}
  function sortRows(rows){if(st.sortCol){const c=cols.find(x=>x.key===st.sortCol);if(c)rows.sort((a,b)=>{if(c.type==='text')return st.sortDir*((a.lab||'')<(b.lab||'')?-1:(a.lab||'')>(b.lab||'')?1:0);return st.sortDir*((cellFor(c,a).sv||0)-(cellFor(c,b).sv||0));});}else rows.sort((a,b)=>b.rec.ttd-a.rec.ttd);return rows;}
  let h2=`<div class="card"><div class="tablewrap"><table data-tid="t_v2"><thead><tr>`;
  cols.forEach(c=>{const active=st.sortCol===c.key;const ar=active?(st.sortDir>0?'▲':'▼'):'⇅';h2+=`<th class="sortable ${active?'sorton':''}" data-tid="t_v2" data-col="${c.key}">${c.label} <span class="sar">${ar}</span></th>`;});
  h2+='</tr><tr class="filterrow">';
  cols.forEach(c=>{const f=st.filters[c.key]||{op:'ge',val:''};if(c.type==='text')h2+=`<th><input class="fltxt" data-tid="t_v2" data-col="${c.key}" placeholder="buscar…" value="${(f.val||'').replace(/"/g,'&quot;')}"></th>`;else h2+=`<th><span class="fnum"><select class="flop" data-tid="t_v2" data-col="${c.key}"><option value="ge"${f.op==='ge'?' selected':''}>≥</option><option value="le"${f.op==='le'?' selected':''}>≤</option></select><input class="flval" data-tid="t_v2" data-col="${c.key}" placeholder="—" value="${f.val||''}"></span></th>`;});
  h2+='</tr></thead><tbody>';
  // 3-level hierarchy: Group -> Channel -> PDV
  const groups=[['Canais Presenciais',PRES],['Canais Remotos',REM],['Outros Canais',outros()]];
  let anyRows=false;let gi=0;
  groups.forEach(([gname,arr])=>{
    const gt=rnoTriple(x=>x.CG===gname);
    if(gt.rec.ttd===0){gi++;return;}
    const grow={lab:gname,rec:gt.rec,ant:gt.ant,ano:gt.ano};
    // build channel rows for this group
    let chans=arr.filter(cn=>S.canais.has(cn)).map(cn=>{const t=rnoTriple(x=>x.CN===cn);return {cn,cg:gname,rec:t.rec,ant:t.ant,ano:t.ano,lab:cn};}).filter(x=>x.rec.ttd>0);
    // apply col filters + search at channel/pdv level
    const gid='g'+gi;
    let chHtml='';let groupHasMatch=false;let groupOpenByQ=false;
    chans=sortRows(chans);
    chans.forEach(ch=>{
      let pdvs=pdvAgg(x=>x.CN===ch.cn);
      pdvs.sort((a,b)=>{const ka=pdvNameKey(a.PDV),kb=pdvNameKey(b.PDV);if(ka<kb)return -1;if(ka>kb)return 1;return b.rec.ttd-a.rec.ttd;});
      pdvs.forEach(p=>p.lab=(p.fant||p.PDV)+' '+p.city);
      // search (matches fantasia, DV code, exec or city)
      let matchPdvs=pdvs;let chMatch=true;
      if(q){chMatch=ch.cn.toLowerCase().includes(q);matchPdvs=pdvs.filter(p=>((p.fant||'')+' '+p.PDV+' '+p.city+' '+(p.exec||'')).toLowerCase().includes(q));if(!chMatch&&matchPdvs.length===0)return;if(!chMatch)pdvs=matchPdvs;}
      // column filters: keep channel if it passes OR any pdv passes
      if(colFilterActive){const chPass=passColFilters(ch);const keptPdvs=pdvs.filter(passColFilters);if(!chPass&&keptPdvs.length===0)return;if(!chPass)pdvs=keptPdvs;}
      groupHasMatch=true;
      const cnid=ch.cn.replace(/[^a-zA-Z]/g,'');const openByQ=(q&&matchPdvs.length>0)||colFilterActive;if(openByQ)groupOpenByQ=true;
      chHtml+=`<tr class="rowchild rowgrp rowsub" data-lvl="c" data-p="${gid}" data-cn="${cnid}" style="background:#F7FAFF!important"${openByQ?' data-open="1"':''}><td style="padding-left:26px">${ch.cn}</td>`;cols.slice(1).forEach(c=>{chHtml+=`<td>${cellHTML(c,cellFor(c,ch))}</td>`;});chHtml+='</tr>';
      pdvs.forEach(p=>{const key=p.PDV+'|'+p.city;const on=S.v2sel.has(key);const disp=cartBadge(p)+(p.fant?`${p.fant} <span class="mut" style="font-size:10px">· ${p.PDV}</span>`:p.PDV);
        chHtml+=`<tr class="rowchild rowpdv pdvrow-${cnid}" data-p="${gid}" style="display:${openByQ?'table-row':'none'}"><td><button class="pdvadd${on?' on':''}" data-selpdv="${key.replace(/"/g,'&quot;')}" title="${on?'Remover da seleção':'Adicionar à seleção'}">${on?'✓':'+'}</button> ${disp} <span class="mut">· ${p.city}</span></td>`;cols.slice(1).forEach(c=>{chHtml+=`<td>${cellHTML(c,cellFor(c,p))}</td>`;});chHtml+='</tr>';});
    });
    if(q||colFilterActive){if(!groupHasMatch){gi++;return;}}
    anyRows=true;
    const gOpen=(q||colFilterActive)&&groupOpenByQ;
    h2+=`<tr class="rowgrp" data-lvl="g" data-g="${gid}"${gOpen?' data-open="1"':''}><td>${gname}</td>`;cols.slice(1).forEach(c=>{h2+=`<td>${cellHTML(c,cellFor(c,grow))}</td>`;});h2+='</tr>';
    // channel rows are display:none unless group open (handled by rowchild + show class)
    h2+=chHtml;
    gi++;
  });
  if(!anyRows)h2+=`<tr><td colspan="${cols.length}" style="text-align:center;color:#9AA6C2;padding:18px">Nenhum resultado com os filtros atuais.</td></tr>`;
  h2+='</tbody></table></div><div class="csub" style="margin-top:8px">Hierarquia: <b>Grupo</b> (Presenciais / Remotos / Outros) → <b>Canal</b> → <b>PDV</b>. Clique para expandir. PDVs ordenados por semelhança de nome (mesmo estabelecimento em códigos diferentes ficam adjacentes).</div></div>';
  return h+h2;
}
// aggregate a set of selected PDVs (key = PDV|city) into a triple, ignoring city filter so selected PDVs always compute
function selPdvTriple(){
  const rec=M0(),ant=M0(),ano=M0();const meta={};
  for(const r of DD.pdv){
    if(!fProd(r)||!fCan(r))continue;
    const key=r.PDV+'|'+r.CIDLAB;if(!S.v2sel.has(key))continue;
    const tgt=r.SAFRA===SAF.rec?rec:r.SAFRA===SAF.ant?ant:r.SAFRA===SAF.ano?ano:null;if(!tgt)continue;accM(tgt,r);
  }
  return {rec:finM(rec),ant:finM(ant),ano:finM(ano)};
}
function v2SelectionBar(){
  if(!S.v2sel.size)return '';
  const cols=metricCols({key:'lab',label:'Seleção de PDVs',type:'text',text:r=>r.lab});
  const t=selPdvTriple();
  const row={lab:`Subtotal — ${S.v2sel.size} PDV(s) selecionado(s)`,rec:t.rec,ant:t.ant,ano:t.ano};
  let tags='';
  [...S.v2sel].forEach(k=>{const nm=k.split('|')[0];const city=k.split('|')[1]||'';tags+=`<span class="ftag act" style="background:#EAF2FF;color:#264a86;border-color:#B9D2F5"><span class="fk">PDV</span> ${nm} <span class="mut" style="font-weight:600">· ${city}</span> <span class="fclr" data-selpdv-rm="${k.replace(/"/g,'&quot;')}" title="Remover">✕</span></span>`;});
  let h='<div class="card" style="border-left:4px solid var(--blue)"><div style="display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap"><h3>Subtotal de PDVs selecionados</h3><button class="print-btn" id="v2clear">Limpar seleção</button></div>';
  h+='<div class="filtbar" style="margin:8px 0 12px">'+tags+'</div>';
  h+='<div class="csub" style="margin-top:-6px;margin-bottom:12px">Soma dos PDVs selecionados (ignora o filtro de cidade para permitir combinar PDVs de cidades diferentes). Cada campo com MoM e YoY.</div>';
  h+=sumStaticTable(cols,[Object.assign({},row)]);
  h+='</div>';
  return h;
}
function bindV2Tools(){
  const sb=document.getElementById('v2search');if(sb){sb.oninput=()=>{S.v2search=sb.value;debouncedSearch(()=>{S._v2Focus=true;render();});};}
  if(S._v2Focus){const sb2=document.getElementById('v2search');if(sb2){sb2.focus();sb2.setSelectionRange(sb2.value.length,sb2.value.length);}S._v2Focus=false;}
  document.querySelectorAll('.pdvadd').forEach(b=>b.onclick=e=>{e.stopPropagation();const k=b.dataset.selpdv;if(S.v2sel.has(k))S.v2sel.delete(k);else S.v2sel.add(k);render();});
  document.querySelectorAll('[data-selpdv-rm]').forEach(b=>b.onclick=e=>{e.stopPropagation();S.v2sel.delete(b.dataset.selpdvRm);render();});
  const cl=document.getElementById('v2clear');if(cl)cl.onclick=()=>{S.v2sel.clear();render();};
}
// PDV aggregates as array of triples with meta
// memoized full PDV aggregation (no extra predicate). Cache invalidated when product/channel/city filters change.
let _pdvCache={sig:null,all:null};
function pdvSig(){return S.prod.size+':'+[...S.prod].sort().join(',')+'|'+S.canais.size+':'+[...S.canais].sort().join(',')+'|'+S.cidades.size+':'+[...S.cidades].sort().join(',')+'|E'+S.execs.size+'G'+S.gns.size+'F'+S.gfils.size+'R'+S.gers.size+'L'+S.cartLevel;}
function invalidatePdvCache(){_pdvCache.sig=null;}
function pdvAggAll(){
  const sig=pdvSig();
  if(_pdvCache.sig===sig&&_pdvCache.all)return _pdvCache.all;
  const rec={},ant={},ano={};
  for(const r of DD.pdv){
    if(!fProd(r)||!fCan(r)||!fCid(r)||!fCart(r))continue;
    const key=r.PDV+'|'+r.CIDLAB;const tgt=r.SAFRA===SAF.rec?rec:r.SAFRA===SAF.ant?ant:r.SAFRA===SAF.ano?ano:null;if(!tgt)continue;
    if(!tgt[key]){tgt[key]=M0();tgt[key]._pdv=r.PDV;tgt[key]._city=r.CIDLAB;tgt[key]._cn=r.CN;tgt[key]._seg=r.SEG;const _eh=effHier(r);tgt[key]._exec=_eh.exec;tgt[key]._gn=_eh.gn;tgt[key]._gfil=_eh.gfil;tgt[key]._ger=_eh.ger;tgt[key]._fant=_eh.fant;tgt[key]._lbl=_eh.fant?(_eh.fant+' · '+r.PDV):r.PDV;tgt[key]._grp=_eh.grupo;}
    accM(tgt[key],r);
  }
  const keys=new Set([...Object.keys(rec),...Object.keys(ant),...Object.keys(ano)]);
  const out=[];
  keys.forEach(k=>{const rr=finM(rec[k]||M0());const meta=rec[k]||ant[k]||ano[k];
    out.push({PDV:meta._pdv,city:meta._city,cn:meta._cn,seg:meta._seg,exec:meta._exec,gn:meta._gn,gfil:meta._gfil,ger:meta._ger,fant:meta._fant,lbl:meta._lbl,grupo:meta._grp,rec:rr,ant:finM(ant[k]||M0()),ano:finM(ano[k]||M0())});});
  _pdvCache={sig,all:out.filter(x=>x.rec.ttd>0)};
  return _pdvCache.all;
}
function pdvAgg(extra){
  if(!extra)return pdvAggAll();
  // extra present (channel filter etc.) — recompute honoring the raw-row predicate
  const rec={},ant={},ano={};
  for(const r of DD.pdv){
    if(!fProd(r)||!fCan(r)||!fCid(r)||!fCart(r))continue;if(!extra(r))continue;
    const key=r.PDV+'|'+r.CIDLAB;const tgt=r.SAFRA===SAF.rec?rec:r.SAFRA===SAF.ant?ant:r.SAFRA===SAF.ano?ano:null;if(!tgt)continue;
    if(!tgt[key]){tgt[key]=M0();tgt[key]._pdv=r.PDV;tgt[key]._city=r.CIDLAB;tgt[key]._cn=r.CN;tgt[key]._seg=r.SEG;const _eh=effHier(r);tgt[key]._exec=_eh.exec;tgt[key]._gn=_eh.gn;tgt[key]._gfil=_eh.gfil;tgt[key]._ger=_eh.ger;tgt[key]._fant=_eh.fant;tgt[key]._lbl=_eh.fant?(_eh.fant+' · '+r.PDV):r.PDV;tgt[key]._grp=_eh.grupo;}
    accM(tgt[key],r);
  }
  const keys=new Set([...Object.keys(rec),...Object.keys(ant),...Object.keys(ano)]);
  const out=[];
  keys.forEach(k=>{const rr=finM(rec[k]||M0());const meta=rec[k]||ant[k]||ano[k];
    out.push({PDV:meta._pdv,city:meta._city,cn:meta._cn,seg:meta._seg,exec:meta._exec,gn:meta._gn,gfil:meta._gfil,ger:meta._ger,fant:meta._fant,lbl:meta._lbl,grupo:meta._grp,rec:rr,ant:finM(ant[k]||M0()),ano:finM(ano[k]||M0())});});
  return out.filter(x=>x.rec.ttd>0);
}
function bindGroups(){
  // show every direct child of the group EXCEPT PDV rows (those are toggled by their own channel row).
  // This covers both the 3-level channel table (data-lvl="c") and simple 2-level tables (city rows .rowsub).
  function openGroup(r){r.classList.add('open');document.querySelectorAll(`.rowchild[data-p="${r.dataset.g}"]`).forEach(ch=>{if(!ch.classList.contains('rowpdv'))ch.classList.add('show');});}
  function closeGroup(r){r.classList.remove('open');
    // hide channel rows and any expanded pdvs under them
    document.querySelectorAll(`.rowchild[data-p="${r.dataset.g}"]`).forEach(ch=>{ch.classList.remove('show');});
    document.querySelectorAll(`.rowgrp[data-lvl="c"][data-p="${r.dataset.g}"]`).forEach(c=>{c.classList.remove('open');const id=c.dataset.cn;if(id)document.querySelectorAll('.pdvrow-'+id).forEach(p=>p.style.display='none');});
  }
  document.querySelectorAll('.rowgrp[data-lvl="g"]').forEach(r=>{
    if(r.dataset.open==='1')openGroup(r);
    r.onclick=()=>{if(r.classList.contains('open'))closeGroup(r);else openGroup(r);};
  });
  document.querySelectorAll('.rowgrp[data-lvl="c"]').forEach(r=>{
    if(r.dataset.open==='1'){r.classList.add('open');const id=r.dataset.cn;document.querySelectorAll('.pdvrow-'+id).forEach(p=>p.style.display='table-row');}
    r.onclick=e=>{e.stopPropagation();r.classList.toggle('open');const id=r.dataset.cn;document.querySelectorAll('.pdvrow-'+id).forEach(p=>p.style.display=r.classList.contains('open')?'table-row':'none');};
  });
}
/* ---------- VIEW 3 (Diária) ---------- */
const V3WK=[[1,7],[8,14],[15,21],[22,28]];
// last week that has ANY data (e.g., 22-27 -> week index 3), regardless of completeness
function lastWeekWithData(days){let last=0;for(let w=0;w<V3WK.length;w++){for(let d=V3WK[w][0];d<=V3WK[w][1];d++){if(days[d]&&days[d].ttd){last=w;}}}return last;}
function v3View(){
  const pct=S.mode==='pct';const isLine=S.v3mode==='linha';
  if(S.v3weeks===null){const rnoDays=dailyAgg('RNO');S.v3weeks=new Set([lastWeekWithData(rnoDays)]);}
  let h=filterBar({})+filterTags();
  h+=`<h2 class="vtitle">Visão Diária — Motivo de Recusa (base 100%)</h2><div class="vdesc">${isLine?'Linha diária por motivo de recusa ao longo do mês.':'Dias agrupados de 7 em 7; abre a última semana com dados e as colunas de média.'} Motivos: Crédito (Rest. Interna+Score) · Restrição Externa · Elegibilidade · Antif. Biometria · Antif. ClearSale. ${pct?'Modo %.':'Modo volume.'} Reflete filtros.</div>`;
  // view mode toggle (tabela / linha)
  h+=`<div style="margin-bottom:14px;display:flex;gap:12px;flex-wrap:wrap;align-items:center">
      <span class="toggle" id="v3vmode"><button data-vm="tabela" class="${!isLine?'on':''}">Tabela</button><button data-vm="linha" class="${isLine?'on':''}">Linhas</button></span>`;
  if(!isLine)h+=`<button class="btn sec" id="v3all">Abrir todas as semanas</button><button class="btn sec" id="v3none">Fechar todas</button><span class="mut" style="font-size:12px">ou clique em ▸/▾ no cabeçalho de cada semana</span>`;
  h+=`</div>`;
  const blocks=[['Brasil','BR'],['Regional Norte (RNO)','RNO']];
  ['Manaus','Belém','São Luís'].filter(c=>S.cidades.has(c)).forEach(c=>blocks.push([c,'CID:'+c]));
  if(isLine){blocks.forEach(([lab,sc])=>{h+=dailyLineBlock(lab,sc,pct);});}
  else{blocks.forEach(([lab,sc])=>{h+=dailyBlock(lab,sc,pct);});}
  h+='<div class="card"><h3>Tendência diária — Antifraude ClearSale (RNO)</h3><div class="csub">Quantidade de reprovas por ClearSale (flag Serasa) por dia · reflete filtros</div><div class="chartbox"><div id="c3" style="width:100%;height:100%"></div></div></div>';
  return h;
}
// line chart per scope with 5 motivo series across the days
function dailyLineBlock(lab,scope,pct){
  const id='dl_'+scope.replace(/[^a-zA-Z]/g,'');
  const note=scope==='BR'?' <span class="mut">(base diária BR sem filtro de produto/cidade)</span>':'';
  return `<div class="card"><h3>${lab}${note}</h3><div class="csub">${pct?'% sobre o total de consultas do dia':'Quantidade por dia'} · uma linha por motivo</div><div class="chartbox" style="height:320px"><div id="${id}" style="width:100%;height:100%"></div></div></div>`;
}
function drawV3Lines(){
  const pct=S.mode==='pct';
  const mets=[['Crédito','cred','#2E5AAC'],['Rest. Externa','ext','#5B8FD9'],['Elegibilidade','eleg','#E8A200'],['Antif. Biometria','bio','#B84AB0'],['Antif. ClearSale','cs','#D6293E']];
  const scopes=[['Brasil','BR'],['Regional Norte (RNO)','RNO']];
  ['Manaus','Belém','São Luís'].filter(c=>S.cidades.has(c)).forEach(c=>scopes.push([c,'CID:'+c]));
  scopes.forEach(([lab,scope])=>{
    const id='dl_'+scope.replace(/[^a-zA-Z]/g,'');if(!document.getElementById(id))return;
    const days=dailyAgg(scope);const dl=[];for(let i=1;i<=27;i++){if(days[i]&&days[i].ttd)dl.push(i);}
    const labels=dl.map(String);
    const series=mets.map(([nm,k,c])=>({name:nm,color:c,data:dl.map(d=>{const o=days[d];if(!o||!o.ttd)return 0;return pct?+(o[k]/o.ttd*100).toFixed(1):o[k];})}));
    const maxv=Math.max(1,...series.flatMap(s=>s.data));
    lineChart(id,labels,series,{min:0,max:pct?Math.min(100,Math.ceil(maxv/5)*5+2):Math.ceil(maxv/10)*10,suffix:pct?'%':''});
  });
}
function bindV3Week(){
  document.querySelectorAll('#v3vmode button').forEach(b=>b.onclick=()=>{S.v3mode=b.dataset.vm;render();});
  const a=document.getElementById('v3all');if(a)a.onclick=()=>{S.v3weeks=new Set([0,1,2,3]);render();};
  const n=document.getElementById('v3none');if(n)n.onclick=()=>{S.v3weeks=new Set();render();};
  document.querySelectorAll('.wktog').forEach(b=>b.onclick=()=>{const w=+b.dataset.w;if(S.v3weeks.has(w))S.v3weeks.delete(w);else S.v3weeks.add(w);render();});
}
function dailyAgg(scope){
  const days={};
  const z=()=>({cred:0,ext:0,eleg:0,bio:0,cs:0,ttd:0});
  if(scope==='BR'){for(const r of DD.brd){if(!S.canais.has(r.CN))continue;const d=r.DIA;if(!days[d])days[d]=z();days[d].cred+=r.cred;days[d].ext+=(r.ext||0);days[d].eleg+=r.eleg;days[d].bio+=(r.bio||0);days[d].cs+=r.cs;days[d].ttd+=r.ttd;}return days;}
  const cf=scope.startsWith('CID:')?scope.slice(4):null;
  for(const r of DD.daily){if(!S.prod.has(r.PROD))continue;if(!S.canais.has(r.CN))continue;if(cf){if(r.CIDLAB!==cf)continue;}else{if(!S.cidades.has(r.CIDLAB))continue;}const d=r.DIA;if(!days[d])days[d]=z();days[d].cred+=r.cred;days[d].ext+=(r.ext||0);days[d].eleg+=r.eleg;days[d].bio+=(r.bio||0);days[d].cs+=r.cs;days[d].ttd+=r.ttd;}
  return days;
}
function dailyBlock(lab,scope,pct){
  const days=dailyAgg(scope);const DMAX=27;const wk=V3WK;
  const mets=[['Crédito (Rest.Int.+Score)','cred'],['Restrição Externa','ext'],['Elegibilidade','eleg'],['Antif. Biometria','bio'],['Antif. ClearSale','cs'],['Total','ttd']];
  const dayVisible=w=>S.v3weeks.has(w);
  const weekHasData=w=>{for(let d=wk[w][0];d<=wk[w][1];d++)if(days[d]&&days[d].ttd)return true;return false;};
  const note=scope==='BR'?' <span class="mut">(base diária BR sem filtro de produto/cidade)</span>':'';
  let h=`<div class="card"><h3>${lab}${note}</h3><div class="csub">${pct?'% sobre o total de consultas do dia':'Quantidade'} · médias por semana · ▸/▾ abre/fecha cada semana</div><div class="scroll-x"><table><thead><tr><th>Motivo</th>`;
  for(let w=0;w<wk.length;w++){const hd=weekHasData(w);const open=dayVisible(w);
    if(open){for(let d=wk[w][0];d<=wk[w][1];d++){if(d<=31&&days[d]&&days[d].ttd)h+=`<th>${d}</th>`;}}
    const tog=hd?`<button class="wktog" data-w="${w}" title="abrir/fechar semana" style="border:none;background:none;cursor:pointer;color:var(--claro);font-weight:800;font-size:11px">${open?'▾':'▸'}</button> `:'';
    h+=`<th class="wk">${tog}Méd ${wk[w][0]}-${wk[w][1]}</th>`;}
  h+='</tr></thead><tbody>';
  mets.forEach(([ml,mk])=>{h+=`<tr><td><b>${ml}</b></td>`;
    for(let w=0;w<wk.length;w++){let sum=0,cnt=0;
      for(let d=wk[w][0];d<=wk[w][1];d++){if(d>31)continue;const rec2=days[d];const has=rec2&&d<=DMAX&&rec2.ttd>0;
        if(dayVisible(w)){if(!has)continue; // skip empty day columns entirely
          if(mk==='ttd'){h+=`<td>${pct?'100%':fmtN(rec2.ttd)}</td>`;sum+=rec2.ttd;cnt++;}else{const v=rec2[mk];if(pct){h+=heatCell(v/rec2.ttd);sum+=v/rec2.ttd;}else{h+=`<td>${fmtN(v)}</td>`;sum+=v;}cnt++;}}
        else{if(has){if(mk==='ttd'){sum+=rec2.ttd;cnt++;}else{const v=rec2[mk];if(pct)sum+=v/rec2.ttd;else sum+=v;cnt++;}}}
      }
      let wv;if(mk==='ttd')wv=pct?'100%':fmtN(sum);else wv=pct?((cnt?sum/cnt:0)*100).toFixed(1).replace('.',',')+'%':fmtN(sum);
      h+=`<td class="wk">${wv}</td>`;}
    h+='</tr>';});
  h+='</tbody></table></div></div>';return h;
}
function heatCell(p){let bg='#E7F6EE',col='#1a7a45';if(p>=0.30){bg='#F8C9CF';col='#8a1220';}else if(p>=0.18){bg='#FBE7C7';col='#8a5a00';}else if(p>=0.08){bg='#FCF3DC';col='#7a6600';}return `<td class="heat" style="background:${bg};color:${col}">${(p*100).toFixed(1).replace('.',',')}%</td>`;}
function drawV3(){const days=dailyAgg('RNO');const l=[],d=[];for(let i=1;i<=27;i++){if(days[i]){l.push(i);d.push(days[i].cs);}}vBars('c3',l,d,{colors:d.map(v=>v>=12?'#D6293E':'#E4002B')});}

/* ---------- VIEW 4 (PDVs) ---------- */
const V4CRITS={credito:['Piores por Crédito (Rest. Int.+Score)','Maior % de recusas por Rest. Interna+Score','cred'],
 externa:['Piores por Restrição Externa','Maior % de recusas por Restrição Externa (bureaus)','ext'],
 fraude:['Piores por Antifraude','Maior % antifraude (Biometria+ClearSale)','anti'],
 clearsale:['Piores por Antif. ClearSale','Maior % de flags ClearSale','cs'],
 volume:['Piores por Volume','Maior nº de consultas','vol'],
 taxa:['Piores por Taxa de aprovação','Menor taxa de aprovação','tx'],
 mix:['Pior mix de clientes','Maior % de clientes de risco alto','mix']};
function v4View(){
  let h=filterBar({})+filterTags();
  h+=`<h2 class="vtitle">PDVs — DV_EQUIPE_VENDA</h2><div class="vdesc">Todos os indicadores da Visão 1, por PDV, com MoM e YoY. Escolha uma categoria de risco, ordene/filtre colunas ou busque um parceiro específico. ${safraLabel(SAF.rec)}.</div>`;
  h+='<div style="margin-bottom:14px"><input class="searchbox" id="pdvSearch" placeholder="Buscar por Nome Fantasia, DV_EQUIPE_VENDA, Executivo, cidade ou canal…" value="'+(S.pdvSearch||'').replace(/"/g,'&quot;')+'"></div>';
  h+='<div class="subtabs" id="v4tabs">';
  Object.entries(V4CRITS).forEach(([k,v])=>h+=`<span class="subtab ${S.v4crit===k?'on':''}" data-k="${k}">${v[0]}</span>`);
  h+='</div>';
  const crit=V4CRITS[S.v4crit];
  const q=(S.pdvSearch||'').trim().toLowerCase();
  const searching=q.length>0;
  h+=`<div class="note"><b>Critério ativo:</b> ${crit[1]}. Exibindo <b>todos</b> os PDVs, ordenados pelo critério escolhido (do pior para o melhor). ${searching?'<b>Busca ativa:</b> filtrando por termo em nome/DV/executivo/cidade/canal.':'Use a busca ou os filtros de coluna para refinar.'}</div>`;
  // compute aggregation ONCE (memoized)
  const allPdv=pdvAggAll();
  const totPDV=allPdv.length;
  let list=allPdv.slice();
  if(q)list=list.filter(p=>((p.fant||'')+' '+p.PDV+' '+p.city+' '+p.cn+' '+(p.exec||'')+' '+(p.gn||'')).toLowerCase().includes(q));
  const key=crit[2];
  // criterion ranking (worst -> best). ties broken by volume.
  function critScore(p){
    const rc=p.rec.rec||1;
    if(key==='cred')return p.rec.rec_cred/rc;
    if(key==='ext')return p.rec.rec_ext/rc;
    if(key==='anti')return p.rec.rec_anti/rc;
    if(key==='cs')return p.rec.rec_cs/rc;
    if(key==='vol')return p.rec.ttd;
    if(key==='tx')return -p.rec.tx;   // pior taxa primeiro
    if(key==='mix')return p.rec.ttd?p.rec.cons_ra/p.rec.ttd:0;
    return 0;
  }
  list.sort((a,b)=>critScore(b)-critScore(a)||b.rec.ttd-a.rec.ttd);
  const ranked=list;
  const stp=tget('t_pdv');
  const worst=ranked[0];
  if(worst){h+='<div class="kpis">';
    h+=`<div class="kpi r"><div class="lab">PDV mais ofensor</div><div class="val" style="font-size:16px">${worst.fant||worst.PDV}</div><div class="sub">${worst.city} · ${worst.cn}${worst.exec?' · '+worst.exec:''} · ${fmtN(worst.rec.ttd)} consultas · Tx ${fmtP(worst.rec.tx)}</div></div>`;
    h+=`<div class="kpi a"><div class="lab">PDVs exibidos</div><div class="val">${fmtN(list.length)}</div><div class="sub">de ${fmtN(totPDV)} PDVs com consultas no recorte</div></div>`;
    const totAnti=list.reduce((s,p)=>s+p.rec.rec_anti,0);const totBio=list.reduce((s,p)=>s+p.rec.rec_bio,0);const totCS=list.reduce((s,p)=>s+p.rec.rec_cs,0);
    h+=`<div class="kpi b"><div class="lab">Antifraude nos PDVs</div><div class="val">${fmtN(totAnti)}</div><div class="sub">Biometria ${fmtN(totBio)} + ClearSale ${fmtN(totCS)}</div></div>`;
    h+='</div>';}
  // table order: honour column-header sort if the user clicked one; otherwise keep criterion order
  let display=stp.sortCol?list:ranked;
  const cols=[{key:'rk',label:'#',type:'text',cls:'c-rk',text:r=>`<span class="rankn ${r._rk===1?'':(r._rk===2?'g2':'g3')}" style="${r._rk>3?'background:#C7CFDC':''}">${r._rk}</span>`},
    {key:'pdv',label:'PDV (Fantasia / DV)',type:'text',cls:'c-pdv',text:r=>cartBadge(r)+(r.fant?`${r.fant} <span class="mut cdim">· ${r.PDV}</span>`:`<span class="cdim2">${r.PDV}</span>`)},
    {key:'exec',label:'Executivo',type:'text',cls:'c-exec',text:r=>r.exec&&r.exec!==NC?r.exec:'<span class="mut">—</span>'},
    {key:'city',label:'Cidade',type:'text',cls:'c-city',text:r=>r.city},
    {key:'cn',label:'Canal',type:'text',cls:'c-cn',text:r=>r.cn},
    ...metricCols({key:'seg',label:'Segmento',type:'text',text:r=>r.seg}).slice(1)];
  // assign rank number by criterion order
  ranked.forEach((p,i)=>p._rk=i+1);
  const subtxt=`${display.length} PDVs · <b>ordenados por ${crit[0].replace(/^Piores por |^Pior /,'').toLowerCase()}</b> (pior → melhor) · clique num cabeçalho para reordenar · ${S.mode==='pct'?'percentuais':'volumes'}`;
  h+=`<div class="card"><h3>PDVs — ${searching?'Busca ('+crit[0]+')':crit[0]}</h3><div class="csub">${subtxt}</div>`;
  h+=renderTable('t_pdv',cols,display,{limit:9999,compact:true,topscroll:true,hl:(r)=>{if(key==='tx'&&r.rec.tx<0.4)return '#FBE7E7';if((key==='anti'||key==='cs')&&(r.rec.rec_anti/r.rec.rec)>0.4)return '#FBE7E7';return '';}});
  h+='<div class="csub" style="margin-top:8px">A coluna <b>#</b> reflete o ranking pelo critério ativo. Clique num cabeçalho para reordenar por qualquer métrica; use a busca ou os filtros ≥/≤ para refinar.</div></div>';
  return h;
}
let _searchTimer=null;
function debouncedSearch(setter,ms){clearTimeout(_searchTimer);_searchTimer=setTimeout(()=>{setter();},ms||160);}
function bindV4(){
  document.querySelectorAll('#v4tabs .subtab').forEach(el=>el.onclick=()=>{S.v4crit=el.dataset.k;render();});
  const sb=document.getElementById('pdvSearch');
  if(sb){sb.oninput=()=>{S.pdvSearch=sb.value;debouncedSearch(()=>{S._pdvFocus=true;render();});};}
  bindDualScroll();
}
// sync top proxy scrollbar with the table body scrollbar
function bindDualScroll(){
  document.querySelectorAll('.dualscroll').forEach(ds=>{
    const top=ds.querySelector('.ds-top'),body=ds.querySelector('.ds-body'),spacer=ds.querySelector('.ds-spacer'),tbl=body.querySelector('table');
    if(!top||!body||!tbl)return;
    const setW=()=>{spacer.style.width=tbl.scrollWidth+'px';};
    setW();window.addEventListener('resize',setW);
    let lock=false;
    top.addEventListener('scroll',()=>{if(lock)return;lock=true;body.scrollLeft=top.scrollLeft;lock=false;});
    body.addEventListener('scroll',()=>{if(lock)return;lock=true;top.scrollLeft=body.scrollLeft;lock=false;});
  });
}
function restorePdvFocus(){if(S._pdvFocus){const sb=document.getElementById('pdvSearch');if(sb){sb.focus();sb.setSelectionRange(sb.value.length,sb.value.length);}S._pdvFocus=false;}}

/* ---------- VIEW 5 ---------- */
function qcard(id,title,sub){
  return `<div class="card"><div style="display:flex;justify-content:space-between;align-items:flex-start;gap:8px"><div><h3>${title}</h3><div class="csub">${sub}</div></div>`+
    `<div class="qtools"><button class="qbtn ${S.insLabels?'on':''}" data-act="labels" title="Rótulos dos top 5 ofensores">Top 5</button><button class="qbtn" data-act="zoom" data-chart="${id}" title="Ampliar">Ampliar</button><button class="qbtn" data-act="export" data-chart="${id}" title="Exportar PNG"> PNG</button></div></div>`+
    `<div class="chartbox" style="height:380px"><div id="${id}" style="width:100%;height:100%"></div></div></div>`;
}
function v5View(){
  const rno=rnoTriple(),br=brTriple();const r=rno.rec;
  const cidT=groupTriples(DD.rno,x=>x.CIDLAB,x=>fProd(x)&&fCan(x)&&fCid(x));
  const arr=Object.entries(cidT).filter(([k,v])=>v.rec.ttd>30).sort((a,b)=>b[1].rec.tx-a[1].rec.tx);
  let h=filterBar({})+filterTags();
  h+='<h2 class="vtitle">Insights adaptativos</h2><div class="vdesc">Recalculam conforme os filtros de cidade, produto e canal. Quadrantes com rótulos de ofensores, ampliação e exportação PNG.</div>';
  // ===== QUADRANTS FIRST =====
  h+='<h3 class="vtitle" style="margin-top:4px">Quadrantes — Cidades</h3><div class="vdesc">Bolha = cidade; tamanho ∝ volume. Botão “Top 5” rotula os principais ofensores; “Ampliar” abre em tela cheia com rótulos laterais; “PNG” exporta.</div>';
  h+='<div class="grid2">'+
     qcard('qc1','Momentum: MoM × YoY (taxa)','x = MoM (p.p.) · y = YoY (p.p.) · sup-direito = melhora consistente')+
     qcard('qc2','Volume × Taxa de aprovação','x = consultas · y = taxa (%) · inf-direito = praça grande com baixa aprovação')+
     qcard('qc3','Antifraude × Taxa','x = % antifraude (Biometria+ClearSale) · y = taxa (%) · inf-direito = antifraude alto + baixa aprovação')+
     qcard('qc4','Mix de risco × Taxa','x = % risco alto · y = taxa (%) · dependência do perfil de risco')+
     '</div>';
  h+='<h3 class="vtitle" style="margin-top:6px">Quadrantes — PDVs (base ≥ 20)</h3><div class="vdesc">Bolha = PDV; tamanho ∝ volume. Ajuda a achar PDVs ofensores e focos de antifraude.</div>';
  h+='<div class="grid2">'+
     qcard('qp1','PDVs: MoM × YoY (taxa)','x = MoM (p.p.) · y = YoY (p.p.)')+
     qcard('qp2','PDVs: Antifraude × Taxa','x = % antifraude (Bio+ClearSale) · y = taxa (%) · vermelho = tem flag ClearSale')+
     '</div>';
  // ===== INSIGHT CARDS: 3 rows x 3 cols =====
  const ins=[];
  ins.push(['a','Gap RNO vs Brasil',`RNO aprova ${fmtP(r.tx)} vs ${fmtP(br.rec.tx)} do Brasil (${fmtPP(r.tx-br.rec.tx)}). MoM ${fmtPP(r.tx-rno.ant.tx)} · YoY ${fmtPP(r.tx-rno.ano.tx)}.`]);
  const csS=r.rec?r.rec_cs/r.rec:0;
  ins.push([csS>0.02?'r':'g','Antifraude (ClearSale)',`Flags ClearSale são ${fmtP(csS)} das recusas (${fmtN(r.rec_cs)}). MoM ${fmtD(r.rec_cs-rno.ant.rec_cs)} · YoY ${fmtD(r.rec_cs-rno.ano.rec_cs)}.`]);
  if(arr.length){const w=arr[arr.length-1],b=arr[0];
    ins.push(['r','Pior cidade do recorte',`${w[0]} aprova ${fmtP(w[1].rec.tx)} (${fmtN(w[1].rec.ttd)} consultas).`]);
    ins.push(['g','Melhor cidade do recorte',`${b[0]} lidera com ${fmtP(b[1].rec.tx)} de aprovação no recorte atual.`]);}
  else{ins.push(['a','Cidades','Sem cidades suficientes no recorte.']);ins.push(['a','Cidades','—']);}
  const bioS=r.rec?r.rec_bio/r.rec:0;
  ins.push([bioS>0.20?'a':'g','Antifraude (Biometria)',`Biometria não concluída é ${fmtP(bioS)} das recusas — ${bioS>0.20?'perda evitável relevante; pode indicar dificuldade técnica ou fraude potencial.':'sob controle.'}`]);
  const raS=r.rec?r.rec_ra/r.rec:0;
  ins.push([raS>0.5?'a':'g','Perfil de risco das recusas',`${fmtP(raS)} das recusas são de clientes de risco alto (Crítico/Altíssimo/Alto).`]);
  const pv=pdvAgg().filter(p=>p.rec.ttd>=20).sort((a,b)=>a.rec.tx-b.rec.tx)[0];
  ins.push(['r','PDV mais crítico por taxa',pv?`${pdvDispPlain(pv)} (${pv.city}, ${pv.cn}) com ${fmtP(pv.rec.tx)} em ${fmtN(pv.rec.ttd)} consultas.`:'Sem PDV com base ≥20 no recorte.']);
  ins.push(['g','Recorte ativo',`Produtos: ${[...S.prod].map(p=>PLAB[p]).join(', ')}. Cidades: ${S.cidades.size}/${allCidades().length}. Canais: ${S.canais.size}/${DD.canais_norm.length}.`]);
  // ensure exactly 9 cards
  while(ins.length<9)ins.push(['g','—','—']);
  const nine=ins.slice(0,9);
  h+='<h3 class="vtitle" style="margin-top:6px">Achados</h3><div class="vdesc">Nove achados em três fileiras.</div>';
  h+='<div class="insgrid">'+nine.map(([c,t,p])=>insCard(c,t,p)).join('')+'</div>';
  h+='<div class="card"><h3>Radar do recorte</h3><div class="csub">Indicadores-chave (%)</div><div class="chartbox"><div id="c5" style="width:100%;height:100%"></div></div></div>';
  return h;
}
function insCard(cls,t,p){const tg={g:'Positivo',a:'Atenção',r:'Crítico'}[cls];return `<div class="ins ${cls} inscard"><span class="tag ${cls}">${tg}</span><b>${t}</b><p>${p}</p></div>`;}
function median(a){if(!a.length)return 0;const s=a.slice().sort((x,y)=>x-y);const m=Math.floor(s.length/2);return s.length%2?s[m]:(s[m-1]+s[m])/2;}
function segColor(seg){return seg==='Grandes Mercados'?'#E4002B':seg==='Mercados em Desenvolvimento'?'#2E5AAC':'#E8A200';}
function drawV5(){
  const rno=rnoTriple(),r=rno.rec;
  hBar('c5',['% Rest.Int+Score','% Rest. Externa','% Elegibilidade','% Antif. Biometria','% Antif. ClearSale','% Aprovação'],[r.rec_cred/r.rec*100,r.rec_ext/r.rec*100,r.rec_eleg/r.rec*100,r.rec_bio/r.rec*100,r.rec_cs/r.rec*100,r.tx*100].map(x=>+(x||0).toFixed(1)),['#2E5AAC','#5B8FD9','#E8A200','#B84AB0','#D6293E','#1E9E5A'],{max:100,suffix:'%'});
  // City quadrants
  const cidT=groupTriples(DD.rno,x=>x.CIDLAB,x=>fProd(x)&&fCan(x)&&fCid(x));
  const cities=Object.entries(cidT).filter(([k,v])=>v.rec.ttd>=30).map(([c,v])=>{
    const mom=(v.rec.tx-(v.ant.ttd?v.ant.tx:v.rec.tx))*100, yoy=(v.rec.tx-(v.ano.ttd?v.ano.tx:v.rec.tx))*100;
    const seg=segOf(c);return {name:c,text:c,seg,color:segColor(seg),
      rr:Math.max(4,Math.min(20,Math.sqrt(v.rec.ttd)/6)),
      mom,yoy,vol:v.rec.ttd,tx:v.rec.tx*100,anti:v.rec.rec?v.rec.rec_anti/v.rec.rec*100:0,mix:v.rec.ttd?v.rec.cons_ra/v.rec.ttd*100:0};});
  const medTx=median(cities.map(c=>c.tx));
  const medW=median(cities.map(c=>c.tx)); // worst = lowest tx
  scatter('qc1',cities.map(c=>({x:c.mom,y:c.yoy,label:c.name,text:c.name,color:c.color,r:c.rr})),{x0:0,y0:0,xlabel:'MoM (p.p.)',ylabel:'YoY (p.p.)',qlabels:{tr:'melhora MoM+YoY',tl:'só YoY',br:'só MoM',bl:'piora ambos'},offenderScore:p=>-(p.x+p.y)});
  scatter('qc2',cities.map(c=>({x:c.vol,y:c.tx,label:c.name,text:c.name,color:c.color,r:c.rr})),{y0:medTx,xlabel:'Consultas (volume)',ylabel:'Taxa de aprovação',ysuffix:'%',qlabels:{tr:'grande + alta',tl:'pequena + alta',br:'grande + baixa ⚠',bl:'pequena + baixa'},offenderScore:p=>p.x*(100-p.y)});
  scatter('qc3',cities.map(c=>({x:c.anti,y:c.tx,label:c.name,text:c.name,color:c.color,r:c.rr})),{y0:medTx,x0:median(cities.map(c=>c.anti)),xlabel:'% recusas antifraude (Bio+ClearSale)',ylabel:'Taxa de aprovação',xsuffix:'%',ysuffix:'%',qlabels:{tr:'antifraude alto/tx alta',tl:'',br:'antifraude alto + tx baixa ⚠',bl:''},offenderScore:p=>p.x+(100-p.y)});
  scatter('qc4',cities.map(c=>({x:c.mix,y:c.tx,label:c.name,text:c.name,color:c.color,r:c.rr})),{y0:medTx,x0:median(cities.map(c=>c.mix)),xlabel:'% clientes risco alto',ylabel:'Taxa de aprovação',xsuffix:'%',ysuffix:'%',qlabels:{tr:'risco alto/tx alta',tl:'risco baixo/tx alta',br:'risco alto/tx baixa',bl:''},offenderScore:p=>p.x+(100-p.y)});
  // PDV quadrants
  const pdvs=pdvAgg().filter(p=>p.rec.ttd>=20).map(p=>{
    const mom=(p.rec.tx-(p.ant.ttd?p.ant.tx:p.rec.tx))*100,yoy=(p.rec.tx-(p.ano.ttd?p.ano.tx:p.rec.tx))*100;
    return {name:(p.fant||p.PDV),color:segColor(p.seg),rr:Math.max(3,Math.min(16,Math.sqrt(p.rec.ttd)/5)),
      mom,yoy,tx:p.rec.tx*100,anti:p.rec.rec?p.rec.rec_anti/p.rec.rec*100:0,cs:p.rec.rec_cs,vol:p.rec.ttd};});
  scatter('qp1',pdvs.map(p=>({x:p.mom,y:p.yoy,label:p.name,color:p.color,r:p.rr})),{x0:0,y0:0,xlabel:'MoM (p.p.)',ylabel:'YoY (p.p.)',qlabels:{tr:'melhora',bl:'piora'},offenderScore:p=>-(p.x+p.y)});
  scatter('qp2',pdvs.map(p=>({x:p.anti,y:p.tx,label:p.name,color:p.cs>0?'#D6293E':'#2E5AAC',r:p.rr,_cs:p.cs})),{y0:median(pdvs.map(p=>p.tx)),x0:median(pdvs.map(p=>p.anti)),xlabel:'% antifraude',ylabel:'Taxa de aprovação',xsuffix:'%',ysuffix:'%',qlabels:{br:'fraude+baixa tx ⚠'},offenderScore:p=>p.x+(100-p.y)+(p._cs>0?50:0)});
}
function bindV5Tools(){
  document.querySelectorAll('.qbtn').forEach(b=>b.onclick=(e)=>{
    const act=b.dataset.act;
    if(act==='labels'){S.insLabels=!S.insLabels;render();return;}
    if(act==='zoom'){openZoom(b.dataset.chart);return;}
    if(act==='export'){openExportMenu(b,b.dataset.chart);return;}
  });
}
function zoomLabelOpts(){return {labelMode:S.zoomMode,labelTop:S.zoomTopN};}
function renderZoomSVG(id){const cfg=CHARTS[id];if(!cfg)return '';return scatterSVG(cfg.points,Object.assign({},cfg.opt,zoomLabelOpts()),true);}
function openZoom(id){
  const cfg=CHARTS[id];if(!cfg)return;
  S.zoomChart=id;
  const title=(document.querySelector(`#${id}`)?.closest('.card')?.querySelector('h3')?.childNodes[0]?.nodeValue||'Quadrante').trim();
  const bg=document.createElement('div');bg.className='modal-bg';bg.id='zoomModal';
  const ctrl=`<div style="display:flex;flex-wrap:wrap;gap:12px;align-items:center;margin-bottom:12px;padding:10px 12px;background:#F7F9FC;border-radius:10px">
    <div style="display:flex;gap:6px;align-items:center"><span class="mut" style="font-size:11px;font-weight:700;text-transform:uppercase">Rótulos</span>
      <span class="toggle" id="zmode"><button data-m="off" class="${S.zoomMode==='off'?'on':''}">Sem rótulo</button><button data-m="lines" class="${S.zoomMode==='lines'?'on':''}">Linhas</button><button data-m="numbers" class="${S.zoomMode==='numbers'?'on':''}">Numérica</button></span></div>
    <div style="display:flex;gap:6px;align-items:center"><span class="mut" style="font-size:11px;font-weight:700;text-transform:uppercase">Top</span>
      <span class="toggle" id="ztop"><button data-n="5" class="${S.zoomTopN===5?'on':''}">5</button><button data-n="10" class="${S.zoomTopN===10?'on':''}">10</button><button data-n="15" class="${S.zoomTopN===15?'on':''}">15</button></span></div>
  </div>`;
  bg.innerHTML=`<div class="modal-box"><div class="mhead"><h3>${title}</h3><div style="display:flex;gap:8px"><button class="qbtn" id="zexp">Exportar PNG</button><button class="mclose" id="zclose">Fechar ✕</button></div></div>${ctrl}<div id="zsvg">${renderZoomSVG(id)}</div></div>`;
  document.body.appendChild(bg);
  bg.onclick=e=>{if(e.target===bg)bg.remove();};
  bg.querySelector('#zclose').onclick=()=>bg.remove();
  bg.querySelector('#zexp').onclick=(e)=>openExportMenu(e.target,id,true);
  bg.querySelectorAll('#zmode button').forEach(btn=>btn.onclick=()=>{S.zoomMode=btn.dataset.m;refreshZoom(id);});
  bg.querySelectorAll('#ztop button').forEach(btn=>btn.onclick=()=>{S.zoomTopN=+btn.dataset.n;refreshZoom(id);});
}
function refreshZoom(id){const bg=document.getElementById('zoomModal');if(!bg)return;
  bg.querySelector('#zsvg').innerHTML=renderZoomSVG(id);
  bg.querySelectorAll('#zmode button').forEach(b=>b.classList.toggle('on',b.dataset.m===S.zoomMode));
  bg.querySelectorAll('#ztop button').forEach(b=>b.classList.toggle('on',+b.dataset.n===S.zoomTopN));
}
function openExportMenu(anchor,id,big){
  document.querySelectorAll('.exp-menu').forEach(m=>m.remove());
  const menu=document.createElement('div');menu.className='exp-menu';
  menu.innerHTML=`<button data-bg="1">Fundo branco (PNG)</button><button data-bg="0">Sem fundo / transparente (PNG)</button>`;
  document.body.appendChild(menu);
  const rc=anchor.getBoundingClientRect();menu.style.left=(rc.left)+'px';menu.style.top=(rc.bottom+4)+'px';
  menu.querySelectorAll('button').forEach(btn=>btn.onclick=()=>{exportChartPNG(id,btn.dataset.bg==='1',big);menu.remove();});
  const closer=(ev)=>{if(!menu.contains(ev.target)&&ev.target!==anchor){menu.remove();document.removeEventListener('click',closer,true);}};
  setTimeout(()=>document.addEventListener('click',closer,true),0);
}
function exportChartPNG(id,white,big){
  const cfg=CHARTS[id];if(!cfg)return;
  // export honours current zoom label settings when exporting from zoom; otherwise uses lines/top5
  const lblOpts=(big!==false&&document.getElementById('zoomModal'))?zoomLabelOpts():{labelMode:(S.insLabels?'lines':'off'),labelTop:5};
  let svgStr=scatterSVG(cfg.points,Object.assign({},cfg.opt,lblOpts),big!==false);
  const m=svgStr.match(/viewBox="0 0 (\d+) (\d+)"/);const W=m?+m[1]:760,H=m?+m[2]:520;const scale=2;
  // set explicit pixel dimensions so the SVG rasterizes correctly as an image
  svgStr=svgStr.replace('width="100%" height="100%"',`width="${W}" height="${H}"`);
  const img=new Image();
  const blob=new Blob([svgStr],{type:'image/svg+xml;charset=utf-8'});
  const url=URL.createObjectURL(blob);
  img.onload=()=>{const cv=document.createElement('canvas');cv.width=W*scale;cv.height=H*scale;const ctx=cv.getContext('2d');ctx.scale(scale,scale);if(white){ctx.fillStyle='#fff';ctx.fillRect(0,0,W,H);}ctx.drawImage(img,0,0,W,H);URL.revokeObjectURL(url);
    cv.toBlob(b=>{const a=document.createElement('a');a.href=URL.createObjectURL(b);a.download=id+(white?'_fundo-branco':'_transparente')+'.png';document.body.appendChild(a);a.click();a.remove();},'image/png');};
  img.onerror=()=>{URL.revokeObjectURL(url);alert('Falha ao exportar. Tente a exportação a partir da visão ampliada.');};
  img.src=url;
}
/* ---------- RESUMO PARA GESTORES ---------- */
function rankBadge(n){return `<span class="rankn ${n===1?'':(n===2?'g2':'g3')}">${n}</span>`;}
function sumStaticTable(cols,rows,opt){
  opt=opt||{};let h='<div class="tablewrap"><table class="stbl"><thead><tr>';
  cols.forEach(c=>h+=`<th>${c.label}</th>`);h+='</tr></thead><tbody>';
  if(!rows.length)h+=`<tr><td colspan="${cols.length}" style="text-align:center;color:#9AA6C2;padding:16px">Sem dados no recorte atual.</td></tr>`;
  rows.forEach(row=>{const cls=row._cls?` class="${row._cls}"`:'';h+=`<tr${cls}>`;
    cols.forEach(c=>{if(c.type==='text')h+=`<td>${c.text(row)}</td>`;else h+=`<td>${cellHTML(c,cellFor(c,row),opt.showDelta)}</td>`;});
    h+='</tr>';});
  h+='</tbody></table></div>';return h;
}
function channelTriplesList(){
  const t=groupTriples(DD.rno,x=>x.CN,x=>fProd(x)&&fCan(x)&&fCid(x));
  return Object.entries(t).map(([cn,v])=>({cn,cg:canalGrupo(cn),rec:v.rec,ant:v.ant,ano:v.ano})).filter(x=>x.rec.ttd>0);
}

/* ---------- CARTEIRA / EXECUTIVOS ---------- */
// build hierarchy tree: Canal -> Gerente Regional -> Gerente Filial -> Coordenador(GN) -> Executivo -> PDVs
// a PDV is carteirized if any hierarchy level is a real name
const NI='Não Identificada';
function pdvCarteirized(p){return !!(p.ger||p.gfil||p.gn||p.exec);}
function cartTree(pdvs){
  const root={ch:{},rec:M0(),ant:M0(),ano:M0()};
  pdvs.forEach(p=>{
    const cart=pdvCarteirized(p);
    // build path skipping empty levels (task 6). Each node tagged with its level name.
    const path=[{lbl:p.cn,lname:'Canal'}];
    if(cart){
      if(p.ger)path.push({lbl:p.ger,lname:'Ger. Regional'});
      if(p.gfil)path.push({lbl:p.gfil,lname:'Ger. de Filial'});
      if(p.gn)path.push({lbl:p.gn,lname:'Coordenador'});
      if(p.exec)path.push({lbl:p.exec,lname:'Executivo'});
    } else {
      path.push({lbl:NI,lname:''});
    }
    let node=root;
    path.forEach(seg=>{const key=seg.lname+'|'+seg.lbl;if(!node.ch[key])node.ch[key]={lbl:seg.lbl,lname:seg.lname,ch:{},rec:M0(),ant:M0(),ano:M0(),leaf:[]};node=node.ch[key];accM(node.rec,p.rec);accM(node.ant,p.ant);accM(node.ano,p.ano);});
    node.leaf.push(p);
  });
  return root;
}
// order key for channel (depth-0): presencial(0)+idx, remoto(100)+idx, outros(900)
function channelOrder(cn){
  const pres=DD.canal_grupos['Canais Presenciais'],rem=DD.canal_grupos['Canais Remotos'];
  let i=pres.indexOf(cn);if(i>=0)return i;
  i=rem.indexOf(cn);if(i>=0)return 100+i;
  return 900;
}
function vCarteira(){
  const pdvs=pdvAggAll();
  const totVol=pdvs.reduce((s,p)=>s+p.rec.ttd,0);
  const covVol=pdvs.filter(pdvCarteirized).reduce((s,p)=>s+p.rec.ttd,0);
  const nExec=new Set(pdvs.filter(p=>p.exec&&p.exec!=='Vago').map(p=>p.exec)).size;
  const nPdvCart=new Set(pdvs.filter(pdvCarteirized).map(p=>p.PDV)).size;
  const ncVol=totVol-covVol;
  // volume by grupo (effective, honoring slider)
  const gvol={'Identificada':0,'Semelhança':0,'Estimada':0,'Não Identificada':0};
  pdvs.forEach(p=>{gvol[p.grupo]=(gvol[p.grupo]||0)+p.rec.ttd;});
  // PDV COUNT by RAW group (independent of slider) — full carteirization breakdown
  const gcnt={'Identificada':new Set(),'Semelhança':new Set(),'Estimada':new Set(),'Não Identificada':new Set()};
  const gcvol={'Identificada':0,'Semelhança':0,'Estimada':0,'Não Identificada':0};
  const rawByPdv={};
  for(const rrow of DD.pdv){if(rrow.SAFRA!==SAF.rec)continue;if(!fProd(rrow)||!fCan(rrow)||!fCid(rrow))continue;const key=rrow.PDV+'|'+rrow.CIDLAB;const g=rrow.CGRP||'Não Identificada';gcnt[g].add(key);gcvol[g]=(gcvol[g]||0)+rrow.ttd;}
  let h=filterBar({})+filterTags();
  h+=`<h2 class="vtitle">Carteira / Hierarquia comercial</h2><div class="vdesc">Drilldown: <b>Canal → Gerente Regional → Gerente de Filial → Coordenador → Executivo → PDV</b> (níveis vagos são pulados). O <b>slider "Nível de qualificação"</b> é cumulativo: no nível ${S.cartLevel} (${LEVELNAMES[S.cartLevel]}), tudo abaixo desse nível vira <b>Não atribuído</b>. Canais presenciais primeiro, remotos depois, "outros" ao fim. Aberto no nível Gerente Regional.</div>`;
  // ===== contador de PDVs por nível (task 1) =====
  const totPdv=gcnt['Identificada'].size+gcnt['Semelhança'].size+gcnt['Estimada'].size+gcnt['Não Identificada'].size;
  const cnt=(g,cls,lbl)=>`<div class="lvlcount ${cls}"><div class="lc-top"><span class="lc-dot"></span><span class="lc-lbl">${lbl}</span></div><div class="lc-num">${fmtN(gcnt[g].size)} <span class="lc-unit">PDVs</span></div><div class="lc-sub">${fmtN(gcvol[g])} consultas · ${fmtP(totPdv?gcnt[g].size/totPdv:0)} dos PDVs</div></div>`;
  h+='<div class="lvlstrip">'+
     cnt('Identificada','g','[1] Identificada')+
     cnt('Semelhança','b','[2] Semelhança')+
     cnt('Estimada','a','[3] Estimada')+
     cnt('Não Identificada','r','[4] Não Identificada')+
     '</div>';
  h+='<div class="kpis">';
  h+=`<div class="kpi g"><div class="lab">Carteira Identificada</div><div class="val">${fmtP(totVol?gvol['Identificada']/totVol:0)}</div><div class="sub">${fmtN(gvol['Identificada'])} consultas · casada por CNPJ (100%)</div></div>`;
  h+=`<div class="kpi b"><div class="lab">Semelhança + Estimada</div><div class="val">${fmtP(totVol?(gvol['Semelhança']+gvol['Estimada'])/totVol:0)}</div><div class="sub">Semelhança ${fmtN(gvol['Semelhança'])} · Estimada ${fmtN(gvol['Estimada'])}</div></div>`;
  h+=`<div class="kpi a"><div class="lab">Não Identificada</div><div class="val">${fmtP(totVol?gvol['Não Identificada']/totVol:0)}</div><div class="sub">${fmtN(gvol['Não Identificada'])} consultas — remotos, outros e sem correspondência</div></div>`;
  h+='</div>';
  h+=`<div class="note"><b>Cascata de carteirização:</b> [1] <b>Identificada</b> — CNPJ do parceiro (SK_PARCEIROS) casa 100% com a carteira no mesmo canal · [2] <b>Semelhança</b> — nome do DV_EQUIPE_VENDA semelhante à razão/fantasia (mesmo canal+município) · [3] <b>Estimada</b> — associação por canal+município (exceto remotos/outros) · [4] <b>Não Identificada</b> — sem correspondência. Cargos vagos na carteira são marcados como <b>"Vago"</b>. Loja Própria carteirizada via arquivo de metas (gestora <b>Fabia Koury</b>).</div>`;
  h+=`<div style="margin-bottom:14px"><input class="searchbox" id="cartSearch" placeholder="Buscar equipe de venda (DV_EQUIPE_VENDA ou Nome Fantasia), gestor, cidade…" value="${(S.cartSearch||'').replace(/"/g,'&quot;')}"></div>`;
  const cq=(S.cartSearch||'').trim().toLowerCase();
  let use=pdvs;
  if(cq)use=pdvs.filter(p=>((p.fant||'')+' '+p.PDV+' '+p.city+' '+p.cn+' '+(p.exec||'')+' '+(p.gn||'')+' '+(p.gfil||'')+' '+(p.ger||'')).toLowerCase().includes(cq));
  const tree=cartTree(use);
  const cols=[
    {key:'cons',label:'Consultas',type:'count',num:a=>a.ttd},
    {key:'ap',label:'Aprovados',type:'count',num:a=>a.ap},
    {key:'tx',label:'Tx Aprov.',type:'rate',num:a=>a.ap,den:a=>a.ttd,pill:true},
    {key:'rec',label:'Recusas',type:'count',num:a=>a.rec},
    {key:'anti',label:S.mode==='pct'?'% Antifraude':'Antifraude',type:'part',num:a=>a.rec_anti,den:a=>a.rec},
    {key:'cs',label:S.mode==='pct'?'% ClearSale':'ClearSale',type:'part',num:a=>a.rec_cs,den:a=>a.rec},
    {key:'ra',label:S.mode==='pct'?'% Risco Alto':'Risco Alto',type:'part',num:a=>a.cons_ra,den:a=>a.ttd},
  ];
  let h2=`<div class="card"><div style="display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap"><h3>Hierarquia comercial${scopeBadge(['prod','canal','cid','ger','gfil','gn','exec'])}</h3><div style="display:flex;gap:8px"><button class="btn sec" id="cartExpand">Expandir tudo</button><button class="btn sec" id="cartCollapse">Recolher ao Regional</button></div></div><div class="csub">Clique numa linha para expandir/recolher. PDVs aparecem por Nome Fantasia. Cada campo com MoM e YoY.</div><div class="tablewrap"><table data-tid="t_cart"><thead><tr><th>Hierarquia</th>`;
  cols.forEach(c=>h2+=`<th>${c.label}</th>`);h2+='</tr></thead><tbody>';
  // recursive flatten
  let uid=0;const rows=[];
  function walk(node,depth,ancChain){
    let kids=Object.values(node.ch);
    if(depth===0){ // channels: presencial -> remoto -> outros, then volume
      kids.sort((a,b)=>{const oa=channelOrder(a.lbl),ob=channelOrder(b.lbl);return oa!==ob?oa-ob:b.rec.ttd-a.rec.ttd;});
    } else { // NI last, else by volume
      kids.sort((a,b)=>{if(a.lbl===NI)return 1;if(b.lbl===NI)return -1;return b.rec.ttd-a.rec.ttd;});
    }
    kids.forEach(k=>{
      const id='n'+(uid++);
      finM(k.rec);finM(k.ant);finM(k.ano);
      const hasKids=Object.keys(k.ch).length>0;const hasLeaf=(k.leaf&&k.leaf.length>0);
      const expandable=hasKids||hasLeaf;
      const isNC=k.lbl===NI;
      const lname=k.lname||'';
      const grp=depth===0?(channelOrder(k.lbl)<100?'Presencial':channelOrder(k.lbl)<900?'Remoto':'Outros'):'';
      rows.push({type:'grp',id,anc:ancChain,depth,label:k.lbl,lname,grp,isNC,expandable,triple:{rec:k.rec,ant:k.ant,ano:k.ano}});
      const chain2=ancChain.concat(id);
      if(hasKids)walk(k,depth+1,chain2);
      if(hasLeaf){k.leaf.sort((a,b)=>b.rec.ttd-a.rec.ttd).forEach(p=>{
        rows.push({type:'pdv',anc:chain2,depth:depth+1,p});});}
    });
  }
  walk(tree,0,[]);
  if(!rows.length)h2+=`<tr><td colspan="${cols.length+1}" style="text-align:center;color:#9AA6C2;padding:18px">Nenhum resultado.</td></tr>`;
  rows.forEach(r=>{
    const pad=8+Math.max(0,r.depth-0)*18;
    if(r.type==='grp'){
      const car=r.expandable?`<span class="cart-car">▸</span>`:'<span class="cart-car" style="visibility:hidden">▸</span>';
      const lbl=`<span class="cname">${r.label}</span>`;
      let tag='';
      if(r.depth===0){tag=`<span class="lvltag">${r.grp}</span>`;}
      else if(!r.isNC){tag=`<span class="lvltag">${r.lname}</span>`;}
      const ncCls=r.isNC?' ncrow':'';
      h2+=`<tr class="cart-row cart-grp${ncCls}" data-node="${r.id}" data-anc="${r.anc.join(',')}" data-depth="${r.depth}"><td style="padding-left:${pad}px">${car} ${tag}${lbl}</td>`;
      cols.forEach(c=>h2+=`<td>${cellHTML(c,cellFor(c,r.triple))}</td>`);h2+='</tr>';
    } else {
      const p=r.p;
      const disp=p.fant?`<b>${p.fant}</b> <span class="mut" style="font-size:10px">· ${p.PDV}</span>`:p.PDV;
      h2+=`<tr class="cart-row cart-pdv" data-anc="${r.anc.join(',')}" data-depth="${r.depth}"><td style="padding-left:${pad+16}px"><span class="mut" style="margin-right:6px">•</span>${cartBadge(p)}${disp} <span class="mut">· ${p.city}</span></td>`;
      cols.forEach(c=>h2+=`<td>${cellHTML(c,cellFor(c,{rec:p.rec,ant:p.ant,ano:p.ano}))}</td>`);h2+='</tr>';
    }
  });
  h2+='</tbody></table></div></div>';
  return h+h2;
}
function cartApplyVisibility(){
  const open=S._cartOpen;
  document.querySelectorAll('.cart-row').forEach(row=>{
    const anc=(row.dataset.anc||'').split(',').filter(Boolean);
    const vis=anc.every(id=>open.has(id));
    row.style.display=vis?'table-row':'none';
  });
  document.querySelectorAll('.cart-grp').forEach(row=>{const c=row.querySelector('.cart-car');if(c)c.textContent=open.has(row.dataset.node)?'▾':'▸';});
}
function bindCarteira(){
  // default open: all depth-0 (canal) nodes -> shows Gerente Regional level. On search, open everything.
  const cq=(S.cartSearch||'').trim();
  if(!S._cartOpen||S._cartOpenReset){S._cartOpen=new Set();S._cartOpenReset=false;
    document.querySelectorAll('.cart-grp').forEach(row=>{if(cq||row.dataset.depth==='0')S._cartOpen.add(row.dataset.node);});}
  if(cq){document.querySelectorAll('.cart-grp').forEach(row=>S._cartOpen.add(row.dataset.node));}
  cartApplyVisibility();
  document.querySelectorAll('.cart-grp').forEach(row=>{row.onclick=()=>{const id=row.dataset.node;if(S._cartOpen.has(id))S._cartOpen.delete(id);else S._cartOpen.add(id);cartApplyVisibility();};});
  const ea=document.getElementById('cartExpand');if(ea)ea.onclick=()=>{document.querySelectorAll('.cart-grp').forEach(row=>S._cartOpen.add(row.dataset.node));cartApplyVisibility();};
  const ca=document.getElementById('cartCollapse');if(ca)ca.onclick=()=>{S._cartOpen=new Set();document.querySelectorAll('.cart-grp[data-depth="0"]').forEach(row=>S._cartOpen.add(row.dataset.node));cartApplyVisibility();};
  const sb=document.getElementById('cartSearch');if(sb){sb.oninput=()=>{S.cartSearch=sb.value;S._cartFocus=true;S._cartOpenReset=true;render();};}
  if(S._cartFocus){const s2=document.getElementById('cartSearch');if(s2){s2.focus();s2.setSelectionRange(s2.value.length,s2.value.length);}S._cartFocus=false;}
}
// structured executive narrative down to executivo level
function texResumoNarrativo(reg,br){
  const r=reg.rec,a=reg.ant,y=reg.ano;
  const dir=(cur,prev,pp)=>{const d=cur-prev;const w=Math.abs(d)<(pp?0.002:0.5)?'estável':(d>0?'alta':'queda');return w;};
  const arrow=v=>v>=0?'▲':'▼';
  // cities
  const cidT=groupTriples(DD.rno,x=>x.CIDLAB,x=>fProd(x)&&fCan(x)&&fCid(x));
  const cidArr=Object.entries(cidT).filter(([k,v])=>v.rec.ttd>50).sort((x,z)=>z[1].rec.tx-x[1].rec.tx);
  const best=cidArr[0],worst=cidArr[cidArr.length-1];
  const manaus=cidT['Manaus'];
  // channels
  const chT=groupTriples(DD.rno,x=>x.CN,x=>fProd(x)&&fCan(x)&&fCid(x));
  const chArr=Object.entries(chT).map(([cn,v])=>({cn,cg:canalGrupo(cn),rec:v.rec,ant:v.ant})).filter(x=>x.rec.ttd>=100);
  const worstCh=chArr.slice().sort((x,z)=>x.rec.tx-z.rec.tx)[0];
  // executives (via pdv carteira)
  const pdvs=pdvAggAll().filter(pdvCarteirized).filter(p=>p.exec&&p.exec!=='Vago');
  const exMap={};pdvs.forEach(p=>{const k=p.exec;if(!exMap[k])exMap[k]={rec:M0(),ant:M0()};accM(exMap[k].rec,p.rec);accM(exMap[k].ant,p.ant);});
  Object.values(exMap).forEach(o=>{finM(o.rec);finM(o.ant);});
  const exArr=Object.entries(exMap).filter(([k,v])=>v.rec.ttd>=80);
  const exBest=exArr.slice().sort((x,z)=>z[1].rec.tx-x[1].rec.tx)[0];
  const exWorst=exArr.slice().sort((x,z)=>x[1].rec.tx-z[1].rec.tx)[0];
  // antifraude focus
  const csShare=r.rec?r.rec_cs/r.rec:0;const bioShare=r.rec?r.rec_bio/r.rec:0;
  let t='<div class="card" style="border-left:4px solid var(--claro)"><h3>Leitura executiva detalhada</h3><div class="csub">Resultados, impactos e comparativos — do panorama regional até o nível de executivo</div>';
  t+='<div class="resnarr">';
  // 1 desempenho geral
  t+=`<p><b>1. Desempenho geral.</b> A Regional Norte encerra ${safraLabel(SAF.rec)} com taxa de aprovação de <b>${fmtP(r.tx)}</b> sobre <b>${fmtN(r.ttd)}</b> consultas (${fmtN(r.ap)} aprovadas, ${fmtN(r.rec)} recusadas). O indicador está em <b>${dir(r.tx,a.tx,1)}</b> no mês (<span class="${r.tx>=a.tx?'up':'down'}">${arrow(r.tx-a.tx)} ${fmtPP(r.tx-a.tx)}</span> MoM) e em <b>${dir(r.tx,y.tx,1)}</b> no ano (<span class="${r.tx>=y.tx?'up':'down'}">${arrow(r.tx-y.tx)} ${fmtPP(r.tx-y.tx)}</span> YoY). Frente ao Brasil (${fmtP(br.rec.tx)}), a RNO opera <b>${fmtPP(r.tx-br.rec.tx)}</b> — um gap estrutural explicado por mix de risco mais pesado.</p>`;
  // 2 motivos de recusa
  t+=`<p><b>2. Composição das recusas.</b> Do total de ${fmtN(r.rec)} recusas: Crédito (Rest. Int.+Score) <b>${fmtP(r.rec_cred/r.rec)}</b>, Restrição Externa <b>${fmtP(r.rec_ext/r.rec)}</b>, Elegibilidade <b>${fmtP(r.rec_eleg/r.rec)}</b>, Antif. Biometria <b>${fmtP(bioShare)}</b> e Antif. ClearSale <b>${fmtP(csShare)}</b>. A frente antifraude soma <b>${fmtP(r.rec_anti/r.rec)}</b> das recusas; a linha ClearSale (fraude Serasa) está em ${dir(r.rec_cs,y.rec_cs,0)} no ano (${fmtD(r.rec_cs-y.rec_cs)} vs. Ago/25), sinalizando ${csShare>0.02?'<b>atenção</b> — concentrada em canais remotos e Banda Larga':'situação sob controle'}.</p>`;
  // 3 cidades
  if(best&&worst){
    t+=`<p><b>3. Praças (municípios).</b> ${best[0]} lidera com <b>${fmtP(best[1].rec.tx)}</b> de aprovação, enquanto ${worst[0]} é a pior (<b>${fmtP(worst[1].rec.tx)}</b>).`;
    if(manaus)t+=` <b>Manaus</b> — maior praça — aprova <b>${fmtP(manaus.rec.tx)}</b> em ${fmtN(manaus.rec.ttd)} consultas e é o principal dreno da média regional.`;
    t+='</p>';
  }
  // 4 canais
  if(worstCh)t+=`<p><b>4. Canais.</b> O canal que mais derruba a performance é <b>${worstCh.cn}</b> (${worstCh.cg}) com apenas <b>${fmtP(worstCh.rec.tx)}</b> de aprovação em ${fmtN(worstCh.rec.ttd)} consultas — foco prioritário de revisão comercial e de perfil de oferta.</p>`;
  // 5 executivos
  if(exBest&&exWorst){
    t+=`<p><b>5. Carteira / Executivos.</b> Entre os executivos carteirizados (base ≥80 consultas), <b>${exBest[0]}</b> tem a melhor taxa (<b>${fmtP(exBest[1].rec.tx)}</b>) e <b>${exWorst[0]}</b> a mais baixa (<b>${fmtP(exWorst[1].rec.tx)}</b>, ${fmtN(exWorst[1].rec.ttd)} consultas). A tabela por executivo abaixo abre o detalhe com MoM e YoY por PDV.</p>`;
    // mini exec table
    t+='<div class="tablewrap" style="margin-top:8px"><table class="stbl"><thead><tr><th>Executivo</th><th>Consultas</th><th>Tx Aprov.</th><th>MoM (p.p.)</th><th>% Antifraude</th></tr></thead><tbody>';
    exArr.slice().sort((x,z)=>z[1].rec.ttd-x[1].rec.ttd).slice(0,10).forEach(([ex,o])=>{
      const mom=o.rec.tx-o.ant.tx;
      t+=`<tr><td>${ex}</td><td>${fmtN(o.rec.ttd)}</td><td>${pillTx(o.rec.tx)}</td><td class="${mom>=0?'up':'down'}">${fmtPP(mom)}</td><td>${fmtP(o.rec.rec?o.rec.rec_anti/o.rec.rec:0)}</td></tr>`;
    });
    t+='</tbody></table></div>';
  }
  // 6 recomendações
  t+=`<p><b>6. Direcionadores de ação.</b> (i) atacar ${worst?worst[0]:'as piores praças'} e ${worstCh?worstCh.cn:'o canal ofensor'} com plano de perfil de oferta; (ii) vigiar a curva de <b>Antif. ClearSale</b> nos canais remotos; (iii) reduzir perdas por <b>Biometria</b> (${fmtP(bioShare)} das recusas — evitável); (iv) acompanhar os executivos abaixo da média regional (${fmtP(r.tx)}).</p>`;
  t+='</div></div>';
  return t;
}
function vResumo(){
  const reg=rnoTriple(),br=brTriple();const r=reg.rec;
  const regMix=r.ttd?r.cons_ra/r.ttd:0;
  let h=filterBar({})+filterTags();
  h+=`<div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px;flex-wrap:wrap">
      <div><h2 class="vtitle">Resumo — Regional Norte (${safraLabel(SAF.rec)})</h2>
      <div class="vdesc">Texto executivo estruturado com resultados, impactos e comparativos, aberto até o nível de executivo. Reflete os filtros ativos, com <b>MoM</b> e <b>YoY</b>.</div></div>
      <button class="print-btn" onclick="window.print()">Imprimir / PDF</button></div>`;
  // ===== d. Apresentação breve dos resultados (primeiro) =====
  const momTx=r.tx-reg.ant.tx,yoyTx=r.tx-reg.ano.tx;
  const csYoY=r.rec_cs-reg.ano.rec_cs;
  h+='<div class="sumsec-h"><span class="bdg"></span><div><h3>Panorama geral</h3><div class="hint">Leitura rápida antes do detalhamento</div></div></div>';
  h+='<div class="xkpis">'+
     xkpi('Taxa de Aprovação',fmtP(r.tx),`Gap Brasil ${fmtPP(r.tx-br.rec.tx)}`,[['MoM',momTx>=0,fmtPP(momTx)],['YoY',yoyTx>=0,fmtPP(yoyTx)]])+
     xkpi('Consultas',fmtN(r.ttd),`Aprov ${fmtN(r.ap)} · Recusas ${fmtN(r.rec)}`,[['MoM',r.ttd>=reg.ant.ttd,fmtD(r.ttd-reg.ant.ttd)],['YoY',r.ttd>=reg.ano.ttd,fmtD(r.ttd-reg.ano.ttd)]])+
     xkpi('Antifraude',fmtN(r.rec_anti),`Biometria ${fmtN(r.rec_bio)} · ClearSale ${fmtN(r.rec_cs)} · ${fmtP(r.rec_anti/r.rec)} das recusas`,[['MoM',r.rec_anti<=reg.ant.rec_anti,fmtD(r.rec_anti-reg.ant.rec_anti)],['YoY',r.rec_anti<=reg.ano.rec_anti,fmtD(r.rec_anti-reg.ano.rec_anti)]])+
     xkpi('Mix Risco Alto',fmtP(regMix),`${fmtN(r.cons_ra)} consultas de risco alto`,[['MoM',(r.cons_ra/r.ttd)<=(reg.ant.ttd?reg.ant.cons_ra/reg.ant.ttd:0),fmtPP((r.cons_ra/r.ttd)-(reg.ant.ttd?reg.ant.cons_ra/reg.ant.ttd:0))]])+
     '</div>';
  h+=`<div class="sumnote"><b>Síntese:</b> a RNO aprova <b>${fmtP(r.tx)}</b> (${fmtPP(r.tx-br.rec.tx)} vs. Brasil), com <b>${fmtN(r.rec)}</b> recusas no mês. A frente de <b>antifraude</b> (Biometria+ClearSale) responde por <b>${fmtP(r.rec_anti/r.rec)}</b> das recusas e a linha de <b>Antif. ClearSale</b> ${csYoY>0?'<b>subiu</b>':'recuou'} ${fmtD(csYoY)} no ano. Abaixo: (a) canais e PDVs que mais derrubam a performance, (b) focos de antifraude por canal presencial e remoto, e (c) PDVs com mix de risco acima da média regional.</div>`;

  // ===== TEXTO EXECUTIVO ESTRUTURADO (task 8) =====
  h+=texResumoNarrativo(reg,br);

  // channels list + regional reference
  const chans=channelTriplesList();
  const chSig=chans.filter(c=>c.rec.ttd>=100); // significant volume

  // ===== a. Canais ofensores em performance =====
  chSig.forEach(c=>{c._imp=c.rec.ttd*Math.max(0,r.tx-c.rec.tx);});
  const perfOff=chSig.slice().sort((a,b)=>b._imp-a._imp||a.rec.tx-b.rec.tx).slice(0,5);
  const perfCols=[
    {key:'lab',label:'Canal / PDV',type:'text',text:x=>x._label},
    {key:'cons',label:'Consultas',type:'count',num:a=>a.ttd},
    {key:'ap',label:'Aprovados',type:'count',num:a=>a.ap},
    {key:'tx',label:'Tx Aprov.',type:'rate',num:a=>a.ap,den:a=>a.ttd,pill:true},
    {key:'rec',label:'Recusas',type:'count',num:a=>a.rec},
    {key:'anti',label:S.mode==='pct'?'% Antifraude':'Rec. Antifraude',type:'part',num:a=>a.rec_anti,den:a=>a.rec},
  ];
  let perfRows=[];
  perfOff.forEach((c,i)=>{
    perfRows.push(Object.assign({},c,{_cls:'grp',_label:`${rankBadge(i+1)}${c.cn} <span class="mut" style="font-weight:600">· ${c.cg}</span>`}));
    let pdvs=pdvAgg(x=>x.CN===c.cn).filter(p=>p.rec.ttd>=20);
    pdvs.forEach(p=>p._imp=p.rec.ttd*Math.max(0,r.tx-p.rec.tx));
    pdvs.sort((a,b)=>b._imp-a._imp||a.rec.tx-b.rec.tx);
    pdvs.slice(0,3).forEach((p,j)=>perfRows.push(Object.assign({},p,{_cls:'pdvln',_label:`${rankBadge(j+1)}${pdvDisp(p)} <span class="mut">· ${p.city}</span>`})));
  });
  h+='<div class="sumsec-h"><span class="bdg">a</span><div><h3>Canais ofensores em performance</h3><div class="hint">Ranqueados pelo impacto na taxa (volume × distância da taxa regional de '+fmtP(r.tx)+') · Top 3 PDVs ofensores por canal</div></div></div>';
  h+=sumStaticTable(perfCols,perfRows);

  // ===== b. Antifraude — canais e PDVs ofensores =====
  h+='<div class="sumsec-h"><span class="bdg">b</span><div><h3>Antifraude — canais e PDVs ofensores</h3><div class="hint">Antifraude = Antif. Biometria + Antif. ClearSale · Top 3 PDVs por canal <b>presencial</b> · Top 5 por canal <b>remoto</b></div></div></div>';
  const fraudCols=[
    {key:'lab',label:'Canal / PDV',type:'text',text:x=>x._label},
    {key:'anti',label:'Antifraude (total)',type:'count',num:a=>a.rec_anti},
    {key:'bio',label:'Antif. Biometria',type:'count',num:a=>a.rec_bio},
    {key:'cs',label:'Antif. ClearSale',type:'count',num:a=>a.rec_cs},
    {key:'antip',label:S.mode==='pct'?'% Antifraude':'Rec. Antifraude',type:'part',num:a=>a.rec_anti,den:a=>a.rec},
    {key:'cons',label:'Consultas',type:'count',num:a=>a.ttd},
    {key:'tx',label:'Tx Aprov.',type:'rate',num:a=>a.ap,den:a=>a.ttd,pill:true},
  ];
  function fraudBlock(groupName,N){
    const gchans=chans.filter(c=>c.cg===groupName&&c.rec.rec_anti>0).sort((a,b)=>b.rec.rec_anti-a.rec.rec_anti);
    let rows=[];
    gchans.forEach((c,i)=>{
      rows.push(Object.assign({},c,{_cls:'grp',_label:`${rankBadge(i+1)}${c.cn}`}));
      const pdvs=pdvAgg(x=>x.CN===c.cn).filter(p=>p.rec.rec_anti>0).sort((a,b)=>b.rec.rec_anti-a.rec.rec_anti).slice(0,N);
      pdvs.forEach((p,j)=>rows.push(Object.assign({},p,{_cls:'pdvln',_label:`${rankBadge(j+1)}${pdvDisp(p)} <span class="mut">· ${p.city}</span>`})));
    });
    return rows;
  }
  h+='<div style="font-weight:800;font-size:12.5px;color:var(--navy2);margin:6px 0 4px">Canais Presenciais — Top 3 PDVs por canal</div>';
  h+=sumStaticTable(fraudCols,fraudBlock('Canais Presenciais',3));
  h+='<div style="font-weight:800;font-size:12.5px;color:var(--navy2);margin:16px 0 4px">Canais Remotos — Top 5 PDVs por canal</div>';
  h+=sumStaticTable(fraudCols,fraudBlock('Canais Remotos',5));
  const outrosRows=fraudBlock('Outros Canais',3);
  if(outrosRows.length){h+='<div style="font-weight:800;font-size:12.5px;color:var(--navy2);margin:16px 0 4px">Outros Canais — Top 3 PDVs por canal</div>';h+=sumStaticTable(fraudCols,outrosRows);}

  // ===== c. PDVs com mix de risco alto acima da média =====
  h+='<div class="sumsec-h"><span class="bdg">c</span><div><h3>PDVs com mix de risco alto acima da média regional</h3><div class="hint">Média regional de risco alto = '+fmtP(regMix)+' das consultas · exibindo os maiores acima da média (base ≥ 20)</div></div></div>';
  const mixCol_rate={key:'mix',label:'% Risco Alto (consultas)',type:'part',num:a=>a.cons_ra,den:a=>a.ttd};
  const mixCols=[
    {key:'lab',label:'PDV',type:'text',text:x=>x._label},
    {key:'cn',label:'Canal',type:'text',text:x=>x.cn},
    {key:'cons',label:'Consultas',type:'count',num:a=>a.ttd},
    mixCol_rate,
    {key:'craalto',label:'Consultas Risco Alto',type:'count',num:a=>a.cons_ra},
    {key:'tx',label:'Tx Aprov.',type:'rate',num:a=>a.ap,den:a=>a.ttd,pill:true},
  ];
  let mixPdvs=pdvAgg().filter(p=>p.rec.ttd>=20).map(p=>Object.assign({},p,{_mix:p.rec.ttd?p.rec.cons_ra/p.rec.ttd:0}));
  mixPdvs=mixPdvs.filter(p=>p._mix>regMix).sort((a,b)=>b._mix-a._mix||b.rec.cons_ra-a.rec.cons_ra).slice(0,15);
  mixPdvs.forEach((p,i)=>{p._label=`${rankBadge(i+1)}${pdvDisp(p)} <span class="mut">· ${p.city}</span>`;});
  h+=sumStaticTable(mixCols,mixPdvs);
  h+='<div class="sumnote" style="background:#FFF7E6;border-color:#F5D08A;color:#8a6400;margin-top:14px">PDVs acima da linha de '+fmtP(regMix)+' concentram clientes de risco Crítico/Altíssimo/Alto — recomenda-se revisão de mix de oferta e reforço de biometria/antifraude nesses pontos.</div>';
  h+='<div class="foot-credit">Elaborado por Arthur Rezende — Planejamento e Performance RNO · Fonte: BASE_ATUAL.xlsx · reflete os filtros ativos</div>';
  return h;
}
function bindSumTools(){}

/* ---------- VIEW IMPORT ---------- */
function vImport(){
  const has=typeof XLSX!=='undefined';
  let h=`<h2 class="vtitle">Importar dados</h2><div class="vdesc">Atualize o painel com uma nova base sem depender do assistente. O processamento é 100% local no seu navegador — nenhum dado é enviado.</div>`;
  if(!has)h+=`<div class="status err">A biblioteca de leitura de Excel (SheetJS) não carregou (sem internet). Conecte-se à internet e recarregue, ou use um arquivo CSV. Você ainda pode navegar com os dados atuais.</div>`;
  h+=`<div class="card"><h3>1) Base granular da RNO (obrigatória)</h3><div class="csub">Arquivo tipo <b>BASE_ATUAL</b> — uma linha por consulta, com as colunas: OPERADORA, DV_EQUIPE_VENDA, PRODUTO1, NM_CANAL_VENDA_GRUPO, Motivo_Recusa, FxRisco, SAFRA, DIA, QTDE_AP, QtTTD.</div>
    <div class="note" style="margin:10px 0"><b> Base grande (acima de ~60 MB)? Use CSV.</b> Navegadores têm um limite rígido de 512 MB de texto por planilha — a BASE_ATUAL atual gera ~655 MB internamente, então <b>nenhum navegador consegue abrir o .xlsx</b> (o Excel consegue porque não usa esse motor). No Excel: <b>Arquivo ▸ Salvar como ▸ CSV UTF-8</b> e envie o CSV aqui. O CSV é lido em <b>streaming</b>, sem limite de tamanho.</div>
    <div class="drop"><b>Selecione a base da RNO</b><br><br><label class="filepick">Escolher arquivo (.csv recomendado / .xlsx)<input type="file" id="fileBase" accept=".xlsx,.xls,.csv,.txt" style="display:none"></label><div id="baseName" class="csub" style="margin-top:10px"></div></div>
  </div>`;
  h+=`<div class="card"><h3>2) Relatório Brasil (opcional)</h3><div class="csub">Arquivo <b>TAXA DE APROVAÇÃO FIXA PF.xlsx</b> — usado só para o comparativo com o Brasil (abas DIN Mensal e Din Diário). Se não enviar, mantém o Brasil atual.</div>
    <div class="drop"><b>Selecione o relatório (BR)</b><br><br><label class="filepick">Escolher arquivo (.xlsx)<input type="file" id="fileBR" accept=".xlsx,.xls" style="display:none"></label><div id="brName" class="csub" style="margin-top:10px"></div></div>
  </div>`;
  h+=`<div class="card"><div style="display:flex;gap:10px;flex-wrap:wrap;align-items:center"><button class="btn" id="btnProcess">Processar e atualizar painel</button><button class="btn sec" id="btnReset">Restaurar dados originais</button><span id="impStatus"></span></div>
    <div id="impLog" style="margin-top:12px"></div></div>`;
  h+=`<div class="note">Definições aplicadas automaticamente (iguais à Tabela Base): agrupamento de canais (Presenciais/Remotos/Outros, unindo grafias similares), motivos em Crédito/Elegibilidade/Antifraude, faixas de risco Alto vs Médio-Baixo, e segmentos de cidade (Grandes Mercados / Mercados em Desenvolvimento / Sem Cabo). O mês mais recente é detectado pela maior SAFRA; mês anterior e ano anterior derivam dele.</div>`;
  setTimeout(bindImport,0);
  return h;
}
let IMP={base:null,br:null};
function bindImport(){
  const fb=document.getElementById('fileBase'),fbr=document.getElementById('fileBR');
  if(fb)fb.onchange=e=>{IMP.base=e.target.files[0];document.getElementById('baseName').textContent=IMP.base?('Selecionado: '+IMP.base.name):'';};
  if(fbr)fbr.onchange=e=>{IMP.br=e.target.files[0];document.getElementById('brName').textContent=IMP.br?('Selecionado: '+IMP.br.name):'';};
  const bp=document.getElementById('btnProcess');if(bp)bp.onclick=processImport;
  const br=document.getElementById('btnReset');if(br)br.onclick=()=>{localStorage.removeItem('RNO_DASH');location.reload();};
}
function setStatus(msg,cls){const s=document.getElementById('impStatus');if(s){s.className='status '+(cls||'info');s.textContent=msg;}}
function logLine(msg,cls){const l=document.getElementById('impLog');if(l)l.innerHTML+=`<div class="status ${cls||'info'}" style="margin-top:6px">${msg}</div>`;}

function jCanalNorm(c){c=String(c||'').trim();const m={'Loja Própria':'Loja Própria','Lojas Próprias':'Loja Própria','Loja Propria':'Loja Própria','Lojas Proprias':'Loja Própria','Porta Porta':'Porta a Porta','Porta Porta Massivo':'Porta a Porta','Porta Porta Massivo -':'Porta a Porta','Porta a Porta':'Porta a Porta','Porta Porta Condominio':'Porta a Porta Condomínio','Porta Porta Condomínio':'Porta a Porta Condomínio','Porta Porta Premium':'Porta a Porta Premium','PME':'PME','Canais Exclusivo Empre':'PME','Canais Exclusivos Empresas':'PME','Canais Exclusivo Empresas':'PME','Canais Eletronicos':'Canais Eletrônicos','Canais Eletrônicos':'Canais Eletrônicos'};return m[c]||c;}
const JPRES=['Agente Autorizado','Loja Própria','Porta a Porta','Porta a Porta Condomínio','Porta a Porta Premium','PME','Distribuidor','Varejo'];
const JREM=['Ativo','Receptivo','DAC','Canais Eletrônicos'];
function jCanalGrupo(cn){return JPRES.includes(cn)?'Canais Presenciais':JREM.includes(cn)?'Canais Remotos':'Outros Canais';}
// NEW split: cred (Rest.Int+Score) · ext (Rest.Externa) · eleg · bio · cs
function jMotivo(m){m=String(m||'');
  if(m==='Restricao Interna'||m==='Restrição Externa - Score')return 'cred';
  if(m==='Restricao Externa')return 'ext';
  if(m==='Outros')return 'eleg';
  if(['Reprovado - Ausência de Biometria','Reprovado - Biometria Negada','Reprovado - Biometria Incompleta'].includes(m))return 'bio';
  if(m==='Reprovado - ClearSale / Aprovado Crédito')return 'cs';
  if(m==='Aprovado')return 'aprovado';return 'outro';}
function jIsCS(m){return String(m)==='Reprovado - ClearSale / Aprovado Crédito';}
function jRisco(r){r=String(r||'');if(['1 - Critico','2 - Altissimo','3 - Alto'].includes(r))return 'alto';if(['4 - Medio','5 - Baixo','6 - Baixissimo'].includes(r))return 'baixo';return 'outro';}
function jFx(r){r=String(r||'');const m={'1 - Critico':'1 - Crítico','2 - Altissimo':'2 - Altíssimo','3 - Alto':'3 - Alto','4 - Medio':'4 - Médio','5 - Baixo':'5 - Baixo','6 - Baixissimo':'6 - Baixíssimo','0 - Score 0 e 1':'0 - Score 0/1','0.1 - Sem informação':'Sem info'};return m[r]||r;}
// robust column resolver: normalize (trim/uppercase/strip accents) and match against candidates
function jNormKey(k){return String(k).normalize('NFKD').replace(/[\u0300-\u036f]/g,'').trim().toUpperCase().replace(/\s+/g,'_');}
function jResolveCols(sampleRow,wanted){
  const map={};const keys=Object.keys(sampleRow||{});
  const norm={};keys.forEach(k=>{norm[jNormKey(k)]=k;});
  for(const w of wanted){map[w]=norm[jNormKey(w)]||null;}
  return {map,keys};
}
const JGRANDES=['MANAUS','BELEM','SAO LUIS','ANANINDEUA','MACAPA','SANTANA','BOA VISTA'];
const JDESENV=['MARABA','IMPERATRIZ','PARAUAPEBAS','CASTANHAL','PARAGOMINAS','TIMON','CAXIAS'];
const JCITY={'MANAUS':'Manaus','BELEM':'Belém','SAO LUIS':'São Luís','ANANINDEUA':'Ananindeua','MACAPA':'Macapá','SANTANA':'Santana','BOA VISTA':'Boa Vista','MARABA':'Marabá','IMPERATRIZ':'Imperatriz','PARAUAPEBAS':'Parauapebas','CASTANHAL':'Castanhal','PARAGOMINAS':'Paragominas','TIMON':'Timon','CAXIAS':'Caxias','SANTAREM':'Santarém','SANTA LUZIA':'Santa Luzia','SAO JOSE DE RIBAMAR':'São José de Ribamar','VIANA':'Viana','SANTA INES':'Santa Inês','PACO DO LUMIAR':'Paço do Lumiar'};
function jSeg(op){op=String(op||'').trim().toUpperCase();if(JGRANDES.includes(op))return 'Grandes Mercados';if(JDESENV.includes(op))return 'Mercados em Desenvolvimento';return 'Sem Cabo';}
function jTitle(s){s=String(s||'').toLowerCase();return s.replace(/\b\w/g,c=>c.toUpperCase());}
function m0(){return {ttd:0,ap:0,rec_cred:0,rec_ext:0,rec_eleg:0,rec_anti:0,rec_cs:0,rec_bio:0,rec_ra:0,rec_rb:0,cons_ra:0,cons_rb:0};}
function addRow(o,mg,cs,rg,ttd,ap){o.ttd+=ttd;o.ap+=ap;
  if(mg==='cred')o.rec_cred+=ttd;if(mg==='ext')o.rec_ext+=ttd;if(mg==='eleg')o.rec_eleg+=ttd;
  if(mg==='bio'){o.rec_bio+=ttd;o.rec_anti+=ttd;}if(mg==='cs'){o.rec_cs+=ttd;o.rec_anti+=ttd;}
  if(mg!=='aprovado'&&rg==='alto')o.rec_ra+=ttd;if(mg!=='aprovado'&&rg==='baixo')o.rec_rb+=ttd;
  if(rg==='alto')o.cons_ra+=ttd;if(rg==='baixo')o.cons_rb+=ttd;}
async function readSheet(file){const buf=await file.arrayBuffer();return XLSX.read(buf,{type:'array',dense:true,cellStyles:false,cellNF:false,cellHTML:false});}
/* ===== CSV STREAMING (handles files of ANY size — no 512MB string limit) ===== */
function csvSplit(line,d){const out=[];let cur='',q=false;
  for(let i=0;i<line.length;i++){const c=line[i];
    if(q){if(c==='"'){if(line[i+1]==='"'){cur+='"';i++;}else q=false;}else cur+=c;}
    else{if(c==='"')q=true;else if(c===d){out.push(cur);cur='';}else cur+=c;}}
  out.push(cur);return out;}
function csvDelim(line){const c=[';',',','\t','|'];let best=',',n=-1;
  c.forEach(d=>{const k=csvSplit(line,d).length;if(k>n){n=k;best=d;}});return best;}
async function csvEncoding(file){ // utf-8 vs latin1 sniff on first 64KB
  const head=await file.slice(0,65536).arrayBuffer();
  try{new TextDecoder('utf-8',{fatal:true}).decode(head);return 'utf-8';}catch(e){return 'windows-1252';}
}
async function parseCSVRows(file,onProg){
  const enc=await csvEncoding(file);
  const stream=file.stream().pipeThrough(new TextDecoderStream(enc));
  const reader=stream.getReader();
  let buf='',header=null,delim=null;const rows=[];let bytes=0,lastTick=0;
  const handleLine=(line)=>{
    if(line.endsWith('\r'))line=line.slice(0,-1);
    if(!line.trim())return;
    if(header===null){delim=csvDelim(line);header=csvSplit(line,delim).map(h=>h.trim());return;}
    const cells=csvSplit(line,delim);const o={};
    for(let i=0;i<header.length;i++){const v=cells[i];o[header[i]]=(v===undefined||v==='')?null:v;}
    rows.push(o);
  };
  while(true){const {value,done}=await reader.read();
    if(value){bytes+=value.length;buf+=value;
      let nl;while((nl=buf.indexOf('\n'))>=0){handleLine(buf.slice(0,nl));buf=buf.slice(nl+1);}
      if(onProg&&bytes-lastTick>8e6){lastTick=bytes;onProg(rows.length);await new Promise(r=>setTimeout(r,0));}}
    if(done)break;}
  if(buf.trim())handleLine(buf);
  return {rows,enc,delim,header};
}
// numeric parser tolerant to pt-BR decimals ("1.234,56")
function jNum(v){if(v==null||v==='')return 0;if(typeof v==='number')return v;
  let s=String(v).trim();if(!s)return 0;
  if(s.indexOf(',')>=0&&s.indexOf('.')>=0)s=s.replace(/\./g,'').replace(',','.');
  else if(s.indexOf(',')>=0)s=s.replace(',','.');
  const n=parseFloat(s);return isNaN(n)?0:n;}
// unified base reader: CSV (streaming) or XLSX (SheetJS), with size diagnostics
async function readBaseRows(file,log){
  const isCSV=/\.(csv|txt)$/i.test(file.name);
  if(isCSV){
    log&&log(`Lendo CSV em streaming (${(file.size/1048576).toFixed(0)} MB)…`,'info');
    const {rows,enc,delim}=await parseCSVRows(file,n=>log&&log(`… ${n.toLocaleString('pt-BR')} linhas lidas`,'info'));
    log&&log(`CSV lido: ${rows.length.toLocaleString('pt-BR')} linhas · separador "${delim==='\t'?'TAB':delim}" · codificação ${enc}.`,'ok');
    return {rows,source:'CSV'};
  }
  if(typeof XLSX==='undefined')throw new Error('SheetJS não carregou (sem internet). Exporte a base como CSV e tente novamente.');
  if(file.size>60*1024*1024)log&&log(`Arquivo grande (${(file.size/1048576).toFixed(0)} MB). O navegador tem limite de memória para XLSX — se falhar, exporte a aba como CSV.`,'info');
  const wb=await readSheet(file);
  const order=[...wb.SheetNames].sort((a,b)=>(jNormKey(a)==='BASE_ATUAL'?-1:0)-(jNormKey(b)==='BASE_ATUAL'?-1:0));
  for(const name of order){
    const ws=wb.Sheets[name];const ref=ws&&ws['!ref'];
    const arr=XLSX.utils.sheet_to_json(ws,{defval:null});
    if(arr.length)return {rows:arr,source:'XLSX:'+name};
    if(ref)log&&log(`Aba "${name}": intervalo ${ref} declarado, mas o navegador não conseguiu carregar as células (arquivo grande demais).`,'err');
  }
  throw new Error('XLSX_TOO_LARGE');
}
async function processImport(){
  if(!IMP.base){setStatus('Selecione ao menos a base da RNO.','err');return;}
  document.getElementById('impLog').innerHTML='';setStatus('Processando base…','info');
  try{
    const t0=performance.now();
    const NEEDED=['SAFRA','DIA','OPERADORA','Motivo_Recusa','FxRisco','NM_CANAL_VENDA_GRUPO','DV_EQUIPE_VENDA','PRODUTO1','QTDE_AP','QtTTD'];
    let rows=null,used=null,colmap=null;
    try{
      const res=await readBaseRows(IMP.base,logLine);
      rows=res.rows;used=res.source;
    }catch(err){
      if(String(err.message)==='XLSX_TOO_LARGE'){
        setStatus('O arquivo XLSX é grande demais para o navegador processar.','err');
        logLine('<b>Motivo técnico:</b> a planilha interna passa de 512 MB de texto — limite rígido do navegador (V8). O Excel abre, mas nenhum navegador consegue.','err');
        logLine('<b>Solução (30s):</b> abra a BASE_ATUAL no Excel → <b>Arquivo ▸ Salvar como ▸ CSV UTF-8 (delimitado por vírgula)</b> → selecione o CSV aqui. A leitura de CSV é feita em streaming e funciona com qualquer tamanho.','info');
        return;
      }
      throw err;
    }
    if(!rows||!rows.length){setStatus('O arquivo foi lido, mas não retornou linhas.','err');return;}
    const {map,keys}=jResolveCols(rows[0],NEEDED);
    if(!(map['OPERADORA']&&map['DV_EQUIPE_VENDA']&&map['QtTTD'])){
      setStatus('Não encontrei as colunas OPERADORA / DV_EQUIPE_VENDA / QtTTD.','err');
      logLine('Colunas detectadas: '+keys.slice(0,25).join(', '),'info');
      logLine('Colunas esperadas (aceita variações de espaço/acentuação): '+NEEDED.join(', '),'info');
      return;
    }
    colmap=map;
    const C=colmap; // resolved actual key names
    logLine(`Base lida (<b>${used}</b>): ${rows.length.toLocaleString('pt-BR')} linhas. Colunas-chave OK.`,'ok');
    const safras=[...new Set(rows.map(r=>Math.round(jNum(r[C.SAFRA]))).filter(x=>x>100000))].sort((a,b)=>a-b);
    const rec=safras[safras.length-1];const ant=safras[safras.length-2]||rec;const mm=rec%100;const ano=(Math.floor(rec/100)-1)*100+mm;const hasAno=safras.includes(ano);
    logLine(`SAFRAs: ${safras.join(', ')}. Recente=${rec}, anterior=${ant}, ano anterior=${hasAno?ano:'(indisponível)'}.`,'info');
    const keep=new Set([rec,ant,ano]);
    const rnoMap={},pdvMap={},dailyMap={},riskMap={},monMap={},monRiskMap={};const canaisSet=new Set();const citiesSeg={};
    const MRO=['Crítico','Altíssimo','Alto','Médio','Baixo','Baixíssimo','Score 0/1','Sem info'];
    const stripFx=fx=>String(fx).indexOf(' - ')>=0?String(fx).split(' - ').pop():String(fx);
    for(const r of rows){const sf=Math.round(jNum(r[C.SAFRA]));if(!sf)continue;
      const cn=jCanalNorm(r[C.NM_CANAL_VENDA_GRUPO]);const cg=jCanalGrupo(cn);
      const mg=jMotivo(r[C.Motivo_Recusa]);const cs=jIsCS(r[C.Motivo_Recusa])?1:0;const rg=jRisco(r[C.FxRisco]);
      const ttd=jNum(r[C.QtTTD]),ap=jNum(r[C.QTDE_AP]);
      // monthly (13m) — all safras
      if(!monMap[sf])monMap[sf]={ttd:0,ap:0,cred:0,ext:0,eleg:0,bio:0,cs:0};
      const mo=monMap[sf];mo.ttd+=ttd;mo.ap+=ap;if(mg==='cred')mo.cred+=ttd;if(mg==='ext')mo.ext+=ttd;if(mg==='eleg')mo.eleg+=ttd;if(mg==='bio')mo.bio+=ttd;if(mg==='cs')mo.cs+=ttd;
      // monthly risk (13m)
      const fxN=stripFx(jFx(r[C.FxRisco]));const mrk=sf+'|'+fxN;if(!monRiskMap[mrk])monRiskMap[mrk]={sf,fx:fxN,ttd:0,ap:0};monRiskMap[mrk].ttd+=ttd;monRiskMap[mrk].ap+=ap;
      if(!keep.has(sf))continue;
      canaisSet.add(cn);
      const op=String(r[C.OPERADORA]||'').trim().toUpperCase();const seg=jSeg(op);const cid=JCITY[op]||jTitle(op);
      const prod=String(r[C.PRODUTO1]||'').trim();const pdv=String(r[C.DV_EQUIPE_VENDA]||'');citiesSeg[cid]=seg;
      const rk=[sf,cid,seg,cg,cn,prod].join('|');if(!rnoMap[rk]){rnoMap[rk]=m0();rnoMap[rk]._m={SAFRA:sf,CIDLAB:cid,SEG:seg,CG:cg,CN:cn,PROD:prod};}addRow(rnoMap[rk],mg,cs,rg,ttd,ap);
      const pk=[sf,pdv,cid,seg,cg,cn,prod].join('|');if(!pdvMap[pk]){pdvMap[pk]=m0();pdvMap[pk]._m={SAFRA:sf,PDV:pdv,CIDLAB:cid,SEG:seg,CG:cg,CN:cn,PROD:prod};}addRow(pdvMap[pk],mg,cs,rg,ttd,ap);
      // risk grain (3 safras) by faixa
      const fxL=jFx(r[C.FxRisco]);const rik=[sf,cid,seg,cg,cn,prod,fxL].join('|');if(!riskMap[rik]){riskMap[rik]={SAFRA:sf,CIDLAB:cid,SEG:seg,CG:cg,CN:cn,PROD:prod,FX:fxL,ttd:0,ap:0};}riskMap[rik].ttd+=ttd;riskMap[rik].ap+=ap;
      if(sf===rec){const dia=Math.round(jNum(r[C.DIA]));const dk=[dia,cid,seg,cg,cn,prod].join('|');if(!dailyMap[dk]){dailyMap[dk]={DIA:dia,CIDLAB:cid,SEG:seg,CG:cg,CN:cn,PROD:prod,ttd:0,ap:0,cred:0,ext:0,eleg:0,bio:0,cs:0};}const o=dailyMap[dk];o.ttd+=ttd;o.ap+=ap;if(mg==='cred')o.cred+=ttd;if(mg==='ext')o.ext+=ttd;if(mg==='eleg')o.eleg+=ttd;if(mg==='bio')o.bio+=ttd;if(mg==='cs')o.cs+=ttd;}}
    const toRows=map=>Object.values(map).map(o=>{const m=o._m;const{_m,...rest}=o;return Object.assign({},m,rest);});
    const newData=JSON.parse(JSON.stringify(DD));
    newData.rno=toRows(rnoMap);
    // ---- reapply carteira mapping (by PDV code) from CURRENT data ----
    const cmap={};for(const p of DD.pdv){if(cmap[p.PDV]===undefined)cmap[p.PDV]={EXEC:p.EXEC,GN:p.GN,GER:p.GER,GFIL:p.GFIL,FANT:p.FANT,CGRP:p.CGRP,CRANK:p.CRANK,CCONF:p.CCONF,CVIA:p.CVIA};}
    newData.pdv=toRows(pdvMap).map(row=>{const c=cmap[row.PDV];if(c&&c.CGRP&&c.CGRP!=='Não Identificada'){row.EXEC=c.EXEC;row.GN=c.GN;row.GER=c.GER;row.GFIL=c.GFIL;row.FANT=c.FANT;row.CGRP=c.CGRP;row.CRANK=c.CRANK;row.CCONF=c.CCONF;row.CVIA=c.CVIA;row._cart=true;}else{row.EXEC=null;row.GN=null;row.GER=null;row.GFIL=null;row.FANT=null;row.CGRP='Não Identificada';row.CRANK=4;row.CCONF='—';row.CVIA='—';row._cart=false;}row.PDVLBL=row.FANT?(row.FANT+' · '+row.PDV):row.PDV;return row;});
    newData.daily=Object.values(dailyMap);
    newData.risk=Object.values(riskMap);
    newData.canais_norm=[...canaisSet].sort();
    const cg2={'Grandes Mercados':[],'Mercados em Desenvolvimento':[],'Sem Cabo':[]};Object.entries(citiesSeg).forEach(([c,s])=>{if(cg2[s])cg2[s].push(c);});Object.keys(cg2).forEach(k=>cg2[k].sort());newData.cidades=cg2;
    newData.safras={rec,ant,ano:hasAno?ano:ant};
    // monthly_rno (last 13)
    const msorted=Object.keys(monMap).map(Number).sort((a,b)=>a-b).slice(-13);
    newData.monthly_rno=msorted.map(sf=>{const o=monMap[sf];return {SAFRA:sf,ttd:o.ttd,ap:o.ap,cred:o.cred,ext:o.ext,eleg:o.eleg,bio:o.bio,cs:o.cs,tx:o.ttd?o.ap/o.ttd:0};});
    // monthly_risk (last 13)
    newData.monthly_risk={order:MRO,data:msorted.map(sf=>{const rec2={SAFRA:sf};MRO.forEach(fx=>{const o=monRiskMap[sf+'|'+fx];rec2[fx]={ttd:o?o.ttd:0,ap:o?o.ap:0};});return rec2;})};
    // rebuild carteira_meta from reapplied pdvs
    const uq=f=>[...new Set(newData.pdv.map(r=>r[f]).filter(Boolean))].sort();
    newData.carteira_meta={execs:uq('EXEC'),gns:uq('GN'),gfils:uq('GFIL'),gers:uq('GER'),grupos:['Identificada','Semelhança','Estimada','Não Identificada'],levels:['Identificada','Semelhança','Estimada'],nc:'Não Identificada'};
    // projection (business days). If month fully elapsed -> factor 1.
    const daysInMonth=new Date(Math.floor(rec/100),mm,0).getDate();let bt=0,be=0;const maxDia=Math.max(...Object.values(dailyMap).map(d=>d.DIA));
    for(let d=1;d<=daysInMonth;d++){const wd=new Date(Math.floor(rec/100),mm-1,d).getDay();if(wd>=1&&wd<=5){bt++;if(d<=maxDia)be++;}}
    newData.proj={bd_total:bt,bd_elapsed:be||1,factor:bt/(be||1)};
    logLine(`Grãos: RNO ${newData.rno.length}, PDV ${newData.pdv.length}, Diário ${newData.daily.length}, Risco ${newData.risk.length}, Mensal ${newData.monthly_rno.length}. Cidades: ${Object.values(cg2).flat().length}. Carteira reaplicada por código de PDV.`,'ok');
    if(IMP.br){setStatus('Processando relatório Brasil…','info');try{const ok=await processBR(newData);logLine(ok?'Brasil atualizado a partir do relatório.':'Não achei as abas DIN Mensal/Din Diário — mantido Brasil anterior.',ok?'ok':'err');}catch(e){logLine('Falha no relatório BR: '+e.message+' — mantido Brasil anterior.','err');}}
    DD=newData;try{localStorage.setItem('RNO_DASH',JSON.stringify(newData));}catch(e){logLine('Aviso: dados grandes demais para salvar no navegador; valem só nesta sessão.','info');}refreshRefs();invalidatePdvCache&&invalidatePdvCache();
    const dt=((performance.now()-t0)/1000).toFixed(1);setStatus('✔ Painel atualizado em '+dt+'s (RNO '+fmtN(newData.rno.filter(x=>x.SAFRA===rec).reduce((s,x)=>s+x.ttd,0))+' consultas em '+rec+'). Navegue pelas abas.','ok');
    logLine('Dica: use "Restaurar dados originais" para voltar ao painel embutido.','info');
  }catch(e){setStatus('Erro ao processar: '+e.message,'err');console.error(e);}
}
// find header row index within a header:1 array by looking for a marker column name
function jFindHeader(arr,markers){for(let i=0;i<Math.min(14,arr.length);i++){const row=(arr[i]||[]).map(c=>jNormKey(c));if(markers.some(mk=>row.includes(jNormKey(mk))))return i;}return -1;}
function jIdx(headRow,name){const n=jNormKey(name);return headRow.map(x=>jNormKey(x)).indexOf(n);}
async function processBR(newData){
  const wb=await readSheet(IMP.br);
  const mn=wb.SheetNames.find(s=>jNormKey(s)==='DIN_MENSAL');if(!mn)return false;
  const arr=XLSX.utils.sheet_to_json(wb.Sheets[mn],{header:1,defval:null});
  const hr=jFindHeader(arr,['NM_CANAL_VENDA_GRUPO']);if(hr<0)return false;const head=arr[hr];
  const iSaf=jIdx(head,'SAFRA'),iCan=jIdx(head,'NM_CANAL_VENDA_GRUPO'),iMot=jIdx(head,'Motivo_Recusa'),iRis=jIdx(head,'FxRisco'),iProd=jIdx(head,'PRODUTO1'),iAp=jIdx(head,'Soma de QTDE_AP'),iTt=jIdx(head,'Soma de QtTTD');
  if(iSaf<0||iTt<0)return false;const rec=newData.safras.rec,ant=newData.safras.ant,ano=newData.safras.ano;const keep=new Set([rec,ant,ano]);
  const map={},monMap={};
  for(let i=hr+1;i<arr.length;i++){const r=arr[i];if(!r)continue;const sf=+r[iSaf];if(isNaN(sf))continue;
    let prod=String(r[iProd]||'').trim();if(prod==='APP')prod='BANDA LARGA';const cn=jCanalNorm(r[iCan]);const mg=jMotivo(r[iMot]);const cs=jIsCS(r[iMot])?1:0;const rg=jRisco(r[iRis]);const ttd=+r[iTt]||0,ap=+r[iAp]||0;
    if(!monMap[sf])monMap[sf]={ttd:0,ap:0,cred:0,ext:0,eleg:0,bio:0,cs:0};const mo=monMap[sf];mo.ttd+=ttd;mo.ap+=ap;if(mg==='cred')mo.cred+=ttd;if(mg==='ext')mo.ext+=ttd;if(mg==='eleg')mo.eleg+=ttd;if(mg==='bio')mo.bio+=ttd;if(mg==='cs')mo.cs+=ttd;
    if(!keep.has(sf))continue;const k=[sf,cn,prod].join('|');if(!map[k]){map[k]=m0();map[k]._m={SAFRA:sf,CN:cn,PROD:prod};}addRow(map[k],mg,cs,rg,ttd,ap);}
  newData.br=Object.values(map).map(o=>{const m=o._m;const{_m,...rest}=o;return Object.assign({},m,rest);});
  const ms=Object.keys(monMap).map(Number).sort((a,b)=>a-b).slice(-13);
  newData.monthly_br=ms.map(sf=>{const o=monMap[sf];return {SAFRA:sf,ttd:o.ttd,ap:o.ap,cred:o.cred,ext:o.ext,eleg:o.eleg,bio:o.bio,cs:o.cs,tx:o.ttd?o.ap/o.ttd:0};});
  const dn=wb.SheetNames.find(s=>jNormKey(s)==='DIN_DIARIO');
  if(dn){const a2=XLSX.utils.sheet_to_json(wb.Sheets[dn],{header:1,defval:null});const h2=jFindHeader(a2,['DIA','NM_CANAL_VENDA_GRUPO']);
    if(h2>=0){const hd=a2[h2];const jDia=jIdx(hd,'DIA'),jCan=jIdx(hd,'NM_CANAL_VENDA_GRUPO'),jMot=jIdx(hd,'Motivo_Recusa'),jTt=jIdx(hd,'Soma de QtTTD'),jAp=jIdx(hd,'Soma de QTDE_AP');const bd={};for(let i=h2+1;i<a2.length;i++){const r=a2[i];if(!r)continue;const dia=+r[jDia];if(isNaN(dia))continue;const cn=jCanalNorm(r[jCan]);const mg=jMotivo(r[jMot]);const ttd=+r[jTt]||0;const ap=jAp>=0?(+r[jAp]||0):0;const k=[dia,cn].join('|');if(!bd[k]){bd[k]={DIA:dia,CN:cn,ttd:0,ap:0,cred:0,ext:0,eleg:0,bio:0,cs:0};}const o=bd[k];o.ttd+=ttd;o.ap+=ap;if(mg==='cred')o.cred+=ttd;if(mg==='ext')o.ext+=ttd;if(mg==='eleg')o.eleg+=ttd;if(mg==='bio')o.bio+=ttd;if(mg==='cs')o.cs+=ttd;}newData.brd=Object.values(bd);}}
  return true;
}
/* ============ GLOBAL EVENT DELEGATION ============ */
document.addEventListener('click',e=>{
  // quality slider tick click
  const tick=e.target.closest('.qsl-tick');
  if(tick){S.cartLevel=+tick.dataset.lv;invalidatePdvCache();render();return;}
  // filter clear tags
  const clr=e.target.closest('[data-clr]');
  if(clr){const w=clr.dataset.clr;
    if(w==='prod'||w==='all')S.prod=new Set(ALLPROD);
    if(w==='canal'||w==='all')S.canais=new Set(DD.canais_norm);
    if(w==='cid'||w==='all')S.cidades=new Set(allCidades());
    if(w==='exec'||w==='all')S.execs=new Set(DD.carteira_meta.execs);
    if(w==='gn'||w==='all')S.gns=new Set(DD.carteira_meta.gns);
    if(w==='gfil'||w==='all')S.gfils=new Set(DD.carteira_meta.gfils||[]);
    if(w==='ger'||w==='all')S.gers=new Set(DD.carteira_meta.gers);
    if(w==='grupo'||w==='all')S.cartLevel=3;
    invalidatePdvCache();render();return;}
  // sort headers
  const th=e.target.closest('th.sortable');
  if(th){const tid=th.dataset.tid,col=th.dataset.col;const st=tget(tid);
    const isText=['lab','pdv','city','cn','seg'].includes(col);
    if(st.sortCol===col)st.sortDir*=-1;else{st.sortCol=col;st.sortDir=isText?1:-1;} // text→A-Z, número→maior-menor
    render();return;}
  // multiselect quick buttons
  const q=e.target.closest('.msquick button, .msbody a[data-grp]');
  if(q){const id=q.dataset.dd;const act=q.dataset.act;const grp=q.dataset.grp;
    if(id==='prod'){if(act==='all')S.prod=new Set(ALLPROD);else if(act==='none')S.prod=new Set([ALLPROD[0]]);}
    else if(id==='canal'){if(act==='all')S.canais=new Set(DD.canais_norm);else if(act==='none')S.canais=new Set([DD.canais_norm[0]]);else if(grp){const arr=grp==='Canais Presenciais'?PRES:grp==='Canais Remotos'?REM:outros();const all=arr.every(x=>S.canais.has(x));if(all)arr.forEach(x=>S.canais.delete(x));else arr.forEach(x=>S.canais.add(x));if(S.canais.size===0)S.canais=new Set(DD.canais_norm);}}
    else if(id==='cid'){if(act==='all')S.cidades=new Set(allCidades());else if(act==='none')S.cidades=new Set([allCidades()[0]]);else if(grp){const arr=DD.cidades[grp]||[];const all=arr.every(x=>S.cidades.has(x));if(all)arr.forEach(x=>S.cidades.delete(x));else arr.forEach(x=>S.cidades.add(x));if(S.cidades.size===0)S.cidades=new Set(allCidades());}}
    else if(id==='exec'){const A=DD.carteira_meta.execs;if(act==='all')S.execs=new Set(A);else if(act==='none')S.execs=new Set([A[0]]);}
    else if(id==='gn'){const A=DD.carteira_meta.gns;if(act==='all')S.gns=new Set(A);else if(act==='none')S.gns=new Set([A[0]]);}
    else if(id==='gfil'){const A=DD.carteira_meta.gfils||[];if(act==='all')S.gfils=new Set(A);else if(act==='none')S.gfils=new Set([A[0]]);}
    else if(id==='ger'){const A=DD.carteira_meta.gers;if(act==='all')S.gers=new Set(A);else if(act==='none')S.gers=new Set([A[0]]);}
    S.openDD.add(id);invalidatePdvCache();render();return;}
});
document.addEventListener('change',e=>{
  // multiselect checkbox
  if(e.target.classList.contains('mscheck')){const id=e.target.dataset.dd,val=e.target.dataset.val,on=e.target.checked;
    if(id==='prod'){const pk=prodFromLabel(val);if(on)S.prod.add(pk);else if(S.prod.size>1)S.prod.delete(pk);}
    else if(id==='canal'){if(on)S.canais.add(val);else if(S.canais.size>1)S.canais.delete(val);}
    else if(id==='cid'){if(on)S.cidades.add(val);else if(S.cidades.size>1)S.cidades.delete(val);}
    else if(id==='exec'){if(on)S.execs.add(val);else if(S.execs.size>1)S.execs.delete(val);}
    else if(id==='gn'){if(on)S.gns.add(val);else if(S.gns.size>1)S.gns.delete(val);}
    else if(id==='gfil'){if(on)S.gfils.add(val);else if(S.gfils.size>1)S.gfils.delete(val);}
    else if(id==='ger'){if(on)S.gers.add(val);else if(S.gers.size>1)S.gers.delete(val);}
    S.openDD.add(id);invalidatePdvCache();render();return;}
  // filter number op select
  if(e.target.classList.contains('flop')){const tid=e.target.dataset.tid,col=e.target.dataset.col;const st=tget(tid);if(!st.filters[col])st.filters[col]={op:'ge',val:''};st.filters[col].op=e.target.value;render();return;}
});
let filterTimer=null;
document.addEventListener('input',e=>{
  // quality level slider
  if(e.target.id==='qslider'){S.cartLevel=+e.target.value;invalidatePdvCache();render();return;}
  // column filters
  if(e.target.classList.contains('fltxt')||e.target.classList.contains('flval')){const tid=e.target.dataset.tid,col=e.target.dataset.col;const st=tget(tid);if(!st.filters[col])st.filters[col]={op:'ge',val:''};st.filters[col].val=e.target.value;
    clearTimeout(filterTimer);const el=e.target;const pos=el.selectionStart;filterTimer=setTimeout(()=>{render();const n=document.querySelector(`[data-tid="${tid}"][data-col="${col}"].${el.className.split(' ')[0]}`);if(n){n.focus();try{n.setSelectionRange(pos,pos);}catch(x){}}},260);return;}
  // multiselect search inside dropdown
  if(e.target.classList.contains('msearch')){const id=e.target.dataset.dd;const q=e.target.value.toLowerCase();const body=e.target.closest('.msbody');body.querySelectorAll('.msitem').forEach(it=>{it.style.display=it.dataset.item.includes(q)?'flex':'none';});return;}
});
// keep dropdowns open state
document.addEventListener('toggle',e=>{if(e.target.classList&&e.target.classList.contains('msdd')){const id=e.target.dataset.dd;if(e.target.open)S.openDD.add(id);else S.openDD.delete(id);}},true);
// close dropdowns when clicking outside
document.addEventListener('click',e=>{if(!e.target.closest('.msdd')){document.querySelectorAll('.msdd[open]').forEach(d=>{d.open=false;S.openDD.delete(d.dataset.dd);});}},true);

/* ============ INIT ============ */
document.querySelectorAll('#nav a').forEach(a=>a.onclick=()=>go(a.dataset.v));
document.querySelectorAll('#modeToggle button').forEach(b=>b.onclick=()=>{S.mode=b.dataset.m;render();});
(function(){const t=document.getElementById('sideToggle');if(t)t.onclick=(e)=>{e.stopPropagation();setSidebar(!S.sidebarCollapsed);};})();
applySidebar();
render();
