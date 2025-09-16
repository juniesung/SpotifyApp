document.getElementById('sayhi').onclick = async () => {
  const r = await fetch('/health');
  document.getElementById('out').textContent =
    r.ok ? JSON.stringify(await r.json(), null, 2) : 'error';
};
