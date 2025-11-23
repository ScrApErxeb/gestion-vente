// static/js/commandes.js
class CommandesManager {
    constructor() {
        this.commandes = [];
        this.fournisseurs = [];
        this.produits = [];
        this.init();
    }

    async init() {
        console.log('🚀 Initialisation gestion commandes...');
        await this.loadFournisseurs();
        await this.loadProduits();
        await this.loadCommandes();
        this.bindEvents();
        this.setupDates();
    }

    bindEvents() {
        // Filtres (submit/change via delegation)
        document.getElementById('filter-fournisseur')?.addEventListener('change', () => this.loadCommandes());
        document.getElementById('filter-statut-cmd')?.addEventListener('change', () => this.loadCommandes());

        // Formulaire commande (submit)
        const form = document.getElementById('form-commande');
        if (form) {
            form.addEventListener('submit', (e) => this.saveCommande(e));
        }

        // Delegation pour click sur boutons dynamiques (recevoir, details, annuler, ajouter-item, retirer-item, toggle-modal)
        document.addEventListener('click', (e) => {
            const btn = e.target.closest('button[data-action], [data-action]');
            if (!btn) return;

            const action = btn.getAttribute('data-action');
            const id = btn.getAttribute('data-id');

            switch (action) {
                case 'recevoir':
                    if (id) this.recevoirCommande(parseInt(id));
                    break;
                case 'details':
                    if (id) this.voirDetails(parseInt(id));
                    break;
                case 'annuler':
                    if (id) this.annulerCommande(parseInt(id));
                    break;
                case 'ajouter-item':
                    this.ajouterItem();
                    break;
                case 'retirer-item':
                    // retirer-item doit avoir un data-id ou target is the remove button inside .cmd-item
                    this.retirerItem(btn);
                    break;
                case 'toggle-modal':
                    const modalId = btn.getAttribute('data-target');
                    if (modalId) this.toggleModal(modalId);
                    break;
                default:
                    break;
            }
        });

        // Delegation pour changement de produit (pour mise à jour du prix via data-prix)
        document.addEventListener('change', (e) => {
            const select = e.target.closest('.item-produit');
            if (select) {
                this.updatePrixProduit(select);
            }
        });

        // Delegation pour inputs quantité/prix -> recalcul total
        document.addEventListener('input', (e) => {
            if (e.target.matches('.item-quantite, .item-prix')) {
                this.calculerTotalCommande();
            }
        });
    }

    setupDates() {
        // Date de livraison par défaut (7 jours)
        const dateLivraison = new Date();
        dateLivraison.setDate(dateLivraison.getDate() + 7);
        const el = document.getElementById('cmd-date-livraison');
        if (el) el.valueAsDate = dateLivraison;
    }

    async loadCommandes() {
        try {
            this.showLoading(true);

            const fournisseurId = document.getElementById('filter-fournisseur')?.value;
            const statut = document.getElementById('filter-statut-cmd')?.value;

            let url = '/api/commandes?';
            if (fournisseurId) url += `fournisseur_id=${encodeURIComponent(fournisseurId)}&`;
            if (statut) url += `statut=${encodeURIComponent(statut)}&`;

            const response = await fetch(url);

            if (!response.ok) {
                throw new Error(`Erreur HTTP: ${response.status}`);
            }

            this.commandes = await response.json();
            this.afficherCommandes(this.commandes);
            this.calculerStats(this.commandes);

        } catch (error) {
            console.error('❌ Erreur chargement commandes:', error);
            this.showError('Impossible de charger les commandes: ' + (error.message || error));
        } finally {
            this.showLoading(false);
        }
    }

    afficherCommandes(commandes) {
        const tbody = document.querySelector('#commandes-table tbody');

        if (!tbody) return;

        if (!commandes || commandes.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="8" style="text-align: center; padding: 40px; color: #7f8c8d;">
                        📭 Aucune commande trouvée
                    </td>
                </tr>
            `;
            console.log('ℹ️ 0 commandes affichées');
            return;
        }

        const statutConfig = {
            'en_attente': { badge: 'warning', icon: '⏳', text: 'EN ATTENTE' },
            'confirmée': { badge: 'info', icon: '✅', text: 'CONFIRMÉE' },
            'reçue': { badge: 'success', icon: '📦', text: 'REÇUE' },
            'annulée': { badge: 'danger', icon: '❌', text: 'ANNULÉE' },
            'partiellement_reçue': { badge: 'warning', icon: '📥', text: 'PARTIELLE' }
        };

        tbody.innerHTML = commandes.map(c => {
            const statut = statutConfig[c.statut] || statutConfig['en_attente'];

            // Buttons now use data-action and data-id; handled by delegation
            return `
                <tr>
                    <td>
                        <div style="font-weight: 600; color: #2c3e50;">${c.numero_commande}</div>
                        ${c.notes ? `<div style="font-size: 11px; color: #7f8c8d;">${c.notes.substring(0, 30)}${c.notes.length > 30 ? '...' : ''}</div>` : ''}
                    </td>
                    <td>
                        <div style="font-weight: 500;">${c.fournisseur}</div>
                        <div style="font-size: 11px; color: #7f8c8d;">${c.mode_paiement || 'Non spécifié'}</div>
                    </td>
                    <td>
                        <div style="font-weight: 500;">${this.formatDate(c.date_commande)}</div>
                        <div style="font-size: 11px; color: #7f8c8d;">${this.formatHeure(c.date_commande)}</div>
                    </td>
                    <td>
                        ${c.date_livraison_prevue ? `
                            <div style="font-weight: 500;">${this.formatDate(c.date_livraison_prevue)}</div>
                            <div style="font-size: 11px; color: ${this.isRetard(c.date_livraison_prevue) ? '#e74c3c' : '#7f8c8d'};">
                                ${this.isRetard(c.date_livraison_prevue) ? '⚠️ En retard' : 'Dans les temps'}
                            </div>
                        ` : '<span style="color: #7f8c8d;">-</span>'}
                    </td>
                    <td style="text-align: right; font-weight: 600;">
                        ${this.formatCurrency(c.montant_total, c.devise)}
                    </td>
                    <td style="text-align: center;">
                        <span style="font-weight: 600; background: #e8f8f5; padding: 4px 8px; border-radius: 4px;">${c.nb_items}</span>
                    </td>
                    <td>
                        <span class="badge badge-${statut.badge}">
                            ${statut.icon} ${statut.text}
                        </span>
                    </td>
                    <td>
                        <div style="display: flex; gap: 5px;">
                            ${c.statut !== 'reçue' && c.statut !== 'annulée' ? `
                                <button type="button" class="btn btn-success btn-sm" data-action="recevoir" data-id="${c.id}" title="Réceptionner">
                                    📦
                                </button>
                            ` : ''}
                            <button type="button" class="btn btn-primary btn-sm" data-action="details" data-id="${c.id}" title="Détails">
                                👁️
                            </button>
                            ${c.statut === 'en_attente' ? `
                                <button type="button" class="btn btn-danger btn-sm" data-action="annuler" data-id="${c.id}" title="Annuler">
                                    ❌
                                </button>
                            ` : ''}
                        </div>
                    </td>
                </tr>
            `;
        }).join('');

        console.log(`✅ ${commandes.length} commandes affichées`);
    }

    isRetard(dateLivraison) {
        if (!dateLivraison) return false;
        const datePrevue = new Date(dateLivraison);
        const aujourdhui = new Date();
        // compare only date (ignore time) for "retard" logic
        datePrevue.setHours(0,0,0,0);
        aujourdhui.setHours(0,0,0,0);
        return datePrevue < aujourdhui;
    }

    calculerStats(commandes) {
        // Utilise les mêmes valeurs de statut que celles renvoyées par l'API (considérées ci-dessus)
        const stats = {
            en_attente: commandes.filter(c => c.statut === 'en_attente').length,
            confirmees: commandes.filter(c => c.statut === 'confirmée').length,
            recues: commandes.filter(c => c.statut === 'reçue').length,
            montant: commandes.filter(c => c.statut !== 'annulée').reduce((sum, c) => sum + (parseFloat(c.montant_total) || 0), 0)
        };

        // Mise à jour du DOM (IDs attendus : cmd-attente, cmd-confirmees, cmd-recues, cmd-montant)
        const elAttente = document.getElementById('cmd-attente');
        const elConfirmees = document.getElementById('cmd-confirmees');
        const elRecues = document.getElementById('cmd-recues');
        const elMontant = document.getElementById('cmd-montant');

        if (elAttente) elAttente.textContent = stats.en_attente;
        if (elConfirmees) elConfirmees.textContent = stats.confirmees;
        if (elRecues) elRecues.textContent = stats.recues;
        if (elMontant) elMontant.textContent = this.formatCurrency(stats.montant);
    }

    async loadFournisseurs() {
        try {
            const response = await fetch('/api/fournisseurs?actif=true');
            if (!response.ok) throw new Error(`Erreur HTTP: ${response.status}`);
            this.fournisseurs = await response.json();

            const selects = ['filter-fournisseur', 'cmd-fournisseur'];
            selects.forEach(selectId => {
                const select = document.getElementById(selectId);
                if (!select) return;
                const defaultOption = selectId === 'filter-fournisseur' ?
                    '<option value="">Tous les fournisseurs</option>' :
                    '<option value="">Sélectionner...</option>';
                select.innerHTML = defaultOption +
                    this.fournisseurs.map(f => `<option value="${f.id}">${f.nom}</option>`).join('');
            });

            console.log(`✅ ${this.fournisseurs.length} fournisseurs chargés`);
        } catch (error) {
            console.error('❌ Erreur chargement fournisseurs:', error);
            this.showError('Impossible de charger les fournisseurs');
        }
    }

    async loadProduits() {
        try {
            const response = await fetch('/produits');
            if (!response.ok) throw new Error(`Erreur HTTP: ${response.status}`);
            this.produits = await response.json();
            this.updateProduitsSelects();
            console.log(`✅ ${this.produits.length} produits chargés`);
        } catch (error) {
            console.error('❌ Erreur chargement produits:', error);
            this.showError('Impossible de charger les produits');
        }
    }

    buildProduitOptions() {
        return '<option value="">Sélectionner un produit...</option>' +
            this.produits.map(p =>
                `<option value="${p.id}" data-prix="${p.prix_achat}">
                    ${this.escapeHtml(p.nom)} - ${this.formatCurrency(p.prix_achat)} - Stock: ${p.stock_actuel}
                </option>`
            ).join('');
    }

    updateProduitsSelects() {
        const selects = document.querySelectorAll('.item-produit');
        const options = this.buildProduitOptions();

        selects.forEach(select => {
            // Remplace le contenu pour éviter doublons
            select.innerHTML = options;
        });
    }

    updatePrixProduit(select) {
        const option = select.options[select.selectedIndex];
        if (!option) return;
        const prix = option.getAttribute('data-prix');
        const item = select.closest('.cmd-item');

        if (prix && item) {
            const prixInput = item.querySelector('.item-prix');
            if (prixInput) {
                prixInput.value = prix;
                this.calculerTotalCommande();
            }
        }
    }

    ajouterItem() {
        const container = document.getElementById('cmd-items-container');
        if (!container) return;

        const itemHTML = `
            <div class="cmd-item" style="display: grid; grid-template-columns: 2fr 1fr 1fr 1fr 50px; gap: 10px; margin-bottom: 10px; align-items: end;">
                <div class="form-group" style="margin: 0;">
                    <select class="item-produit" required>
                        ${this.buildProduitOptions()}
                    </select>
                </div>
                <div class="form-group" style="margin: 0;">
                    <input type="number" class="item-quantite" min="1" required placeholder="Quantité">
                </div>
                <div class="form-group" style="margin: 0;">
                    <input type="number" class="item-prix" step="0.01" required placeholder="Prix unitaire">
                </div>
                <div class="form-group" style="margin: 0;">
                    <input type="text" class="item-total" readonly style="background: #f8f9fa;" placeholder="Total">
                </div>
                <button type="button" class="btn btn-danger btn-sm" data-action="retirer-item" style="height: 42px;">❌</button>
            </div>
        `;
        container.insertAdjacentHTML('beforeend', itemHTML);

        // recalcul au cas où
        this.calculerTotalCommande();
    }

    retirerItem(btn) {
        // btn peut être le bouton passé depuis delegation
        const item = btn.closest('.cmd-item');
        if (!item) return;

        const items = document.querySelectorAll('.cmd-item');
        if (items.length > 1) {
            item.remove();
            this.calculerTotalCommande();
        } else {
            this.showWarning('Au moins un article est requis');
        }
    }

    calculerTotalCommande() {
        const items = document.querySelectorAll('.cmd-item');
        let total = 0;

        items.forEach(item => {
            const quantite = parseFloat(item.querySelector('.item-quantite')?.value) || 0;
            const prix = parseFloat(item.querySelector('.item-prix')?.value) || 0;
            const sousTotal = quantite * prix;

            const totalInput = item.querySelector('.item-total');
            if (totalInput) totalInput.value = this.formatCurrency(sousTotal);

            total += sousTotal;
        });

        const totalEl = document.getElementById('cmd-total-final');
        if (totalEl) totalEl.textContent = this.formatCurrency(total);
    }

    async saveCommande(event) {
        event.preventDefault();

        const form = event.target;
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        // Récupérer les items
        const items = [];
        document.querySelectorAll('.cmd-item').forEach(item => {
            const produitId = item.querySelector('.item-produit')?.value;
            const quantite = item.querySelector('.item-quantite')?.value;
            const prixUnitaire = item.querySelector('.item-prix')?.value;

            if (produitId && quantite && prixUnitaire) {
                items.push({
                    produit_id: parseInt(produitId),
                    quantite: parseInt(quantite),
                    prix_unitaire: parseFloat(prixUnitaire)
                });
            }
        });

        // Validation
        if (items.length === 0) {
            this.showError('Ajoutez au moins un article à la commande');
            return;
        }

        if (!data.fournisseur_id) {
            this.showError('Veuillez sélectionner un fournisseur');
            return;
        }

        // Conversion des types
        data.fournisseur_id = parseInt(data.fournisseur_id);
        data.items = items;

        try {
            this.showLoading(true);

            const response = await fetch('/api/commandes', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (response.ok) {
                // Fermer le modal d'abord, puis afficher le message
                this.toggleModal('modal-commande');

                // Réinitialiser après la fermeture
                setTimeout(() => {
                    form.reset();
                    this.resetItemsCommande();
                    this.loadCommandes();
                    this.showSuccess('✅ Commande créée avec succès!');
                }, 300);

            } else {
                throw new Error(result.error || result.message || 'Erreur inconnue');
            }

        } catch (error) {
            console.error('❌ Erreur sauvegarde commande:', error);
            this.showError('Erreur: ' + (error.message || error));
        } finally {
            this.showLoading(false);
        }
    }

    resetItemsCommande() {
        const container = document.getElementById('cmd-items-container');
        if (!container) return;
        container.innerHTML = '';
        this.ajouterItem();
        this.setupDates();
    }

    async recevoirCommande(commandeId) {
        const commande = this.commandes.find(c => c.id === commandeId);
        if (!commande) return;

        if (confirm(`Confirmer la réception complète de la commande ${commande.numero_commande} ?\nLes stocks seront mis à jour automatiquement.`)) {
            try {
                const response = await fetch(`/api/commandes/${commandeId}/recevoir`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });

                if (response.ok) {
                    await this.loadCommandes();
                    this.showSuccess('✅ Commande réceptionnée! Les stocks ont été mis à jour.');
                } else {
                    const error = await response.json();
                    throw new Error(error.error || error.message);
                }
            } catch (error) {
                console.error('❌ Erreur réception:', error);
                this.showError('Erreur lors de la réception: ' + (error.message || error));
            }
        }
    }

    async annulerCommande(commandeId) {
        const commande = this.commandes.find(c => c.id === commandeId);
        if (!commande) return;

        if (!confirm(`Voulez-vous vraiment annuler la commande ${commande.numero_commande} ?\nCette action est irréversible.`)) {
            return;
        }

        try {
            const response = await fetch(`/api/commandes/${commandeId}/annuler`, {
                method: 'PUT'
            });

            if (response.ok) {
                await this.loadCommandes();
                this.showSuccess('✅ Commande annulée avec succès');
            } else {
                const error = await response.json();
                throw new Error(error.error || error.message);
            }
        } catch (error) {
            console.error('❌ Erreur annulation:', error);
            this.showError('Erreur lors de l\'annulation: ' + (error.message || error));
        }
    }

    voirDetails(commandeId) {
        const commande = this.commandes.find(c => c.id === commandeId);
        if (!commande) return;

        const details = `
📋 COMMANDE: ${commande.numero_commande}
🏭 FOURNISSEUR: ${commande.fournisseur}
📅 DATE COMMANDE: ${this.formatDate(commande.date_commande)} ${this.formatHeure(commande.date_commande)}
${commande.date_livraison_prevue ? `📦 LIVRAISON PRÉVUE: ${this.formatDate(commande.date_livraison_prevue)}` : ''}
💳 MODE PAIEMENT: ${commande.mode_paiement}
🏷️ STATUT: ${commande.statut.toUpperCase()}
💰 MONTANT TOTAL: ${this.formatCurrency(commande.montant_total, commande.devise)}
📦 NOMBRE D'ARTICLES: ${commande.nb_items}
${commande.notes ? `📝 NOTES: ${commande.notes}` : ''}
        `.trim();

        alert(details);
    }

    // Utilitaires
    formatCurrency(amount, currency = 'F CFA') {
        const num = parseFloat(amount) || 0;
        return new Intl.NumberFormat('fr-FR').format(num) + ' ' + (currency || '');
    }

    formatDate(dateString) {
        if (!dateString) return '-';
        const d = new Date(dateString);
        return d.toLocaleDateString('fr-FR');
    }

    formatHeure(dateString) {
        if (!dateString) return '';
        return new Date(dateString).toLocaleTimeString('fr-FR', {
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    toggleModal(modalId) {
        const modal = document.getElementById(modalId);
        if (!modal) return;
        modal.style.display = modal.style.display === 'block' ? 'none' : 'block';
    }

    showLoading(show) {
        if (show) {
            document.body.style.cursor = 'wait';
        } else {
            document.body.style.cursor = 'default';
        }
    }

    showError(message) {
        // Remplacer alert si tu utilises un toast system
        alert('❌ ' + message);
    }

    showSuccess(message) {
        alert('✅ ' + message);
    }

    showWarning(message) {
        alert('⚠️ ' + message);
    }

    // Petit utilitaire pour échapper du HTML dans les options
    escapeHtml(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }
}

// Initialisation globale
let commandesManager;
document.addEventListener('DOMContentLoaded', function () {
    commandesManager = new CommandesManager();
});

/*
Notes importantes:
- Ce fichier utilise l'approche "event delegation" : les boutons et actions sont gérés
  par des attributs data-action/data-id. Pour que cela fonctionne, évite d'utiliser
  des handlers inline `onclick="..."` dans ton HTML. Par exemple:

  <button data-action="ajouter-item">Ajouter</button>
  <button data-action="toggle-modal" data-target="modal-commande">Ouvrir</button>

- Si tu veux absolument garder les `onclick` inline pour compatibilité, je peux
  réintroduire (proprement) des wrappers globaux, mais c'est moins recommandé.
*/
