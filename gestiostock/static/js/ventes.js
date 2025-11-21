

class VentesManager {
    constructor() {
        this.ventes = [];
        this.clients = [];
        this.produits = [];
        this.panier = [];
        this.init();
    }

    async init() {
        console.log('🚀 Initialisation gestion ventes...');
        await this.loadClients();
        await this.loadProduits();
        await this.loadVentes();
        this.bindEvents();
        this.setupDatesParDefaut();
    }

    bindEvents() {
        // Filtres
        ['filter-date-debut', 'filter-date-fin', 'filter-client', 'filter-statut'].forEach(id => {
            document.getElementById(id).addEventListener('change', () => this.loadVentes());
        });

        // Formulaire vente
        document.getElementById('form-vente').addEventListener('submit', (e) => this.saveVente(e));

        // Calculs
        document.getElementById('vente-produit').addEventListener('change', () => this.updatePrixVente());
        document.getElementById('vente-quantite').addEventListener('input', () => this.calculerTotal());
        document.getElementById('vente-remise').addEventListener('input', () => this.calculerTotal());
        document.getElementById('vente-devise').addEventListener('change', () => this.calculerTotal());
    }

    setupDatesParDefaut() {
        const aujourdhui = new Date();
        document.getElementById('filter-date-debut').valueAsDate = aujourdhui;
        document.getElementById('filter-date-fin').valueAsDate = aujourdhui;
    }

    async loadVentes() {
        try {
            this.showLoading(true);

            const params = new URLSearchParams();
            const dateDebut = document.getElementById('filter-date-debut').value;
            const dateFin = document.getElementById('filter-date-fin').value;
            const clientId = document.getElementById('filter-client').value;
            const statut = document.getElementById('filter-statut').value;

            if(dateDebut) params.append('date_debut', dateDebut);
            if(dateFin) params.append('date_fin', dateFin);
            if(clientId) params.append('client_id', clientId);
            if(statut) params.append('statut', statut);

            const response = await fetch(`/api/ventes?${params.toString()}`);
            if(!response.ok) throw new Error(`Erreur HTTP: ${response.status}`);

            this.ventes = await response.json();
            this.afficherVentes(this.ventes);
            this.calculerStats(this.ventes);
        } catch (error) {
            console.error('❌ Erreur chargement ventes:', error);
            this.showError('Impossible de charger les ventes: ' + error.message);
        } finally {
            this.showLoading(false);
        }
    }

    afficherVentes(ventes) {
        const tbody = document.querySelector('#ventes-table tbody');
        if(!ventes || ventes.length === 0) {
            tbody.innerHTML = `<tr><td colspan="9" style="text-align:center; padding:40px; color:#7f8c8d;">📭 Aucune vente trouvée</td></tr>`;
            return;
        }

        tbody.innerHTML = ventes.map(vente => `
            <tr>
                <td>
                    <div style="font-weight:600; color:#2c3e50;">${vente.numero_facture}</div>
                    ${vente.notes ? `<div style="font-size:11px; color:#7f8c8d;">${vente.notes.substring(0,30)}${vente.notes.length>30?'...':''}</div>` : ''}
                </td>
                <td>
                    <div style="font-weight:500;">${this.formatDate(vente.date_vente)}</div>
                    <div style="font-size:11px; color:#7f8c8d;">${this.formatHeure(vente.date_vente)}</div>
                </td>
                <td>${vente.client||'<span style="color:#7f8c8d;">Client anonyme</span>'}</td>
                <td>
                    <div style="font-weight:500;">${vente.produit}</div>
                    <div style="font-size:11px; color:#7f8c8d;">${this.formatCurrency(vente.prix_unitaire, vente.devise)}/unité</div>
                </td>
                <td style="text-align:center;">
                    <span style="font-weight:600; background:#e8f8f5; padding:4px 8px; border-radius:4px;">${vente.quantite}</span>
                </td>
                <td style="text-align:right; font-weight:600;">
                    ${this.formatCurrency(vente.montant_total, vente.devise)}
                    ${vente.remise>0?`<div style="font-size:11px; color:#e74c3c;">Remise: ${vente.remise}%</div>`:''}
                </td>
                <td><span class="badge badge-info">${this.getPaiementIcon(vente.mode_paiement)} ${vente.mode_paiement}</span></td>
                <td>${this.getStatutBadge(vente.statut)}</td>
                <td>
                    <div style="display:flex; gap:5px;">
                        <button class="btn btn-secondary btn-sm" onclick="ventesManager.telechargerFacture(${vente.id})" title="Facture PDF">📄</button>
                        <button class="btn btn-primary btn-sm" onclick="ventesManager.voirDetails(${vente.id})" title="Détails">👁️</button>
                        ${vente.statut==='confirmée'?`<button class="btn btn-danger btn-sm" onclick="ventesManager.annulerVente(${vente.id})" title="Annuler">❌</button>`:''}
                    </div>
                </td>
            </tr>
        `).join('');
    }

    getPaiementIcon(mode) {
        return {'espèces':'💰','carte':'💳','mobile':'📱','virement':'🏦'}[mode]||'💸';
    }

    getStatutBadge(statut) {
        const badges = {
            'confirmée':'<span class="badge badge-success">✅ Confirmée</span>',
            'annulée':'<span class="badge badge-danger">❌ Annulée</span>',
            'brouillon':'<span class="badge badge-warning">📝 Brouillon</span>'
        };
        return badges[statut]||'<span class="badge badge-secondary">❓ Inconnu</span>';
    }

    calculerStats(ventes) {
        const aujourdhui = new Date().toISOString().split('T')[0];
        const ventesJour = ventes.filter(v => v.date_vente.startsWith(aujourdhui) && v.statut==='confirmée');

        const caJour = ventesJour.reduce((sum,v)=>sum+v.montant_total,0);
        const nbVentes = ventesJour.length;
        const articlesVendus = ventesJour.reduce((sum,v)=>sum+v.quantite,0);

        document.getElementById('ca-jour').textContent = this.formatCurrency(caJour);
        document.getElementById('nb-ventes-jour').textContent = nbVentes;
        document.getElementById('articles-vendus').textContent = articlesVendus;
    }

    async loadClients() {
        try {
            const response = await fetch('/api/clients');
            this.clients = await response.json();

            ['filter-client','vente-client'].forEach(selectId=>{
                const select=document.getElementById(selectId);
                const defaultOption = selectId==='filter-client'?'<option value="">Tous les clients</option>':'<option value="">Client anonyme</option>';
                select.innerHTML = defaultOption + this.clients.map(c=>`<option value="${c.id}">${c.nom} ${c.prenom||''}${c.telephone?` - ${c.telephone}`:''}</option>`).join('');
            });
        } catch(err){ console.error(err); }
    }

    async loadProduits() {
        try {
            const response = await fetch('/api/produits');
            this.produits = await response.json();

            const select = document.getElementById('vente-produit');
            const produitsEnStock = this.produits.filter(p=>p.stock_actuel>0);
            select.innerHTML = '<option value="">Sélectionner un produit</option>' +
                produitsEnStock.map(p=>`<option value="${p.id}" data-prix="${p.prix_vente}" data-stock="${p.stock_actuel}">${p.nom} - ${this.formatCurrency(p.prix_vente)} - Stock: ${p.stock_actuel}</option>`).join('');
        } catch(err){ console.error(err); }
    }

    updatePrixVente() {
        const select = document.getElementById('vente-produit');
        const option = select.options[select.selectedIndex];
        const prix = parseFloat(option?.getAttribute('data-prix')) || 0;
        const stock = parseInt(option?.getAttribute('data-stock')) || 0;

        const inputQuantite = document.getElementById('vente-quantite');
        const totalElement = document.getElementById('vente-total');
        const stockIndicator = document.getElementById('stock-indicator');

        document.getElementById('vente-prix').value = prix;
        inputQuantite.max = stock;

        if(stock===0){
            inputQuantite.disabled=true;
            totalElement.textContent='Rupture de stock';
            totalElement.style.color='#e74c3c';
            stockIndicator.style.display='none';
        } else {
            inputQuantite.disabled=false;
            totalElement.style.color='#1abc9c';
        }

        if(parseInt(inputQuantite.value)>stock){
            inputQuantite.value = stock;
        }

        this.calculerTotal();
    }

    calculerTotal() {
        const quantite = parseFloat(document.getElementById('vente-quantite').value) || 0;
        const prix = parseFloat(document.getElementById('vente-prix').value) || 0;
        const remise = parseFloat(document.getElementById('vente-remise').value) || 0;
        const devise = document.getElementById('vente-devise').value;
        const totalElement = document.getElementById('vente-total');
        const stockIndicator = document.getElementById('stock-indicator');

        const sousTotal = quantite * prix;
        const montantRemise = sousTotal * (remise/100);
        const total = sousTotal - montantRemise;

        totalElement.textContent = sousTotal===0?'0 '+devise:this.formatCurrency(total,devise);

        const maxQty = parseInt(document.getElementById('vente-quantite').max)||0;
        if(quantite>maxQty){
            totalElement.style.color='#e74c3c';
            stockIndicator.style.display='block';
        } else {
            totalElement.style.color='#1abc9c';
            stockIndicator.style.display='none';
        }
    }

    async saveVente(event){
        event.preventDefault();
        const form = event.target;
        const formData = new FormData(form);
        const data = Object.fromEntries(formData);

        if(!data.produit_id){ this.showError('Veuillez sélectionner un produit'); return; }
        if(!data.quantite || data.quantite<=0){ this.showError('Veuillez saisir une quantité valide'); return; }

        const option = document.getElementById('vente-produit').options[document.getElementById('vente-produit').selectedIndex];
        const stockDisponible = parseInt(option.getAttribute('data-stock'));
        if(parseInt(data.quantite) > stockDisponible){
            this.showError(`Stock insuffisant! Disponible: ${stockDisponible}`);
            return;
        }

        ['quantite','prix_unitaire','remise'].forEach(k=>{ if(data[k]) data[k]=parseFloat(data[k]); });
        ['produit_id','client_id'].forEach(k=>{ if(data[k]) data[k]=parseInt(data[k])||null; });

        data.statut='confirmée';
        data.statut_paiement='payé';

        try{
            this.showLoading(true);
            const response = await fetch('/api/ventes',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
            const result = await response.json();
            if(response.ok){
                this.closeSaleModal();
                form.reset();
                document.getElementById('vente-total').textContent='0 F CFA';
                await this.loadVentes();
                await this.loadProduits();
                this.showSuccess('✅ Vente enregistrée avec succès!');
            } else throw new Error(result.error||result.message||'Erreur inconnue');
        } catch(error){
            console.error('❌ Erreur sauvegarde vente:', error);
            this.showError('Erreur: '+error.message);
        } finally{ this.showLoading(false); }

        if (response.ok) {
    this.toggleModal('modal-vente');
    form.reset();
    document.getElementById('vente-total').textContent = '0 F CFA';

    // ✅ Vider le panier après vente
    this.panier = [];
    this.afficherPanier();

    await this.loadVentes();
    await this.loadProduits(); // Recharger les stocks
    this.showSuccess('✅ Vente enregistrée avec succès!');
} 

    }

    async annulerVente(id){
        const vente = this.ventes.find(v=>v.id===id);
        if(!vente) return;
        if(!confirm(`Voulez-vous vraiment annuler la vente ${vente.numero_facture} ?`)) return;

        try{
            const response = await fetch(`/api/ventes/${id}/annuler`,{method:'PUT'});
            if(response.ok){
                await this.loadVentes();
                await this.loadProduits();
                this.showSuccess('✅ Vente annulée avec succès');
            } else {
                const error = await response.json();
                throw new Error(error.error||error.message);
            }
        } catch(error){
            console.error('❌ Erreur annulation:', error);
            this.showError('Erreur lors de l\'annulation: '+error.message);
        }
    }

    async telechargerFacture(id){ window.open(`/api/export/facture/${id}`,'_blank'); }

    voirDetails(id){
        const vente = this.ventes.find(v=>v.id===id);
        if(!vente) return;
        alert(`
📄 FACTURE: ${vente.numero_facture}
📅 DATE: ${this.formatDate(vente.date_vente)} ${this.formatHeure(vente.date_vente)}
👤 CLIENT: ${vente.client||'Client anonyme'}
📦 PRODUIT: ${vente.produit}
🔢 QUANTITÉ: ${vente.quantite}
💰 PRIX UNITAIRE: ${this.formatCurrency(vente.prix_unitaire,vente.devise)}
🎫 REMISE: ${vente.remise}%
💳 MODE PAIEMENT: ${vente.mode_paiement}
🏷️ STATUT: ${vente.statut}
${vente.notes?`📝 NOTES: ${vente.notes}`:''}
💵 TOTAL: ${this.formatCurrency(vente.montant_total,vente.devise)}
        `.trim());
    }

    async exporterVentes(){
        const params = new URLSearchParams();
        const dateDebut = document.getElementById('filter-date-debut').value;
        const dateFin = document.getElementById('filter-date-fin').value;
        if(dateDebut) params.append('date_debut',dateDebut);
        if(dateFin) params.append('date_fin',dateFin);
        window.location.href=`/api/export/ventes/excel?${params.toString()}`;
    }


    // Ajouter dans la classe VentesManager
ajouterAuPanier() {
    const produitSelect = document.getElementById('vente-produit');
    const option = produitSelect.options[produitSelect.selectedIndex];
    const produitId = parseInt(option.value);
    const produitNom = option.text.split(' - ')[0];
    const prixUnitaire = parseFloat(option.getAttribute('data-prix')) || 0;
    const stockDisponible = parseInt(option.getAttribute('data-stock')) || 0;

    const quantite = parseInt(document.getElementById('vente-quantite').value) || 0;
    const remise = parseFloat(document.getElementById('vente-remise').value) || 0;

    // Vérification stock
    if (quantite <= 0 || quantite > stockDisponible) {
        this.showWarning(`Quantité invalide ou stock insuffisant (max: ${stockDisponible})`);
        return;
    }

    // Vérifier si le produit est déjà dans le panier
    const index = this.panier.findIndex(item => item.produitId === produitId);
    if (index !== -1) {
        // Mise à jour de la quantité et remise
        this.panier[index].quantite += quantite;
        this.panier[index].remise = remise;
    } else {
        // Ajout au panier
        this.panier.push({
            produitId,
            produitNom,
            quantite,
            prixUnitaire,
            remise
        });
    }

    this.afficherPanier();
}

// Méthode pour afficher le panier dans le tableau
afficherPanier() {
    const tbody = document.querySelector('#panier-table tbody');
    if (!this.panier.length) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; color:#7f8c8d;">Le panier est vide</td></tr>`;
        document.getElementById('vente-total').textContent = '0 F CFA';
        return;
    }

    let totalGeneral = 0;
    tbody.innerHTML = this.panier.map((item, index) => {
        const total = item.quantite * item.prixUnitaire * (1 - item.remise / 100);
        totalGeneral += total;
        return `
        <tr>
            <td>${item.produitNom}</td>
            <td style="text-align:center;">${item.quantite}</td>
            <td style="text-align:right;">${this.formatCurrency(item.prixUnitaire)}</td>
            <td style="text-align:center;">${item.remise}%</td>
            <td style="text-align:right; font-weight:bold;">${this.formatCurrency(total)}</td>
            <td style="text-align:center;">
                <button class="btn btn-danger btn-sm" onclick="ventesManager.supprimerDuPanier(${index})">❌</button>
            </td>
        </tr>
        `;
    }).join('');

    document.getElementById('vente-total').textContent = this.formatCurrency(totalGeneral);
}

// Méthode pour supprimer un produit du panier
supprimerDuPanier(index) {
    this.panier.splice(index, 1);
    this.afficherPanier();
}





    closeSaleModal(){ this.toggleModal('modal-vente'); }

    // Utilitaires
    formatCurrency(amount,currency='F CFA'){ return new Intl.NumberFormat('fr-FR').format(amount||0)+' '+currency; }
    formatDate(date){ return new Date(date).toLocaleDateString('fr-FR'); }
    formatHeure(date){ return new Date(date).toLocaleTimeString('fr-FR',{hour:'2-digit',minute:'2-digit'}); }
    toggleModal(id){ const m=document.getElementById(id); m.style.display=m.style.display==='block'?'none':'block'; }
    showLoading(show){ document.body.style.cursor=show?'wait':'default'; }
    showError(msg){ alert('❌ '+msg); }
    showSuccess(msg){ alert('✅ '+msg); }
    showWarning(msg){ alert('⚠️ '+msg); }
}

// Fonctions globales
function toggleModal(id){ ventesManager?.toggleModal(id); }
function exporterVentes(){ ventesManager?.exporterVentes(); }
function updateSalePrice(){ ventesManager?.updatePrixVente(); }
function calculateTotal(){ ventesManager?.calculerTotal(); }
function closeSaleModal(){ ventesManager?.closeSaleModal(); }


// Initialisation globale
let ventesManager;

document.addEventListener('DOMContentLoaded', function() {
    ventesManager = new VentesManager();
});

// Fonctions globales pour les onclick
function toggleModal(modalId) {
    if (ventesManager) {
        ventesManager.toggleModal(modalId);
    }
}

function exporterVentes() {
    if (ventesManager) {
        ventesManager.exporterVentes();
    }
}

// ⭐ AJOUT : Fonctions globales pour les anciens appels
function updateSalePrice() {
    if (ventesManager) {
        ventesManager.updatePrixVente();
    }
}

function calculateTotal() {
    if (ventesManager) {
        ventesManager.calculerTotal();
    }
}

function closeSaleModal() {
    if (ventesManager) {
        ventesManager.closeSaleModal();
    }
}