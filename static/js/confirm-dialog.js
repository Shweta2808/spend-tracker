// A styled, focusable replacement for window.confirm().
function confirmDialog(message) {
  return new Promise((resolve) => {
    const overlay = document.createElement('div');
    overlay.className = 'dialog-overlay';
    overlay.innerHTML = `
      <div class="dialog-box" role="alertdialog" aria-modal="true" aria-labelledby="dialogMessage">
        <p id="dialogMessage">${escapeHtml(message)}</p>
        <div class="actions">
          <button type="button" class="danger" data-confirm>Delete</button>
          <button type="button" class="secondary" data-cancel>Cancel</button>
        </div>
      </div>`;
    document.body.appendChild(overlay);

    const cleanup = (result) => {
      overlay.remove();
      resolve(result);
    };
    overlay.querySelector('[data-confirm]').addEventListener('click', () => cleanup(true));
    overlay.querySelector('[data-cancel]').addEventListener('click', () => cleanup(false));
    overlay.addEventListener('click', (event) => {
      if (event.target === overlay) cleanup(false);
    });
    overlay.querySelector('[data-confirm]').focus();
  });
}
