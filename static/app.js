const API_KEY_STORAGE_KEY = 'spendTracker.apiKey';

const currencyFormatter = new Intl.NumberFormat('en-IN', {
  style: 'currency',
  currency: 'INR',
});

function formatCurrency(value) {
  return currencyFormatter.format(value);
}

function getApiKey() {
  return sessionStorage.getItem(API_KEY_STORAGE_KEY) || 'dev-local-key';
}

function setApiKey(value) {
  sessionStorage.setItem(API_KEY_STORAGE_KEY, value);
}

function initApiKeyField(inputEl) {
  inputEl.value = getApiKey();
  inputEl.addEventListener('change', () => setApiKey(inputEl.value));
}

async function apiFetch(path, options = {}) {
  const headers = Object.assign({}, options.headers, { 'X-API-Key': getApiKey() });
  const response = await fetch(path, Object.assign({}, options, { headers }));
  return response;
}

function escapeHtml(str) {
  return String(str).replace(/[&<>"']/g, (c) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
  }[c]));
}

function showBanner(el, message, kind) {
  el.textContent = message;
  el.className = 'banner show ' + kind;
}

function hideBanner(el) {
  el.className = 'banner';
  el.textContent = '';
}
