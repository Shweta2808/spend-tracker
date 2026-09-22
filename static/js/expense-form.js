// Controls the "Add Expense" form: client-side validation, create/update submission,
// and switching in and out of edit mode. `onSaved` is called after a successful
// create/update/delete-recovery so the caller (the list) can refresh itself.
function createExpenseForm({ onSaved }) {
  const form = document.getElementById('expenseForm');
  const addExpenseBtn = document.getElementById('addExpenseBtn');
  const cancelEditBtn = document.getElementById('cancelEditBtn');
  const expenseBanner = document.getElementById('expenseBanner');
  const noteInput = document.getElementById('note');

  const fields = {
    amount: { input: document.getElementById('amount'), error: document.getElementById('amountError') },
    category: { input: document.getElementById('category'), error: document.getElementById('categoryError') },
    date: { input: document.getElementById('date'), error: document.getElementById('dateError') },
  };

  const API_FIELD_MAP = { amount: 'amount', category: 'category', date: 'date' };

  let editingExpenseId = null;

  fields.date.input.value = todayIsoDate();
  fields.amount.input.focus();

  function clearFieldErrors() {
    Object.values(fields).forEach(({ input, error }) => {
      input.classList.remove('invalid');
      error.textContent = '';
    });
  }

  function setFieldError(fieldName, message) {
    const { input, error } = fields[fieldName];
    input.classList.add('invalid');
    error.textContent = message;
  }

  function validateClientSide() {
    clearFieldErrors();
    let valid = true;
    if (fields.amount.input.value === '' || Number(fields.amount.input.value) <= 0) {
      setFieldError('amount', 'Enter an amount greater than 0.');
      valid = false;
    }
    if (fields.category.input.value.trim() === '') {
      setFieldError('category', 'Category is required.');
      valid = false;
    }
    if (fields.date.input.value === '') {
      setFieldError('date', 'Date is required.');
      valid = false;
    }
    return valid;
  }

  function humanizeApiError(field) {
    if (field === 'amount') return 'Amount must be greater than 0.';
    if (field === 'category') return 'Category cannot be empty.';
    if (field === 'date') return 'Enter a valid date.';
    return 'Invalid value.';
  }

  function applyServerValidationErrors(detail) {
    clearFieldErrors();
    if (!Array.isArray(detail)) {
      showBanner(expenseBanner, 'Could not save this expense — please check the form and try again.', 'error');
      return;
    }
    for (const issue of detail) {
      const field = issue.loc && issue.loc[issue.loc.length - 1];
      const formField = Object.keys(API_FIELD_MAP).find((key) => API_FIELD_MAP[key] === field);
      if (formField) setFieldError(formField, humanizeApiError(field));
    }
    showBanner(expenseBanner, 'Please fix the highlighted fields.', 'error');
  }

  function startEditing(expense) {
    editingExpenseId = expense.id;
    fields.amount.input.value = expense.amount;
    fields.category.input.value = expense.category;
    fields.date.input.value = expense.date;
    noteInput.value = expense.note || '';
    addExpenseBtn.textContent = 'Save Changes';
    cancelEditBtn.classList.remove('hidden');
    hideBanner(expenseBanner);
    form.scrollIntoView({ behavior: 'smooth' });
  }

  function stopEditing() {
    editingExpenseId = null;
    form.reset();
    fields.date.input.value = todayIsoDate();
    addExpenseBtn.textContent = 'Add Expense';
    cancelEditBtn.classList.add('hidden');
    clearFieldErrors();
  }

  cancelEditBtn.addEventListener('click', stopEditing);

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    hideBanner(expenseBanner);

    if (!validateClientSide()) {
      showBanner(expenseBanner, 'Please fix the highlighted fields.', 'error');
      return;
    }

    const payload = {
      amount: Number(fields.amount.input.value),
      category: fields.category.input.value.trim(),
      note: noteInput.value.trim() || null,
      date: fields.date.input.value,
    };

    const isEditing = editingExpenseId !== null;
    addExpenseBtn.disabled = true;
    addExpenseBtn.textContent = isEditing ? 'Saving…' : 'Adding…';

    try {
      const response = await apiFetch(
        isEditing ? `/expenses/${editingExpenseId}` : '/expenses',
        {
          method: isEditing ? 'PUT' : 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        },
      );

      if (response.status === 401) {
        showBanner(expenseBanner, 'Invalid API key — check the key above and try again.', 'error');
        return;
      }
      if (response.status === 422) {
        applyServerValidationErrors((await response.json()).detail);
        return;
      }
      if (response.status === 404) {
        showBanner(expenseBanner, 'This expense no longer exists — it may have been deleted.', 'error');
        stopEditing();
        onSaved();
        return;
      }
      if (!response.ok) {
        showBanner(expenseBanner, 'Something went wrong saving this expense. Please try again.', 'error');
        return;
      }

      clearFieldErrors();
      showBanner(expenseBanner, isEditing ? 'Expense updated.' : 'Expense added.', 'success');
      stopEditing();
      onSaved();
    } catch (networkError) {
      showBanner(expenseBanner, 'Could not reach the server. Check your connection and try again.', 'error');
    } finally {
      addExpenseBtn.disabled = false;
      addExpenseBtn.textContent = editingExpenseId !== null ? 'Save Changes' : 'Add Expense';
    }
  });

  return { startEditing };
}
