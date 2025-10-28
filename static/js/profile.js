(function(){
  const nameEl = document.getElementById('userName');
  const avatarEl = document.getElementById('avatar');
  const statBooks = document.getElementById('statTotalBooks');
  const statMembers = document.getElementById('statTotalMembers');
  const statActive = document.getElementById('statActiveLoans');
  const list = document.getElementById('recentList');
  const formProfile = document.getElementById('formProfile');
  const formPassword = document.getElementById('formPassword');
  const inpFullName = document.getElementById('inpFullName');
  const inpEmail = document.getElementById('inpEmail');
  const inpCurrentPassword = document.getElementById('inpCurrentPassword');
  const inpNewPassword = document.getElementById('inpNewPassword');
  const inpConfirmPassword = document.getElementById('inpConfirmPassword');
  const settingsAlert = document.getElementById('settingsAlert');

  async function load(){
    const res = await fetch('/api/profile');
    const data = await res.json();
    nameEl.textContent = data.user?.name || 'Guest';
    if (data.user?.avatarUrl) {
      avatarEl.style.backgroundImage = `url('${data.user.avatarUrl}')`;
      avatarEl.style.backgroundSize = 'cover';
      avatarEl.style.backgroundPosition = 'center';
    } else {
      avatarEl.style.backgroundImage = '';
    }
    statBooks.textContent = data.stats?.totalBooks ?? 0;
    statMembers.textContent = data.stats?.totalMembers ?? 0;
    statActive.textContent = data.stats?.activeLoans ?? 0;

    list.innerHTML = '';
    (data.recentTransactions || []).forEach(item => {
      const a = document.createElement('div');
      a.className = 'list-group-item';
      a.innerHTML = `
        <div class="d-flex justify-content-between">
          <div>
            <div><strong>${escapeHtml(item.member || '')}</strong> borrowed <em>${escapeHtml(item.book || '')}</em></div>
            <div class="small text-muted">${escapeHtml(item.issue_date || '')}</div>
          </div>
          <div>
            <a class="btn btn-sm btn-outline-secondary" href="/books?q=${encodeURIComponent(item.book||'')}">View</a>
          </div>
        </div>`;
      list.appendChild(a);
    });
  }

  async function loadMe(){
    try {
      const res = await fetch('/auth/me');
      if (!res.ok) return;
      const me = await res.json();
      if (me.full_name) inpFullName.value = me.full_name;
      if (me.email) inpEmail.value = me.email;
    } catch {}
  }

  function showAlert(type, msg){
    settingsAlert.className = `alert alert-${type}`;
    settingsAlert.textContent = msg;
  }

  function clearAlert(){
    settingsAlert.className = 'alert d-none';
    settingsAlert.textContent = '';
  }

  if (formProfile) {
    formProfile.addEventListener('submit', async (e) => {
      e.preventDefault();
      clearAlert();
      const body = { full_name: inpFullName.value.trim(), email: inpEmail.value.trim() };
      try {
        const res = await fetch('/auth/update_profile', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
        const j = await res.json();
        if (res.ok) {
          showAlert('success', j.message || 'Profile updated');
          // Refresh header name
          nameEl.textContent = body.full_name || nameEl.textContent;
        } else {
          showAlert('danger', j.error || 'Failed to update profile');
        }
      } catch {
        showAlert('danger', 'Network error');
      }
    });
  }

  if (formPassword) {
    formPassword.addEventListener('submit', async (e) => {
      e.preventDefault();
      clearAlert();
      const body = {
        current_password: inpCurrentPassword.value,
        new_password: inpNewPassword.value,
        confirm_password: inpConfirmPassword.value
      };
      try {
        const res = await fetch('/auth/change_password', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
        const j = await res.json();
        if (res.ok) {
          showAlert('success', j.message || 'Password changed');
          formPassword.reset();
        } else {
          showAlert('danger', j.error || 'Failed to change password');
        }
      } catch {
        showAlert('danger', 'Network error');
      }
    });
  }

  function escapeHtml(str){ return String(str).replace(/[&<>"']/g, s => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;','\'':'&#39;'}[s])); }

  load();
  loadMe();
})();
