(function(){
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
  function setLast30Days(){
    const end = new Date();
    const start = new Date();
    start.setDate(end.getDate()-30);
    startInp.value = start.toISOString().slice(0,10);
    endInp.value = end.toISOString().slice(0,10);
  }

  function buildQuery(){
    const params = new URLSearchParams();
    params.set('type', typeSel.value);
    if(startInp.value) params.set('start', startInp.value);
    if(endInp.value) params.set('end', endInp.value);
    return '/api/reports?' + params.toString();
  }

  async function fetchData(){
    const url = buildQuery();
    const res = await fetch(url);
    if(!res.ok){
      throw new Error('Failed to fetch report');
    }
    return await res.json();
  }

  function renderSummary(data){
    statBooks.textContent = data.totals.books;
    statMembers.textContent = data.totals.members;
    statIssued.textContent = data.totals.issued;
    statReturned.textContent = data.totals.returned;
    statActive.textContent = data.totals.activeLoans;
  }

  function renderPopularBooks(items){
    thead.innerHTML = '<tr><th>#</th><th>Title</th><th>Count</th></tr>';
    tbody.innerHTML = '';
    items.forEach((item, idx)=>{
      const tr = document.createElement('tr');
      tr.innerHTML = `<td>${idx+1}</td><td>${escapeHtml(item.title)}</td><td><span class="badge bg-primary">${item.count}</span></td>`;
      tbody.appendChild(tr);
    });
  }

  function renderTransactionsChart(series){
    if(chart){ chart.destroy(); }
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

  function toggleSections({showSummary=false, showTable=false, showChart=false}){
    summaryCards.style.display = showSummary ? '' : 'none';
    tableSection.style.display = showTable ? '' : 'none';
    chartSection.style.display = showChart ? '' : 'none';
  }

  function toCSV(headers, rows){
    const escape = (v) => '"' + (String(v).replaceAll('"','""')) + '"';
    const head = headers.map(escape).join(',');
    const body = rows.map(r => r.map(escape).join(',')).join('\n');
    return head + '\n' + body;
  }

  function download(filename, text){
    const blob = new Blob([text], {type: 'text/csv;charset=utf-8;'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  function escapeHtml(str){
    return String(str).replace(/[&<>"]+/g, s => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[s]));
  }

  async function run(){
    runBtn.disabled = true;
    runBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
    try{
      const type = typeSel.value;
      const data = await fetchData();
      if(type === 'summary'){
        toggleSections({showSummary: true, showTable: false, showChart: false});
        renderSummary(data);
      } else if(type === 'popular_books'){
        toggleSections({showSummary: false, showTable: true, showChart: false});
        renderPopularBooks(data.items || []);
      } else if(type === 'transactions_by_day'){
        toggleSections({showSummary: false, showTable: false, showChart: true});
        renderTransactionsChart(data);
      }
    } catch(err){
      console.error(err);
      alert('Error: ' + err.message);
    } finally {
      runBtn.disabled = false;
      runBtn.innerHTML = '<i class="fas fa-play me-2"></i>Run';
    }
  }

  exportBtn?.addEventListener('click', ()=>{
    const type = typeSel.value;
    if(type === 'popular_books'){
      const rows = Array.from(tbody.querySelectorAll('tr')).map(tr => Array.from(tr.children).map(td => td.textContent.trim()));
      const csv = toCSV(['#','Title','Count'], rows);
      download('popular_books.csv', csv);
    } else if(type === 'summary'){
      const rows = [
        ['Books', statBooks.textContent],
        ['Members', statMembers.textContent],
        ['Issued', statIssued.textContent],
        ['Returned', statReturned.textContent],
        ['Active Loans', statActive.textContent]
      ];
      const csv = toCSV(['Metric','Value'], rows);
      download('summary.csv', csv);
    } else {
      alert('Export is available for Summary and Popular Books');
    }
  });

  last30Btn.addEventListener('click', ()=>{
    setLast30Days();
  });

  runBtn.addEventListener('click', run);

  // Initial state
  setLast30Days();
  run();
})();
