
// Append to Curve tab Alerts table (TS & Text)
function appendAlertRowCurve(tsEpoch, text){
  try{
    const tbody = document.getElementById('alertsTableCurve')?.querySelector('tbody');
    if(!tbody) return;
    const tr = document.createElement('tr');
    const ts = new Date(tsEpoch*1000).toLocaleString();
    const tdTs = document.createElement('td'); tdTs.textContent = ts;
    const tdText = document.createElement('td'); tdText.textContent = text;
    tr.appendChild(tdTs); tr.appendChild(tdText);
    tbody.prepend(tr);
    while (tbody.rows.length > 200) tbody.deleteRow(200);
  }catch(e){ console.error('appendAlertRowCurve error', e); }
}

// ===== Globals =====
const TENOR_ORDER = ["1W","2W","1M","2M","3M","6M","9M","1Y","18M","2Y","3Y","4Y","5Y","6Y","7Y","8Y","9Y","10Y"];
let curvePoints = {}; // tenor -> value
let chart = null; // Chart.js instance

// ===== Utils =====
function qs(id){ return document.getElementById(id); }
function logLine(msg){
  const el = qs('log'); if(!el) return;
  const line = document.createElement('div');
  const ts = new Date().toISOString().replace('T',' ').slice(0,19);
  line.textContent = `[${ts}] ${msg}`;
  el.appendChild(line); el.scrollTop = el.scrollHeight;
}
function setStatus(connected){
  document.body.dataset.ws = connected ? 'on' : 'off';
  const dot = qs('connDot'); if(dot) dot.style.background = connected ? 'var(--ok)' : 'var(--danger)';
  const lab = qs('connLabel'); if(lab) lab.textContent = connected ? 'connected' : 'disconnected';
}
function fmtTs(ts){
  try { if (typeof ts === 'number') return new Date(ts*1000).toLocaleString();
        if (typeof ts === 'string') return new Date(ts).toLocaleString(); } catch {}
  return String(ts ?? '—');
}
function themeColors(){
  const s = getComputedStyle(document.documentElement);
  return {
    grid: s.getPropertyValue('--border').trim() || '#2a3448',
    text: s.getPropertyValue('--text').trim() || '#e2e8f0',
    line: s.getPropertyValue('--accent').trim() || '#38bdf8',
    bg: s.getPropertyValue('--bg').trim() || '#0b1220',
    card: s.getPropertyValue('--card').trim() || '#0f172a',
  };
}

// ===== Table =====
function upsertYieldRow(obj){
  const tb = qs('yieldTable')?.querySelector('tbody'); if(!tb) return;
  const k = obj.tenor || '—';
  let tr = Array.from(tb.querySelectorAll('tr')).find(r => r.dataset.tenor === k);
  if (!tr){
    tr = document.createElement('tr'); tr.dataset.tenor = k;
    ['tenor','value','instrument','currency','valuationDate','publishedAt','source'].forEach((col)=>{
      const td = document.createElement('td'); td.dataset.col = col; tr.appendChild(td);
    });
    tb.appendChild(tr);
  }
  tr.querySelector('td[data-col="tenor"]').textContent = k;
  tr.querySelector('td[data-col="value"]').textContent = (obj.value!=null? obj.value : '—');
  tr.querySelector('td[data-col="instrument"]').textContent = obj.instrument || '—';
  tr.querySelector('td[data-col="currency"]').textContent = obj.currency || '—';
  tr.querySelector('td[data-col="valuationDate"]').textContent = obj.valuationDate || '—';
  tr.querySelector('td[data-col="publishedAt"]').textContent = obj.publishedAt ? fmtTs(obj.publishedAt) : '—';
  tr.querySelector('td[data-col="source"]').textContent = obj.source || '—';
}

// ===== Chart.js =====
function computeYBounds(){
  const vals = TENOR_ORDER.map(t => (curvePoints[t] != null ? +curvePoints[t] : null)).filter(v => v != null && !isNaN(v));
  if (vals.length === 0) return {min: 0, max: 1};
  let vmin = Math.min(...vals), vmax = Math.max(...vals);
  if (vmin === vmax){
    const pad = (Math.abs(vmin) || 1) * 0.05;
    vmin -= pad; vmax += pad;
  } else {
    const pad = (vmax - vmin) * 0.1;
    vmin -= pad; vmax += pad;
  }
  return {min: vmin, max: vmax};
}
function createChart(){
  const el = qs('chart'); if(!el || !window.Chart) return;
  const ctx = el.getContext('2d');
  const c = themeColors();
  if (chart) { chart.destroy(); chart = null; }

  const gradient = ctx.createLinearGradient(0, 0, 0, el.height || 300);
  gradient.addColorStop(0, (c.line || '#38bdf8') + '33');
  gradient.addColorStop(1, c.bg || '#0b1220');

  const bounds = computeYBounds();

  chart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: TENOR_ORDER,
      datasets: [{
        label: 'Yield',
        data: TENOR_ORDER.map(t => (curvePoints[t] != null ? +curvePoints[t] : null)),
        spanGaps: true,
        tension: 0.35,
        borderWidth: 2.5,
        pointRadius: 4,
        pointHoverRadius: 6,
        borderColor: c.line || '#38bdf8',
        pointBackgroundColor: c.bg || '#0b1220',
        pointBorderColor: c.line || '#38bdf8',
        fill: { target: 'origin', above: gradient, below: gradient },
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 400 },
      interaction: { mode: 'nearest', intersect: false },
      plugins: {
        legend: { display: false },
        title: { display: true, text: 'Yield Curve (CSV + WS)', color: c.text || '#e2e8f0', padding: {bottom: 10} },
        tooltip: {
          callbacks: {
            title: (items) => (items && items[0] && items[0].label ? `Tenor: ${items[0].label}` : ''),
            label: (ctx) => {
              const y = ctx.parsed && ctx.parsed.y;
              if (y == null) return 'Yield: —';
              return `Yield: ${(y*100).toFixed(2)}%`;
            }
          },
          backgroundColor: c.card || c.bg || '#0f172a',
          titleColor: c.text || '#e2e8f0',
          bodyColor: c.text || '#e2e8f0',
          borderColor: c.grid || '#2a3448',
          borderWidth: 1
        }
      },
      scales: {
        x: {
          title: { display: true, text: 'Tenor', color: c.text || '#e2e8f0' },
          grid: { color: c.grid || '#2a3448', lineWidth: 1, tickLength: 4 },
          ticks: { color: c.text || '#e2e8f0' }
        },
        y: {
          title: { display: true, text: 'Yield (%)', color: c.text || '#e2e8f0' },
          grid: { color: c.grid || '#2a3448', lineWidth: 1 },
          ticks: { color: c.text || '#e2e8f0', callback: function(value){ try { return (value*100).toFixed(1)+'%'; } catch(e){ return value; } } },
          reverse: false,
          beginAtZero: false,
          suggestedMin: bounds.min,
          suggestedMax: bounds.max
        }
      }
    }
  });
}
function updateChart(){
  if (!chart || !window.Chart) { createChart(); return; }
  const c = themeColors();
  const bounds = computeYBounds();
  const ds = chart.data.datasets[0];
  ds.data = TENOR_ORDER.map(t => (curvePoints[t] != null ? +curvePoints[t] : null));
  ds.borderColor = c.line || '#38bdf8';
  ds.pointBorderColor = c.line || '#38bdf8';
  ds.pointBackgroundColor = c.bg || '#0b1220';
  chart.options.plugins.title.color = c.text || '#e2e8f0';
  chart.options.scales.x.grid.color = c.grid || '#2a3448';
  chart.options.scales.y.grid.color = c.grid || '#2a3448';
  chart.options.scales.x.ticks.color = c.text || '#e2e8f0';
  chart.options.scales.y.ticks.color = c.text || '#e2e8f0';
  chart.options.scales.x.title.color = c.text || '#e2e8f0';
  chart.options.scales.y.title.color = c.text || '#e2e8f0';
  chart.options.scales.y.beginAtZero = false;
  chart.options.scales.y.reverse = false;
  chart.options.scales.y.suggestedMin = bounds.min;
  chart.options.scales.y.suggestedMax = bounds.max;
  chart.update('none');
}
// Backward compatibility
function redrawChart(){ updateChart(); }

// ===== CSV Bootstrap =====
async function loadCSV(){
  try{
    const res = await fetch('yielddata.csv', {cache:'no-store'});
    if(!res.ok) throw new Error('yielddata.csv not found');
    const text = await res.text();
    const firstLine = text.split(/\r?\n/)[0] || '';
    const delim = (firstLine.indexOf(';')>-1 && firstLine.indexOf(',')===-1) ? ';' : ',';
    const rows = text.trim().split(/\r?\n/).filter(r=>r.trim().length>0);
    const header = rows.shift().replace(/^\ufeff/, '').split(delim).map(h=>h.trim().toLowerCase());
    function idx(name){ const i = header.indexOf(name.toLowerCase()); return i>=0 ? i : -1; }
    const ti = idx('tenor'), vi = idx('value'), vdi = idx('valuationdate'), insi = idx('instrument'), curi = idx('currency'), src = idx('source');
    for(const row of rows){
      const cols = row.split(delim).map(c=>c.trim());
      const tenor = ti>=0 ? cols[ti] : null;
      let val = vi>=0 ? cols[vi] : null;
      if (val!=null){ val = val.replace('%','').replace(',','.'); }
      const fval = parseFloat(val);
      if(!tenor || Number.isNaN(fval)) continue;
      curvePoints[tenor] = fval;
      upsertYieldRow({ tenor, value:fval, instrument: insi>=0?cols[insi]:'', currency: curi>=0?cols[curi]:'', valuationDate: vdi>=0?cols[vdi]:'', publishedAt:'', source: src>=0?cols[src]:'csv' });
    }
    const ts = (new Date()).toISOString(); const el = qs('lastTs'); if (el) el.textContent = Object.keys(curvePoints).length ? ts : '—';
    logLine('bootstrapped from yielddata.csv ('+Object.keys(curvePoints).length+' points)');
    updateChart();
  }catch(e){
    logLine('CSV bootstrap error: '+(e && e.message ? e.message : e));
  }
}

// ===== WS (Yield) =====
let YIELD_WS = null, manualDisconnect = false, reconnectTimer = null;
function currentYieldCandidates(){
  const inp = qs('wsUrl'); const base = (inp && inp.value.trim()) || 'ws://localhost:8000/ws/yield';
  const list = [];
  if (/^wss?:\/\//i.test(base)) list.push(base);
  else { if (base.startsWith('/')) list.push(location.origin.replace(/^http/,'ws') + base); }
  list.push('ws://localhost:8000/ws/yield'); list.push('ws://127.0.0.1:8000/ws/yield');
  list.push('ws://localhost:8000/ws?channel=yield'); list.push('ws://127.0.0.1:8000/ws?channel=yield');
  return Array.from(new Set(list));
}
function tryConnectYield(cands, idx){
  if (manualDisconnect) return;
  if (idx >= cands.length){ logLine('All yield endpoints failed. Retrying in 3s...'); reconnectTimer = setTimeout(()=>connectWS(), 3000); return; }
  const url = cands[idx]; logLine(`connecting to ${url}`);
  const ws = new WebSocket(url); YIELD_WS = ws;
  ws.onopen = () => { setStatus(true); logLine('yield ws connected'); };
  ws.onmessage = (ev) => {
    try{
      const obj = JSON.parse(ev.data);
      if (obj && obj.tenor !== undefined){
        curvePoints[obj.tenor] = obj.value; upsertYieldRow(obj); updateChart();
        if (obj.publishedAt) qs('lastTs').textContent = fmtTs(obj.publishedAt);
      } else if (obj && obj.message){ logLine(`msg: ${obj.message}`); }
      else { logLine(`raw: ${ev.data.slice(0,200)}`); }
    }catch(e){ logLine(`parse error: ${e}`); }
  };
  ws.onerror = () => { logLine(`yield ws error on ${url}`); };
  ws.onclose = () => { setStatus(false); if (!manualDisconnect){ logLine(`yield ws closed on ${url}`); tryConnectYield(cands, idx+1); } };
}
function connectWS(){ manualDisconnect = false; clearTimeout(reconnectTimer); tryConnectYield(currentYieldCandidates(), 0); }
function disconnectWS(){ manualDisconnect = true; clearTimeout(reconnectTimer); try{ YIELD_WS && YIELD_WS.close(); }catch{}; setStatus(false); }


// ===== POSITIONS (DB-Live) =====
let POS_WS = null, posReconnectTimer = null, manualPosDisconnect = false, posPollTimer = null;

function setPositionsStatus(ok){
  const s = document.getElementById('positionsStatus'); if (s) s.textContent = ok ? 'connected' : 'disconnected';
  const d = document.getElementById('positionsDot'); if (d) d.style.background = ok ? 'var(--ok)' : 'var(--danger)';
}
function normalizePosRow(r){
  // Accept multiple key variants from backend and map to UI columns
  const get = (obj, keys, def='—')=>{
    for (const k of keys){ if (obj[k] != null) return obj[k]; }
    return def;
  };
  return {
    TradeID: get(r, ['TradeID','trade_id','id','tradeId']),
    ISIN: get(r, ['ISIN','isin','isin_code','instrument','code']),
    SettlementDate: get(r, ['SettlementDate','settlementDate','settlement_date','date','valuationDate']),
    Notional: get(r, ['Notional','notional','qty','quantity','size','amount']),
    Side: get(r, ['Side','side','buysell','direction','type'])
  };
}
function renderPositionsRows(rows){
  const tb = document.querySelector('#positionsTable tbody'); if(!tb) return;
  tb.innerHTML = '';
  (rows||[]).forEach(r=>{
    const n = normalizePosRow(r);
    const tr = document.createElement('tr');
    const td = (v)=>{ const e=document.createElement('td'); e.textContent = v; return e; };
    tr.appendChild(td(n.TradeID));
    tr.appendChild(td(n.ISIN));
    tr.appendChild(td(n.SettlementDate));
    tr.appendChild(td(n.Notional));
    tr.appendChild(td(n.Side));
    tb.appendChild(tr);
  });
}
function currentPositionsCandidates(){
  const txt = document.getElementById('txtPositionsWs');
  const base = (txt && txt.value.trim()) || 'ws://localhost:8000/ws/positions';
  const list = [];
  if (/^wss?:\/\//i.test(base)) list.push(base);
  else if (base.startsWith('/')) list.push(location.origin.replace(/^http/,'ws') + base);
  list.push('ws://localhost:8000/ws/positions'); list.push('ws://127.0.0.1:8000/ws/positions');
  list.push('ws://localhost:8000/ws?channel=positions'); list.push('ws://127.0.0.1:8000/ws?channel=positions');
  return Array.from(new Set(list));
}
function connectPositionsWS(){
  manualPosDisconnect = false;
  clearTimeout(posReconnectTimer);
  const cands = currentPositionsCandidates(); let i = 0;
  function next(){
    if (i >= cands.length){
      console.log('positions: all WS endpoints failed, fallback to REST poll');
      setPositionsStatus(false);
      startPositionsPoll(); // fallback
      posReconnectTimer = setTimeout(connectPositionsWS, 10000); // retry WS occasionally
      return;
    }
    const url = cands[i++]; console.log('positions: connecting', url);
    stopPositionsPoll();
    try{
      const ws = new WebSocket(url); POS_WS = ws;
      ws.onopen = ()=>{ setPositionsStatus(true); console.log('positions: ws connected'); };
      ws.onmessage = (ev)=>{
        try{
          const msg = JSON.parse(ev.data);
          if (Array.isArray(msg)) renderPositionsRows(msg);
          else if (msg && msg.rows && Array.isArray(msg.rows)) renderPositionsRows(msg.rows);
          else if (msg && msg.row) renderPositionsRows([msg.row]);
          else if (msg && msg.type==='ping'){ /* ignore */ }
          else { /* unknown; try append single line */ renderPositionsRows([msg]); }
        }catch(e){
          // plain text row?
          renderPositionsRows([{TradeID:'—', ISIN:String(ev.data).slice(0,60), SettlementDate:'—', Notional:'—', Side:'—'}]);
        }
      };
      ws.onerror = ()=>{ console.log('positions ws error'); };
      ws.onclose = ()=>{
        setPositionsStatus(false);
        if (!manualPosDisconnect){ console.log('positions ws closed'); next(); }
      };
    }catch(e){
      console.log('positions connect err', e);
      setTimeout(next, 500);
    }
  }
  next();
}
function disconnectPositionsWS(){
  manualPosDisconnect = true;
  try{ if (POS_WS){ POS_WS.close(); POS_WS = null; } }catch(e){}
  setPositionsStatus(false);
  startPositionsPoll(); // keep data via REST if available
}

// REST fallback
async function fetchPositionsOnce(){
  try{
    const url = (document.getElementById('txtPositionsRest')?.value || '/positions').trim();
    const res = await fetch(url, {cache:'no-store'});
    if (!res.ok) throw new Error('HTTP '+res.status);
    const data = await res.json();
    if (Array.isArray(data)) renderPositionsRows(data);
    else if (data && Array.isArray(data.rows)) renderPositionsRows(data.rows);
    else renderPositionsRows([]);
  }catch(e){ console.error('fetchPositionsOnce', e); }
}
function startPositionsPoll(intervalMs=5000){
  stopPositionsPoll();
  posPollTimer = setInterval(fetchPositionsOnce, intervalMs);
  fetchPositionsOnce();
}
function stopPositionsPoll(){
  if (posPollTimer){ clearInterval(posPollTimer); posPollTimer = null; }
}

// ===== WS (Alerts) =====
let ALERTS_WS = null, alertsReconnectTimer = null, manualAlertsDisconnect = false;
function setAlertsStatus(ok){ const el = qs('alertsStatus'); if (el) el.textContent = ok ? 'connected' : 'disconnected'; const dot = qs('alertsDot'); if (dot) dot.style.background = ok ? 'var(--ok)' : 'var(--danger)'; }
function currentAlertsCandidates(){
  const txt = qs('txtAlertsWs'); const base = (txt && txt.value.trim()) || 'ws://localhost:8000/ws/alerts';
  const list = [];
  if (/^wss?:\/\//i.test(base)) list.push(base);
  else if (base.startsWith('/')) list.push(location.origin.replace(/^http/,'ws') + base);
  list.push('ws://localhost:8000/ws/alerts'); list.push('ws://127.0.0.1:8000/ws/alerts');
  list.push('ws://localhost:8000/ws?channel=alerts'); list.push('ws://127.0.0.1:8000/ws?channel=alerts');
  return Array.from(new Set(list));
}
function upsertAlertRow(obj){
  const tb = qs('alertsTableBody'); if(!tb) return;
  const tr = document.createElement('tr');
  const td = (t)=>{ const e = document.createElement('td'); e.textContent = t; return e; };
  tr.appendChild(td(fmtTs(obj.ts || obj.publishedAt || Date.now()/1000)));
  tr.appendChild(td(obj.text || '—'));
  tb.prepend(tr);
}
function connectAlerts(){
  manualAlertsDisconnect = false;
  clearTimeout(alertsReconnectTimer);
  const cands = currentAlertsCandidates(); let i = 0;
  function next(){
    if (i >= cands.length){
      logLine('All alerts endpoints failed. Retrying in 3s...');
      alertsReconnectTimer = setTimeout(connectAlerts, 3000);
      return;
    }
    const url = cands[i++]; logLine(`alerts: connecting ${url}`);
    try{
      const ws = new WebSocket(url); ALERTS_WS = ws;
      ws.onopen = ()=>{ setAlertsStatus(true); logLine('alerts connected'); };
      ws.onmessage = (ev)=>{
        try { const obj = JSON.parse(ev.data); upsertAlertRow(obj); }
        catch (e) { upsertAlertRow({text: ev.data}); }
      };
      ws.onerror = ()=>{ logLine('alerts ws error'); };
      ws.onclose = ()=>{
        setAlertsStatus(false);
        if (!manualAlertsDisconnect){ logLine('alerts ws closed'); next(); }
      };
    }catch(e){ logLine(`alerts connect err: ${e}`); setTimeout(next, 500); }
  }
  next();
}
function disconnectAlerts(){
  manualAlertsDisconnect = true;
  try{ if (ALERTS_WS){ ALERTS_WS.close(); ALERTS_WS = null; } }catch(e){}
  clearTimeout(alertsReconnectTimer);
  setAlertsStatus(false);
}

// ===== Tabs & Theme =====
document.addEventListener('DOMContentLoaded', () => {
  // tabs
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
      btn.classList.add('active'); document.getElementById(btn.dataset.tab).classList.add('active');
    });
  });
  // theme
  function setTheme(t){
    document.documentElement.setAttribute('data-theme', t);
    try{ localStorage.setItem('ui_theme', t); }catch(e){}
    updateChart();
  }
  qs('btnThemeBlack')?.addEventListener('click', ()=>setTheme('black'));
  qs('btnThemeDark')?.addEventListener('click', ()=>setTheme('dark'));
  qs('btnThemeLight')?.addEventListener('click', ()=>setTheme('light'));
  // wire service controls
  qs('btnConnect')?.addEventListener('click', ()=>{ try{ disconnectWS(); }catch(e){} connectWS(); });
  qs('btnDisconnect')?.addEventListener('click', ()=>{ disconnectWS(); });
  qs('btnAlertsConnect')?.addEventListener('click', ()=>{ try{ disconnectAlerts(); }catch(e){} connectAlerts(); });
  qs('btnAlertsDisconnect')?.addEventListener('click', ()=>{ disconnectAlerts(); });
  qs('btnClear')?.addEventListener('click', ()=>{ const log = qs('log'); if (log) log.innerHTML=''; });
  qs('btnPositionsConnect')?.addEventListener('click', ()=>{ try{ disconnectPositionsWS(); }catch{} connectPositionsWS(); });
  qs('btnPositionsDisconnect')?.addEventListener('click', ()=>{ disconnectPositionsWS(); });
  qs('btnPositionsRefresh')?.addEventListener('click', ()=>{ fetchPositionsOnce(); });
  qs('btnClearAlerts')?.addEventListener('click', ()=>{ const tb = qs('alertsTableBody'); if (tb) tb.innerHTML=''; });


  // bootstrap
  updateChart();            // will create on first run
  loadCSV();                // preload from CSV
  connectWS();              // connect yield
  connectAlerts();          // connect alerts
});

// Hook wsAlerts to feed Curve tab alerts table
(function(){
  try{
    if (typeof wsAlerts !== 'undefined' && wsAlerts && typeof wsAlerts.addEventListener === 'function'){
      wsAlerts.addEventListener('message', function(ev){
        try{
          const msg = JSON.parse(ev.data);
          if (msg && msg.text && msg.ts) appendAlertRowCurve(msg.ts, msg.text);
        }catch(e){}
      });
    }
  }catch(e){}
})();
