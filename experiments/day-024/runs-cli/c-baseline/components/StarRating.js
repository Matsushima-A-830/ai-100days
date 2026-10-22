// Star-rating input rendered as a group of radio buttons (1-5 stars).
function createStarRating({ name, label, required = false, max = 5 }) {
  const req = required ? 'required' : '';
  const stars = [];
  for (let value = max; value >= 1; value--) {
    stars.push(
      `<input type="radio" id="${name}-${value}" name="${name}" value="${value}" ${req}><label for="${name}-${value}">${value}</label>`
    );
  }
  return `<fieldset class="star-rating">\n<legend>${label}</legend>\n${stars.join('\n')}\n</fieldset>`;
}

module.exports = { createStarRating };
