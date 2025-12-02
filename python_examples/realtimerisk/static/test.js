function wsURL(path){
  const proto = (location.protocol === 'https:') ? 'wss' : 'ws';
  const host = location.host || 'localhost:8000';
  if (path.startsWith('/')) return `${proto}://${host}${path}`;
  return `${proto}://${host}/${path}`;
}

const elStatus = document.getElementById('status');
const elLog = document.getElementById('log');
const btnPing = document.getElementById('btnPing');

function log(line, cls){
  const p = document.createElement('div');
  if (cls) p.className = cls;
  p.textContent = `[${new Date().toLocaleTimeString()}] ${line}`;
  elLog.appendChild(p);
  elLog.scrollTop = elLog.scrollHeight;
}

const sock = new WebSocket(wsURL('/ws/alerts'));
sock.onopen = () => { elStatus.textContent = 'connected'; log('connected', 'ok'); };
sock.onclose = (ev) => { elStatus.textContent = 'closed'; log(`closed code=${ev.code}`, 'err'); };
sock.onerror = (ev) => { log('error (see console)', 'err'); console.error(ev); };
sock.onmessage = (ev) => {
  try{
    const msg = JSON.parse(ev.data);
    log(`message: ${JSON.stringify(msg)}`);
  }catch(e){
    log(`text: ${ev.data}`);
  }
};

btnPing.onclick = () => {
  if (sock.readyState === WebSocket.OPEN){
    sock.send('ping');
    log('sent: ping');
  }
};
