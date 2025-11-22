// static/js/produits.js
class ProduitsManager {
    constructor() {
        this.produits = [];
        this.categories = [];
        this.fournisseurs = [];
        this.init();
    }

    async init() {
        console.log('🚀 Initialisation gestion produits...');
        await this.loadCategories();
        await this.loadFournisseurs();
        await this.loadProduits();
        this.bindEvents();
    }

    bindEvents() {
        // Recherche en temps réel
        document.getElementById('search-produit').addEventListener('input', (e) => {
            clearTimeout(this.searchTimeout);
            this.searchTimeout = setTimeout(() => this.loadProduits(), 500);
        });

        // Filtres
        document.getElementById('filter-categorie').addEventListener('change', () => this.loadProduits());
        document.getElementById('filter-stock').addEventListener('change', () => this.loadProduits());

        // Formulaire produit
        document.getElementById('form-produit').addEventListener('submit', (e) => this.saveProduit(e));

        // Calcul automatique des marges
        document.getElementById('produit-prix-achat').addEventListener('input', () => this.calculerMarge());
        document.getElementById('produit-prix-vente').addEventListener('input', () => this.calculerMarge());
    }

    async loadProduits() {
        try {
            this.showLoading(true);
            
            const search = document.getElementById('search-produit').value;
            const categorie = document.getElementById('filter-categorie').value;
            const stockFaible = document.getElementById('filter-stock').value;
            
            let url = '/api/produits?';
            if (search) url += `search=${encodeURIComponent(search)}&`;
            if (categorie) url += `categorie_id=${categorie}&`;
            if (stockFaible === 'faible') url += `stock_faible=true&`;
            
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`Erreur HTTP: ${response.status}`);
            }
            
            this.produits = await response.json();
            this.afficherProduits(this.produits);
            
        } catch (error) {
            console.error('❌ Erreur chargement produits:', error);
            this.showError('Impossible de charger les produits: ' + error.message);
        } finally {
            this.showLoading(false);
        }
    }

    afficherProduits(produits) {
        const tbody = document.querySelector('#produits-table tbody');
        
        if (!produits || produits.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="9" style="text-align: center; padding: 40px; color: #7f8c8d;">
                        📭 Aucun produit trouvé
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = produits.map(produit => `
            <tr>
                <td>
                    <div style="font-weight: 600; color: #2c3e50;">${produit.reference}</div>
                    ${produit.code_barre ? `<div style="font-size: 11px; color: #7f8c8d;">📊 ${produit.code_barre}</div>` : ''}
                </td>
                <td>
                    <div style="font-weight: 600;">${produit.nom}</div>
                    ${produit.description ? `<div style="font-size: 12px; color: #7f8c8d; margin-top: 2px;">${produit.description.substring(0, 50)}${produit.description.length > 50 ? '...' : ''}</div>` : ''}
                </td>
                <td>${produit.categorie || '<span style="color: #7f8c8d;">-</span>'}</td>
                <td style="text-align: right;">${this.formatCurrency(produit.prix_achat)}</td>
                <td style="text-align: right;">
                    <div style="font-weight: 600;">${this.formatCurrency(produit.prix_vente)}</div>
                    <div style="font-size: 11px; color: #27ae60;">
                        Marge: ${this.calculerMargePourcentage(produit.prix_achat, produit.prix_vente)}%
                    </div>
                </td>
                <td>
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="font-weight: 600; color: ${this.getStockColor(produit)};">${produit.stock_actuel}</span>
                        <span style="font-size: 12px; color: #7f8c8d;">${produit.unite_mesure || 'unité'}</span>
                    </div>
                    ${produit.stock_min > 0 ? `<div style="font-size: 11px; color: #7f8c8d;">Min: ${produit.stock_min}</div>` : ''}
                </td>
                <td style="text-align: right; font-weight: 600;">
                        ${this.formatCurrency(produit.valeur_stock || produit.prix_achat * produit.stock_actuel)}
                    </td>
                    <td>
                        ${produit.emplacement || '-'}
                    </td>
                    <td>
                        ${this.getStatutBadge(produit)}
                    </td>

                <td>
                    <div style="display: flex; gap: 5px;">
                        <button class="btn btn-secondary btn-sm" onclick="produitsManager.editProduit(${produit.id})" title="Modifier">
                            ✏️
                        </button>
                        <button class="btn btn-danger btn-sm" onclick="produitsManager.deleteProduit(${produit.id})" title="Supprimer">
                            🗑️
                        </button>
                        ${produit.stock_actuel > 0 ? `
                        <button class="btn btn-info btn-sm" onclick="produitsManager.ajusterStock(${produit.id})" title="Ajuster stock">
                            📦
                        </button>
                        ` : ''}
                    </div>
                </td>
            </tr>
        `).join('');

        console.log(`✅ ${produits.length} produits affichés`);
    }

    getStockColor(produit) {
        if (produit.stock_actuel === 0) return '#e74c3c';
        if (produit.stock_actuel <= produit.stock_min) return '#f39c12';
        return '#27ae60';
    }

    getStatutBadge(produit) {
        if (produit.stock_actuel === 0) {
            return '<span class="badge badge-danger">❌ Rupture</span>';
        } else if (produit.stock_actuel <= produit.stock_min) {
            return '<span class="badge badge-warning">⚠️ Stock faible</span>';
        } else {
            return '<span class="badge badge-success">✅ En stock</span>';
        }
    }

    calculerMargePourcentage(prixAchat, prixVente) {
        if (!prixAchat || !prixVente || prixAchat === 0) return 0;
        return Math.round(((prixVente - prixAchat) / prixAchat) * 100);
    }

    async loadCategories() {
        try {
            const response = await fetch('/api/categories');
            this.categories = await response.json();
            
            const selects = ['filter-categorie', 'produit-categorie'];
            selects.forEach(selectId => {
                const select = document.getElementById(selectId);
                select.innerHTML = '<option value="">Toutes les catégories</option>' +
                    this.categories.map(c => `<option value="${c.id}">${c.nom}</option>`).join('');
            });
            
            console.log(`✅ ${this.categories.length} catégories chargées`);
        } catch (error) {
            console.error('❌ Erreur chargement catégories:', error);
        }
    }

    async loadFournisseurs() {
        try {
            const response = await fetch('/api/fournisseurs');
            this.fournisseurs = await response.json();
            
            const select = document.getElementById('produit-fournisseur');
            select.innerHTML = '<option value="">Sélectionner un fournisseur...</option>' +
                this.fournisseurs.map(f => `<option value="${f.id}">${f.nom}</option>`).join('');
                
            console.log(`✅ ${this.fournisseurs.length} fournisseurs chargés`);
        } catch (error) {
            console.error('❌ Erreur chargement fournisseurs:', error);
        }
    }

    async saveProduit(event) {
        event.preventDefault();
        
        const form = event.target;
        const formData = new FormData(form);
        const data = Object.fromEntries(formData);
        
        // Validation
        if (!data.reference || !data.nom || !data.prix_achat || !data.prix_vente) {
            this.showError('Veuillez remplir les champs obligatoires');
            return;
        }

        // Conversion des types
        const numericFields = ['prix_achat', 'prix_vente', 'tva', 'stock_actuel', 'stock_min', 'stock_max'];
        const integerFields = ['categorie_id', 'fournisseur_id'];
        
        numericFields.forEach(key => {
            if (data[key]) data[key] = parseFloat(data[key]);
        });
        
        integerFields.forEach(key => {
            if (data[key]) data[key] = parseInt(data[key]);
        });

        // Nettoyage des données
        Object.keys(data).forEach(key => {
            if (data[key] === '' || data[key] === null) {
                delete data[key];
            }
        });

        const id = document.getElementById('produit-id').value;
        const method = id ? 'PUT' : 'POST';
        const url = id ? `/api/produits/${id}` : '/api/produits';

        try {
            this.showLoading(true);
            
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (response.ok) {
                this.toggleModal('modal-produit');
                form.reset();
                document.getElementById('produit-id').value = '';
                await this.loadProduits();
                this.showSuccess(id ? '✅ Produit modifié avec succès!' : '✅ Produit créé avec succès!');
            } else {
                throw new Error(result.error || result.message || 'Erreur inconnue');
            }
            
        } catch (error) {
            console.error('❌ Erreur sauvegarde produit:', error);
            this.showError('Erreur: ' + error.message);
        } finally {
            this.showLoading(false);
        }
    }

    editProduit(id) {
        const produit = this.produits.find(p => p.id === id);
        if (!produit) {
            this.showError('Produit non trouvé');
            return;
        }

        document.getElementById('modal-produit-title').textContent = 'Modifier le produit';
        document.getElementById('produit-id').value = produit.id;
        document.getElementById('produit-reference').value = produit.reference;
        document.getElementById('produit-code-barre').value = produit.code_barre || '';
        document.getElementById('produit-nom').value = produit.nom;
        document.getElementById('produit-description').value = produit.description || '';
        document.getElementById('produit-prix-achat').value = produit.prix_achat;
        document.getElementById('produit-prix-vente').value = produit.prix_vente;
        document.getElementById('produit-tva').value = produit.tva || 18;
        document.getElementById('produit-stock-actuel').value = produit.stock_actuel;
        document.getElementById('produit-stock-min').value = produit.stock_min || 0;
        document.getElementById('produit-stock-max').value = produit.stock_max || 1000;
        document.getElementById('produit-emplacement').value = produit.emplacement || '';
        
        // Sélectionner la catégorie et le fournisseur
        if (produit.categorie_id) {
            document.getElementById('produit-categorie').value = produit.categorie_id;
        }
        if (produit.fournisseur_id) {
            document.getElementById('produit-fournisseur').value = produit.fournisseur_id;
        }
        
        // Sélectionner l'unité de mesure
        if (produit.unite_mesure) {
            document.getElementById('produit-unite').value = produit.unite_mesure;
        }

        this.toggleModal('modal-produit');
        this.calculerMarge();
    }

    async deleteProduit(id) {
        const produit = this.produits.find(p => p.id === id);
        if (!produit) return;

        if (!confirm(`Voulez-vous vraiment supprimer le produit "${produit.nom}" ?\nCette action est irréversible.`)) {
            return;
        }

        try {
            const response = await fetch(`/api/produits/${id}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                await this.loadProduits();
                this.showSuccess('✅ Produit supprimé avec succès');
            } else {
                const error = await response.json();
                throw new Error(error.error || error.message);
            }
        } catch (error) {
            console.error('❌ Erreur suppression:', error);
            this.showError('Erreur lors de la suppression: ' + error.message);
        }
    }

    async ajusterStock(id) {
        const produit = this.produits.find(p => p.id === id);
        if (!produit) return;

        const nouveauStock = prompt(`Ajuster le stock pour "${produit.nom}"\nStock actuel: ${produit.stock_actuel}`, produit.stock_actuel);
        
        if (nouveauStock === null) return;

        const stock = parseInt(nouveauStock);
        if (isNaN(stock) || stock < 0) {
            this.showError('Veuillez entrer un nombre valide');
            return;
        }

        try {
            const response = await fetch(`/api/produits/${id}/stock`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ stock_actuel: stock })
            });

            if (response.ok) {
                await this.loadProduits();
                this.showSuccess(`✅ Stock ajusté à ${stock}`);
            } else {
                const error = await response.json();
                throw new Error(error.error || error.message);
            }
        } catch (error) {
            console.error('❌ Erreur ajustement stock:', error);
            this.showError('Erreur: ' + error.message);
        }
    }

    calculerMarge() {
        const prixAchat = parseFloat(document.getElementById('produit-prix-achat').value) || 0;
        const prixVente = parseFloat(document.getElementById('produit-prix-vente').value) || 0;
        
        if (prixAchat > 0 && prixVente > 0) {
            const marge = prixVente - prixAchat;
            const margePourcentage = Math.round((marge / prixAchat) * 100);
            
            // Afficher la marge quelque part (vous pouvez ajouter un élément dans le modal)
            console.log(`💰 Marge: ${this.formatCurrency(marge)} (${margePourcentage}%)`);
        }
    }

    async exporterProduits() {
        try {
            window.location.href = '/api/export/produits/excel';
        } catch (error) {
            console.error('❌ Erreur export:', error);
            this.showError('Erreur lors de l\'export');
        }
    }

    toggleModal(modalId) {
        const modal = document.getElementById(modalId);
        modal.style.display = modal.style.display === 'block' ? 'none' : 'block';
    }

    formatCurrency(amount, currency = 'F CFA') {
        if (!amount) amount = 0;
        return new Intl.NumberFormat('fr-FR').format(amount) + ' ' + currency;
    }

    showLoading(show) {
        // Implémentez un indicateur de chargement si nécessaire
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
}

// Initialisation globale
let produitsManager;

document.addEventListener('DOMContentLoaded', function() {
    produitsManager = new ProduitsManager();
});

// Fonctions globales pour les onclick
function toggleModal(modalId) {
    if (produitsManager) {
        produitsManager.toggleModal(modalId);
    }
}

function exporterProduits() {
    if (produitsManager) {
        produitsManager.exporterProduits();
    }
}