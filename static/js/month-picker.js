// A Month + Year <select> pair that behaves consistently across browsers,
// unlike <input type="month"> (unsupported by desktop Safari/Firefox, which
// silently fall back to a plain text field).
function createMonthPicker(monthSelectEl, yearSelectEl, { yearsBack = 5 } = {}) {
  const MONTH_NAMES = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December',
  ];

  const now = new Date();
  MONTH_NAMES.forEach((name, index) => {
    const option = document.createElement('option');
    option.value = String(index + 1).padStart(2, '0');
    option.textContent = name;
    monthSelectEl.appendChild(option);
  });

  const currentYear = now.getFullYear();
  for (let year = currentYear; year >= currentYear - yearsBack; year--) {
    const option = document.createElement('option');
    option.value = String(year);
    option.textContent = String(year);
    yearSelectEl.appendChild(option);
  }

  monthSelectEl.value = String(now.getMonth() + 1).padStart(2, '0');
  yearSelectEl.value = String(currentYear);

  function getValue() {
    return `${yearSelectEl.value}-${monthSelectEl.value}`;
  }

  function setValue(monthValue) {
    const [year, month] = monthValue.split('-');
    yearSelectEl.value = year;
    monthSelectEl.value = month;
  }

  return { getValue, setValue };
}
