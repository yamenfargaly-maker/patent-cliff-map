import json

D = json.load(open("/home/claude/patent-cliff-map/data.json"))

HTML = r"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>The 2030 Patent Cliff Map</title>
<style>
:root{
  --surface-1:#fcfcfb; --page:#f9f9f7; --text-primary:#0b0b0b; --text-secondary:#52514e;
  --muted:#898781; --grid:#e1e0d9; --axis:#c3c2b7;
  --s1:#2a78d6; --s2:#eb6834; --border:rgba(11,11,11,.10); --wash:rgba(42,120,214,.06);
  color-scheme:light;
}
@media (prefers-color-scheme:dark){ :root:where(:not([data-theme=light])){
  --surface-1:#1a1a19; --page:#0d0d0d; --text-primary:#fff; --text-secondary:#c3c2b7;
  --muted:#898781; --grid:#2c2c2a; --axis:#383835;
  --s1:#3987e5; --s2:#d95926; --border:rgba(255,255,255,.10); --wash:rgba(57,135,229,.10);
  color-scheme:dark; }}
:root[data-theme=dark]{
  --surface-1:#1a1a19; --page:#0d0d0d; --text-primary:#fff; --text-secondary:#c3c2b7;
  --muted:#898781; --grid:#2c2c2a; --axis:#383835;
  --s1:#3987e5; --s2:#d95926; --border:rgba(255,255,255,.10); --wash:rgba(57,135,229,.10);
  color-scheme:dark; }
*{box-sizing:border-box}
body{margin:0;background:var(--page);color:var(--text-primary);
  font:15px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif;-webkit-font-smoothing:antialiased}
.wrap{max-width:1180px;margin:0 auto;padding:40px 24px 80px}
header{margin-bottom:32px}
h1{font-size:34px;line-height:1.15;margin:0 0 8px;letter-spacing:-.02em;font-weight:650}
.sub{color:var(--text-secondary);font-size:16px;max-width:74ch;margin:0 0 14px}
.meta{color:var(--muted);font-size:12.5px;display:flex;gap:16px;flex-wrap:wrap;align-items:center}
.toggle{margin-left:auto;background:none;border:1px solid var(--border);color:var(--text-secondary);
  border-radius:6px;padding:5px 11px;font-size:12px;cursor:pointer;font-family:inherit}
.toggle:hover{background:var(--wash)}
.card{background:var(--surface-1);border:1px solid var(--border);border-radius:12px;
  padding:22px 24px;margin-bottom:20px}
.tiles{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:20px}
.tile{background:var(--surface-1);border:1px solid var(--border);border-radius:12px;padding:18px 20px}
.tile .k{font-size:11.5px;text-transform:uppercase;letter-spacing:.055em;color:var(--muted);
  margin-bottom:9px;font-weight:600}
.tile .v{font-size:31px;font-weight:650;letter-spacing:-.02em;line-height:1}
.tile .d{font-size:12.5px;color:var(--text-secondary);margin-top:7px}
h2{font-size:19px;margin:0 0 5px;letter-spacing:-.01em;font-weight:640}
.note{color:var(--text-secondary);font-size:13.5px;margin:0 0 18px;max-width:82ch}
.legend{display:flex;gap:18px;flex-wrap:wrap;font-size:12.5px;color:var(--text-secondary);margin-bottom:10px}
.legend i{width:10px;height:10px;border-radius:2px;display:inline-block;margin-right:6px;vertical-align:-1px}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:20px}
svg{display:block;width:100%;overflow:visible}
.gl{stroke:var(--grid);stroke-width:1}
.ax{stroke:var(--axis);stroke-width:1}
.tk{fill:var(--muted);font-size:11px}
.lbl{fill:var(--text-secondary);font-size:10.5px;font-weight:600}
.qd{fill:var(--muted);font-size:10.5px;text-transform:uppercase;letter-spacing:.06em;font-weight:650;opacity:.75}
.dot{fill:var(--s1);fill-opacity:.42;stroke:var(--s1);stroke-width:1.5;cursor:pointer}
.dot:hover{fill-opacity:.72}
.bar{fill:var(--s1)}.bar2{fill:var(--s2)}
.brow:hover .bar,.brow:hover .bar2{opacity:.72}
table{width:100%;border-collapse:collapse;font-size:13px}
#tgt{min-width:1080px}
#tgt td.n,#tgt th.n{white-space:nowrap}
#tgt td:nth-child(2){min-width:210px}
th{text-align:left;font-size:11px;text-transform:uppercase;letter-spacing:.05em;color:var(--muted);
  font-weight:650;padding:8px 9px;border-bottom:1px solid var(--axis);white-space:nowrap;cursor:pointer;user-select:none}
th:hover{color:var(--text-primary)}
th.n,td.n{text-align:right;font-variant-numeric:tabular-nums}
td{padding:9px;border-bottom:1px solid var(--grid);vertical-align:top}
tbody tr:hover{background:var(--wash)}
.tick{font-weight:640}
.mut{color:var(--text-secondary);font-size:12.2px}
.pill{display:inline-block;font-size:10.5px;padding:2px 7px;border-radius:99px;
  border:1px solid var(--border);color:var(--text-secondary);white-space:nowrap}
.fitbar{position:relative;height:6px;background:var(--grid);border-radius:99px;width:58px;display:inline-block;
  vertical-align:middle;margin-right:8px}
.fitbar span{position:absolute;inset:0 auto 0 0;background:var(--s1);border-radius:99px}
.filters{display:flex;gap:7px;flex-wrap:wrap;margin-bottom:14px}
.filters button{background:none;border:1px solid var(--border);color:var(--text-secondary);
  border-radius:99px;padding:4px 12px;font-size:12px;cursor:pointer;font-family:inherit}
.filters button:hover{background:var(--wash)}
.filters button[aria-pressed=true]{background:var(--s1);border-color:var(--s1);color:#fff}
#tip{position:fixed;pointer-events:none;opacity:0;transition:opacity .1s;background:var(--surface-1);
  border:1px solid var(--border);border-radius:9px;padding:10px 13px;font-size:12.5px;max-width:290px;
  box-shadow:0 6px 24px rgba(0,0,0,.14);z-index:99;line-height:1.45}
#tip b{display:block;font-size:13.5px;margin-bottom:4px}
#tip .r{color:var(--text-secondary);display:flex;justify-content:space-between;gap:16px}
#tip .r b{display:inline;font-size:12.5px;color:var(--text-primary);margin:0}
details{margin-top:8px}
summary{cursor:pointer;color:var(--text-secondary);font-size:12.5px;padding:6px 0}
summary:hover{color:var(--text-primary)}
footer{color:var(--muted);font-size:12px;margin-top:34px;line-height:1.7}
footer a{color:var(--text-secondary)}
@media(max-width:900px){.tiles{grid-template-columns:repeat(2,1fr)}.grid2{grid-template-columns:1fr}
  h1{font-size:27px}.wrap{padding:26px 15px 60px}}
</style></head><body>
<div class="wrap">
<header>
  <h1>The 2030 Patent Cliff Map</h1>
  <p class="sub">Every large-cap pharma ranked by the revenue it loses to patent expiry between 2027 and 2032,
  set against the balance-sheet capacity it has to replace that revenue — then matched to a scored universe of
  acquisition targets at precedent-transaction premiums.</p>
  <div class="meta">
    <span>Data as of <strong>17 August 2026</strong></span><span>·</span>
    <span>Q2-2026 balance sheets, FY2025 revenue</span><span>·</span>
    <span>__NACQ__ acquirers · __NTGT__ targets</span>
    <button class="toggle" id="tt">Dark</button>
  </div>
</header>

<div class="tiles">
  <div class="tile"><div class="k">Revenue at risk 2027–32</div><div class="v">$__DEDUP__B</div>
    <div class="d">__PCTDEDUP__% of $__REV__B revenue, net of $15.3B of partner double-counts
    (gross of company lines: $__ATRISK__B)</div></div>
  <div class="tile"><div class="k">BD firepower at 3.0×</div><div class="v">$__FIRE__B</div>
    <div class="d">Debt capacity to a 3.0× net-debt/EBITDA ceiling</div></div>
  <div class="tile"><div class="k">Coverage ratio</div><div class="v">__COV__×</div>
    <div class="d">Firepower per dollar of revenue lost</div></div>
  <div class="tile"><div class="k">Target universe cost</div><div class="v">$__TAKE__B</div>
    <div class="d">__NTGT__ names at phase-adjusted precedent premiums</div></div>
</div>

<div class="card">
  <h2>Who must buy, and who can afford to</h2>
  <p class="note">Horizontal axis is the urgency score — 70% weight on the share of revenue exposed, 30% on how
  soon the largest expiry lands. Vertical axis is debt capacity to a 3.0× leverage ceiling, adjusted for deals
  already announced but not yet closed. Bubble area is absolute revenue at risk. Quadrant dividers sit at the
  cohort medians.</p>
  <div id="scatter"></div>
  <details><summary>Show as table</summary><div id="acqtable"></div></details>
</div>

<div class="grid2">
  <div class="card">
    <h2>Exposure</h2>
    <p class="note">Share of FY2025 revenue losing exclusivity in the window.</p>
    <div id="bars1"></div>
  </div>
  <div class="card">
    <h2>The hole vs. the wallet</h2>
    <p class="note">Revenue at risk against capacity to replace it. Both in $B on one scale.</p>
    <div class="legend">
      <span><i style="background:var(--s2)"></i>Revenue at risk</span>
      <span><i style="background:var(--s1)"></i>BD firepower</span>
    </div>
    <div id="bars2"></div>
  </div>
</div>

<div class="card">
  <h2>Target screen</h2>
  <p class="note">Fit weights how urgently the asset's natural acquirers need revenue (40%), whether the asset is
  large enough to matter against those cliffs (40%), and whether any natural buyer can write the cheque (20%).
  <strong>PoS</strong> is the modelled probability the lead asset reaches approval from its current phase.
  <strong>rNPV</strong> is the risk-adjusted NPV of that one asset. <strong>Lead asset</strong> is the share of the
  takeout price the lead asset alone explains — high means you are buying a product, low means you are buying a
  platform or a pipeline. Sort any column.</p>
  <div class="filters" id="filters"></div>
  <div style="overflow-x:auto"><table id="tgt"><thead><tr>
    <th data-k="fit" class="n">Fit</th><th data-k="name">Company</th><th data-k="ta">Area</th>
    <th data-k="asset">Lead asset</th><th data-k="phase">Phase</th>
    <th data-k="pos" class="n">PoS</th>
    <th data-k="mcap" class="n">Mkt cap</th><th data-k="takeout" class="n">Takeout</th>
    <th data-k="rnpv" class="n">rNPV</th><th data-k="cover" class="n">Lead asset</th>
    <th data-k="capable">Can fund</th>
  </tr></thead><tbody></tbody></table></div>
</div>

<div class="card">
  <h2>How probability of success is estimated</h2>
  <p class="note" style="max-width:none">
  Phase-transition probabilities come from <strong>BIO / Informa Pharma Intelligence / QLS Advisors, "Clinical
  Development Success Rates and Contributing Factors 2011–2020"</strong> — 12,728 transitions across 9,704 programs.
  It is preferred to Wong, Siah &amp; Lo (2019) because it is the most recent complete phase-by-phase publication,
  uses a four-transition structure matching how rNPV is built, and does not impute unresolved trial outcomes.
  Wong reports CNS at 15.0% against BIO's 5.9% for neurology, a 2.5× disagreement driven almost entirely by that
  imputation — a reviewer will raise it, so it is named here. A uniform 0.85× drift factor is applied because
  industry-wide likelihood of approval fell from 7.9% (2011–20) to 6.7% (2014–23) per Citeline.<br><br>
  <strong>Modifiers are not multiplied.</strong> Lead-indication status, biomarker preselection, genetic target
  validation and rare-disease designation are each reported marginally against the all-indication baseline, and they
  are strongly correlated with one another. Stacking them raw gives a 49× uplift and a probability above 1.0. They
  are instead combined in log-odds space with a 0.55 damping exponent and a hard 3.5× cap on total uplift — for a
  Phase 2 neurology asset, four modifiers move the estimate from 10.5% to 36.7%, where naive multiplication would
  produce 390%.<br><br>
  <strong>Clinical risk lives in the PoS term, not the discount rate.</strong> The discount rate is a WACC-style 10%
  (Baras et al., <em>Nat Rev Drug Discov</em> 2012, median 10%; DiMasi 2016, 10.5% real; Alacrita 10–13%). Applying
  a venture-style 20–40% rate <em>and</em> probability weights double-counts the same risk, and is the most common
  error in published biotech valuations.<br><br>
  <strong>What the rNPV is not.</strong> It values one asset, on a lead-indication basis, over a single exclusivity
  window, at area-median commercial assumptions from Tendler et al. (<em>Ther Innov Regul Sci</em> 2026, n=391
  launches). It is not a price target and it does not value platforms, second indications, or pipelines. That is
  precisely why the "lead asset" column is expressed as coverage of the takeout price rather than as a
  buy/sell signal. <strong>Peak-sales figures are my own estimates</strong> — scaled off reported revenue for
  commercial names, area medians otherwise. A real desk would take them from FactSet or Evaluate consensus. They
  are the weakest input in the model and the first thing to replace.<br><br>
  <strong>An empirical model is shipped but not yet run.</strong> <code>pos_train.py</code> reconstructs development
  paths from AACT or ClinicalTrials.gov, labels each trial by whether its program advanced, and fits a calibrated
  gradient-boosted classifier with cross-validation grouped by sponsor. Its output blends with these priors rather
  than replacing them, because the registry label is biased upward by right-censoring, unregistered follow-on
  trials, and silent discontinuation. The ranking it produces across therapeutic areas is trustworthy; the absolute
  levels are not.</p>
</div>

<div class="card">
  <h2>Method and known weaknesses</h2>
  <p class="note" style="max-width:none">
  <strong>Firepower</strong> = max(0, 3.0 × LTM EBITDA − pro-forma net debt). Three point zero is the leverage an
  A−/BBB+ issuer can defend without a downgrade; it is a modelling convention, not a company target. Pro-forma
  adjusts for AbbVie/Apogee ($10.9B), GSK/Nuvalent ($10.6B) and Vertex/Crinetics ($8.8B) — announced, not closed,
  and therefore absent from the 30 June balance sheets.<br><br>
  <strong>EBITDA is stated before acquired IPR&amp;D and non-recurring items</strong>, which is the basis a rating
  agency uses for a leverage test. On strict GAAP the 2026 numbers are unusable for this purpose: Merck expensed
  $14.7B of acquired IPR&amp;D in H1-2026 (Cidara, Terns) and Gilead $11.3B (Arcellx, Tubulis, Ouro), which pushes
  Merck's GAAP LTM EBITDA to roughly $12B and Gilead's to roughly zero. Both are real cash outflows already
  reflected in net debt; expensing them again through EBITDA would double-count them.<br><br>
  <strong>Aggregate revenue at risk is de-duplicated.</strong> Three franchises are booked by two companies each —
  Pfizer's Eliquis alliance revenue derives from BMS's gross sales, Merck's Lynparza from AstraZeneca's, and
  Regeneron's collaboration revenue from Sanofi's Dupixent. That is $15.3B counted twice. The per-company lines are
  correct as shown; only the portfolio total is adjusted.<br><br>
  <strong>Three things this model gets wrong on purpose.</strong> First, it treats debt capacity as spendable,
  when several boards have said otherwise — Pfizer publicly guides to roughly $6B of remaining BD capacity against
  the $24B this model computes, and Gilead has said it is done for the year. Second, erosion is not modelled: a
  small-molecule cliff loses 55–70% in year one, a self-administered biologic around 40% (Stelara's actual year-one
  result), and a vaccine essentially nothing, so raw at-risk revenue overstates the economic hole for Merck's
  Gardasil and GSK's Shingrix. Third, premiums are medians applied mechanically; the real distribution is wide and
  leak-distorted, and several 2026 deals printed single-digit premiums to the prior close against 30–86% to VWAP.<br><br>
  <strong>Where the data is thin.</strong> Roche and Novartis publish no product-level patent table, so roughly $43B
  of at-risk revenue rests on estimated dates — Roche discloses nothing for Ocrevus, Hemlibra, Tecentriq, Kadcyla or
  Alecensa, and Novartis's only company statement is that Cosentyx expires "around the end of the decade." Both are
  flagged low confidence and should be read as unknown rather than estimated. Takeda does not disclose product-level revenue in its release.
  Boehringer Ingelheim is excluded entirely — it has the highest concentration in the industry (Jardiance plus Ofev,
  ~45% of group sales) but is private, so there is no balance sheet to model. Confidence is flagged per company in
  the table above.</p>
</div>

<footer>
  Built from company 10-K and 20-F patent tables, Q2-2026 earnings releases and balance sheets, FDA Orange Book
  exclusivity data, and 70 precedent transactions announced January 2024 – August 2026.
  Full line-level sourcing in the accompanying memo. Independent work, not investment advice.
</footer>
</div>

<div id="tip"></div>
<script>
const DATA = __DATA__;
const A = DATA.acquirers, T = DATA.targets, P = DATA.params;
const tip = document.getElementById('tip');
const fmt = (n,d=1)=>n.toFixed(d);
function show(e,html){tip.innerHTML=html;tip.style.opacity=1;move(e);}
function move(e){const r=tip.getBoundingClientRect();
  let x=e.clientX+14,y=e.clientY+14;
  if(x+r.width>innerWidth-10)x=e.clientX-r.width-14;
  if(y+r.height>innerHeight-10)y=e.clientY-r.height-14;
  tip.style.left=x+'px';tip.style.top=y+'px';}
function hide(){tip.style.opacity=0;}
const row=(k,v)=>`<div class="r"><span>${k}</span><b>${v}</b></div>`;
const SVG='http://www.w3.org/2000/svg';
function el(t,a){const n=document.createElementNS(SVG,t);for(const k in a)n.setAttribute(k,a[k]);return n;}

/* ---------- quadrant scatter ---------- */
(function(){
  const W=1080,H=650,m={t:26,r:30,b:52,l:64};
  const pw=W-m.l-m.r, ph=H-m.t-m.b;
  const xMax=90, yMax=90;
  const X=v=>m.l+v/xMax*pw, Y=v=>m.t+ph-v/yMax*ph;
  const rMax=Math.max(...A.map(a=>a.at_risk));
  const R=v=>7+Math.sqrt(v/rMax)*30;
  const s=el('svg',{viewBox:`0 0 ${W} ${H}`,role:'img','aria-label':'Urgency versus firepower'});

  for(let g=0;g<=yMax;g+=15){s.appendChild(el('line',{x1:m.l,x2:m.l+pw,y1:Y(g),y2:Y(g),class:'gl'}));
    const t=el('text',{x:m.l-11,y:Y(g)+4,class:'tk','text-anchor':'end'});t.textContent='$'+g+'B';s.appendChild(t);}
  for(let g=0;g<=xMax;g+=15){const t=el('text',{x:X(g),y:m.t+ph+22,class:'tk','text-anchor':'middle'});
    t.textContent=g;s.appendChild(t);}
  s.appendChild(el('line',{x1:m.l,x2:m.l+pw,y1:m.t+ph,y2:m.t+ph,class:'ax'}));
  s.appendChild(el('line',{x1:m.l,x2:m.l,y1:m.t,y2:m.t+ph,class:'ax'}));

  // quadrant dividers at cohort medians
  s.appendChild(el('line',{x1:X(P.u_med),x2:X(P.u_med),y1:m.t,y2:m.t+ph,class:'ax','stroke-dasharray':'0'}));
  s.appendChild(el('line',{x1:m.l,x2:m.l+pw,y1:Y(P.f_med),y2:Y(P.f_med),class:'ax'}));
  const q=(x,y,txt,anc)=>{const t=el('text',{x,y,class:'qd','text-anchor':anc});t.textContent=txt;s.appendChild(t);};
  q(m.l+pw-4,m.t+14,'MUST BUY · CAN BUY','end');
  q(m.l+4,m.t+14,'CAN BUY · NEEDN’T','start');
  q(m.l+pw-4,m.t+ph-8,'MUST BUY · CAN’T BUY','end');
  q(m.l+4,m.t+ph-8,'SIDELINED','start');

  const ax=el('text',{x:m.l+pw/2,y:H-8,class:'tk','text-anchor':'middle'});
  ax.textContent='Urgency score  (exposure depth 70% · cliff proximity 30%)';s.appendChild(ax);
  const ay=el('text',{x:-(m.t+ph/2),y:15,class:'tk','text-anchor':'middle',transform:'rotate(-90)'});
  ay.textContent='BD firepower to 3.0× leverage';s.appendChild(ay);

  // nudge labels that would collide
  // [dx, dy] — dy -1 = above the mark, +1 = below, 0 = beside it (vertically centred)
  const nudge={JNJ:[0,-1],LLY:[-34,0],RHHBY:[40,0],NVO:[0,-1],MRK:[-44,0],BMY:[0,1],
               AZN:[0,-1],REGN:[-44,0],SNY:[0,1],GILD:[0,1],PFE:[26,-1],NVS:[0,1],
               AMGN:[0,-1],GSK:[0,1],VRTX:[0,-1],ABBV:[0,1],TAK:[0,-1],BIIB:[0,-1],
               BAYRY:[48,1]};
  A.forEach(a=>{
    const cx=X(a.urgency),cy=Y(a.firepower),r=R(a.at_risk);
    const c=el('circle',{cx,cy,r,class:'dot'});
    c.addEventListener('mousemove',e=>show(e,`<b>${a.name}</b>`+
      row('Revenue at risk','$'+fmt(a.at_risk)+'B ('+a.pct_at_risk+'%)')+
      row('Peak expiry',a.peak_yr)+row('Urgency',a.urgency)+
      row('Net debt / EBITDA',a.lev+'×'+(a.pf_lev!==a.lev?' → '+a.pf_lev+'× PF':''))+
      row('Firepower','$'+fmt(a.firepower)+'B')+row('Coverage',a.coverage+'×')+
      `<div class="r" style="margin-top:7px;display:block">${a.note}</div>`));
    c.addEventListener('mouseleave',hide);
    s.appendChild(c);
    const n=nudge[a.ticker]||[0,-1];
    const ly = n[1]===0 ? cy+4 : (n[1]<0 ? cy-r-7 : cy+r+15);
    const anc = n[1]===0 ? (n[0]<0?'end':'start') : 'middle';
    const lx = n[1]===0 ? cx+(n[0]<0?-r-6:r+6) : cx+n[0];
    const t=el('text',{x:lx,y:ly,class:'lbl','text-anchor':anc});
    t.textContent=a.ticker;s.appendChild(t);
  });
  document.getElementById('scatter').appendChild(s);

  let h='<table><thead><tr><th>Company</th><th class="n">Rev $B</th><th class="n">At risk $B</th>'+
    '<th class="n">%</th><th class="n">Peak</th><th class="n">Urgency</th><th class="n">Lev</th>'+
    '<th class="n">Firepower $B</th><th class="n">Cov</th><th>Confidence</th></tr></thead><tbody>';
  A.forEach(a=>h+=`<tr><td class="tick">${a.name}</td><td class="n">${a.rev}</td>`+
    `<td class="n">${a.at_risk}</td><td class="n">${a.pct_at_risk}</td><td class="n">${a.peak_yr}</td>`+
    `<td class="n">${a.urgency}</td><td class="n">${a.pf_lev}×</td><td class="n">${a.firepower}</td>`+
    `<td class="n">${a.coverage}×</td><td class="mut">${a.conf}</td></tr>`);
  document.getElementById('acqtable').innerHTML=h+'</tbody></table>';
})();

/* ---------- exposure bars ---------- */
(function(){
  const d=[...A].sort((a,b)=>b.pct_at_risk-a.pct_at_risk);
  const W=500,rh=23,m={t:8,r:52,b:26,l:104},H=m.t+d.length*rh+m.b;
  const pw=W-m.l-m.r, max=80;
  const s=el('svg',{viewBox:`0 0 ${W} ${H}`,role:'img','aria-label':'Share of revenue at risk'});
  for(let g=0;g<=max;g+=20){const x=m.l+g/max*pw;
    s.appendChild(el('line',{x1:x,x2:x,y1:m.t,y2:m.t+d.length*rh,class:'gl'}));
    const t=el('text',{x,y:H-8,class:'tk','text-anchor':'middle'});t.textContent=g+'%';s.appendChild(t);}
  d.forEach((a,i)=>{
    const y=m.t+i*rh, w=Math.max(2,a.pct_at_risk/max*pw), bh=rh-9;
    const g=el('g',{class:'brow'});
    g.appendChild(el('rect',{x:m.l,y:y+4,width:w,height:bh,rx:4,class:'bar'}));
    const nm=el('text',{x:m.l-9,y:y+4+bh-2,class:'tk','text-anchor':'end'});nm.textContent=a.name;
    g.appendChild(nm);
    const v=el('text',{x:m.l+w+7,y:y+4+bh-2,class:'lbl'});v.textContent=a.pct_at_risk+'%';g.appendChild(v);
    g.appendChild(el('rect',{x:m.l,y,width:pw,height:rh,fill:'transparent'}));
    g.addEventListener('mousemove',e=>show(e,`<b>${a.name}</b>`+
      row('At risk 2027–32','$'+fmt(a.at_risk)+'B')+row('Of revenue',a.pct_at_risk+'%')+
      row('Peak expiry',a.peak_yr)));
    g.addEventListener('mouseleave',hide);
    s.appendChild(g);
  });
  document.getElementById('bars1').appendChild(s);
})();

/* ---------- hole vs wallet ---------- */
(function(){
  const d=[...A].sort((a,b)=>b.at_risk-a.at_risk);
  const W=500,rh=28,m={t:8,r:46,b:26,l:104},H=m.t+d.length*rh+m.b;
  const pw=W-m.l-m.r, max=90;
  const s=el('svg',{viewBox:`0 0 ${W} ${H}`,role:'img','aria-label':'Revenue at risk versus firepower'});
  for(let g=0;g<=max;g+=30){const x=m.l+g/max*pw;
    s.appendChild(el('line',{x1:x,x2:x,y1:m.t,y2:m.t+d.length*rh,class:'gl'}));
    const t=el('text',{x,y:H-8,class:'tk','text-anchor':'middle'});t.textContent='$'+g+'B';s.appendChild(t);}
  d.forEach((a,i)=>{
    const y=m.t+i*rh, bh=9;
    const g=el('g',{class:'brow'});
    g.appendChild(el('rect',{x:m.l,y:y+3,width:Math.max(2,a.at_risk/max*pw),height:bh,rx:4,class:'bar2'}));
    g.appendChild(el('rect',{x:m.l,y:y+3+bh+2,width:Math.max(2,a.firepower/max*pw),height:bh,rx:4,class:'bar'}));
    const nm=el('text',{x:m.l-9,y:y+16,class:'tk','text-anchor':'end'});nm.textContent=a.name;g.appendChild(nm);
    g.appendChild(el('rect',{x:m.l,y,width:pw,height:rh,fill:'transparent'}));
    g.addEventListener('mousemove',e=>show(e,`<b>${a.name}</b>`+
      row('Revenue at risk','$'+fmt(a.at_risk)+'B')+row('Firepower','$'+fmt(a.firepower)+'B')+
      row('Coverage',a.coverage+'×')+
      `<div class="r" style="margin-top:7px;display:block">${a.quadrant}</div>`));
    g.addEventListener('mouseleave',hide);
    s.appendChild(g);
  });
  document.getElementById('bars2').appendChild(s);
})();

/* ---------- target table ---------- */
(function(){
  const tb=document.querySelector('#tgt tbody');
  const areas=['All',...new Set(T.map(t=>t.ta))];
  let area='All', key='fit', dir=-1;
  const fbox=document.getElementById('filters');
  areas.forEach(a=>{const b=document.createElement('button');b.textContent=a;
    b.setAttribute('aria-pressed',a===area);
    b.onclick=()=>{area=a;[...fbox.children].forEach(c=>c.setAttribute('aria-pressed',c.textContent===a));draw();};
    fbox.appendChild(b);});
  document.querySelectorAll('#tgt th').forEach(th=>th.onclick=()=>{
    const k=th.dataset.k; dir = key===k ? -dir : (typeof T[0][k]==='number'?-1:1); key=k; draw();});
  function draw(){
    const rows=T.filter(t=>area==='All'||t.ta===area).sort((a,b)=>{
      const x=a[key],y=b[key];
      return (typeof x==='number'? x-y : String(x).localeCompare(String(y)))*dir;});
    tb.innerHTML=rows.map(t=>`<tr>
      <td class="n"><span class="fitbar"><span style="width:${t.fit}%"></span></span>${fmt(t.fit,1)}</td>
      <td><span class="tick">${t.name}</span> <span class="mut">${t.ticker}</span>
          <div class="mut">${t.thesis}</div></td>
      <td class="mut">${t.ta}</td>
      <td><span>${t.asset}</span><div class="mut">${t.mech}</div></td>
      <td><span class="pill">${t.phase}</span></td>
      <td class="n">${t.pos_phase==='Commercial'?'<span class="mut">approved</span>':fmt(t.pos,0)+'%'}</td>
      <td class="n">$${fmt(t.mcap)}B</td>
      <td class="n"><b>$${fmt(t.takeout)}B</b> <span class="mut">+${fmt(t.premium,0)}%</span></td>
      <td class="n">$${fmt(t.rnpv)}B</td>
      <td class="n"><span class="fitbar" style="width:44px"><span style="width:${Math.min(t.cover,100)}%"></span></span>${fmt(t.cover,0)}%</td>
      <td class="mut">${t.capable.length?t.capable.join(' '):'— none'}</td></tr>`).join('');
  }
  draw();
})();

/* ---------- theme ---------- */
(function(){
  const b=document.getElementById('tt');
  const cur=()=>document.documentElement.getAttribute('data-theme')||
    (matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light');
  const set=()=>b.textContent=cur()==='dark'?'Light':'Dark'; set();
  b.onclick=()=>{document.documentElement.setAttribute('data-theme',cur()==='dark'?'light':'dark');set();};
})();
document.addEventListener('scroll',hide,{passive:true});
</script></body></html>"""

t = D["totals"]
rep = {
    "__DATA__": json.dumps(D, separators=(",", ":")),
    "__NACQ__": str(len(D["acquirers"])), "__NTGT__": str(t["n_targets"]),
    "__ATRISK__": str(t["at_risk"]), "__PCTRISK__": str(t["pct_at_risk"]),
    "__REV__": str(t["rev"]), "__FIRE__": str(t["firepower"]),
    "__TAKE__": str(t["takeout_universe"]),
    "__DEDUP__": str(t["at_risk_dedup"]), "__PCTDEDUP__": str(t["pct_at_risk_dedup"]),
    "__COV__": f"{t['firepower']/t['at_risk_dedup']:.2f}",
}
for k, v in rep.items():
    HTML = HTML.replace(k, v)
open("/home/claude/patent-cliff-map/patent-cliff-map.html", "w").write(HTML)
print("built", len(HTML), "bytes")
