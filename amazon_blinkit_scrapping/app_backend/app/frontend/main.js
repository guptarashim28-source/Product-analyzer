const form = document.getElementById('scrape-form');
const loading = document.getElementById('loading');
const results = document.getElementById('results');
const summary = document.getElementById('summary');
const brandList = document.getElementById('brand-list');
const productsTableBody = document.querySelector('#products-table tbody');
const downloadBtn = document.getElementById('download-csv');

let lastParams = null;

function show(el) { el.classList.remove('hidden'); }
function hide(el) { el.classList.add('hidden'); }

form.addEventListener('submit', async (e) => {
  e.preventDefault();

  hide(results);
  show(loading);

  const query = document.getElementById('query').value.trim();
  const pincodesRaw = document.getElementById('pincodes').value.trim();
  const save_html = document.getElementById('save_html').checked;

  const pincodes = pincodesRaw
    .split(/\n|,/) // split by comma or newline
    .map(p => p.trim())
    .filter(Boolean);

  lastParams = { query, pincodes, save_html };

  try {
    const resp = await fetch('/api/scrape', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(lastParams),
    });

    if (!resp.ok) {
      throw new Error(`Request failed: ${resp.status}`);
    }

    const data = await resp.json();

    // Summary
    summary.innerHTML = `
      <div class="card">
        <h2>Summary</h2>
        <p><strong>Query:</strong> ${data.summary.query}</p>
        <p><strong>Pincodes:</strong> ${data.summary.pincodes.join(', ')}</p>
        <p><strong>Total products:</strong> ${data.summary.total_products}</p>
      </div>
    `;

    // Brand list
    brandList.innerHTML = '';
    data.brand_top10_counts.forEach(({ brand, count }) => {
      const li = document.createElement('li');
      li.textContent = `${brand}: ${count}`;
      brandList.appendChild(li);
    });

    // Products table
    productsTableBody.innerHTML = '';
    data.products.forEach((p) => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${p.pincode}</td>
        <td>${p.rank ?? ''}</td>
        <td>${p.brand ?? ''}</td>
        <td>${p.name ?? ''}</td>
        <td>${p.weight ?? ''}</td>
        <td>${p.price != null ? `₹${p.price}` : (p.price_text || '')}</td>
        <td>${p.price_per_100g != null ? `₹${p.price_per_100g}` : ''}</td>
      `;
      productsTableBody.appendChild(tr);
    });

    hide(loading);
    show(results);
  } catch (err) {
    hide(loading);
    alert(`Error: ${err.message}`);
  }
});

downloadBtn?.addEventListener('click', async () => {
  if (!lastParams) {
    alert('Run a search first.');
    return;
  }
  try {
    const resp = await fetch('/api/export-csv', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(lastParams),
    });
    if (!resp.ok) throw new Error(`Request failed: ${resp.status}`);
    const blob = await resp.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'blinkit_products.csv';
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  } catch (e) {
    alert(`Error exporting CSV: ${e.message}`);
  }
});
