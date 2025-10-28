(function(){
  const searchInp = document.getElementById('booksSearch');
  const categorySel = document.getElementById('booksCategory');
  const sortSel = document.getElementById('booksSort');
  const orderSel = document.getElementById('booksOrder');
  const perPageSel = document.getElementById('booksPerPage');
  const tableBody = document.querySelector('#booksTable tbody');
  const pagination = document.getElementById('booksPagination');
  const summaryEl = document.getElementById('booksSummary');

  let state = {
    q: '',
    category: '',
    sort: 'title',
    order: 'asc',
    page: 1,
    per_page: 10,
    total: 0,
  };

  function buildQuery(){
    const p = new URLSearchParams();
    if(state.q) p.set('q', state.q);
    if(state.category) p.set('category', state.category);
    p.set('sort', state.sort);
    p.set('order', state.order);
    p.set('page', state.page);
    p.set('per_page', state.per_page);
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

  function availabilityBadge(total, avail){
    const cls = avail <= 0 ? 'out' : (avail <= Math.max(1, Math.floor(total*0.2)) ? 'low' : 'available');
    return `<span class="badge badge-availability ${cls}">${avail}/${total}</span>`;
  }

  function renderRows(items){
    tableBody.innerHTML = '';
    items.forEach(b => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${b.id}</td>
        <td>${escapeHtml(b.title || '')}</td>
        <td>${escapeHtml(b.author || '')}</td>
        <td>${escapeHtml(b.publisher || '')}</td>
        <td>${escapeHtml(b.year_published || '')}</td>
        <td>${escapeHtml(b.category || '')}</td>
        <td>${b.total_copies ?? ''}</td>
        <td>${availabilityBadge(b.total_copies || 0, b.available_copies || 0)}</td>
        <td>
          <div class="btn-group btn-group-sm" role="group">
            <a href="/books/delete/${b.id}" class="btn btn-outline-danger" onclick="return confirmDelete('${escapeAttr(b.title || '')}')"><i class="fas fa-trash"></i></a>
          </div>
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
    // Simple windowed pagination
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
    const res = await fetch('/books/api?' + buildQuery());
    const data = await res.json();
    state.total = data.total;
    renderRows(data.items || []);
    renderPagination();
    renderSummary();
  }

  function debounce(fn, ms){
    let t; return (...args)=>{ clearTimeout(t); t=setTimeout(()=>fn(...args), ms); };
  }

  // Event bindings
  searchInp.addEventListener('input', debounce(()=>{ state.q = searchInp.value.trim(); state.page=1; load(); }, 300));
  categorySel.addEventListener('change', ()=>{ state.category = categorySel.value; state.page=1; load(); });
  sortSel.addEventListener('change', ()=>{ state.sort = sortSel.value; state.page=1; load(); });
  orderSel.addEventListener('change', ()=>{ state.order = orderSel.value; state.page=1; load(); });
  perPageSel.addEventListener('change', ()=>{ state.per_page = parseInt(perPageSel.value,10)||10; state.page=1; load(); });

  // Helpers accessible for inline onclick
  window.confirmDelete = function(title){
    return confirm(`Are you sure you want to delete "${title}"?`);
  };
  function escapeHtml(str){
    return String(str).replace(/[&<>"']/g, s => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;','\'':'&#39;'}[s]));
  }
  function escapeAttr(str){
    return String(str).replace(/["']/g, s => ({'"':'&quot;','\'':'&#39;'}[s]));
  }

  // Init
  (async function init(){
    const params = new URLSearchParams(location.search);
    const catParam = params.get('category') || '';
    const qParam = params.get('q') || '';
    if (catParam) state.category = catParam;
    if (qParam) state.q = qParam;

    await fetchCategories();
    if (state.category) categorySel.value = state.category;
    if (state.q) searchInp.value = state.q;
    load();
  })();
})();
