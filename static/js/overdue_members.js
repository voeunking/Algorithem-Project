(function(){
  const searchInp = document.getElementById('odSearch');
  const daysInp = document.getElementById('odDays');
  const sortSel = document.getElementById('odSort');
  const orderSel = document.getElementById('odOrder');
  const perPageSel = document.getElementById('odPerPage');
  const tableBody = document.querySelector('#odTable tbody');
  const pagination = document.getElementById('odPagination');
  const summaryEl = document.getElementById('odSummary');

  let state = {
    q: '',
    days: 14,
    sort: 'days_overdue',
    order: 'desc',
    page: 1,
    per_page: 10,
    total: 0,
  };

  function buildQuery(){
    const p = new URLSearchParams();
    if(state.q) p.set('q', state.q);
    p.set('days', state.days);
    p.set('sort', state.sort);
    p.set('order', state.order);
    p.set('page', state.page);
    p.set('per_page', state.per_page);
    return p.toString();
  }

  function daysBadge(d){
    const cls = d >= 21 ? 'high' : (d >= 14 ? 'med' : 'low');
    return `<span class="badge badge-days ${cls}">${d}d</span>`;
  }

  function renderRows(items){
    tableBody.innerHTML = '';
    items.forEach((it, idx)=>{
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${(state.page-1)*state.per_page + idx + 1}</td>
        <td><a href="/members" class="text-decoration-none">${escapeHtml(it.member_name || '')}</a></td>
        <td><a href="/books?q=${encodeURIComponent(it.book_title||'')}" class="text-decoration-none">${escapeHtml(it.book_title || '')}</a></td>
        <td>${escapeHtml(it.issue_date || '')}</td>
        <td class="text-center">${daysBadge(it.days_overdue || 0)}</td>
        <td>
          <div class="btn-group btn-group-sm" role="group">
            <a class="btn btn-outline-success" href="/transactions/return/${it.transaction_id}"><i class="fas fa-undo"></i> Return</a>
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
    summaryEl.textContent = `${start}-${end} of ${state.total} overdue loans (≥ ${state.days} days)`;
  }

  async function load(){
    const res = await fetch('/members/api/overdue?' + buildQuery());
    const data = await res.json();
    state.total = data.total;
    state.days = data.days;
    renderRows(data.items || []);
    renderPagination();
    renderSummary();
  }

  function debounce(fn, ms){ let t; return (...a)=>{ clearTimeout(t); t=setTimeout(()=>fn(...a), ms); }; }
  function escapeHtml(str){ return String(str).replace(/[&<>"']/g, s => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;','\'':'&#39;'}[s])); }

  // Events
  searchInp.addEventListener('input', debounce(()=>{ state.q = searchInp.value.trim(); state.page=1; load(); }, 300));
  daysInp.addEventListener('change', ()=>{ state.days = Math.max(1, parseInt(daysInp.value||'14',10)); state.page=1; load(); });
  sortSel.addEventListener('change', ()=>{ state.sort = sortSel.value; state.page=1; load(); });
  orderSel.addEventListener('change', ()=>{ state.order = orderSel.value; state.page=1; load(); });
  perPageSel.addEventListener('change', ()=>{ state.per_page = parseInt(perPageSel.value||'10',10); state.page=1; load(); });

  // Init from URL
  (function init(){
    const params = new URLSearchParams(location.search);
    const q = params.get('q'); if (q){ state.q = q; searchInp.value = q; }
    const d = parseInt(params.get('days')||''); if (!isNaN(d)){ state.days = Math.max(1,d); daysInp.value = String(state.days); }
    load();
  })();
})();
