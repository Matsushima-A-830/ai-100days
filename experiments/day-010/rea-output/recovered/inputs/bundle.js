document.getElementById('go').addEventListener('click', async () => {
  const code = document.getElementById('code').value;
  const subtotal = document.getElementById('subtotal').value;
  const price = await window.couponApi.getQuote(code, subtotal);
  document.getElementById('out').textContent = JSON.stringify({ price });
});
