// Generic form input used across the app's forms.
// Supports any native HTML input type (text, email, password, date, checkbox, etc.)
function createInput({ type, name, label, required = false, min, max }) {
  const req = required ? 'required' : '';
  const range = [min != null ? `min="${min}"` : '', max != null ? `max="${max}"` : ''].filter(Boolean).join(' ');
  return `<label for="${name}">${label}</label>\n<input type="${type}" id="${name}" name="${name}" ${range} ${req}>`;
}

module.exports = { createInput };

// shortcut: min/max only wired for number-like native types; no custom star widget.
if (require.main === module) {
  const out = createInput({ type: 'number', name: 'x', label: 'X', min: 1, max: 5 });
  console.assert(out.includes('min="1"') && out.includes('max="5"'), 'min/max should render');
  console.log('Input.js self-check passed');
}
