// Library Management System - Enhanced with modern JavaScript

// Utility functions
const debounce = (func, delay) => {
  let timeoutId;
  return (...args) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func.apply(this, args), delay);
  };
};

const showToast = (message, type = 'info') => {
  const toast = document.createElement('div');
  toast.className = `toast show ${type}`;
  toast.textContent = message;
  document.body.appendChild(toast);
  
  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 300);
  }, 3000);};

// Form validation and handling
document.addEventListener('DOMContentLoaded', () => {
  // Initialize tooltips
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));

  // Enhanced form validation
  const validateForm = (form) => {
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
      if (!field.value.trim()) {
        field.classList.add('is-invalid');
        isValid = false;
      } else {
        field.classList.remove('is-invalid');
      }
    });
    
    return isValid;
  };

  // Book form validation
  const bookForm = document.getElementById('bookForm');
  if (bookForm) {
    bookForm.addEventListener('submit', (e) => {
      if (!validateForm(bookForm)) {
        e.preventDefault();
        showToast('Please fill in all required fields', 'error');
        return;
      }
      
      const total = parseInt(bookForm.total_copies.value || '0', 10);
      const avail = parseInt(bookForm.available_copies.value || '0', 10);
      
      if (avail > total) {
        e.preventDefault();
        showToast('Available copies cannot exceed total copies', 'error');
      }
    });
  }

  // Enhanced search functionality
  const setupSearch = (inputId, tableId) => {
    const searchInput = document.getElementById(inputId);
    const table = document.getElementById(tableId);
    
    if (!searchInput || !table) return;
    
    const searchTable = debounce((searchTerm) => {
      const rows = table.querySelectorAll('tbody tr');
      const searchTermLower = searchTerm.toLowerCase();
      
      rows.forEach(row => {
        const cells = Array.from(row.getElementsByTagName('td'));
        const rowText = cells.map(cell => cell.textContent.toLowerCase()).join(' ');
        row.style.display = rowText.includes(searchTermLower) ? '' : 'none';
      });
    }, 300);
    
    searchInput.addEventListener('input', (e) => searchTable(e.target.value));
  };

  // Initialize search for different tables
  setupSearch('searchBooks', 'booksTable');
  setupSearch('searchMembers', 'memberTable');
  setupSearch('searchTransactions', 'transactionsTable');

  // Enhanced delete confirmation
  const setupDeleteConfirmation = (selector, itemName) => {
    document.querySelectorAll(selector).forEach(btn => {
      btn.addEventListener('click', (e) => {
        if (!confirm(`Are you sure you want to delete this ${itemName}?`)) {
          e.preventDefault();
        }
      });
    });
  };

  setupDeleteConfirmation('.delete-book', 'book');
  setupDeleteConfirmation('.delete-member', 'member');
  setupDeleteConfirmation('.delete-transaction', 'transaction');

  // Auto-calculate available copies
  const totalCopiesInput = document.getElementById('total_copies');
  const availableCopiesInput = document.getElementById('available_copies');
  
  if (totalCopiesInput && availableCopiesInput) {
    totalCopiesInput.addEventListener('input', () => {
      availableCopiesInput.max = totalCopiesInput.value;
      if (parseInt(availableCopiesInput.value) > parseInt(totalCopiesInput.value)) {
        availableCopiesInput.value = totalCopiesInput.value;
      }
    });
  }

  // Initialize dashboard stats if on homepage
  if (document.getElementById('dashboard-stats')) {
    updateDashboardStats();
  }
});

// Dashboard statistics
async function updateDashboardStats() {
  try {
    const res = await fetch('/api/dashboard_stats');
    if (!res.ok) throw new Error('Network response was not ok');
    const stats = await res.json();

    const elBooks = document.getElementById('total-books');
    const elMembers = document.getElementById('total-members');
    const elIssued = document.getElementById('books-issued');
    if (elBooks) elBooks.textContent = stats.totalBooks ?? 0;
    if (elMembers) elMembers.textContent = stats.totalMembers ?? 0;
    if (elIssued) elIssued.textContent = stats.booksIssued ?? 0;

    // Popular books list
    const popularList = document.getElementById('popular-books');
    if (popularList) {
      popularList.innerHTML = '';
      (stats.popularBooks || []).forEach(item => {
        const li = document.createElement('li');
        li.className = 'list-group-item d-flex justify-content-between align-items-center';
        li.innerHTML = `<span>${item.title}</span><span class="badge bg-primary rounded-pill">${item.count}</span>`;
        popularList.appendChild(li);
      });
      if ((stats.popularBooks || []).length === 0) {
        const li = document.createElement('li');
        li.className = 'list-group-item text-muted';
        li.textContent = 'No data available';
        popularList.appendChild(li);
      }
    }

    // Recent transactions table
    const txBody = document.getElementById('recent-transactions');
    if (txBody) {
      txBody.innerHTML = '';
      (stats.recentTransactions || []).forEach(tx => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>${tx.member}</td>
          <td>${tx.book}</td>
          <td>${tx.issue_date}</td>
        `;
        txBody.appendChild(tr);
      });
      if ((stats.recentTransactions || []).length === 0) {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td colspan="3" class="text-muted">No recent transactions</td>`;
        txBody.appendChild(tr);
      }
    }

    // Animate stat cards
    document.querySelectorAll('.stats-card').forEach((card, index) => {
      setTimeout(() => {
        card.classList.add('fade-in');
      }, index * 150);
    });

  } catch (error) {
    console.error('Error fetching dashboard stats:', error);
    showToast('Failed to load dashboard statistics', 'error');
  }
}

// Responsive table handling
function setupResponsiveTables() {
  document.querySelectorAll('table').forEach(table => {
    const wrapper = document.createElement('div');
    wrapper.className = 'table-responsive';
    table.parentNode.insertBefore(wrapper, table);
    wrapper.appendChild(table);
  });
}

// Initialize when DOM is fully loaded
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', setupResponsiveTables);
} else {
  setupResponsiveTables();
}

// Export to CSV functionality
function exportToCSV(tableId, filename) {
  const table = document.getElementById(tableId);
  if (!table) return;
  
  const rows = table.querySelectorAll('tr');
  let csv = [];
  
  for (let i = 0; i < rows.length; i++) {
    const row = [];
    const cols = rows[i].querySelectorAll('td, th');
    
    for (let j = 0; j < cols.length; j++) {
      // Don't include action buttons in export
      if (cols[j].classList.contains('actions')) continue;
      row.push('"' + cols[j].textContent.replace(/"/g, '""') + '"');
    }
    
    csv.push(row.join(','));
  }
  
  // Download CSV file
  const csvContent = 'data:text/csv;charset=utf-8,' + csv.join('\n');
  const encodedUri = encodeURI(csvContent);
  const link = document.createElement('a');
  link.setAttribute('href', encodedUri);
  link.setAttribute('download', `${filename}_${new Date().toISOString().split('T')[0]}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

// Add event listeners for export buttons
document.addEventListener('click', (e) => {
  if (e.target.matches('.export-csv')) {
    const tableId = e.target.dataset.table;
    const filename = e.target.dataset.filename || 'export';
    exportToCSV(tableId, filename);
  }
});
