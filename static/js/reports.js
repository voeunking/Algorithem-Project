(function () {
  const typeSel = document.getElementById('reportType');
  const startInp = document.getElementById('startDate');
  const endInp = document.getElementById('endDate');
  const runBtn = document.getElementById('runReport');
  const last30Btn = document.getElementById('quickLast30');

  const summaryCards = document.getElementById('summaryCards');
  const tableSection = document.getElementById('tableSection');
  const chartSection = document.getElementById('chartSection');
  const exportBtn = document.getElementById('exportCSV');

  const statBooks = document.getElementById('statBooks');
  const statMembers = document.getElementById('statMembers');
  const statIssued = document.getElementById('statIssued');
  const statReturned = document.getElementById('statReturned');
  const statActive = document.getElementById('statActive');

  const table = document.getElementById('resultsTable');
  const thead = table.querySelector('thead');
  const tbody = table.querySelector('tbody');

  let chart;
  const ctx = document.getElementById('reportChart');

  // Initialize default dates: last 30 days
  function setLast30Days() {
    const end = new Date();
    const start = new Date();
    start.setDate(end.getDate() - 30);
    startInp.value = start.toISOString().slice(0, 10);
    endInp.value = end.toISOString().slice(0, 10);
  }

  function buildQuery() {
    const params = new URLSearchParams();
    params.set('type', typeSel.value);
    if (startInp.value) params.set('start', startInp.value);
    if (endInp.value) params.set('end', endInp.value);
    return '/api/reports?' + params.toString();
  }

  async function fetchData() {
    const url = buildQuery();
    const res = await fetch(url);
    if (!res.ok) {
      throw new Error('Failed to fetch report');
    }
    return await res.json();
  }

  function renderSummary(data) {
    statBooks.textContent = data.totals.books;
    statMembers.textContent = data.totals.members;
    statIssued.textContent = data.totals.issued;
    statReturned.textContent = data.totals.returned;
    statActive.textContent = data.totals.activeLoans;
  }

  function renderPopularBooks(items) {
    thead.innerHTML = '<tr><th>#</th><th>Title</th><th>Count</th></tr>';
    tbody.innerHTML = '';
    items.forEach((item, idx) => {
      const tr = document.createElement('tr');
      tr.innerHTML = `<td>${idx + 1}</td><td>${escapeHtml(item.title)}</td><td><span class="badge bg-primary">${item.count}</span></td>`;
      tbody.appendChild(tr);
    });
  }

  function renderTransactionsChart(series) {
    if (chart) { chart.destroy(); }
    thead.innerHTML = '';
    tbody.innerHTML = '';
    chart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: series.labels,
        datasets: [
          { label: 'Issued', data: series.issued, borderColor: '#4a6fa5', backgroundColor: 'rgba(74,111,165,.2)', tension: .3 },
          { label: 'Returned', data: series.returned, borderColor: '#28a745', backgroundColor: 'rgba(40,167,69,.2)', tension: .3 }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: { y: { beginAtZero: true } }
      }
    });
  }

  function toggleSections({ showSummary = false, showTable = false, showChart = false }) {
    summaryCards.style.display = showSummary ? '' : 'none';
    tableSection.style.display = showTable ? '' : 'none';
    chartSection.style.display = showChart ? '' : 'none';
  }

  function toCSV(headers, rows) {
    const escape = (v) => '"' + (String(v).replaceAll('"', '""')) + '"';
    const head = headers.map(escape).join(',');
    const body = rows.map(r => r.map(escape).join(',')).join('\n');
    return head + '\n' + body;
  }

  function download(filename, text) {
    const blob = new Blob([text], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  function escapeHtml(str) {
    return String(str).replace(/[&<>"]+/g, s => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[s]));
  }

  async function run() {
    runBtn.disabled = true;
    runBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
    try {
      const type = typeSel.value;
      const data = await fetchData();
      if (type === 'summary') {
        toggleSections({ showSummary: true, showTable: false, showChart: false });
        renderSummary(data);
        // fetch daily series to render sparklines and compute simple deltas
        try {
          const params = new URLSearchParams();
          params.set('type', 'transactions_by_day');
          if (startInp.value) params.set('start', startInp.value);
          if (endInp.value) params.set('end', endInp.value);
          const url = '/api/reports?' + params.toString();
          const res2 = await fetch(url);
          if (res2.ok) {
            const series = await res2.json();
            renderSparklines(series);
            computeAndRenderDeltas(series);
          }
        } catch (e) {
          console.debug('sparkline/delta error', e);
        }
      } else if (type === 'popular_books') {
        toggleSections({ showSummary: false, showTable: true, showChart: false });
        renderPopularBooks(data.items || []);
      } else if (type === 'transactions_by_day') {
        toggleSections({ showSummary: false, showTable: false, showChart: true });
        renderTransactionsChart(data);
      }
    } catch (err) {
      console.error(err);
      alert('Error: ' + err.message);
    } finally {
      runBtn.disabled = false;
      runBtn.innerHTML = '<i class="fas fa-play me-2"></i>Run';
    }
  }

  // Small helper to compute sum over arrays
  function sum(arr) { return arr.reduce((s, v) => s + Number(v || 0), 0); }

  // Render tiny sparklines for issued/returned (and reuse for other metrics)
  const sparkCharts = {};
  function renderSparklines(series) {
    try {
      // issued
      const ids = [
        { id: 'sparkIssued', data: series.issued || [], color: '#4a6fa5' },
        { id: 'sparkReturned', data: series.returned || [], color: '#22c55e' }
      ];
      ids.forEach(s => {
        const el = document.getElementById(s.id);
        if (!el) return;
        if (sparkCharts[s.id]) { sparkCharts[s.id].destroy(); }
        sparkCharts[s.id] = new Chart(el.getContext('2d'), {
          type: 'line',
          data: { labels: series.labels, datasets: [{ data: s.data, borderColor: s.color, backgroundColor: s.color + '33', fill: true, pointRadius: 0, tension: .3 }] },
          options: { responsive: true, maintainAspectRatio: false, elements: { point: { radius: 0 } }, plugins: { legend: { display: false } }, scales: { x: { display: false }, y: { display: false } } }
        });
      });
    } catch (e) { console.debug('spark error', e); }
  }

  // Compute deltas between first half and second half of range and render badges
  function computeAndRenderDeltas(series) {
    try {
      const issued = series.issued || [];
      const returned = series.returned || [];
      const mid = Math.floor(issued.length / 2) || 1;
      const firstIssued = sum(issued.slice(0, mid));
      const secondIssued = sum(issued.slice(mid));
      const issuedDelta = Math.round(((secondIssued - firstIssued) / Math.max(firstIssued, 1)) * 100);
      const firstReturned = sum(returned.slice(0, mid));
      const secondReturned = sum(returned.slice(mid));
      const returnedDelta = Math.round(((secondReturned - firstReturned) / Math.max(firstReturned, 1)) * 100);

      const setDelta = (id, val) => {
        const el = document.getElementById(id);
        if (!el) return;
        el.textContent = (val > 0 ? '+' : '') + val + '%';
        el.classList.remove('up', 'down');
        if (val > 0) el.classList.add('up'); else if (val < 0) el.classList.add('down');
      };

      setDelta('deltaIssued', issuedDelta);
      setDelta('deltaReturned', returnedDelta);
      // For Books/Members/Active we show placeholders or reuse issued trend as an approximation
      setDelta('deltaBooks', issuedDelta);
      setDelta('deltaMembers', returnedDelta);
      setDelta('deltaActive', issuedDelta - returnedDelta);
    } catch (e) { console.debug('delta error', e); }
  }

  // Manage saved reports UI
  function refreshSavedReportsList() {
    const listEl = document.getElementById('savedReportsList');
    if (!listEl) return;
    listEl.innerHTML = '';
    const saved = JSON.parse(localStorage.getItem('savedReports') || '[]');
    if (saved.length === 0) {
      const li = document.createElement('li'); li.className = 'list-group-item text-muted'; li.textContent = 'No saved reports'; listEl.appendChild(li); return;
    }
    saved.slice().reverse().forEach((r, idx) => {
      const li = document.createElement('li'); li.className = 'list-group-item';
      const meta = document.createElement('div'); meta.innerHTML = `<strong>${r.type.replace('_', ' ')}</strong><div class='meta'>${r.start || '—'} → ${r.end || '—'}</div>`;
      const actions = document.createElement('div'); actions.className = 'actions';
      const runBtn = document.createElement('button'); runBtn.className = 'btn btn-sm btn-primary'; runBtn.textContent = 'Run';
      runBtn.addEventListener('click', () => { typeSel.value = r.type; startInp.value = r.start || ''; endInp.value = r.end || ''; run(); });
      const delBtn = document.createElement('button'); delBtn.className = 'btn btn-sm btn-outline-danger'; delBtn.textContent = 'Delete';
      delBtn.addEventListener('click', () => { saved.splice(saved.length - 1 - idx, 1); localStorage.setItem('savedReports', JSON.stringify(saved)); refreshSavedReportsList(); });
      actions.appendChild(runBtn); actions.appendChild(delBtn);
      li.appendChild(meta); li.appendChild(actions); listEl.appendChild(li);
    });
  }


  exportBtn?.addEventListener('click', () => {
    const type = typeSel.value;
    if (type === 'popular_books') {
      const rows = Array.from(tbody.querySelectorAll('tr')).map(tr => Array.from(tr.children).map(td => td.textContent.trim()));
      const csv = toCSV(['#', 'Title', 'Count'], rows);
      download('popular_books.csv', csv);
    } else if (type === 'summary') {
      const rows = [
        ['Books', statBooks.textContent],
        ['Members', statMembers.textContent],
        ['Issued', statIssued.textContent],
        ['Returned', statReturned.textContent],
        ['Active Loans', statActive.textContent]
      ];
      const csv = toCSV(['Metric', 'Value'], rows);
      download('summary.csv', csv);
    } else {
      alert('Export is available for Summary and Popular Books');
    }
  });

  last30Btn.addEventListener('click', () => {
    setLast30Days();
  });

  runBtn.addEventListener('click', run);

  // Preset buttons
  document.getElementById('presetWeek')?.addEventListener('click', () => {
    const end = new Date();
    const start = new Date(); start.setDate(end.getDate() - 7);
    startInp.value = start.toISOString().slice(0, 10);
    endInp.value = end.toISOString().slice(0, 10);
  });
  document.getElementById('preset30')?.addEventListener('click', () => { setLast30Days(); });
  document.getElementById('preset90')?.addEventListener('click', () => {
    const end = new Date();
    const start = new Date(); start.setDate(end.getDate() - 90);
    startInp.value = start.toISOString().slice(0, 10);
    endInp.value = end.toISOString().slice(0, 10);
  });

  // Export PDF - simple print of results & chart area
  document.getElementById('exportPDF')?.addEventListener('click', () => {
    const content = document.querySelector('#tableSection .card-body').innerHTML + '\n' + document.querySelector('#chartSection .card-body')?.innerHTML || '';
    const w = window.open('', '_blank');
    if (!w) { alert('Please allow popups to export PDF'); return; }
    w.document.write('<html><head><title>Report</title>');
    w.document.write('<link rel="stylesheet" href="' + window.location.origin + '/static/css/reports.css">');
    w.document.write('</head><body>' + content + '</body></html>');
    w.document.close();
    w.focus();
    setTimeout(() => { w.print(); }, 600);
  });

  // Save report (example: save filter to localStorage)
  document.getElementById('saveReport')?.addEventListener('click', () => {
    const payload = { type: typeSel.value, start: startInp.value, end: endInp.value, savedAt: new Date().toISOString() };
    const saved = JSON.parse(localStorage.getItem('savedReports' || '[]')) || [];
    saved.push(payload);
    localStorage.setItem('savedReports', JSON.stringify(saved));
    alert('Report saved locally (demo).');
  });

  // Schedule report modal handling
  const scheduleModalEl = document.getElementById('scheduleModal');
  let bootstrapModal = null;
  if (scheduleModalEl) {
    bootstrapModal = new bootstrap.Modal(scheduleModalEl);
    document.getElementById('scheduleReport')?.addEventListener('click', () => bootstrapModal.show());
    document.getElementById('saveSchedule')?.addEventListener('click', () => {
      const freq = document.getElementById('schedFreq').value;
      const email = document.getElementById('schedEmail').value;
      bootstrapModal.hide();
      alert('Schedule saved: ' + freq + ' to ' + email + ' (demo)');
    });
  }

  // Initial state
  setLast30Days();
  run();
})();
