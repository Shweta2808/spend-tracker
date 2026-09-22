const apiKeyInput = document.getElementById('apiKey');
initApiKeyField(apiKeyInput);

const refreshBtn = document.getElementById('refreshBtn');
const summaryBanner = document.getElementById('summaryBanner');
const summaryContent = document.getElementById('summaryContent');

const monthPicker = createMonthPicker(
  document.getElementById('monthSelect'),
  document.getElementById('yearSelect'),
);

function renderSummary(data) {
  const categoryEntries = Object.entries(data.spend_by_category);
  const spikeCategories = new Set(data.category_spikes.map((s) => s.category));
  const change = data.month_over_month_change;
  const changeDirectionClass = change.absolute_change > 0 ? 'positive' : change.absolute_change < 0 ? 'negative' : '';
  const changeText = change.percent_change === null
    ? `${change.absolute_change >= 0 ? '+' : ''}${formatCurrency(change.absolute_change)}`
    : `${change.absolute_change >= 0 ? '+' : ''}${formatCurrency(change.absolute_change)} (${change.percent_change.toFixed(1)}%)`;

  const categoryRows = categoryEntries.length
    ? categoryEntries.map(([category, total]) => `
        <div class="category-row">
          <span>${escapeHtml(category)}${spikeCategories.has(category) ? '<span class="spike-badge">▲ spike</span>' : ''}</span>
          <span class="amount">${formatCurrency(total)}</span>
        </div>`).join('')
    : '<p class="empty-state">No expenses recorded this month.</p>';

  summaryContent.innerHTML = `
    <div class="stat-cards">
      <div class="stat-card">
        <div class="label">Month</div>
        <div class="value">${escapeHtml(data.month)}</div>
      </div>
      <div class="stat-card">
        <div class="label">Total spend</div>
        <div class="value">${formatCurrency(data.total_spend)}</div>
      </div>
      <div class="stat-card">
        <div class="label">Vs. last month</div>
        <div class="value ${changeDirectionClass}">${changeText}</div>
      </div>
    </div>
    ${categoryRows}
  `;
}

async function refreshSummary() {
  hideBanner(summaryBanner);
  refreshBtn.disabled = true;
  try {
    const month = monthPicker.getValue();
    const response = await apiFetch(`/summary?month=${encodeURIComponent(month)}`);

    if (response.status === 401) {
      showBanner(summaryBanner, 'Invalid API key — check the key above and try again.', 'error');
      return;
    }
    if (response.status === 422) {
      showBanner(summaryBanner, 'Enter a valid month.', 'error');
      return;
    }
    if (!response.ok) {
      showBanner(summaryBanner, 'Could not load the summary. Please try again.', 'error');
      return;
    }

    const data = await response.json();
    monthPicker.setValue(data.month);
    renderSummary(data);
  } catch (networkError) {
    showBanner(summaryBanner, 'Could not reach the server. Check your connection and try again.', 'error');
  } finally {
    refreshBtn.disabled = false;
  }
}

refreshBtn.addEventListener('click', refreshSummary);
document.getElementById('monthSelect').addEventListener('change', refreshSummary);
document.getElementById('yearSelect').addEventListener('change', refreshSummary);
refreshSummary();
