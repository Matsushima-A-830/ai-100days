// Generic form input used across the app's forms.
// Supports any native HTML input type (text, email, password, date, checkbox, etc.)
function createInput({ type, name, label, required = false }) {
  const req = required ? 'required' : '';
  return `<label for="${name}">${label}</label>\n<input type="${type}" id="${name}" name="${name}" ${req}>`;
}

// Star rating field (1-5 stars), built from a group of radio inputs so it
// works without any client-side JS. Rendered as a <fieldset> with one radio
// per star value; CSS (not included here) can restyle the radios as stars,
// e.g. by hiding the inputs and styling the sibling <label>s.
function createStarRating({ name, label, max = 5, required = false }) {
  const req = required ? 'required' : '';
  const stars = [];
  for (let value = max; value >= 1; value -= 1) {
    const id = `${name}-${value}`;
    stars.push(
      `<input type="radio" id="${id}" name="${name}" value="${value}" ${req}>\n` +
        `<label for="${id}" title="${value} star${value === 1 ? '' : 's'}">★</label>`
    );
  }
  return (
    `<fieldset class="star-rating" data-name="${name}">\n` +
    `<legend>${label}</legend>\n` +
    `${stars.join('\n')}\n` +
    `</fieldset>`
  );
}

module.exports = { createInput, createStarRating };
