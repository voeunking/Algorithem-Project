(function(){
  const searchInp = document.getElementById('popSearch');
  const categorySel = document.getElementById('popCategory');
  const startInp = document.getElementById('popStart');
  const endInp = document.getElementById('popEnd');
  const limitSel = document.getElementById('popLimit');
  const sortSel = document.getElementById('popSort');

  const tableBody = document.querySelector('#popTable tbody');
  const topCards = document.getElementById('topCards');

  let state = {
    q: '',
    category: '',
    start: '',
    end: '',
    limit: 20,
    sort: 'count',
    order: 'desc'
  };

  function setDefaultDates(){
    const end = new Date();
    const start = new Date();
    start.setDate(end.getDate()-30);
    startInp.value = start.toISOString().slice(0,10);
    endInp.value = end.toISOString().slice(0,10);
  }

  function availabilityBadge(total, avail){
    const cls = avail <= 0 ? 'out' : (avail <= Math.max(1, Math.floor(total*0.2)) ? 'low' : 'available');
    return `<span class="badge badge-availability ${cls}">${avail}/${total}</span>`;
  }

  function params(){
    const p = new URLSearchParams();
    if(state.q) p.set('q', state.q);
    if(state.category) p.set('category', state.category);
    if(startInp.value) p.set('start', startInp.value);
    if(endInp.value) p.set('end', endInp.value);
    p.set('limit', limitSel.value || '20');
    p.set('sort', sortSel.value || 'count');
    p.set('order', 'desc');
    return p.toString();
  }

  async function fetchCategories(){
    const res = await fetch('/books/api/categories');
    const data = await res.json();
    (data.categories || []).forEach(c => {
      const opt = document.createElement('option');
      opt.value = c; opt.textContent = c;
      categorySel.appendChild(opt);
    });
  }

  async function load(){
    const res = await fetch('/books/api/popular?' + params());
    const data = await res.json();
    renderTopCards(data.items || []);
    renderTable(data.items || []);
  }

  function renderTopCards(items){
    const top = items.slice(0, 3);
    topCards.innerHTML = '';
    top.forEach((b, idx)=>{
      const col = document.createElement('div');
      col.className = 'col-md-4';
      col.innerHTML = `
        <div class="card-pop">
          <div class="d-flex justify-content-between align-items-start mb-1">
            <div class="badge bg-primary">#${idx+1}</div>
            <div class="small text-muted">${b.count} issues</div>
          </div>
          <div class="title mb-1">${escapeHtml(b.title || '')}</div>
          <div class="meta mb-2">${escapeHtml(b.author || '')} ${b.publisher? ' • '+escapeHtml(b.publisher): ''}</div>
          <div class="d-flex justify-content-between align-items-center">
            <span class="badge-soft">${escapeHtml(b.category || 'Uncategorized')}</span>
            ${availabilityBadge(b.total_copies || 0, b.available_copies || 0)}
          </div>
        </div>`;
      topCards.appendChild(col);
    });
  }

  function renderTable(items){
    tableBody.innerHTML = '';
    items.forEach((b, idx)=>{
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${idx+1}</td>
        <td>${escapeHtml(b.title || '')}</td>
        <td>${escapeHtml(b.author || '')}</td>
        <td>${escapeHtml(b.publisher || '')}</td>
        <td>${escapeHtml(b.category || '')}</td>
        <td class="text-center">${b.total_copies ?? ''}</td>
        <td class="text-center">${availabilityBadge(b.total_copies || 0, b.available_copies || 0)}</td>
        <td class="text-center"><span class="badge bg-primary">${b.count}</span></td>
        <td>
          <div class="btn-group btn-group-sm" role="group">
            <a class="btn btn-outline-secondary" href="/books?q=${encodeURIComponent(b.title||'')}"><i class="fas fa-eye"></i></a>
          </div>
        </td>
      `;
      tableBody.appendChild(tr);
    });
  }

  function debounce(fn, ms){ let t; return (...a)=>{ clearTimeout(t); t=setTimeout(()=>fn(...a), ms); }; }
  function escapeHtml(str){ return String(str).replace(/[&<>"']/g, s => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;','\'':'&#39;'}[s])); }

  // Events
  searchInp.addEventListener('input', debounce(()=>{ state.q = searchInp.value.trim(); load(); }, 300));
  categorySel.addEventListener('change', ()=>{ state.category = categorySel.value; load(); });
  startInp.addEventListener('change', load);
  endInp.addEventListener('change', load);
  limitSel.addEventListener('change', load);
  sortSel.addEventListener('change', load);

  // Init
  (async function init(){
    const params = new URLSearchParams(location.search);
    const catParam = params.get('category') || '';
    const qParam = params.get('q') || '';
    if (catParam) state.category = catParam;
    if (qParam) state.q = qParam;

    setDefaultDates();
    await fetchCategories();
    if (state.category) categorySel.value = state.category;
    if (state.q) searchInp.value = state.q;
    load();
  })();
})();
