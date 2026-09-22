// A text input + listbox that lets the user pick an existing category or type a new one.
// Uses the ARIA 1.2 "combobox with managed focus" pattern: the input keeps DOM focus
// throughout, and `aria-activedescendant` tracks the highlighted option.
function initCategoryCombobox(inputEl, listEl, { allowCreate = true } = {}) {
  let categories = [];
  let activeIndex = -1;
  let optionId = 0;

  function currentOptions() {
    return Array.from(listEl.querySelectorAll('.combobox-option'));
  }

  function render() {
    const raw = inputEl.value;
    const query = raw.trim().toLowerCase();
    const matches = categories.filter((c) => c.includes(query));
    const exactMatch = categories.includes(query);
    const showCreate = allowCreate && query !== '' && !exactMatch;

    listEl.innerHTML = '';
    matches.forEach((category) => {
      const li = document.createElement('li');
      li.id = `combobox-opt-${optionId++}`;
      li.textContent = category;
      li.setAttribute('role', 'option');
      li.dataset.value = category;
      li.className = 'combobox-option';
      listEl.appendChild(li);
    });
    if (showCreate) {
      const li = document.createElement('li');
      li.id = `combobox-opt-${optionId++}`;
      li.textContent = `Create "${raw.trim()}"`;
      li.setAttribute('role', 'option');
      li.dataset.value = raw.trim();
      li.className = 'combobox-option combobox-option-create';
      listEl.appendChild(li);
    }

    activeIndex = -1;
    inputEl.removeAttribute('aria-activedescendant');
    const hasOptions = listEl.children.length > 0;
    listEl.classList.toggle('hidden', !hasOptions);
    inputEl.setAttribute('aria-expanded', hasOptions ? 'true' : 'false');
  }

  function close() {
    listEl.classList.add('hidden');
    inputEl.setAttribute('aria-expanded', 'false');
    inputEl.removeAttribute('aria-activedescendant');
    activeIndex = -1;
  }

  function selectOption(li) {
    inputEl.value = li.dataset.value;
    close();
    inputEl.dispatchEvent(new Event('change'));
    inputEl.focus();
  }

  function highlight(options) {
    options.forEach((o, i) => o.classList.toggle('active', i === activeIndex));
    if (options[activeIndex]) {
      options[activeIndex].scrollIntoView({ block: 'nearest' });
      inputEl.setAttribute('aria-activedescendant', options[activeIndex].id);
    }
  }

  listEl.addEventListener('mousedown', (event) => {
    const li = event.target.closest('.combobox-option');
    if (li) {
      event.preventDefault();
      selectOption(li);
    }
  });

  // Close as soon as the user starts interacting elsewhere. This must happen on
  // `mousedown` (not a delayed `blur`): the list is `position: absolute` and can
  // visually cover whatever sits below it (a date field, a table row, a submit
  // button); if it's still open when the browser resolves the *next* click's
  // target, that click lands on the list instead of the real target underneath.
  // Closing synchronously on the outside `mousedown` — which always fires before
  // the paired `click` — removes the list from the layout in time for the click's
  // own hit-test to land correctly.
  document.addEventListener('mousedown', (event) => {
    if (!inputEl.contains(event.target) && !listEl.contains(event.target)) {
      close();
    }
  });
  inputEl.addEventListener('blur', close);

  inputEl.addEventListener('input', render);
  inputEl.addEventListener('focus', render);

  inputEl.addEventListener('keydown', (event) => {
    if (listEl.classList.contains('hidden') && event.key !== 'Escape') {
      if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
        event.preventDefault();
        render();
      }
      return;
    }
    const options = currentOptions();
    if (event.key === 'ArrowDown') {
      event.preventDefault();
      activeIndex = Math.min(activeIndex + 1, options.length - 1);
      highlight(options);
    } else if (event.key === 'ArrowUp') {
      event.preventDefault();
      activeIndex = Math.max(activeIndex - 1, 0);
      highlight(options);
    } else if (event.key === 'Enter') {
      if (activeIndex >= 0 && options[activeIndex]) {
        event.preventDefault();
        selectOption(options[activeIndex]);
      } else {
        close();
      }
    } else if (event.key === 'Escape') {
      close();
    }
  });

  return {
    setCategories(newCategories) {
      categories = newCategories;
    },
  };
}
