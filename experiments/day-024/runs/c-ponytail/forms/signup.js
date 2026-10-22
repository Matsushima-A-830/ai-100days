const { createInput } = require('../components/Input');

function renderSignupForm() {
  return [
    createInput({ type: 'text', name: 'fullName', label: 'Full name', required: true }),
    createInput({ type: 'email', name: 'email', label: 'Email', required: true }),
    createInput({ type: 'password', name: 'password', label: 'Password', required: true }),
    createInput({ type: 'number', name: 'excitement', label: 'How excited are you to join? (1-5 stars, optional)', min: 1, max: 5 }),
  ].join('\n');
}

module.exports = { renderSignupForm };
