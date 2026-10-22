const { createInput, createStarRating } = require('../components/Input');

function renderSignupForm() {
  return [
    createInput({ type: 'text', name: 'fullName', label: 'Full name', required: true }),
    createInput({ type: 'email', name: 'email', label: 'Email', required: true }),
    createInput({ type: 'password', name: 'password', label: 'Password', required: true }),
    createStarRating({
      name: 'excitement',
      label: 'How excited are you to join? (optional)',
      max: 5,
      required: false,
    }),
  ].join('\n');
}

module.exports = { renderSignupForm };
