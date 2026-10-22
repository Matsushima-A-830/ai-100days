const { createInput } = require('../components/Input');

function renderSignupForm() {
  return [
    createInput({ type: 'text', name: 'fullName', label: 'Full name', required: true }),
    createInput({ type: 'email', name: 'email', label: 'Email', required: true }),
    createInput({ type: 'password', name: 'password', label: 'Password', required: true }),
    createInput({ type: 'checkbox', name: 'rememberMe', label: 'Remember me' }),
  ].join('\n');
}

module.exports = { renderSignupForm };
