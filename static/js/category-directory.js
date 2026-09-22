// Keeps one or more category comboboxes in sync with the server's distinct-category list.
function createCategoryDirectory(comboboxes) {
  async function refresh() {
    try {
      const response = await apiFetch('/expenses/categories');
      if (!response.ok) return;
      const categories = await response.json();
      comboboxes.forEach((combobox) => combobox.setCategories(categories));
    } catch (networkError) {
      // Autocomplete is a nicety; silently skip if it can't be loaded.
    }
  }

  return { refresh };
}
