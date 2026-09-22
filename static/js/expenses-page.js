// Wires the Expenses page's independent modules together.
const apiKeyInput = document.getElementById('apiKey');
initApiKeyField(apiKeyInput);

const categoryCombobox = initCategoryCombobox(
  document.getElementById('category'),
  document.getElementById('categoryListbox'),
  { allowCreate: true },
);
const filterCategoryCombobox = initCategoryCombobox(
  document.getElementById('filterCategory'),
  document.getElementById('filterCategoryListbox'),
  { allowCreate: false },
);
const categoryDirectory = createCategoryDirectory([categoryCombobox, filterCategoryCombobox]);

const expenseList = createExpenseList({
  pageSize: 10,
  onEditRequested: (expense) => expenseForm.startEditing(expense),
  onDeleted: () => categoryDirectory.refresh(),
});

const expenseForm = createExpenseForm({
  onSaved: () => {
    expenseList.refresh();
    categoryDirectory.refresh();
  },
});

apiKeyInput.addEventListener('change', () => {
  expenseList.refresh();
  categoryDirectory.refresh();
});

expenseList.refresh();
categoryDirectory.refresh();
