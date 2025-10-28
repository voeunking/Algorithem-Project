(function(){
  const searchInp = document.getElementById('catSearch');
  const sortSel = document.getElementById('catSort');
  const orderSel = document.getElementById('catOrder');
  const perPageSel = document.getElementById('catPerPage');
  const tableBody = document.querySelector('#catTable tbody');
  const pagination = document.getElementById('catPagination');
  const summaryEl = document.getElementById('catSummary');

  let state = {
    q: '',
    sort: 'category',
    order: 'asc',
    page: 1,
    per_page: 10,
    total: 0,
  };

  function buildQuery(){
    const p = new URLSearchParams();
    if(state.q) p.set('q', state.q);
    p.set('sort', state.sort);
    p.set('order', state.order);
    p.set('page', state.page);
    p.set('per_page', state.per_page);
    return p.toString();
  }

  function renderRows(items){
    tableBody.innerHTML = '';
    items.forEach(cat => {
      const pct = Number(cat.availability_pct || 0);
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${escapeHtml(cat.category || 'Uncategorized')}</td>
        <td class="text-center"><span class="badge bg-secondary">${cat.total}</span></td>
        <td class="text-center"><span class="badge bg-success">${cat.available}</span></td>
        <td class="text-center"><span class="badge bg-info text-dark">${cat.authors}</span></td>
        <td class="text-center" style="min-width:160px;">
          <div class="d-flex align-items-center gap-2">
            <div class="progress flex-grow-1" role="progressbar" aria-valuenow="${pct}" aria-valuemin="0" aria-valuemax="100">
              <div class="progress-bar" style="width:${pct}%"></div>
            </div>
            <span class="small text-muted">${pct}%</span>
          </div>
        </td>
        <td>
          <a class="btn btn-sm btn-outline-primary" href="/books?category=${encodeURIComponent(cat.category || '')}"><i class="fas fa-eye me-1"></i>View</a>
        </td>
      `;
      tableBody.appendChild(tr);
    });
  }

  function renderPagination(){
    const pages = Math.max(1, Math.ceil(state.total / state.per_page));
    pagination.innerHTML = '';
    const createItem = (label, page, disabled=false, active=false) => {
      const li = document.createElement('li');
      li.className = `page-item ${disabled?'disabled':''} ${active?'active':''}`;
      const a = document.createElement('a');
      a.className = 'page-link';
      a.textContent = label;
      a.href = 'javascript:void(0)';
      a.addEventListener('click', ()=>{ if(!disabled && !active){ state.page = page; load(); } });
      li.appendChild(a);
      return li;
    };
    pagination.appendChild(createItem('«', Math.max(1, state.page-1), state.page===1));
    const windowSize = 5;
    const start = Math.max(1, state.page - Math.floor(windowSize/2));
    const end = Math.min(pages, start + windowSize - 1);
    for(let p=start; p<=end; p++){
      pagination.appendChild(createItem(String(p), p, false, p===state.page));
    }
    pagination.appendChild(createItem('»', Math.min(pages, state.page+1), state.page===pages));
  }

  function renderSummary(){
    const start = (state.total === 0) ? 0 : (state.page-1)*state.per_page + 1;
    const end = Math.min(state.total, state.page*state.per_page);
    summaryEl.textContent = `${start}-${end} of ${state.total}`;
  }

  async function load(){
    const res = await fetch('/books/api/categories_stats?' + buildQuery());
    const data = await res.json();
    state.total = data.total;
    renderRows(data.items || []);
    renderPagination();
    renderSummary();
  }

  function debounce(fn, ms){ let t; return (...a)=>{ clearTimeout(t); t=setTimeout(()=>fn(...a), ms); }; }

  // Event bindings
  searchInp.addEventListener('input', debounce(()=>{ state.q = searchInp.value.trim(); state.page=1; load(); }, 300));
  sortSel.addEventListener('change', ()=>{ state.sort = sortSel.value; state.page=1; load(); });
  orderSel.addEventListener('change', ()=>{ state.order = orderSel.value; state.page=1; load(); });
  perPageSel.addEventListener('change', ()=>{ state.per_page = parseInt(perPageSel.value,10)||10; state.page=1; load(); });

  function escapeHtml(str){ return String(str).replace(/[&<>"']/g, s => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;','\'':'&#39;'}[s])); }

  // Init
  load();
})();
