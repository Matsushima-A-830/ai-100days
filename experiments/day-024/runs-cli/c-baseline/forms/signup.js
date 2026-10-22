const { createInput } = require('../components/Input');
const { createStarRating } = require('../components/StarRating');

function renderSignupForm() {
  return [
    createInput({ type: 'text', name: 'fullName', label: 'Full name', required: true }),
    createInput({ type: 'email', name: 'email', label: 'Email', required: true }),
    createInput({ type: 'password', name: 'password', label: 'Password', required: true }),
    createStarRating({ name: 'excitement', label: 'How excited are you to join?' }),
  ].join('\n');
}

module.exports = { renderSignupForm };
