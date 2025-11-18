// ================================
// VENTES.JS - GestioStock
// ================================

// Variables globales
let ventes = [];
let produits = [];
let clients = [];
let articlesCount = 0;

// ================================
// INITIALISATION
// ================================
document.addEventListener('DOMContentLoaded', function() {
    // Définir les dates par défaut
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('filter-date-debut').value = today;
    document.getElementById('filter-date-fin').value = today;
    
    // Charger les données
    chargerVentes();
    chargerProduits();
    chargerClients();
});

// ================================
// CHARGEMENT DES DONNÉES
// ================================
async function chargerVentes() {
    try {
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
        ventes = await response.json();
        
        afficherVentes(ventes);
        calculerStats(ventes);
    } catch (error) {
        console.error('Erreur chargement ventes:', error);
        afficherErreur('Impossible de charger les ventes');
    }
}

async function chargerProduits() {
    try {
        const response = await fetch('/api/produits');
        produits = await response.json();
    } catch (error) {
        console.error('Erreur chargement produits:', error);
    }
}

async function chargerClients() {
    try {
        const response = await fetch('/api/clients');
        clients = await response.json();
        
        // Remplir les selects
        const selectFiltre = document.getElementById('filter-client');
        const selectVente = document.getElementById('vente-client');
        
        selectFiltre.innerHTML = '<option value="">Tous les clients</option>' +
            clients.map(c => `<option value="${c.id}">${c.nom} ${c.prenom || ''}</option>`).join('');
        
        selectVente.innerHTML = '<option value="">Client anonyme</option>' +
            clients.map(c => `<option value="${c.id}">${c.nom} ${c.prenom || ''}</option>`).join('');
    } catch (error) {
        console.error('Erreur chargement clients:', error);
    }
}

// ================================
// AFFICHAGE DES VENTES
// ================================
function afficherVentes(data) {
    const tbody = document.querySelector('#ventes-table tbody');
    
    if (data.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="text-center text-muted">
                    Aucune vente trouvée pour cette période
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = data.map(v => {
        const nbArticles = v.items ? v.items.length : (v.produit ? 1 : 0);
        return `
            <tr>
                <td><strong>${v.numero_facture}</strong></td>
                <td>${v.date_vente}</td>
                <td>${v.client}</td>
                <td>${nbArticles} article(s)</td>
                <td><strong>${formatCurrency(v.montant_total, v.devise)}</strong></td>
                <td><span class="badge badge-info">${v.mode_paiement}</span></td>
                <td>
                    ${v.statut === 'confirmée' ? 
                        '<span class="badge badge-success">✅ Confirmée</span>' : 
                        '<span class="badge badge-danger">❌ Annulée</span>'}
                </td>
                <td>
                    <button class="btn btn-secondary btn-sm btn-icon" 
                            onclick="telechargerFacture(${v.id})" 
                            title="Télécharger PDF">📄</button>
                    <button class="btn btn-primary btn-sm btn-icon" 
                            onclick="voirDetails(${v.id})" 
                            title="Détails">👁️</button>
                </td>
            </tr>
        `;
    }).join('');
}

function calculerStats(data) {
    const today = new Date().toISOString().split('T')[0];
    const ventesJour = data.filter(v => 
        v.date_vente.startsWith(today) && v.statut === 'confirmée'
    );
    
    const caJour = ventesJour.reduce((sum, v) => sum + v.montant_total, 0);
    const nbVentes = ventesJour.length;
    
    // Calculer les articles vendus
    let articlesVendus = 0;
    ventesJour.forEach(v => {
        if (v.items && v.items.length > 0) {
            articlesVendus += v.items.reduce((sum, item) => sum + item.quantite, 0);
        } else if (v.quantite) {
            articlesVendus += v.quantite;
        }
    });
    
    document.getElementById('ca-jour').textContent = formatCurrency(caJour);
    document.getElementById('nb-ventes-jour').textContent = nbVentes;
    document.getElementById('articles-vendus').textContent = articlesVendus;
}

// ================================
// GESTION DU MODAL
// ================================
function ouvrirModalVente() {
    const modal = document.getElementById('modal-vente');
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
    
    // Ajouter une première ligne d'article
    if (articlesCount === 0) {
        ajouterLigneArticle();
    }
}

function fermerModalVente() {
    const modal = document.getElementById('modal-vente');
    modal.classList.remove('active');
    document.body.style.overflow = '';
    
    // Réinitialiser le formulaire
    document.getElementById('form-vente').reset();
    document.getElementById('articles-container').innerHTML = `
        <div class="empty-state">
            <div class="empty-icon">🛒</div>
            <p>Aucun article ajouté. Cliquez sur "Ajouter un article"</p>
        </div>
    `;
    articlesCount = 0;
}

// ================================
// GESTION DES ARTICLES
// ================================
function ajouterLigneArticle() {
    articlesCount++;
    const container = document.getElementById('articles-container');
    
    // Supprimer le message vide si présent
    const emptyState = container.querySelector('.empty-state');
    if (emptyState) {
        emptyState.remove();
    }
    
    const articleDiv = document.createElement('div');
    articleDiv.className = 'article-item';
    articleDiv.id = `article-${articlesCount}`;
    articleDiv.innerHTML = `
        <div class="article-item-header">
            <span class="article-item-number">Article #${articlesCount}</span>
            <button type="button" class="btn btn-danger btn-sm" 
                    onclick="supprimerLigneArticle(${articlesCount})">
                🗑️ Supprimer
            </button>
        </div>
        
        <div class="article-grid">
            <div class="form-group">
                <label>Produit *</label>
                <select class="article-produit" 
                        data-id="${articlesCount}" 
                        onchange="updatePrixArticle(${articlesCount})" 
                        required>
                    <option value="">Sélectionner un produit</option>
                    ${produits.filter(p => p.stock_actuel > 0).map(p => 
                        `<option value="${p.id}" 
                                 data-prix="${p.prix_vente}" 
                                 data-tva="${p.tva || 0}" 
                                 data-stock="${p.stock_actuel}">
                            ${p.nom} (Stock: ${p.stock_actuel})
                        </option>`
                    ).join('')}
                </select>
            </div>
            
            <div class="form-group">
                <label>Quantité *</label>
                <input type="number" 
                       class="article-quantite" 
                       data-id="${articlesCount}"
                       min="1" 
                       value="1" 
                       onchange="calculerLigne(${articlesCount})" 
                       required>
            </div>
            
            <div class="form-group">
                <label>Prix unitaire</label>
                <input type="number" 
                       class="article-prix" 
                       data-id="${articlesCount}"
                       step="0.01" 
                       value="0" 
                       onchange="calculerLigne(${articlesCount})">
            </div>
            
            <div class="form-group">
                <label>Remise %</label>
                <input type="number" 
                       class="article-remise" 
                       data-id="${articlesCount}"
                       min="0" 
                       max="100" 
                       step="0.01" 
                       value="0" 
                       onchange="calculerLigne(${articlesCount})">
            </div>
            
            <div class="form-group">
                <label>TVA %</label>
                <input type="number" 
                       class="article-tva" 
                       data-id="${articlesCount}"
                       step="0.01" 
                       value="0" 
                       readonly>
            </div>
            
            <div class="form-group">
                <label>Total</label>
                <div class="article-total" id="total-${articlesCount}">0 F CFA</div>
            </div>
        </div>
    `;
    
    container.appendChild(articleDiv);
}

function supprimerLigneArticle(id) {
    const article = document.getElementById(`article-${id}`);
    if (article) {
        article.remove();
        calculerTotalVente();
        
        // Afficher le message vide si plus d'articles
        const container = document.getElementById('articles-container');
        if (container.children.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">🛒</div>
                    <p>Aucun article ajouté. Cliquez sur "Ajouter un article"</p>
                </div>
            `;
        }
    }
}

function updatePrixArticle(id) {
    const select = document.querySelector(`.article-produit[data-id="${id}"]`);
    const option = select.options[select.selectedIndex];
    
    if (option.value) {
        const prix = option.getAttribute('data-prix');
        const tva = option.getAttribute('data-tva');
        
        document.querySelector(`.article-prix[data-id="${id}"]`).value = prix || 0;
        document.querySelector(`.article-tva[data-id="${id}"]`).value = tva || 0;
        
        calculerLigne(id);
    }
}

function calculerLigne(id) {
    const quantite = parseFloat(document.querySelector(`.article-quantite[data-id="${id}"]`).value) || 0;
    const prix = parseFloat(document.querySelector(`.article-prix[data-id="${id}"]`).value) || 0;
    const remise = parseFloat(document.querySelector(`.article-remise[data-id="${id}"]`).value) || 0;
    const tva = parseFloat(document.querySelector(`.article-tva[data-id="${id}"]`).value) || 0;
    
    // Calculs
    const montantHT = quantite * prix;
    const montantRemise = montantHT * (remise / 100);
    const montantHTApresRemise = montantHT - montantRemise;
    const montantTVA = montantHTApresRemise * (tva / 100);
    const total = montantHTApresRemise + montantTVA;
    
    // Afficher le total
    const devise = document.getElementById('vente-devise').value;
    document.getElementById(`total-${id}`).textContent = formatCurrency(total, devise);
    
    // Recalculer le total général
    calculerTotalVente();
}

function calculerTotalVente() {
    let sousTotal = 0;
    
    // Parcourir tous les articles
    const articles = document.querySelectorAll('.article-item');
    articles.forEach(article => {
        const id = article.id.replace('article-', '');
        const quantite = parseFloat(document.querySelector(`.article-quantite[data-id="${id}"]`)?.value) || 0;
        const prix = parseFloat(document.querySelector(`.article-prix[data-id="${id}"]`)?.value) || 0;
        const remise = parseFloat(document.querySelector(`.article-remise[data-id="${id}"]`)?.value) || 0;
        const tva = parseFloat(document.querySelector(`.article-tva[data-id="${id}"]`)?.value) || 0;
        
        const montantHT = quantite * prix;
        const montantRemise = montantHT * (remise / 100);
        const montantHTApresRemise = montantHT - montantRemise;
        const montantTVA = montantHTApresRemise * (tva / 100);
        sousTotal += montantHTApresRemise + montantTVA;
    });
    
    // Appliquer la remise globale
    const remiseGlobale = parseFloat(document.getElementById('vente-remise-globale').value) || 0;
    const montantRemiseGlobale = sousTotal * (remiseGlobale / 100);
    const total = sousTotal - montantRemiseGlobale;
    
    // Afficher le total
    const devise = document.getElementById('vente-devise').value;
    document.getElementById('vente-total').textContent = formatCurrency(total, devise);
}

// ================================
// ENREGISTREMENT DE LA VENTE
// ================================
async function enregistrerVente(event) {
    event.preventDefault();
    
    // Récupérer les articles
    const articles = document.querySelectorAll('.article-item');
    
    if (articles.length === 0) {
        afficherErreur('Veuillez ajouter au moins un article');
        return;
    }
    
    const items = [];
    let isValid = true;
    
    articles.forEach(article => {
        const id = article.id.replace('article-', '');
        const produitId = document.querySelector(`.article-produit[data-id="${id}"]`).value;
        const quantite = parseFloat(document.querySelector(`.article-quantite[data-id="${id}"]`).value);
        const prixUnitaire = parseFloat(document.querySelector(`.article-prix[data-id="${id}"]`).value);
        const remise = parseFloat(document.querySelector(`.article-remise[data-id="${id}"]`).value) || 0;
        const tva = parseFloat(document.querySelector(`.article-tva[data-id="${id}"]`).value) || 0;
        
        if (!produitId || quantite <= 0) {
            isValid = false;
            return;
        }
        
        // Calculer le montant total de la ligne
        const montantHT = quantite * prixUnitaire;
        const montantRemise = montantHT * (remise / 100);
        const montantHTApresRemise = montantHT - montantRemise;
        const montantTVA = montantHTApresRemise * (tva / 100);
        const montantTotal = montantHTApresRemise + montantTVA;
        
        items.push({
            produit_id: parseInt(produitId),
            quantite: quantite,
            prix_unitaire: prixUnitaire,
            remise: remise,
            tva: tva,
            montant_total: montantTotal
        });
    });
    
    if (!isValid) {
        afficherErreur('Tous les produits doivent être sélectionnés avec une quantité valide');
        return;
    }
    
    // Préparer les données de la vente
    const form = document.getElementById('form-vente');
    const formData = new FormData(form);
    
    const data = {
        client_id: formData.get('client_id') ? parseInt(formData.get('client_id')) : null,
        mode_paiement: formData.get('mode_paiement'),
        devise: formData.get('devise'),
        remise: parseFloat(formData.get('remise')) || 0,
        notes: formData.get('notes'),
        statut_paiement: 'payé',
        items: items
    };
    
    try {
        const response = await fetch('/api/ventes', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            afficherSucces('✅ Vente enregistrée avec succès!');
            fermerModalVente();
            chargerVentes();
        } else {
            const error = await response.json();
            afficherErreur(error.error || 'Erreur lors de l\'enregistrement');
        }
    } catch (error) {
        console.error('Erreur:', error);
        afficherErreur('Erreur de connexion au serveur');
    }
}

// ================================
// FONCTIONS UTILITAIRES
// ================================
function formatCurrency(montant, devise = 'XOF') {
    const symboles = {
        'XOF': 'F CFA',
        'EUR': '€',
        'USD': '$',
        'GBP': '£'
    };
    
    const montantFormate = montant.toLocaleString('fr-FR', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 2
    });
    
    return `${montantFormate} ${symboles[devise] || devise}`;
}

function filtrerVentes() {
    chargerVentes();
}

function afficherSucces(message) {
    alert(message);
}

function afficherErreur(message) {
    alert('❌ ' + message);
}

// ================================
// ACTIONS SUR LES VENTES
// ================================
async function telechargerFacture(venteId) {
    window.location.href = `/api/export/facture/${venteId}`;
}

async function voirDetails(venteId) {
    const vente = ventes.find(v => v.id === venteId);
    if (!vente) return;
    
    const modal = document.getElementById('modal-details');
    const content = document.getElementById('details-content');
    
    let detailsHTML = `
        <div style="padding: 1rem;">
            <div style="margin-bottom: 1.5rem;">
                <h3 style="margin-bottom: 1rem; color: #2c3e50;">Informations générales</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 0.5rem; border-bottom: 1px solid #e9ecef;"><strong>N° Facture:</strong></td>
                        <td style="padding: 0.5rem; border-bottom: 1px solid #e9ecef;">${vente.numero_facture}</td>
                    </tr>
                    <tr>
                        <td style="padding: 0.5rem; border-bottom: 1px solid #e9ecef;"><strong>Date:</strong></td>
                        <td style="padding: 0.5rem; border-bottom: 1px solid #e9ecef;">${vente.date_vente}</td>
                    </tr>
                    <tr>
                        <td style="padding: 0.5rem; border-bottom: 1px solid #e9ecef;"><strong>Client:</strong></td>
                        <td style="padding: 0.5rem; border-bottom: 1px solid #e9ecef;">${vente.client}</td>
                    </tr>
                    <tr>
                        <td style="padding: 0.5rem; border-bottom: 1px solid #e9ecef;"><strong>Mode de paiement:</strong></td>
                        <td style="padding: 0.5rem; border-bottom: 1px solid #e9ecef;">${vente.mode_paiement}</td>
                    </tr>
                    <tr>
                        <td style="padding: 0.5rem;"><strong>Statut:</strong></td>
                        <td style="padding: 0.5rem;">${vente.statut}</td>
                    </tr>
                </table>
            </div>
    `;
    
    if (vente.items && vente.items.length > 0) {
        detailsHTML += `
            <div>
                <h3 style="margin-bottom: 1rem; color: #2c3e50;">Articles</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr style="background: #f8f9fa;">
                            <th style="padding: 0.75rem; text-align: left; border-bottom: 2px solid #dee2e6;">Produit</th>
                            <th style="padding: 0.75rem; text-align: right; border-bottom: 2px solid #dee2e6;">Quantité</th>
                            <th style="padding: 0.75rem; text-align: right; border-bottom: 2px solid #dee2e6;">Prix unit.</th>
                            <th style="padding: 0.75rem; text-align: right; border-bottom: 2px solid #dee2e6;">Total</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${vente.items.map(item => `
                            <tr>
                                <td style="padding: 0.75rem; border-bottom: 1px solid #e9ecef;">${item.produit}</td>
                                <td style="padding: 0.75rem; text-align: right; border-bottom: 1px solid #e9ecef;">${item.quantite}</td>
                                <td style="padding: 0.75rem; text-align: right; border-bottom: 1px solid #e9ecef;">${formatCurrency(item.prix_unitaire, vente.devise)}</td>
                                <td style="padding: 0.75rem; text-align: right; border-bottom: 1px solid #e9ecef;"><strong>${formatCurrency(item.montant_total, vente.devise)}</strong></td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    }
    
    detailsHTML += `
            <div style="margin-top: 1.5rem; padding: 1rem; background: #f8f9fa; border-radius: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 1.25rem; font-weight: 600;">TOTAL:</span>
                    <span style="font-size: 1.5rem; font-weight: 700; color: #28a745;">${formatCurrency(vente.montant_total, vente.devise)}</span>
                </div>
            </div>
        </div>
    `;
    
    content.innerHTML = detailsHTML;
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function fermerModalDetails() {
    const modal = document.getElementById('modal-details');
    modal.classList.remove('active');
    document.body.style.overflow = '';
}

async function exporterVentes() {
    const dateDebut = document.getElementById('filter-date-debut').value;
    const dateFin = document.getElementById('filter-date-fin').value;
    let url = '/api/export/ventes/excel?';
    if (dateDebut) url += `date_debut=${dateDebut}&`;
    if (dateFin) url += `date_fin=${dateFin}`;
    window.location.href = url;
}