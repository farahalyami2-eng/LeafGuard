/* ============================================================
   LEAFGUARD — APP.JS
   ============================================================ */

/* ---- PRODUCTS DATA ---- */
const PRODUCTS = [
  {id:'AF0001',name:'Citrus Bacteria Clear',              primary:'Biological Pesticides',   secondary:'Bacillus Fungicides',                          crops:'Citrus, vegetables, fruit trees',               price:165},
  {id:'AF0002',name:'Onion-Ginger-Garlic Bacteria Clear', primary:'Biological Pesticides',   secondary:'Bacillus Fungicides',                          crops:'Scallion, ginger, garlic, vegetables',          price:155},
  {id:'AF0003',name:'Rice Bacteria Clear',                primary:'Biological Pesticides',   secondary:'Bacillus Fungicides',                          crops:'Rice, vegetables, fruit trees',                 price:155},
  {id:'AF0004',name:'Cabbage & Kale Anti-rot Agent',      primary:'Fertilizers',             secondary:'Foliar Fertilizers/Nutrient Solutions',        crops:'Cabbage, kale, tomato, pepper',                 price:175},
  {id:'AF0005',name:'Strawberry Bacteria Clear',          primary:'Biological Pesticides',   secondary:'Bacillus Fungicides',                          crops:'Strawberry, vegetables, fruit trees',           price:160},
  {id:'AF0006',name:'Bacteria Clear Universal',           primary:'Biological Pesticides',   secondary:'Bacillus Fungicides',                          crops:'Vegetables, fruit trees, melons',               price:170},
  {id:'AF0007',name:'Chili Pepper Bacteria Clear',        primary:'Biological Pesticides',   secondary:'Bacillus Fungicides',                          crops:'Chili pepper, vegetables',                      price:155},
  {id:'AF0008',name:'Cucumber Bacteria Clear',            primary:'Biological Pesticides',   secondary:'Bacillus Fungicides',                          crops:'Cucumber, vegetables, melons',                  price:155},
  {id:'AF0012',name:'Root Nematode Clear',                primary:'Biological Pesticides',   secondary:'Microbial Agents',                             crops:'General crops — root protection',               price:195},
  {id:'AF0013',name:'Citrus Water-Soluble Fertilizer',    primary:'Fertilizers',             secondary:'Secondary Nutrient Water-Soluble Fertilizers', crops:'Citrus, fruit trees, tomato',                   price:145},
  {id:'AF0016',name:'Vigorous Root Growth',               primary:'Fertilizers',             secondary:'Macronutrient Water-Soluble Fertilizers',      crops:'Fruit trees, tomato, pepper, garlic',           price:150},
  {id:'AF0017',name:'One Spray Green',                    primary:'Fertilizers',             secondary:'Foliar Fertilizers/Nutrient Solutions',        crops:'Wheat, corn, rice, apple, tomato',              price:130},
  {id:'AF0018',name:'Melon Booster',                      primary:'Fertilizers',             secondary:'Secondary Nutrient Water-Soluble Fertilizers', crops:'Cucumber, pumpkin, watermelon, tomato',         price:140},
  {id:'AF0019',name:'Underground Root & Tuber Enlarger',  primary:'Fertilizers',             secondary:'Secondary Nutrient Water-Soluble Fertilizers', crops:'Potato, sweet potato, garlic, radish',          price:155},
  {id:'AF0020',name:'Sweet Potato Baby',                  primary:'Fertilizers',             secondary:'Foliar Fertilizers/Nutrient Solutions',        crops:'Sweet potato, strawberry, banana, mango',       price:145},
  {id:'CP001', name:'1.8% Abamectin',                     primary:'Chemical Pesticides',     secondary:'Insecticides',                                 crops:'Vegetables, fruit trees — mites, miners',       price:95},
  {id:'CP002', name:'10% Imidacloprid',                   primary:'Chemical Pesticides',     secondary:'Insecticides',                                 crops:'Rice, wheat, vegetables — aphids, whitefly',    price:85},
  {id:'CP003', name:'10% Thiamethoxam',                   primary:'Chemical Pesticides',     secondary:'Insecticides',                                 crops:'Vegetables, fruit trees — whitefly',            price:90},
  {id:'CP004', name:'3.2% Emamectin Benzoate',            primary:'Chemical Pesticides',     secondary:'Insecticides',                                 crops:'Vegetables — caterpillars, moths',              price:100},
  {id:'CP005', name:'1.8% Cymoxanil Acetate',             primary:'Chemical Pesticides',     secondary:'Fungicides',                                   crops:'Vegetables, potatoes — downy mildew',           price:110},
  {id:'CP006', name:'3% Metalaxyl-M',                     primary:'Chemical Pesticides',     secondary:'Fungicides',                                   crops:'Vegetables, tomatoes — root rot',               price:120},
  {id:'CP007', name:'6% Kasugamycin',                     primary:'Chemical Pesticides',     secondary:'Fungicides',                                   crops:'Rice, vegetables — bacterial blight',           price:115},
  {id:'CP008', name:'5% Cyazofamid',                      primary:'Chemical Pesticides',     secondary:'Fungicides',                                   crops:'Cucumber, tomato, pepper — downy mildew',       price:125},
  {id:'CP009', name:'10% Glufosinate-Ammonium',           primary:'Chemical Pesticides',     secondary:'Herbicides',                                   crops:'General weeds — non-selective',                 price:75},
  {id:'CP010', name:'33% Glyphosate Ammonium',            primary:'Chemical Pesticides',     secondary:'Herbicides',                                   crops:'Broad spectrum weed control',                   price:70},
  {id:'BP001', name:'Pyraclostrobin-Kairun',              primary:'Chemical Pesticides',     secondary:'Fungicides',                                   crops:'Fruits, vegetables — powdery mildew',           price:135},
  {id:'BP002', name:'Benomyl Fungicide',                  primary:'Chemical Pesticides',     secondary:'Fungicides',                                   crops:'Broad spectrum — mildew, gray mold',            price:105},
  {id:'PGR001',name:'Biostimulant Regulator A',           primary:'Plant Growth Regulators', secondary:'Biostimulants/Regulators',                     crops:'Vegetables, fruit trees — growth',              price:160},
  {id:'PGR002',name:'Biostimulant Regulator B',           primary:'Plant Growth Regulators', secondary:'Biostimulants/Regulators',                     crops:'Cereals, oilseeds — lodging resistance',        price:155},
];

/* ============================================================
   STATE
   ============================================================ */
let currentPage = 'home';
let cart        = [];
let chatHistory = [];
let cartOpen    = false;
let currentUser = null;    // {id, name, email}
let userLocation = null;   // {lat, lng, city, country} — set after permission granted
let selectedImages = [];   // [{ file, url }] — images attached to next chat message (max 4)

let shopState = { category:'All', subtype:'All', maxPrice:500, search:'', sort:'name' };

/* ============================================================
   HELPERS
   ============================================================ */
function getInitials(name) {
  const words = name.split(/\s+/).filter(w => !/^[\d.%]+$/.test(w));
  if (!words.length) return name.slice(0,2).toUpperCase();
  if (words.length === 1) return words[0].slice(0,2).toUpperCase();
  return (words[0][0] + words[1][0]).toUpperCase();
}

function catMeta(primary) {
  if (primary === 'Biological Pesticides')   return { bg:'#1a3820', badge:'BIO',  cls:'badge-bio'  };
  if (primary === 'Chemical Pesticides')     return { bg:'#3d2010', badge:'CHEM', cls:'badge-chem' };
  if (primary === 'Fertilizers')             return { bg:'#102040', badge:'FERT', cls:'badge-fert' };
  if (primary === 'Plant Growth Regulators') return { bg:'#251535', badge:'PGR',  cls:'badge-pgr'  };
  return { bg:'#1a1a1a', badge:'—', cls:'' };
}

function subtypeMatch(secondary, filter) {
  const s = secondary.toLowerCase();
  if (filter === 'Insecticides')     return s.includes('insect');
  if (filter === 'Fungicides')       return s.includes('fungic');
  if (filter === 'Herbicides')       return s.includes('herbic');
  if (filter === 'Foliar Nutrients') return s.includes('foliar');
  if (filter === 'Bacillus Bio')     return s.includes('bacillus');
  return true;
}

function greeting() {
  const h = new Date().getHours();
  if (h < 12) return 'Good morning';
  if (h < 17) return 'Good afternoon';
  return 'Good evening';
}

/* ============================================================
   AUTH
   ============================================================ */
async function loadUser() {
  try {
    const res = await fetch('/api/auth/me');
    if (!res.ok) { window.location.href = '/'; return; }
    currentUser = await res.json();
    applyUserToUI();
  } catch {
    window.location.href = '/';
  }
}

function applyUserToUI() {
  if (!currentUser) return;
  const first = currentUser.name.split(' ')[0];
  // Nav avatar
  const av = document.getElementById('userAvatar');
  if (av) av.textContent = currentUser.name[0].toUpperCase();
  const nm = document.getElementById('userNameNav');
  if (nm) nm.textContent = first;
  // Dropdown
  const dn = document.getElementById('dropdownName');
  if (dn) dn.textContent = currentUser.name;
  const de = document.getElementById('dropdownEmail');
  if (de) de.textContent = currentUser.email;
  // Dashboard greeting
  refreshDashboard();
}

async function handleLogout() {
  await fetch('/api/auth/logout', { method: 'POST' });
  window.location.href = '/';
}

function toggleUserDropdown() {
  document.getElementById('userDropdown').classList.toggle('hidden');
}

// Close dropdown when clicking outside
document.addEventListener('click', e => {
  const dd = document.getElementById('userDropdown');
  if (!dd) return;
  if (!e.target.closest('#userBtn') && !e.target.closest('#userDropdown')) {
    dd.classList.add('hidden');
  }
});

/* ============================================================
   LOCATION
   ============================================================ */
function showLocationModal() {
  if (localStorage.getItem('lg_location_decided')) return;
  document.getElementById('locationModal').classList.remove('hidden');
}

function allowLocation() {
  document.getElementById('locationModal').classList.add('hidden');
  localStorage.setItem('lg_location_decided', '1');

  navigator.geolocation.getCurrentPosition(
    pos => {
      const { latitude: lat, longitude: lng } = pos.coords;
      // Reverse-geocode with free API (no key required)
      fetch(`https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lng}&format=json`)
        .then(r => r.json())
        .then(data => {
          userLocation = {
            lat, lng,
            city:    data.address?.city || data.address?.town || data.address?.village || '',
            country: data.address?.country || '',
          };
          localStorage.setItem('lg_location', JSON.stringify(userLocation));
          showLocationBadge();
        })
        .catch(() => {
          userLocation = { lat, lng, city: '', country: '' };
          localStorage.setItem('lg_location', JSON.stringify(userLocation));
        });
    },
    () => { /* user denied or error — silently skip */ }
  );
}

function skipLocation() {
  document.getElementById('locationModal').classList.add('hidden');
  localStorage.setItem('lg_location_decided', '1');
}

function showLocationBadge() {
  if (!userLocation || !userLocation.city) return;
  const wrap = document.getElementById('locationBadgeWrap');
  const text = document.getElementById('locationText');
  if (wrap && text) {
    text.textContent = userLocation.city + (userLocation.country ? ', ' + userLocation.country : '');
    wrap.style.display = '';
  }
}

function loadSavedLocation() {
  const saved = localStorage.getItem('lg_location');
  if (saved) {
    try { userLocation = JSON.parse(saved); showLocationBadge(); } catch {}
  }
}

/* ============================================================
   NAVIGATION
   ============================================================ */
function goPage(name) {
  if (name !== 'orders') stopTrackingPoll();

  document.querySelectorAll('.page').forEach(p => p.classList.add('hidden'));
  const el = document.getElementById('page-' + name);
  if (el) el.classList.remove('hidden');

  const nav = document.getElementById('mainNav');
  const darkPages = ['home', 'sim'];
  nav.classList.toggle('nav--dark',  darkPages.includes(name));
  nav.classList.toggle('nav--light', !darkPages.includes(name));

  document.querySelectorAll('.nav-link').forEach(l =>
    l.classList.toggle('active', l.dataset.page === name)
  );

  currentPage = name;
  if (name === 'dashboard') refreshDashboard();
  if (name === 'shop')      renderProducts();
  if (name === 'orders') {
    initOrdersPage();
    setTimeout(() => { if (_trackingMap) _trackingMap.invalidateSize(); }, 120);
  }
  if (name === 'sim') {
    const frame = document.getElementById('simFrame');
    if (frame && !frame.getAttribute('src')) frame.src = '/simulation.html';
  }
}

/* ============================================================
   CART
   ============================================================ */
function addToCart(productId) {
  const p = PRODUCTS.find(x => x.id === productId);
  if (!p) return;
  const ex = cart.find(i => i.id === productId);
  if (ex) { ex.qty++; } else { cart.push({id:p.id,name:p.name,primary:p.primary,price:p.price,qty:1}); }
  updateCartBadge();
  renderCart();
  renderProducts();
  refreshDashboard();
  showCartToast(p.name);
  if (!cartOpen) toggleCart();
}

function showCartToast(name) {
  let t = document.getElementById('cartToast');
  if (!t) {
    t = document.createElement('div');
    t.id = 'cartToast';
    document.body.appendChild(t);
  }
  t.textContent = (typeof window.t === 'function' ? window.t('added_to_cart') : '✓ Added to cart: ') + name;
  t.className = 'cart-toast show';
  clearTimeout(t._timer);
  t._timer = setTimeout(() => t.classList.remove('show'), 2500);
}

function removeFromCart(id) {
  cart = cart.filter(i => i.id !== id);
  updateCartBadge(); renderCart(); renderProducts(); refreshDashboard();
}

function updateCartQty(id, delta) {
  const item = cart.find(i => i.id === id);
  if (!item) return;
  item.qty = Math.max(0, item.qty + delta);
  if (item.qty === 0) removeFromCart(id);
  else { updateCartBadge(); renderCart(); refreshDashboard(); }
}

function updateCartBadge() {
  const n = cart.reduce((s,i) => s+i.qty, 0);
  document.getElementById('cartBadge').textContent = n;
}

function toggleCart() {
  cartOpen = !cartOpen;
  document.getElementById('cartDrawer').classList.toggle('open', cartOpen);
  document.getElementById('cartOverlay').classList.toggle('open', cartOpen);
  if (cartOpen) renderCart();
}

function cartSubtotal() { return cart.reduce((s,i) => s+i.price*i.qty, 0); }

function renderCart() {
  const itemsEl  = document.getElementById('cartItems');
  const footerEl = document.getElementById('cartFooter');

  if (!cart.length) {
    itemsEl.innerHTML = `<div class="cart-empty">
      <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"><path d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 01-8 0"/></svg>
      <span>${t('cart_empty_title')}</span>
    </div>`;
    footerEl.innerHTML = '';
    return;
  }

  itemsEl.innerHTML = cart.map(item => {
    const m = catMeta(item.primary);
    return `<div class="cart-item">
      <div class="cart-item-icon" style="background:${m.bg}">${getInitials(item.name)}</div>
      <div class="cart-item-info">
        <div class="cart-item-name">${item.name}</div>
        <div class="cart-item-cat">${item.primary}</div>
      </div>
      <div class="cart-item-controls">
        <button class="qty-btn" onclick="updateCartQty('${item.id}',-1)">−</button>
        <span class="qty-num">${item.qty}</span>
        <button class="qty-btn" onclick="updateCartQty('${item.id}',1)">+</button>
      </div>
      <div class="cart-item-price">SAR ${(item.price*item.qty).toLocaleString()}</div>
      <button class="cart-item-remove" onclick="removeFromCart('${item.id}')">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
      </button>
    </div>`;
  }).join('');

  const sub = cartSubtotal();
  const shipping = 15;
  const vat   = Math.round(sub * 0.15);
  const total = sub + shipping + vat;

  footerEl.innerHTML = `
    <div class="cart-line"><span>${t('cart_subtotal')}</span><span>SAR ${sub.toLocaleString()}</span></div>
    <div class="cart-line"><span>${t('cart_shipping')}</span><span>SAR ${shipping}</span></div>
    <div class="cart-line"><span>${t('cart_vat')}</span><span>SAR ${vat.toLocaleString()}</span></div>
    <div class="cart-line total"><span>${t('cart_grand_total')}</span><span>SAR ${total.toLocaleString()}</span></div>
    <button class="checkout-btn" onclick="submitOrder()">${t('cart_checkout')}</button>`;
}

/* ============================================================
   SHOP
   ============================================================ */
function getFilteredProducts() {
  return PRODUCTS
    .filter(p => {
      if (shopState.category !== 'All' && p.primary !== shopState.category) return false;
      if (shopState.subtype  !== 'All' && !subtypeMatch(p.secondary, shopState.subtype)) return false;
      if (p.price > shopState.maxPrice) return false;
      if (shopState.search) {
        const q = shopState.search.toLowerCase();
        if (!p.name.toLowerCase().includes(q) && !p.crops.toLowerCase().includes(q)) return false;
      }
      return true;
    })
    .sort((a,b) => {
      if (shopState.sort === 'price-asc')  return a.price - b.price;
      if (shopState.sort === 'price-desc') return b.price - a.price;
      if (shopState.sort === 'type')       return a.primary.localeCompare(b.primary);
      return a.name.localeCompare(b.name);
    });
}

function renderProducts() {
  const grid = document.getElementById('productGrid');
  if (!grid) return;
  const list = getFilteredProducts();

  if (!list.length) {
    grid.innerHTML = '<div style="grid-column:1/-1;text-align:center;padding:60px 0;color:rgba(14,18,9,.35);font-size:.9rem;">No products match your filters</div>';
    return;
  }
  grid.innerHTML = list.map(p => {
    const m      = catMeta(p.primary);
    const inCart = cart.some(i => i.id === p.id);
    return `<div class="product-card">
      <div class="product-img" style="background:${m.bg}">
        <span class="product-initials">${getInitials(p.name)}</span>
        <span class="product-badge ${m.cls}">${m.badge}</span>
      </div>
      <div class="product-body">
        <div class="product-name">${p.name}</div>
        <div class="product-cat">${p.primary}</div>
        <div class="product-footer">
          <div class="product-price">SAR ${p.price}</div>
          <button class="add-cart-btn ${inCart?'in-cart':''}" onclick="addToCart('${p.id}')">
            ${inCart ? '✓ In cart' : 'Add to cart'}
          </button>
        </div>
      </div>
    </div>`;
  }).join('');
}

function initShopFilters() {
  document.getElementById('filterCategory').addEventListener('click', e => {
    const li = e.target.closest('.filter-item');
    if (!li) return;
    document.querySelectorAll('#filterCategory .filter-item').forEach(x => x.classList.remove('active'));
    li.classList.add('active');
    shopState.category = li.dataset.cat;
    renderProducts();
  });
  document.getElementById('filterSubtype').addEventListener('click', e => {
    const li = e.target.closest('.filter-item');
    if (!li) return;
    document.querySelectorAll('#filterSubtype .filter-item').forEach(x => x.classList.remove('active'));
    li.classList.add('active');
    shopState.subtype = li.dataset.sub;
    renderProducts();
  });
  document.getElementById('priceSlider').addEventListener('input', e => {
    shopState.maxPrice = parseInt(e.target.value);
    document.getElementById('priceMax').textContent = e.target.value;
    renderProducts();
  });
  document.getElementById('searchInput').addEventListener('input', e => {
    shopState.search = e.target.value.trim();
    renderProducts();
  });
  document.getElementById('sortSelect').addEventListener('change', e => {
    shopState.sort = e.target.value;
    renderProducts();
  });
}

/* ============================================================
   AI ADVISOR CHAT — uses /api/chat (LeafGuardAgent backend)
   ============================================================ */
function escHtml(t) {
  return t.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

function inlineFormat(escaped) {
  return escaped.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
}

function formatBotMsg(text) {
  const lines = text.split('\n');
  let html = '';
  let inUl = false;
  let inOl = false;

  function closeList() {
    if (inUl) { html += '</ul>'; inUl = false; }
    if (inOl) { html += '</ol>'; inOl = false; }
  }

  for (const raw of lines) {
    // ### / ## / # heading
    const hm = raw.match(/^#{1,3}\s+(.+)$/);
    if (hm) {
      closeList();
      html += `<div class="msg-heading">${inlineFormat(escHtml(hm[1]))}</div>`;
      continue;
    }
    // Numbered list: 1. item
    const nm = raw.match(/^(\d+)\.\s+(.+)$/);
    if (nm) {
      if (inUl) { html += '</ul>'; inUl = false; }
      if (!inOl) { html += '<ol>'; inOl = true; }
      html += `<li>${inlineFormat(escHtml(nm[2]))}</li>`;
      continue;
    }
    // Bullet: - item or * item
    const bm = raw.match(/^[\*\-]\s+(.+)$/);
    if (bm) {
      if (inOl) { html += '</ol>'; inOl = false; }
      if (!inUl) { html += '<ul>'; inUl = true; }
      html += `<li>${inlineFormat(escHtml(bm[1]))}</li>`;
      continue;
    }
    // Regular paragraph line
    closeList();
    const t = raw.trim();
    if (t) html += `<p>${inlineFormat(escHtml(t))}</p>`;
  }

  closeList();
  return html;
}

function appendMsg(role, content) {
  const container = document.getElementById('chatMessages');
  const div = document.createElement('div');
  div.className = `msg msg--${role === 'user' ? 'user' : 'bot'}`;
  const label = role === 'user' ? (currentUser ? currentUser.name[0].toUpperCase() : 'U') : 'L';
  div.innerHTML = `
    <div class="msg-avatar">${label}</div>
    <div class="msg-bubble">${role === 'user' ? `<p>${escHtml(content)}</p>` : formatBotMsg(content)}</div>`;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}

function handleImageSelect(input) {
  const files = Array.from(input.files || []);
  if (!files.length) return;
  const remaining = 4 - selectedImages.length;
  files.slice(0, remaining).forEach(file => {
    selectedImages.push({ file, url: URL.createObjectURL(file) });
  });
  renderImagePreviews();
  input.value = '';
}

function renderImagePreviews() {
  const row = document.getElementById('imgPreviewRow');
  row.innerHTML = '';
  selectedImages.forEach((img, i) => {
    const chip = document.createElement('div');
    chip.className = 'img-preview-chip';
    const name = img.file.name;
    chip.innerHTML = `
      <img src="${img.url}" alt="">
      <span>${name.length > 18 ? name.slice(0,15) + '…' : name}</span>
      <button class="clear-img" title="Remove">&#x2715;</button>`;
    chip.querySelector('.clear-img').onclick = () => removeImage(i);
    row.appendChild(chip);
  });
  if (selectedImages.length) row.classList.add('visible');
  else row.classList.remove('visible');
}

function removeImage(index) {
  URL.revokeObjectURL(selectedImages[index].url);
  selectedImages.splice(index, 1);
  renderImagePreviews();
}

function clearImage() {
  selectedImages.forEach(img => URL.revokeObjectURL(img.url));
  selectedImages = [];
  renderImagePreviews();
}

let typingEl = null;
function showTyping() {
  const c = document.getElementById('chatMessages');
  typingEl = document.createElement('div');
  typingEl.className = 'typing-indicator';
  typingEl.innerHTML = `<div class="msg-avatar" style="background:var(--moss)">L</div><div class="typing-dots"><span></span><span></span><span></span></div>`;
  c.appendChild(typingEl);
  c.scrollTop = c.scrollHeight;
}
function hideTyping() { if (typingEl) { typingEl.remove(); typingEl = null; } }

function appendBotMsg(text, tools) {
  const container = document.getElementById('chatMessages');
  const div = document.createElement('div');
  div.className = 'msg msg--bot';
  const toolsHtml = tools && tools.length
    ? `<div class="msg-tools">${tools.map(t => `<span class="tool-chip">${escHtml(t)}</span>`).join('')}</div>`
    : '';
  div.innerHTML = `
    <div class="msg-avatar" style="background:var(--moss)">L</div>
    <div class="msg-bubble">${formatBotMsg(text)}${toolsHtml}</div>`;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}

async function sendMessage() {
  const input = document.getElementById('chatInput');
  const text  = input.value.trim();
  if (!text && !selectedImages.length) return;

  // Hide tips panel on first message
  const tipsPanel = document.getElementById('chatTipsPanel');
  if (tipsPanel) tipsPanel.classList.add('hidden');

  input.value = ''; input.style.height = '';
  input.disabled = true;
  document.getElementById('sendBtn').disabled = true;

  // Render user message with all attached images
  const container = document.getElementById('chatMessages');
  const userDiv = document.createElement('div');
  userDiv.className = 'msg msg--user';
  const label = currentUser ? currentUser.name[0].toUpperCase() : 'U';
  const imgsHtml = selectedImages.map(img =>
    `<img src="${img.url}" class="msg-image" alt="Attached image">`
  ).join('');
  userDiv.innerHTML = `
    <div class="msg-avatar">${label}</div>
    <div class="msg-bubble">${imgsHtml}${text ? `<p>${escHtml(text)}</p>` : ''}</div>`;
  container.appendChild(userDiv);
  container.scrollTop = container.scrollHeight;

  const historyText = text || '(image attached)';
  chatHistory.push({ role: 'user', content: historyText });
  showTyping();

  try {
    let res;
    if (selectedImages.length) {
      const fd = new FormData();
      fd.append('message', text || 'Please analyze this plant image.');
      selectedImages.forEach((img, i) => {
        fd.append(i === 0 ? 'image' : `image_${i + 1}`, img.file);
      });
      if (userLocation) fd.append('location', JSON.stringify(userLocation));
      clearImage();
      res = await fetch('/api/chat', { method: 'POST', body: fd });
    } else {
      res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, location: userLocation || null }),
      });
    }

    if (res.status === 401) {
      hideTyping();
      appendBotMsg(t('err_session'), []);
      setTimeout(() => window.location.href = '/', 2000);
      return;
    }

    const data = await res.json();
    hideTyping();
    const reply = data.reply || 'No response received.';
    if (data.low_confidence) appendLowConfidenceWarning();
    appendBotMsg(reply, data.tools || []);
    chatHistory.push({ role: 'assistant', content: reply });
  } catch {
    hideTyping();
    const errMsg = t('err_network');
    appendBotMsg(errMsg, []);
    chatHistory.push({ role: 'assistant', content: errMsg });
  } finally {
    input.disabled = false;
    document.getElementById('sendBtn').disabled = false;
    input.focus();
  }
}

function appendLowConfidenceWarning() {
  const container = document.getElementById('chatMessages');
  const el = document.createElement('div');
  el.className = 'low-conf-warning';
  el.innerHTML = `
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
    <span>${t('low_conf')}</span>`;
  container.appendChild(el);
  container.scrollTop = container.scrollHeight;
}

function sendQuickQuestion(q) {
  if (currentPage !== 'chat') goPage('chat');
  const input = document.getElementById('chatInput');
  input.value = q;
  setTimeout(() => sendMessage(), 80);
}

function initChat() {

  const ta = document.getElementById('chatInput');
  ta.addEventListener('input', () => {
    ta.style.height = '';
    ta.style.height = Math.min(ta.scrollHeight, 90) + 'px';
  });
  ta.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  });
  document.querySelectorAll('.topic-item').forEach(item => {
    item.addEventListener('click', () => {
      document.querySelectorAll('.topic-item').forEach(x => x.classList.remove('active'));
      item.classList.add('active');
    });
  });
}

/* ============================================================
   ORDERS & ORDER TRACKING
   ============================================================ */

let _trackingPollTimer   = null;
let _trackingMap         = null;
let _warehouseMarker     = null;
let _destMarker          = null;
let _courierMarker       = null;
let _routeLine           = null;
let _activeOrderId       = null;
let _lastWarehouse       = null;
let _lastDest            = null;

async function initOrdersPage() {
  await loadOrders();
}

async function loadOrders() {
  try {
    const res  = await fetch('/api/orders');
    if (!res.ok) return;
    const data = await res.json();
    renderOrdersList(data.orders || []);
  } catch(e) { console.warn('loadOrders:', e); }
}

function renderOrdersList(orders) {
  const el      = document.getElementById('ordersList');
  const badge   = document.getElementById('ordersCountBadge');
  if (!el) return;
  if (badge) badge.textContent = orders.length || '';

  if (!orders.length) {
    el.innerHTML = `<div class="orders-list-empty">${t('orders_none').replace('\n','<br>')}</div>`;
    return;
  }

  el.innerHTML = orders.map(o => `
    <div class="order-row ${_activeOrderId === o.id ? 'active' : ''}" onclick="openOrder(${o.id})">
      <div class="order-row-top">
        <span class="order-row-id">Order #${o.id}</span>
        <span class="order-row-date">${o.created || ''}</span>
      </div>
      <div class="order-row-status ${o.status_key === 'delivered' ? 'done' : ''}">${escHtml(o.status_label)}</div>
      ${o.preview ? `<div class="order-row-preview">${escHtml(o.preview)}${o.total_qty > 1 ? ' +' + (o.total_qty - 1) + ' more' : ''}</div>` : ''}
      <div class="order-row-bar"><div class="order-row-bar-fill" style="width:${o.progress}%"></div></div>
    </div>`).join('');
}

async function openOrder(id) {
  stopTrackingPoll();
  _activeOrderId = id;

  document.getElementById('ordersEmptyState').classList.add('hidden');
  document.getElementById('orderTrackingView').classList.remove('hidden');

  await fetchAndRenderOrder(id);
  startTrackingPoll(id);
  loadOrders();  // re-render sidebar to highlight active row
}

async function fetchAndRenderOrder(id) {
  try {
    const res  = await fetch(`/api/order/${id}`);
    if (!res.ok) return;
    const data = await res.json();
    if (!data.ok) return;
    renderTracking(id, data);
  } catch(e) { console.warn('fetchAndRenderOrder:', e); }
}

function renderTracking(id, data) {
  const st    = data.status;
  const items = data.items || [];
  const wh    = data.warehouse
    ? [data.warehouse.lat, data.warehouse.lng]
    : [24.6877, 46.7219];
  const dest  = data.dest
    ? [data.dest.lat, data.dest.lng]
    : [wh[0] + 0.04, wh[1] + 0.035];

  _lastWarehouse = wh;
  _lastDest      = dest;

  // Header
  const idEl = document.getElementById('trackingOrderId');
  if (idEl) idEl.textContent = `Order #${id}`;
  const lblEl = document.getElementById('trackingStatusLbl');
  if (lblEl) lblEl.textContent = st.current_label;
  const elEl  = document.getElementById('trackingElapsed');
  if (elEl) elEl.textContent = st.elapsed_min < 1
    ? 'Just placed'
    : `${Math.round(st.elapsed_min)} min ago`;

  // Progress bar
  const bar = document.getElementById('trackingProgressBar');
  if (bar) bar.style.width = st.progress + '%';

  // Status steps
  const stepsEl = document.getElementById('trackingSteps');
  if (stepsEl) {
    stepsEl.innerHTML = (st.steps || []).map(s => `
      <li class="step-item ${s.done ? 'done' : ''}">
        <div class="step-dot"></div>
        <div class="step-body">
          <span class="step-label">${escHtml(s.label)}</span>
          <span class="step-badge ${s.done ? '' : 'pending'}">${s.done ? 'Done' : 'Pending'}</span>
        </div>
      </li>`).join('');
  }

  // Order items
  const itemsEl = document.getElementById('trackingItems');
  if (itemsEl) {
    itemsEl.innerHTML = items.length
      ? items.map(it => `
          <li class="tracking-item">
            <span class="tracking-item-name">${escHtml(it.name)}</span>
            <span class="tracking-item-qty">×${it.qty}</span>
            <span class="tracking-item-price">SAR ${(it.price * it.qty).toLocaleString()}</span>
          </li>`).join('')
      : '<li class="tracking-item"><span class="tracking-item-name" style="color:rgba(14,18,9,.35)">No items</span></li>';
  }

  // Map
  initOrUpdateMap(wh, dest, st);
}

function _makeIcon(emoji) {
  return L.divIcon({
    html:      `<div class="map-marker-${emoji === '🏪' ? 'store' : emoji === '📍' ? 'dest' : 'courier'}">${emoji}</div>`,
    iconSize:  [36, 36],
    iconAnchor:[18, 18],
    className: '',
  });
}

function initOrUpdateMap(wh, dest, status) {
  const mapEl = document.getElementById('trackingMap');
  if (!mapEl) return;

  if (!_trackingMap) {
    _trackingMap = L.map('trackingMap', { zoomControl: true });
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(_trackingMap);

    _warehouseMarker = L.marker(wh, { icon: _makeIcon('🏪'), title: 'LeafGuard Warehouse' })
      .addTo(_trackingMap).bindPopup('LeafGuard Warehouse');
    _destMarker      = L.marker(dest, { icon: _makeIcon('📍'), title: 'Your Location' })
      .addTo(_trackingMap).bindPopup('Delivery Destination');
    _courierMarker   = L.marker(wh, { icon: _makeIcon('🚚'), title: 'Courier' })
      .addTo(_trackingMap).bindPopup('Your order is on the way!');
    _routeLine       = L.polyline([wh, dest], {
      color: '#5a9e3c', weight: 4, opacity: 0.6, dashArray: '8 5'
    }).addTo(_trackingMap);
  } else {
    _warehouseMarker.setLatLng(wh);
    _destMarker.setLatLng(dest);
    _routeLine.setLatLngs([wh, dest]);
  }

  _updateCourierPos(wh, dest, status);

  const group = L.featureGroup([_warehouseMarker, _destMarker, _routeLine]);
  _trackingMap.fitBounds(group.getBounds().pad(0.3));
  _trackingMap.invalidateSize();
}

function _lerp(a, b, t) { return a + (b - a) * t; }

function _updateCourierPos(wh, dest, status) {
  if (!_courierMarker) return;
  const steps   = status.steps || [];
  const elapsed = status.elapsed_min || 0;
  const outStep = steps.find(s => s.key === 'out_for_delivery');
  const delStep = steps.find(s => s.key === 'delivered');
  let t = 0;

  if (status.current_key === 'delivered') {
    t = 1;
  } else if (outStep && outStep.done) {
    const start = outStep.at_min ?? 0;
    const end   = delStep ? (delStep.at_min ?? start + 6) : start + 6;
    t = Math.max(0, Math.min(0.95, (elapsed - start) / Math.max(1, end - start)));
  }

  _courierMarker.setLatLng([
    _lerp(wh[0], dest[0], t),
    _lerp(wh[1], dest[1], t),
  ]);
}

function startTrackingPoll(id) {
  _trackingPollTimer = setInterval(() => fetchAndRenderOrder(id), 5000);
}

function stopTrackingPoll() {
  if (_trackingPollTimer) { clearInterval(_trackingPollTimer); _trackingPollTimer = null; }
}

async function submitOrder() {
  if (!cart.length) { alert('Your cart is empty.'); return; }

  const btn = document.querySelector('.checkout-btn');
  if (btn) { btn.disabled = true; btn.textContent = 'Placing order…'; }

  try {
    const payload = {
      items:    cart.map(i => ({ id: i.id, name: i.name, qty: i.qty, price: i.price })),
      dest_lat: userLocation?.lat ?? null,
      dest_lng: userLocation?.lng ?? null,
    };

    const res = await fetch('/api/order/submit', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify(payload),
    });

    if (res.status === 401) { window.location.href = '/'; return; }
    if (!res.ok) { alert((await res.json()).error || 'Failed to submit order.'); return; }

    const data = await res.json();
    if (!data.ok) { alert('Order failed.'); return; }

    // Clear cart
    cart = [];
    updateCartBadge();
    renderCart();
    cartOpen = false;
    document.getElementById('cartDrawer').classList.remove('open');
    document.getElementById('cartOverlay').classList.remove('open');

    // Navigate to order tracking
    goPage('orders');
    setTimeout(() => openOrder(data.order_id), 250);

  } catch(e) {
    alert('Network error — please try again.');
  } finally {
    if (btn) { btn.disabled = false; btn.textContent = 'Checkout'; }
  }
}

/* ============================================================
   DASHBOARD
   ============================================================ */
function refreshDashboard() {
  const s = window.simState || {};
  const simDayEl = document.getElementById('simDay');
  if (simDayEl) simDayEl.textContent = s.day || 1;

  const kpiHealth = document.getElementById('kpiHealth');
  if (kpiHealth) kpiHealth.textContent = s.avgHealth != null ? Math.round(s.avgHealth) + '%' : '—';

  const kpiYield = document.getElementById('kpiYield');
  if (kpiYield) kpiYield.textContent = s.yieldEst != null ? s.yieldEst + ' t/ha' : '—';

  const count = cart.reduce((s,i) => s+i.qty, 0);
  const total = cartSubtotal();
  const kpiCart = document.getElementById('kpiCart');
  if (kpiCart) kpiCart.textContent = count;
  const kpiCartTotal = document.getElementById('kpiCartTotal');
  if (kpiCartTotal) kpiCartTotal.textContent = 'SAR ' + total.toLocaleString();

  const dashDate = document.getElementById('dashDate');
  if (dashDate) dashDate.textContent = new Date().toLocaleDateString('en-GB', { day:'numeric', month:'long', year:'numeric' });

  // Dynamic greeting with user name
  const greetEl = document.getElementById('dashGreeting');
  if (greetEl) {
    const name = currentUser ? ', ' + currentUser.name.split(' ')[0] : '';
    greetEl.textContent = greeting() + name;
  }
}

function setDashSection(section) {
  document.querySelectorAll('.dash-nav-item').forEach(el =>
    el.classList.toggle('active', el.dataset.section === section)
  );
}

/* ============================================================
   CUSTOM CURSOR
   ============================================================ */
function initCursor() {
  const dot  = document.getElementById('cursorDot');
  const ring = document.getElementById('cursorRing');
  let mx = -100, my = -100, rx = -100, ry = -100;

  document.addEventListener('mousemove', e => {
    mx = e.clientX; my = e.clientY;
    dot.style.left = mx + 'px'; dot.style.top = my + 'px';
  });
  (function loop() {
    rx += (mx-rx) * 0.12; ry += (my-ry) * 0.12;
    ring.style.left = rx + 'px'; ring.style.top = ry + 'px';
    requestAnimationFrame(loop);
  })();

  const sel = 'a,button,.feature-card,.product-card,.filter-item,.topic-item,.quick-btn,.dash-nav-item,.cart-btn,.nav-link,.user-btn';
  document.addEventListener('mouseover', e => { if (e.target.closest(sel)) document.body.classList.add('cursor-hover'); });
  document.addEventListener('mouseout',  e => { if (e.target.closest(sel)) document.body.classList.remove('cursor-hover'); });
  document.addEventListener('mouseleave', () => { dot.style.opacity='0'; ring.style.opacity='0'; });
  document.addEventListener('mouseenter', () => { dot.style.opacity='1'; ring.style.opacity='1'; });
}

/* ============================================================
   WINDOW GLOBALS (simulation integration hooks)
   ============================================================ */
/* ============================================================
   FIELD MONITOR — Simulated IoT sensor dashboard
   Wrap goPage() so we can start/stop the sensor interval.
   ============================================================ */
const _mon = {
  moisture: 58, temp: 33, humidity: 42, light: 2400,
  history: [],        // rolling 40-reading moisture log
  pumpOn: false,
  pumpOverride: false,
  emailOn: false,
  alertEmail: '',
  alertLog: [],
  alertCooldowns: {}, // { key: lastTimestamp }
  ticker: null,
};

// ────────────────────────────────────────────────────────────────────
// SWAP POINT — replace fetchSensorReading() with a real HTTP fetch
// when the ESP32 is connected, e.g.:
//   const res = await fetch('http://esp32.local/api/sensors');
//   return await res.json();
// The rest of the monitor logic stays unchanged.
// ────────────────────────────────────────────────────────────────────
function fetchSensorReading() {
  // Gentle drift simulation
  const driftMoisture = _mon.pumpOn ? 0.9 : -0.5;
  _mon.moisture = Math.max(10, Math.min(95, _mon.moisture + driftMoisture + (Math.random() - 0.5) * 0.7));
  _mon.temp     = Math.max(18, Math.min(46, _mon.temp     + (Math.random() - 0.5) * 0.5));
  _mon.humidity = Math.max(10, Math.min(95, _mon.humidity + (Math.random() - 0.5) * 0.9));
  _mon.light    = Math.max(0,  Math.min(8000, _mon.light  + (Math.random() - 0.5) * 100));
  return { moisture: _mon.moisture, temp: _mon.temp, humidity: _mon.humidity, light: _mon.light };
}

// Thresholds — readings that trigger a warning card state + alert
const _THRESH = { moisture: 35, temp: 38, humidity: 30, light: 1500 };

// Pump auto-hysteresis: turns ON below 35%, stays ON until above 60%
function _updatePump(moisture) {
  if (_mon.pumpOverride) return;
  if (!_mon.pumpOn && moisture < 35) _mon.pumpOn = true;
  if (_mon.pumpOn  && moisture > 60) _mon.pumpOn = false;
}

// Rate-limited alert checker (12 s cooldown per sensor type)
function _checkAlerts(r) {
  const now = Date.now();
  const checks = [
    { key:'moisture', label:'Soil moisture low', cond: r.moisture < _THRESH.moisture, val: r.moisture.toFixed(1) + '%' },
    { key:'temp',     label:'Temperature high',  cond: r.temp     > _THRESH.temp,     val: r.temp.toFixed(1)     + '°C' },
    { key:'humidity', label:'Humidity low',       cond: r.humidity < _THRESH.humidity, val: r.humidity.toFixed(1) + '%' },
    { key:'light',    label:'Light insufficient', cond: r.light    < _THRESH.light,    val: Math.round(r.light)   + ' lux' },
  ];
  checks.forEach(c => {
    if (!c.cond) return;
    if (now - (_mon.alertCooldowns[c.key] || 0) < 12000) return;
    _mon.alertCooldowns[c.key] = now;
    // TODO: real email delivery — POST to a server-side endpoint here:
    //   fetch('/api/alerts/send', { method:'POST', body: JSON.stringify({ to: _mon.alertEmail, message: c.label + ': ' + c.val }) })
    //   Use Resend / SendGrid / SES on the server side, never from the browser.
    _mon.alertLog.unshift({
      text: c.label + ': ' + c.val,
      time: new Date().toLocaleTimeString([], { hour:'2-digit', minute:'2-digit', second:'2-digit' }),
      emailed: (_mon.emailOn && _mon.alertEmail) ? _mon.alertEmail : null,
    });
    if (_mon.alertLog.length > 60) _mon.alertLog.pop();
  });
}

function _renderSensors(r) {
  function card(id, rawVal, isWarn, decimals) {
    const sc = document.getElementById('sc-' + id);
    const sv = document.getElementById('sv-' + id);
    if (!sc || !sv) return;
    sv.textContent = rawVal.toFixed(decimals);
    sc.classList.toggle('warn', isWarn);
  }
  card('moisture', r.moisture, r.moisture < _THRESH.moisture, 1);
  card('temp',     r.temp,     r.temp     > _THRESH.temp,     1);
  card('humidity', r.humidity, r.humidity < _THRESH.humidity, 1);
  card('light',    r.light,    r.light    < _THRESH.light,    0);
}

function _renderPump() {
  const state   = document.getElementById('pumpState');
  const sub     = document.getElementById('pumpSub');
  const iconWrp = document.getElementById('pumpIconWrap');
  const btn     = document.getElementById('pumpOverrideBtn');
  if (!state) return;
  const on = _mon.pumpOn;
  state.textContent = on ? 'WATERING' : 'IDLE';
  state.classList.toggle('watering', on);
  iconWrp && iconWrp.classList.toggle('watering', on);
  if (sub) sub.textContent = _mon.pumpOverride
    ? (on ? 'Manual override — pump forced ON' : 'Manual override — pump forced OFF')
    : (on ? 'Auto: moisture below 35%' : 'Moisture adequate');
  if (btn) {
    btn.textContent = _mon.pumpOverride ? 'Cancel override' : (on ? 'Force OFF' : 'Force ON');
    btn.classList.toggle('active', _mon.pumpOverride);
  }
}

function _drawChart() {
  const canvas = document.getElementById('moistureChart');
  if (!canvas || !canvas.parentElement) return;
  const W = canvas.parentElement.clientWidth - 44;
  const H = 160;
  if (W < 1) return;
  canvas.width  = W;
  canvas.height = H;
  const ctx = canvas.getContext('2d');
  const hist = _mon.history;
  if (hist.length < 2) return;

  const pad = { t:10, r:8, b:10, l:28 };
  const gW = W - pad.l - pad.r;
  const gH = H - pad.t - pad.b;

  ctx.clearRect(0, 0, W, H);

  // Faint grid lines at 25 / 50 / 75 %
  ctx.strokeStyle = 'rgba(14,18,9,.05)'; ctx.lineWidth = 1;
  [25, 50, 75].forEach(pct => {
    const y = pad.t + gH - (pct / 100) * gH;
    ctx.beginPath(); ctx.moveTo(pad.l, y); ctx.lineTo(W - pad.r, y); ctx.stroke();
    ctx.fillStyle = 'rgba(14,18,9,.28)';
    ctx.font = '9px Cabinet Grotesk, sans-serif';
    ctx.fillText(pct + '%', 0, y + 3);
  });

  // Threshold dashed line at 35%
  const ty = pad.t + gH - (35 / 100) * gH;
  ctx.setLineDash([5, 4]);
  ctx.strokeStyle = 'rgba(184,118,74,.7)';
  ctx.lineWidth = 1.5;
  ctx.beginPath(); ctx.moveTo(pad.l, ty); ctx.lineTo(W - pad.r, ty); ctx.stroke();
  ctx.setLineDash([]);

  // Map history → canvas points
  const pts = hist.map((v, i) => ({
    x: pad.l + (i / (hist.length - 1)) * gW,
    y: pad.t + gH - (Math.max(0, Math.min(100, v)) / 100) * gH,
  }));

  // Filled area under the line
  const grad = ctx.createLinearGradient(0, pad.t, 0, pad.t + gH);
  grad.addColorStop(0, 'rgba(90,158,60,.2)');
  grad.addColorStop(1, 'rgba(90,158,60,.0)');
  ctx.fillStyle = grad;
  ctx.beginPath();
  ctx.moveTo(pts[0].x, pad.t + gH);
  pts.forEach(p => ctx.lineTo(p.x, p.y));
  ctx.lineTo(pts[pts.length - 1].x, pad.t + gH);
  ctx.closePath(); ctx.fill();

  // Moisture line
  ctx.strokeStyle = '#5a9e3c'; ctx.lineWidth = 2; ctx.lineJoin = 'round';
  ctx.beginPath();
  pts.forEach((p, i) => i === 0 ? ctx.moveTo(p.x, p.y) : ctx.lineTo(p.x, p.y));
  ctx.stroke();

  // Current-value dot
  const last = pts[pts.length - 1];
  ctx.fillStyle = '#5a9e3c';
  ctx.beginPath(); ctx.arc(last.x, last.y, 4, 0, Math.PI * 2); ctx.fill();
  ctx.fillStyle = '#fff';
  ctx.beginPath(); ctx.arc(last.x, last.y, 2, 0, Math.PI * 2); ctx.fill();
}

function _renderAlertLog() {
  const list  = document.getElementById('alertLogList');
  const badge = document.getElementById('alertCountBadge');
  if (!list) return;
  if (badge) badge.textContent = _mon.alertLog.length;
  if (_mon.alertLog.length === 0) {
    list.innerHTML = '<div class="alert-log-empty">No alerts yet &mdash; monitoring in progress</div>';
    return;
  }
  list.innerHTML = _mon.alertLog.map(a => `
    <div class="alert-log-row">
      <div class="alert-log-dot"></div>
      <div class="alert-log-body">
        <div class="alert-log-text">${a.text}</div>
        ${a.emailed ? `<div class="alert-log-emailed">emailed &rarr; ${a.emailed}</div>` : ''}
      </div>
      <div class="alert-log-time">${a.time}</div>
    </div>`).join('');
}

function _monitorTick() {
  const r = fetchSensorReading();
  _mon.history.push(r.moisture);
  if (_mon.history.length > 40) _mon.history.shift();
  _updatePump(r.moisture);
  _checkAlerts(r);
  _renderSensors(r);
  _renderPump();
  _drawChart();
  _renderAlertLog();
}

// Public handlers referenced from HTML
window.togglePumpOverride = function() {
  if (!_mon.pumpOverride) {
    _mon.pumpOverride = true;
    _mon.pumpOn = !_mon.pumpOn; // flip from current state
  } else {
    _mon.pumpOverride = false;  // return to auto
  }
  _renderPump();
};

window.toggleEmailAlerts = function() {
  _mon.emailOn = !_mon.emailOn;
  const btn = document.getElementById('emailToggle');
  if (btn) btn.setAttribute('aria-checked', String(_mon.emailOn));
  const status = document.getElementById('emailStatus');
  if (status) status.textContent = _mon.emailOn
    ? 'Alerts will be marked as emailed when they fire.'
    : '';
};

// Wrap goPage to start/stop the sensor interval
(function() {
  const _orig = window.goPage;
  window.goPage = function(name) {
    _orig(name);
    if (name === 'monitor') {
      if (!_mon.ticker) _mon.ticker = setInterval(_monitorTick, 2000);
      _monitorTick(); // immediate render on page open
    } else {
      if (_mon.ticker) { clearInterval(_mon.ticker); _mon.ticker = null; }
    }
  };
})();

window.simState = { day:1, plants:[], avgHealth:0, avgWater:0, yieldEst:0, appliedProducts:[] };
window.addToCartById   = id => addToCart(id);
window.goPage          = goPage;
window.refreshDashboard = refreshDashboard;

/* ============================================================
   INIT
   ============================================================ */
document.addEventListener('DOMContentLoaded', async () => {
  initCursor();

  // Auth check — redirect to login if not authenticated
  await loadUser();

  // Load saved location
  loadSavedLocation();

  // Init shop + chat
  initShopFilters();
  renderProducts();
  initChat();
  refreshDashboard();

  // Start on home page
  goPage('home');

  // Show location modal on first visit (slight delay for UX)
  setTimeout(showLocationModal, 1200);

  // Poll dashboard KPIs for sim state changes
  setInterval(() => { if (currentPage === 'dashboard') refreshDashboard(); }, 2000);

  // Wire email input → monitor state
  const _alertEmailEl = document.getElementById('alertEmail');
  if (_alertEmailEl) _alertEmailEl.addEventListener('input', () => { _mon.alertEmail = _alertEmailEl.value.trim(); });
});
