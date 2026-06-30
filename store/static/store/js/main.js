// ── CSRF helper ──────────────────────────────────────
function getCookie(name) {
  let value = null;
  document.cookie.split(';').forEach(c => {
    const [k, v] = c.trim().split('=');
    if (k === name) value = decodeURIComponent(v);
  });
  return value;
}

// ── Ajax Add-to-Cart ─────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {

  // Intercept add-to-cart forms on product list
  document.querySelectorAll('.add-to-cart-form').forEach(form => {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const btn = form.querySelector('.add-cart-btn');
      btn.disabled = true;
      btn.textContent = '…';

      const data = new FormData(form);
      const res = await fetch(form.action, {
        method: 'POST',
        body: data,
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
      });
      const json = await res.json();

      if (json.success) {
        // Update cart badge
        document.querySelectorAll('#cart-count').forEach(el => {
          el.textContent = json.cart_count;
        });
        btn.textContent = '✓ Added';
        btn.style.background = '#28a745';
        setTimeout(() => {
          btn.textContent = '+ Cart';
          btn.style.background = '';
          btn.disabled = false;
        }, 1500);
      }
    });
  });

  // Auto-dismiss alerts after 5s
  document.querySelectorAll('.alert').forEach(alert => {
    setTimeout(() => alert.remove(), 5000);
  });

  // Sort link active state
  const currentSort = new URLSearchParams(location.search).get('sort') || 'name';
  document.querySelectorAll('.sort-link').forEach(link => {
    if (link.dataset.sort === currentSort) link.classList.add('active');
  });
});

// ── Quantity helper on detail page ──────────────────
window.changeQty = function(delta) {
  const input = document.getElementById('qty');
  if (!input) return;
  const max = parseInt(input.max) || 99;
  input.value = Math.max(1, Math.min(max, parseInt(input.value || 1) + delta));
};
