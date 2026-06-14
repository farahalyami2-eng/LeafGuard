/* ============================================================
   LEAFGUARD — AUTH.JS
   ============================================================ */

function switchTab(tab) {
  const isIn = tab === 'signin';
  document.getElementById('tabSignIn').classList.toggle('active', isIn);
  document.getElementById('tabSignUp').classList.toggle('active', !isIn);
  document.getElementById('formSignIn').classList.toggle('hidden', !isIn);
  document.getElementById('formSignUp').classList.toggle('hidden', isIn);
}

async function handleSignIn(e) {
  e.preventDefault();
  const btn  = document.getElementById('siBtn');
  const errEl = document.getElementById('siError');
  setLoading(btn, true, 'Signing in...');
  errEl.textContent = '';

  try {
    const res  = await fetch('/api/auth/login', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        email:    document.getElementById('siEmail').value,
        password: document.getElementById('siPassword').value,
      }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Login failed');
    window.location.href = '/app';
  } catch (err) {
    errEl.textContent = err.message;
    setLoading(btn, false, 'Sign In');
  }
}

async function handleSignUp(e) {
  e.preventDefault();
  const btn  = document.getElementById('suBtn');
  const errEl = document.getElementById('suError');
  setLoading(btn, true, 'Creating account...');
  errEl.textContent = '';

  try {
    const res  = await fetch('/api/auth/register', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        name:     document.getElementById('suName').value,
        email:    document.getElementById('suEmail').value,
        password: document.getElementById('suPassword').value,
      }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Registration failed');
    window.location.href = '/app';
  } catch (err) {
    errEl.textContent = err.message;
    setLoading(btn, false, 'Create Account');
  }
}

function setLoading(btn, loading, label) {
  btn.disabled = loading;
  btn.querySelector('span').textContent = label;
}

/* ---- Cursor ---- */
function initCursor() {
  const dot  = document.getElementById('cursorDot');
  const ring = document.getElementById('cursorRing');
  let mx = -100, my = -100, rx = -100, ry = -100;
  document.addEventListener('mousemove', e => {
    mx = e.clientX; my = e.clientY;
    dot.style.left = mx + 'px';
    dot.style.top  = my + 'px';
  });
  (function loop() {
    rx += (mx - rx) * 0.12;
    ry += (my - ry) * 0.12;
    ring.style.left = rx + 'px';
    ring.style.top  = ry + 'px';
    requestAnimationFrame(loop);
  })();
  const sel = 'a,button,input';
  document.addEventListener('mouseover', e => { if (e.target.closest(sel)) document.body.classList.add('cursor-hover'); });
  document.addEventListener('mouseout',  e => { if (e.target.closest(sel)) document.body.classList.remove('cursor-hover'); });
}

/* ---- Check if already logged in → skip to app ---- */
async function checkExistingSession() {
  try {
    const res = await fetch('/api/auth/me');
    if (res.ok) window.location.href = '/app';
  } catch {}
}

document.addEventListener('DOMContentLoaded', () => {
  initCursor();
  checkExistingSession();
});
