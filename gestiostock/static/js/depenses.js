// Enhanced depenses UI: AJAX submit, live table update and solde refresh
(function(){
  function qs(sel){ return document.querySelector(sel); }
  function qsa(sel){ return Array.from(document.querySelectorAll(sel)); }

  const btnNew = qs('#btn-new-depense');
  const formContainer = qs('#depense-form-container');
  const form = qs('#depense-form');
  const btnCancel = qs('#btn-cancel');
  const tbody = qs('#depenses-tbody');
  const soldeEl = qs('#solde-caisse');
  const alerts = qs('#alerts');

  function showAlert(message, type='info'){
    const div = document.createElement('div');
    div.className = `alert alert-${type}`;
    div.textContent = message;
    alerts.prepend(div);
    setTimeout(()=> div.remove(), 5000);
  }

  btnNew && btnNew.addEventListener('click', function(){
    formContainer.style.display = '';
    form.querySelector('[name=libelle]').focus();
  });
  btnCancel && btnCancel.addEventListener('click', function(){
    formContainer.style.display = 'none';
    form.reset();
  });

  function formatCurrency(v){
    try{ return Number(v).toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2}) + ' F'; }
    catch(e){ return v + ' F'; }
  }

  function appendRow(dep){
    const tr = document.createElement('tr');
    tr.dataset.id = dep.id;
    tr.innerHTML = `<td>${dep.libelle}</td><td>${formatCurrency(dep.montant)}</td><td>${dep.description||''}</td><td>${(new Date(dep.date)).toLocaleString()}</td>`;
    if(tbody.firstChild) tbody.insertBefore(tr, tbody.firstChild);
    else tbody.appendChild(tr);
  }

  form && form.addEventListener('submit', function(ev){
    ev.preventDefault();
    const fd = new FormData(form);
    const payload = {};
    fd.forEach((v,k)=> payload[k]=v);

    fetch('/depenses/add', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
      },
      body: JSON.stringify(payload)
    }).then(r=> {
      if(!r.ok){
        return r.text().then(text=> {
          console.error('Server response:', r.status, text);
          throw new Error(`HTTP ${r.status}: ${text.substring(0,200)}`);
        });
      }
      return r.json();
    }).then(body=>{
      // success
      appendRow(body.depense);
      soldeEl.textContent = (Number(body.nouveau_solde) || 0).toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2}) + ' F';
      showAlert('Dépense enregistrée', 'success');
      form.reset();
      formContainer.style.display = 'none';
    }).catch(err=>{
      console.error('Fetch error:', err);
      showAlert('Erreur: ' + err.message, 'danger');
    });
  });

})();
