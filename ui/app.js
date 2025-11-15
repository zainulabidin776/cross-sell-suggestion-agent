const baseUrl = window.location.origin;

const $ = id => document.getElementById(id);

async function postJson(path, body){
  const res = await fetch(path, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(body)
  });
  return res;
}

$('btn_recommend').addEventListener('click', async ()=>{
  const product_id = $('product_id').value.trim();
  const session_id = $('session_id').value.trim();
  const limit = parseInt($('limit').value) || 3;
  if(!product_id){ alert('Enter product_id'); return; }

  const payload = { product_id, session_id: session_id || undefined, limit };
  $('output').textContent = 'Loading...';
  try{
    const r = await postJson('/api/recommend', payload);
    const j = await r.json();
    $('output').textContent = JSON.stringify(j, null, 2);
  }catch(e){
    $('output').textContent = 'Error: ' + e.toString();
  }
});

$('btn_search').addEventListener('click', async ()=>{
  const q = $('search_query').value.trim();
  if(!q){ alert('Enter search query'); return; }
  $('output').textContent = 'Searching...';
  try{
    const r = await postJson('/api/search', { query: q, session_id: 'ui_search' });
    const j = await r.json();
    $('output').textContent = JSON.stringify(j, null, 2);
  }catch(e){ $('output').textContent = 'Error: ' + e.toString(); }
});

$('btn_status').addEventListener('click', async ()=>{
  $('status_area').textContent = 'Loading...';
  try{
    const r = await fetch('/api/status');
    const j = await r.json();
    $('status_area').textContent = JSON.stringify(j, null, 2);
  }catch(e){ $('status_area').textContent = 'Error: ' + e.toString(); }
});

// Initialize default example
document.addEventListener('DOMContentLoaded', ()=>{
  $('product_id').value = 'laptop';
});
