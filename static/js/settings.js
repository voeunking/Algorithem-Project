(function(){
  const settingsAlert = document.getElementById('settingsAlert');
  const formProfile = document.getElementById('formProfile');
  const formPassword = document.getElementById('formPassword');
  const inpFullName = document.getElementById('inpFullName');
  const inpEmail = document.getElementById('inpEmail');
  const inpCurrentPassword = document.getElementById('inpCurrentPassword');
  const inpNewPassword = document.getElementById('inpNewPassword');
  const inpConfirmPassword = document.getElementById('inpConfirmPassword');
  const avatarEl = document.getElementById('avatar');

  function showAlert(type, msg){
    settingsAlert.className = `alert alert-${type}`;
    settingsAlert.textContent = msg;
  }
  function clearAlert(){
    settingsAlert.className = 'alert d-none';
    settingsAlert.textContent = '';
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

  async function loadAvatar(){
    try {
      const res = await fetch('/api/profile');
      if (!res.ok) return;
      const data = await res.json();
      if (data.user?.avatarUrl) {
        avatarEl.style.backgroundImage = `url('${data.user.avatarUrl}')`;
        avatarEl.style.backgroundSize = 'cover';
        avatarEl.style.backgroundPosition = 'center';
      } else {
        avatarEl.style.backgroundImage = '';
      }
    } catch {}
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

  loadMe();
  loadAvatar();
})();
