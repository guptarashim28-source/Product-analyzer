const form = document.getElementById('scrape-form');
const loading = document.getElementById('loading');
const loadingMessage = document.getElementById('loading-message');
const results = document.getElementById('results');
const summary = document.getElementById('summary');
const brandList = document.getElementById('brand-list');
const productsTableBody = document.querySelector('#products-table tbody');
const downloadBtn = document.getElementById('download-csv');
const gapAnalysisSection = document.getElementById('gap-analysis');
const gapContent = document.getElementById('gap-content');
const analyzedProductsSection = document.getElementById('analyzed-products');
const analysisList = document.getElementById('analysis-list');
const newsTrendsSection = document.getElementById('news-trends');
const newsContent = document.getElementById('news-content');
const trendsContent = document.getElementById('trends-content');

let lastParams = null;

function show(el) { el.classList.remove('hidden'); }
function hide(el) { el.classList.add('hidden'); }

form.addEventListener('submit', async (e) => {
  e.preventDefault();

  hide(results);
  hide(gapAnalysisSection);
  hide(analyzedProductsSection);
  hide(newsTrendsSection);
  show(loading);

  const query = document.getElementById('query').value.trim();
  const pincodesRaw = document.getElementById('pincodes').value.trim();
  const save_html = document.getElementById('save_html').checked;
  const ai_analysis = document.getElementById('ai_analysis').checked;

  const pincodes = pincodesRaw
    .split(/\n|,/) // split by comma or newline
    .map(p => p.trim())
    .filter(Boolean);

  lastParams = { query, pincodes, save_html };

  try {
    const endpoint = ai_analysis ? '/api/analyze' : '/api/scrape';
    
    if (ai_analysis) {
      loadingMessage.textContent = 'Scraping and analyzing with AI... Analyzing top 5 products (this may take 1-2 minutes).';
    } else {
      loadingMessage.textContent = 'Scraping Blinkit... This can take ~30–60 seconds per pincode.';
    }

    const requestBody = ai_analysis 
      ? { ...lastParams, top_n: 5, include_gap_analysis: true }
      : lastParams;

    const resp = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestBody),
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
        ${data.summary.analyzed_count ? `<p><strong>AI Analyzed:</strong> ${data.summary.analyzed_count}</p>` : ''}
      </div>
    `;

    // Gap Analysis
    if (ai_analysis && data.gap_analysis) {
      renderGapAnalysis(data.gap_analysis);
      show(gapAnalysisSection);
    }

    // Analyzed Products
    if (ai_analysis && data.analyzed_products) {
      renderAnalyzedProducts(data.analyzed_products);
      show(analyzedProductsSection);
    }

    // Fetch News & Trends
    if (ai_analysis) {
      fetchNewsAndTrends(query);
    }

    // Brand list
    brandList.innerHTML = '';
    data.brand_top10_counts.forEach(({ brand, count }) => {
      const li = document.createElement('li');
      li.textContent = `${brand}: ${count}`;
      brandList.appendChild(li);
    });

    // Products table
    productsTableBody.innerHTML = '';
    const products = data.analyzed_products || data.products;
    products.forEach((p) => {
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

function renderGapAnalysis(gap) {
  let html = `
    <div class="gap-section">
      <h3>Market Overview</h3>
      <p>${gap.market_overview || 'N/A'}</p>
    </div>
  `;

  if (gap.common_strengths?.length) {
    html += `
      <div class="gap-section">
        <h3>✅ Common Strengths in Market</h3>
        <ul>${gap.common_strengths.map(s => `<li>${s}</li>`).join('')}</ul>
      </div>
    `;
  }

  if (gap.common_weaknesses?.length) {
    html += `
      <div class="gap-section">
        <h3>⚠️ Common Weaknesses in Market</h3>
        <ul>${gap.common_weaknesses.map(w => `<li>${w}</li>`).join('')}</ul>
      </div>
    `;
  }

  if (gap.market_gaps?.length) {
    html += `
      <div class="gap-section">
        <h3>🎯 Market Gaps & Opportunities</h3>
        ${gap.market_gaps.map(g => `
          <div class="gap-item">
            <strong>${g.gap}</strong> <span class="priority priority-${g.priority?.toLowerCase()}">${g.priority}</span>
            <p>${g.opportunity}</p>
          </div>
        `).join('')}
      </div>
    `;
  }

  if (gap.recommended_product) {
    const rec = gap.recommended_product;
    html += `
      <div class="gap-section recommended-product">
        <h3>🚀 Recommended Product to Launch</h3>
        <p><strong>Concept:</strong> ${rec.product_concept || 'N/A'}</p>
        <p><strong>USP:</strong> ${rec.usp || 'N/A'}</p>
        <p><strong>Target Price:</strong> ${rec.target_price_range || 'N/A'}</p>
        <p><strong>Target Audience:</strong> ${rec.target_audience || 'N/A'}</p>
        ${rec.key_features?.length ? `
          <div>
            <strong>Key Features:</strong>
            <ul>${rec.key_features.map(f => `<li>${f}</li>`).join('')}</ul>
          </div>
        ` : ''}
        ${rec.competitive_advantages?.length ? `
          <div>
            <strong>Competitive Advantages:</strong>
            <ul>${rec.competitive_advantages.map(a => `<li>${a}</li>`).join('')}</ul>
          </div>
        ` : ''}
      </div>
    `;
  }

  if (gap.implementation_strategy) {
    const impl = gap.implementation_strategy;
    html += `
      <div class="gap-section">
        <h3>📋 Implementation Strategy</h3>
        ${impl.ingredients_to_include?.length ? `
          <p><strong>Include:</strong> ${impl.ingredients_to_include.join(', ')}</p>
        ` : ''}
        ${impl.ingredients_to_avoid?.length ? `
          <p><strong>Avoid:</strong> ${impl.ingredients_to_avoid.join(', ')}</p>
        ` : ''}
        <p><strong>Packaging:</strong> ${impl.packaging_recommendations || 'N/A'}</p>
        <p><strong>Pricing:</strong> ${impl.pricing_strategy || 'N/A'}</p>
      </div>
    `;
  }

  gapContent.innerHTML = html;
}

function renderAnalyzedProducts(products) {
  analysisList.innerHTML = products.map((p, idx) => {
    const analysis = p.analysis || {};
    return `
      <div class="card product-analysis">
        <h3>#${idx + 1} ${p.brand} - ${p.name}</h3>
        <div class="product-meta">
          <span>₹${p.price} (${p.weight})</span>
          <span>₹${p.price_per_100g}/100g</span>
          ${analysis.health_score ? `<span class="health-score">Health: ${analysis.health_score}</span>` : ''}
        </div>
        
        ${analysis.description ? `
          <div class="analysis-section">
            <strong>Description:</strong>
            <p>${analysis.description}</p>
          </div>
        ` : ''}
        
        ${analysis.nutrition_analysis ? `
          <div class="analysis-section">
            <strong>Nutrition Analysis:</strong>
            <p>${analysis.nutrition_analysis}</p>
          </div>
        ` : ''}
        
        ${analysis.ingredient_analysis ? `
          <div class="analysis-section">
            <strong>Ingredient Analysis:</strong>
            <p>${analysis.ingredient_analysis}</p>
          </div>
        ` : ''}
        
        <div class="pros-cons">
          ${analysis.pros?.length ? `
            <div class="pros">
              <strong>✅ Pros:</strong>
              <ul>${analysis.pros.map(pro => `<li>${pro}</li>`).join('')}</ul>
            </div>
          ` : ''}
          
          ${analysis.cons?.length ? `
            <div class="cons">
              <strong>❌ Cons:</strong>
              <ul>${analysis.cons.map(con => `<li>${con}</li>`).join('')}</ul>
            </div>
          ` : ''}
        </div>
        
        ${analysis.target_audience ? `
          <div class="analysis-section">
            <strong>Target Audience:</strong>
            <p>${analysis.target_audience}</p>
          </div>
        ` : ''}
      </div>
    `;
  }).join('');
}

// Tab switching for news section
document.querySelectorAll('.tab-button').forEach(btn => {
  btn.addEventListener('click', (e) => {
    const tab = e.target.dataset.tab;
    
    // Update button states
    document.querySelectorAll('.tab-button').forEach(b => b.classList.remove('active'));
    e.target.classList.add('active');
    
    // Update content visibility
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    if (tab === 'news') {
      newsContent.classList.add('active');
    } else {
      trendsContent.classList.add('active');
    }
  });
});

async function fetchNewsAndTrends(query) {
  try {
    // Fetch news
    const newsResp = await fetch(`/api/news/${encodeURIComponent(query)}?days=7&max_results=10`);
    const newsData = await newsResp.json();
    renderNews(newsData);

    // Fetch trends
    const trendsResp = await fetch(`/api/market-trends/${encodeURIComponent(query)}`);
    const trendsData = await trendsResp.json();
    renderTrends(trendsData);

    show(newsTrendsSection);
  } catch (err) {
    console.error('Error fetching news/trends:', err);
    newsContent.innerHTML = `<p class="error">Failed to load news: ${err.message}</p>`;
    trendsContent.innerHTML = `<p class="error">Failed to load trends: ${err.message}</p>`;
  }
}

function renderNews(data) {
  if (!data.success) {
    newsContent.innerHTML = `
      <div class="news-error">
        <p>⚠️ ${data.error}</p>
        ${data.error.includes('not configured') ? `
          <p>Get your free API key from <a href="https://newsapi.org/" target="_blank">NewsAPI.org</a> and add it to your .env file.</p>
        ` : ''}
      </div>
    `;
    return;
  }

  if (!data.articles?.length) {
    newsContent.innerHTML = '<p>No recent news found for this topic.</p>';
    return;
  }

  newsContent.innerHTML = `
    <div class="news-header">
      <p><strong>Found ${data.total_results} articles</strong> (showing ${data.articles.length})</p>
      <p class="date-range">${data.date_range}</p>
    </div>
    <div class="news-grid">
      ${data.articles.map(article => `
        <div class="news-card">
          ${article.image_url ? `<img src="${article.image_url}" alt="${article.title}" class="news-image" onerror="this.style.display='none'">` : ''}
          <div class="news-content">
            <h4><a href="${article.url}" target="_blank">${article.title}</a></h4>
            <p class="news-source">${article.source} • ${new Date(article.published_at).toLocaleDateString()}</p>
            ${article.description ? `<p class="news-description">${article.description}</p>` : ''}
          </div>
        </div>
      `).join('')}
    </div>
  `;
}

function renderTrends(data) {
  if (!data.success) {
    trendsContent.innerHTML = `
      <div class="news-error">
        <p>⚠️ ${data.error}</p>
      </div>
    `;
    return;
  }

  if (!data.trends?.length) {
    trendsContent.innerHTML = '<p>No market trends found for this category.</p>';
    return;
  }

  let html = '';
  
  if (data.insights?.length) {
    html += `
      <div class="insights-section">
        <h4>🔍 Key Insights</h4>
        <ul class="insights-list">
          ${data.insights.map(insight => `<li>${insight}</li>`).join('')}
        </ul>
      </div>
    `;
  }

  html += `
    <div class="trends-list">
      ${data.trends.map(trend => `
        <div class="trend-card">
          <h4><a href="${trend.url}" target="_blank">${trend.title}</a></h4>
          <p class="news-source">${trend.source} • ${new Date(trend.published_at).toLocaleDateString()}</p>
          ${trend.description ? `<p>${trend.description}</p>` : ''}
        </div>
      `).join('')}
    </div>
  `;

  trendsContent.innerHTML = html;
}
