const { createInput } = require('../components/Input');

function renderSignupForm() {
  return [
    createInput({ type: 'text', name: 'fullName', label: 'Full name', required: true }),
    createInput({ type: 'email', name: 'email', label: 'Email', required: true }),
    createInput({ type: 'password', name: 'password', label: 'Password', required: true }),
    '<label for="excitement">How excited are you to join? (optional)</label>\n<select id="excitement" name="excitement">\n  <option value="">N/A</option>\n  <option value="1">★</option>\n  <option value="2">★★</option>\n  <option value="3">★★★</option>\n  <option value="4">★★★★</option>\n  <option value="5">★★★★★</option>\n</select>',
  ].join('\n');
}

module.exports = { renderSignupForm };
