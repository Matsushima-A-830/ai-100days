// Generic form input used across the app's forms.
// Supports any native HTML input type (text, email, password, date, checkbox, etc.)
function createInput({ type, name, label, required = false }) {
  const req = required ? 'required' : '';
  return `<label for="${name}">${label}</label>\n<input type="${type}" id="${name}" name="${name}" ${req}>`;
}

module.exports = { createInput };
