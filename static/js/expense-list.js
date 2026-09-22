// Controls the "Browse Expenses" table: filters, pagination, rendering, and delete.
// `onEditRequested(expense)` is called when the user clicks Edit on a row.
// `onDeleted()` is called after a successful delete (e.g. to refresh category options).
function createExpenseList({ pageSize, onEditRequested, onDeleted }) {
  const listBanner = document.getElementById('listBanner');
  const listContent = document.getElementById('listContent');
  const pageInfo = document.getElementById('pageInfo');
  const prevPageBtn = document.getElementById('prevPageBtn');
  const nextPageBtn = document.getElementById('nextPageBtn');
  const filterCategoryInput = document.getElementById('filterCategory');
  const filterStartInput = document.getElementById('filterStart');
  const filterEndInput = document.getElementById('filterEnd');

  let currentOffset = 0;

  const { start: defaultStart, end: defaultEnd, today: todayIso } = currentMonthRange();
  filterStartInput.max = todayIso;
  filterEndInput.max = todayIso;
  filterStartInput.value = defaultStart;
  filterEndInput.value = defaultEnd;

  document.getElementById('applyFilterBtn').addEventListener('click', () => {
    currentOffset = 0;
    refresh();
  });
  prevPageBtn.addEventListener('click', () => {
    currentOffset = Math.max(0, currentOffset - pageSize);
    refresh();
  });
  nextPageBtn.addEventListener('click', () => {
    currentOffset += pageSize;
    refresh();
  });

  function buildListQuery() {
    const params = new URLSearchParams();
    const category = filterCategoryInput.value.trim();
    const start = filterStartInput.value;
    const end = filterEndInput.value;
    if (category) params.set('category', category);
    if (start) params.set('start_date', start);
    if (end) params.set('end_date', end);
    params.set('limit', pageSize);
    params.set('offset', currentOffset);
    return params.toString();
  }

  async function deleteExpense(id) {
    const confirmed = await confirmDialog('Delete this expense? This cannot be undone.');
    if (!confirmed) return;
    try {
      const response = await apiFetch(`/expenses/${id}`, { method: 'DELETE' });
      if (response.status === 401) {
        showBanner(listBanner, 'Invalid API key — check the key above and try again.', 'error');
        return;
      }
      if (!response.ok && response.status !== 204) {
        showBanner(listBanner, 'Could not delete this expense. Please try again.', 'error');
        return;
      }
      refresh();
      onDeleted();
    } catch (networkError) {
      showBanner(listBanner, 'Could not reach the server. Check your connection and try again.', 'error');
    }
  }

  function renderList(data) {
    if (!data.items.length) {
      listContent.innerHTML = '<p class="empty-state">No expenses match these filters.</p>';
    } else {
      const rows = data.items.map((expense) => `
        <tr>
          <td>${escapeHtml(expense.date)}</td>
          <td>${escapeHtml(expense.category)}</td>
          <td class="note-cell" title="${escapeHtml(expense.note || '')}">${escapeHtml(expense.note || '')}</td>
          <td class="amount-cell">${formatCurrency(expense.amount)}</td>
          <td class="actions-cell">
            <div class="button-group">
              <button type="button" class="secondary small" data-edit="${expense.id}">Edit</button>
              <button type="button" class="danger small" data-delete="${expense.id}">Delete</button>
            </div>
          </td>
        </tr>`).join('');
      listContent.innerHTML = `
        <div class="table-scroll">
          <table class="expense-table">
            <thead><tr><th>Date</th><th>Category</th><th>Note</th><th>Amount</th><th></th></tr></thead>
            <tbody>${rows}</tbody>
          </table>
        </div>`;
      listContent.querySelectorAll('[data-edit]').forEach((btn) => {
        btn.addEventListener('click', () => {
          const expense = data.items.find((e) => e.id === Number(btn.dataset.edit));
          if (expense) onEditRequested(expense);
        });
      });
      listContent.querySelectorAll('[data-delete]').forEach((btn) => {
        btn.addEventListener('click', () => deleteExpense(Number(btn.dataset.delete)));
      });
    }

    const shown = data.items.length ? data.offset + 1 : 0;
    const shownEnd = data.offset + data.items.length;
    pageInfo.textContent = data.total
      ? `Showing ${shown}-${shownEnd} of ${data.total}`
      : 'No results';
    prevPageBtn.disabled = data.offset === 0;
    nextPageBtn.disabled = shownEnd >= data.total;
  }

  async function refresh() {
    hideBanner(listBanner);
    try {
      const response = await apiFetch(`/expenses?${buildListQuery()}`);
      if (response.status === 401) {
        showBanner(listBanner, 'Invalid API key — check the key above and try again.', 'error');
        return;
      }
      if (response.status === 400) {
        showBanner(listBanner, (await response.json()).detail || 'Invalid filter.', 'error');
        return;
      }
      if (!response.ok) {
        showBanner(listBanner, 'Could not load expenses. Please try again.', 'error');
        return;
      }
      renderList(await response.json());
    } catch (networkError) {
      showBanner(listBanner, 'Could not reach the server. Check your connection and try again.', 'error');
    }
  }

  return { refresh };
}
