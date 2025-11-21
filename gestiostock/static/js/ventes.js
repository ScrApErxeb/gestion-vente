// static/js/ventes.js
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
        document.getElementById('filter-date-debut').addEventListener('change', () => this.loadVentes());
        document.getElementById('filter-date-fin').addEventListener('change', () => this.loadVentes());
        document.getElementById('filter-client').addEventListener('change', () => this.loadVentes());
        document.getElementById('filter-statut').addEventListener('change', () => this.loadVentes());

        // Formulaire vente
        document.getElementById('form-vente').addEventListener('submit', (e) => this.saveVente(e));

        // Événements calculs - CORRECTION DES NOMS
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
            
            const dateDebut = document.getElementById('filter-date-debut').value;
            const dateFin = document.getElementById('filter-date-fin').value;
            const clientId = document.getElementById('filter-client').value;
            const statut = document.getElementById('filter-statut').value;
            
            let url = '/api/ventes?';
            if (dateDebut) url += `date_debut=${dateDebut}&`;
            if (dateFin) url += `date_fin=${dateFin}&`;
            if (clientId) url += `client_id=${clientId}&`;
            if (statut) url += `statut=${statut}&`;
            
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`Erreur HTTP: ${response.status}`);
            }
            
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
        
        if (!ventes || ventes.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="9" style="text-align: center; padding: 40px; color: #7f8c8d;">
                        📭 Aucune vente trouvée
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = ventes.map(vente => `
            <tr>
                <td>
                    <div style="font-weight: 600; color: #2c3e50;">${vente.numero_facture}</div>
                    ${vente.notes ? `<div style="font-size: 11px; color: #7f8c8d;">${vente.notes.substring(0, 30)}${vente.notes.length > 30 ? '...' : ''}</div>` : ''}
                </td>
                <td>
                    <div style="font-weight: 500;">${this.formatDate(vente.date_vente)}</div>
                    <div style="font-size: 11px; color: #7f8c8d;">${this.formatHeure(vente.date_vente)}</div>
                </td>
                <td>${vente.client || '<span style="color: #7f8c8d;">Client anonyme</span>'}</td>
                <td>
                    <div style="font-weight: 500;">${vente.produit}</div>
                    <div style="font-size: 11px; color: #7f8c8d;">${this.formatCurrency(vente.prix_unitaire, vente.devise)}/unité</div>
                </td>
                <td style="text-align: center;">
                    <span style="font-weight: 600; background: #e8f8f5; padding: 4px 8px; border-radius: 4px;">${vente.quantite}</span>
                </td>
                <td style="text-align: right; font-weight: 600;">
                    ${this.formatCurrency(vente.montant_total, vente.devise)}
                    ${vente.remise > 0 ? `<div style="font-size: 11px; color: #e74c3c;">Remise: ${vente.remise}%</div>` : ''}
                </td>
                <td>
                    <span class="badge badge-info">${this.getPaiementIcon(vente.mode_paiement)} ${vente.mode_paiement}</span>
                </td>
                <td>
                    ${this.getStatutBadge(vente.statut)}
                </td>
                <td>
                    <div style="display: flex; gap: 5px;">
                        <button class="btn btn-secondary btn-sm" onclick="ventesManager.telechargerFacture(${vente.id})" title="Facture PDF">
                            📄
                        </button>
                        <button class="btn btn-primary btn-sm" onclick="ventesManager.voirDetails(${vente.id})" title="Détails">
                            👁️
                        </button>
                        ${vente.statut === 'confirmée' ? `
                        <button class="btn btn-danger btn-sm" onclick="ventesManager.annulerVente(${vente.id})" title="Annuler">
                            ❌
                        </button>
                        ` : ''}
                    </div>
                </td>
            </tr>
        `).join('');

        console.log(`✅ ${ventes.length} ventes affichées`);
    }

    getPaiementIcon(modePaiement) {
        const icons = {
            'espèces': '💰',
            'carte': '💳',
            'mobile': '📱',
            'virement': '🏦'
        };
        return icons[modePaiement] || '💸';
    }

    getStatutBadge(statut) {
        const badges = {
            'confirmée': '<span class="badge badge-success">✅ Confirmée</span>',
            'annulée': '<span class="badge badge-danger">❌ Annulée</span>',
            'brouillon': '<span class="badge badge-warning">📝 Brouillon</span>'
        };
        return badges[statut] || '<span class="badge badge-secondary">❓ Inconnu</span>';
    }

    calculerStats(ventes) {
        const aujourdhui = new Date().toISOString().split('T')[0];
        const ventesJour = ventes.filter(v => v.date_vente.startsWith(aujourdhui) && v.statut === 'confirmée');
        
        const caJour = ventesJour.reduce((sum, v) => sum + v.montant_total, 0);
        const nbVentes = ventesJour.length;
        const articlesVendus = ventesJour.reduce((sum, v) => sum + v.quantite, 0);
        
        document.getElementById('ca-jour').textContent = this.formatCurrency(caJour);
        document.getElementById('nb-ventes-jour').textContent = nbVentes;
        document.getElementById('articles-vendus').textContent = articlesVendus;
    }

    async loadClients() {
        try {
            const response = await fetch('/api/clients');
            this.clients = await response.json();
            
            const selects = ['filter-client', 'vente-client'];
            selects.forEach(selectId => {
                const select = document.getElementById(selectId);
                const defaultOption = selectId === 'filter-client' ? 
                    '<option value="">Tous les clients</option>' : 
                    '<option value="">Client anonyme</option>';
                select.innerHTML = defaultOption +
                    this.clients.map(c => `<option value="${c.id}">${c.nom} ${c.prenom || ''}${c.telephone ? ` - ${c.telephone}` : ''}</option>`).join('');
            });
            
            console.log(`✅ ${this.clients.length} clients chargés`);
        } catch (error) {
            console.error('❌ Erreur chargement clients:', error);
        }
    }

    async loadProduits() {
        try {
            const response = await fetch('/api/produits');
            this.produits = await response.json();
            
            const select = document.getElementById('vente-produit');
            const produitsEnStock = this.produits.filter(p => p.stock_actuel > 0);
            
            select.innerHTML = '<option value="">Sélectionner un produit</option>' +
                produitsEnStock.map(p => 
                    `<option value="${p.id}" data-prix="${p.prix_vente}" data-stock="${p.stock_actuel}">
                        ${p.nom} - ${this.formatCurrency(p.prix_vente)} - Stock: ${p.stock_actuel}
                    </option>`
                ).join('');
                
            console.log(`✅ ${produitsEnStock.length} produits en stock chargés`);
        } catch (error) {
            console.error('❌ Erreur chargement produits:', error);
        }
    }

    // ⭐ CORRECTION : Cette méthode existe déjà, pas besoin de la renommer
    updatePrixVente() {
        const select = document.getElementById('vente-produit');
        const option = select.options[select.selectedIndex];
        const prix = option.getAttribute('data-prix');
        const stock = option.getAttribute('data-stock');
        
        document.getElementById('vente-prix').value = prix || 0;
        
        // Mettre à jour la quantité max
        const inputQuantite = document.getElementById('vente-quantite');
        inputQuantite.max = stock || 1;
        
        if (parseInt(inputQuantite.value) > parseInt(stock)) {
            inputQuantite.value = stock;
            this.showWarning(`Stock disponible: ${stock} unités`);
        }
        
        this.calculerTotal();
    }

    // ⭐ CORRECTION : Cette méthode existe déjà, pas besoin de la renommer
    calculerTotal() {
        const quantite = parseFloat(document.getElementById('vente-quantite').value) || 0;
        const prix = parseFloat(document.getElementById('vente-prix').value) || 0;
        const remise = parseFloat(document.getElementById('vente-remise').value) || 0;
        const devise = document.getElementById('vente-devise').value;
        
        const sousTotal = quantite * prix;
        const montantRemise = sousTotal * (remise / 100);
        const total = sousTotal - montantRemise;
        
        document.getElementById('vente-total').textContent = this.formatCurrency(total, devise);
    }

    async saveVente(event) {
        event.preventDefault();
        
        const form = event.target;
        const formData = new FormData(form);
        const data = Object.fromEntries(formData);
        
        // Validation
        if (!data.produit_id) {
            this.showError('Veuillez sélectionner un produit');
            return;
        }

        if (!data.quantite || data.quantite <= 0) {
            this.showError('Veuillez saisir une quantité valide');
            return;
        }

        // Vérifier le stock
        const produitSelect = document.getElementById('vente-produit');
        const option = produitSelect.options[produitSelect.selectedIndex];
        const stockDisponible = parseInt(option.getAttribute('data-stock'));
        const quantiteDemandee = parseInt(data.quantite);
        
        if (quantiteDemandee > stockDisponible) {
            this.showError(`Stock insuffisant! Disponible: ${stockDisponible}, Demandé: ${quantiteDemandee}`);
            return;
        }

        // Conversion des types
        const numericFields = ['quantite', 'prix_unitaire', 'remise'];
        const integerFields = ['produit_id', 'client_id'];
        
        numericFields.forEach(key => {
            if (data[key]) data[key] = parseFloat(data[key]);
        });
        
        integerFields.forEach(key => {
            if (data[key]) data[key] = parseInt(data[key]) || null;
        });

        // Données par défaut
        data.statut = 'confirmée';
        data.statut_paiement = 'payé';

        try {
            this.showLoading(true);
            
            const response = await fetch('/api/ventes', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (response.ok) {
                this.toggleModal('modal-vente');
                form.reset();
                document.getElementById('vente-total').textContent = '0 F CFA';
                await this.loadVentes();
                await this.loadProduits(); // Recharger les stocks
                this.showSuccess('✅ Vente enregistrée avec succès!');
            } else {
                throw new Error(result.error || result.message || 'Erreur inconnue');
            }
            
        } catch (error) {
            console.error('❌ Erreur sauvegarde vente:', error);
            this.showError('Erreur: ' + error.message);
        } finally {
            this.showLoading(false);
        }
    }

    async annulerVente(id) {
        const vente = this.ventes.find(v => v.id === id);
        if (!vente) return;

        if (!confirm(`Voulez-vous vraiment annuler la vente ${vente.numero_facture} ?\nCette action est irréversible.`)) {
            return;
        }

        try {
            const response = await fetch(`/api/ventes/${id}/annuler`, {
                method: 'PUT'
            });

            if (response.ok) {
                await this.loadVentes();
                await this.loadProduits(); // Recharger les stocks
                this.showSuccess('✅ Vente annulée avec succès');
            } else {
                const error = await response.json();
                throw new Error(error.error || error.message);
            }
        } catch (error) {
            console.error('❌ Erreur annulation:', error);
            this.showError('Erreur lors de l\'annulation: ' + error.message);
        }
    }

    async telechargerFacture(venteId) {
        try {
            window.open(`/api/export/facture/${venteId}`, '_blank');
        } catch (error) {
            console.error('❌ Erreur téléchargement facture:', error);
            this.showError('Erreur lors du téléchargement');
        }
    }

    voirDetails(venteId) {
        const vente = this.ventes.find(v => v.id === venteId);
        if (!vente) return;

        const details = `
📄 FACTURE: ${vente.numero_facture}
📅 DATE: ${this.formatDate(vente.date_vente)} ${this.formatHeure(vente.date_vente)}
👤 CLIENT: ${vente.client || 'Client anonyme'}
📦 PRODUIT: ${vente.produit}
🔢 QUANTITÉ: ${vente.quantite}
💰 PRIX UNITAIRE: ${this.formatCurrency(vente.prix_unitaire, vente.devise)}
🎫 REMISE: ${vente.remise}%
💳 MODE PAIEMENT: ${vente.mode_paiement}
🏷️ STATUT: ${vente.statut}
${vente.notes ? `📝 NOTES: ${vente.notes}` : ''}

💵 TOTAL: ${this.formatCurrency(vente.montant_total, vente.devise)}
        `.trim();

        alert(details);
    }

    async exporterVentes() {
        try {
            const dateDebut = document.getElementById('filter-date-debut').value;
            const dateFin = document.getElementById('filter-date-fin').value;
            let url = '/api/export/ventes/excel?';
            if (dateDebut) url += `date_debut=${dateDebut}&`;
            if (dateFin) url += `date_fin=${dateFin}`;
            window.location.href = url;
        } catch (error) {
            console.error('❌ Erreur export:', error);
            this.showError('Erreur lors de l\'export');
        }
    }

    // ⭐ AJOUT : Méthode pour fermer le modal
    closeSaleModal() {
        this.toggleModal('modal-vente');
    }

    // Utilitaires
    formatCurrency(amount, currency = 'F CFA') {
        if (!amount) amount = 0;
        return new Intl.NumberFormat('fr-FR').format(amount) + ' ' + currency;
    }

    formatDate(dateString) {
        return new Date(dateString).toLocaleDateString('fr-FR');
    }

    formatHeure(dateString) {
        return new Date(dateString).toLocaleTimeString('fr-FR', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
    }

    toggleModal(modalId) {
        const modal = document.getElementById(modalId);
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
        alert('❌ ' + message);
    }

    showSuccess(message) {
        alert('✅ ' + message);
    }

    showWarning(message) {
        alert('⚠️ ' + message);
    }
}

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