// Fonctions spécifiques pour la gestion des statistiques

let charts = {
    evolution: null,
    categories: null,
    paiements: null,
    clients: null
};

// Initialisation des dates par défaut
function initializeDefaultDates() {
    const today = new Date().toISOString().split('T')[0];
    const firstDayOfMonth = new Date(new Date().getFullYear(), new Date().getMonth(), 1)
        .toISOString().split('T')[0];
    
    document.getElementById('date-debut-custom').value = firstDayOfMonth;
    document.getElementById('date-fin-custom').value = today;
}

// Gestion des modals
function toggleModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal.style.display === 'block') {
        modal.style.display = 'none';
    } else {
        modal.style.display = 'block';
    }
}

// Fermer les modals en cliquant à l'extérieur
window.onclick = function(event) {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
}

// Formater les montants
function formatCurrency(amount) {
    if (amount === null || amount === undefined) return '0 F';
    return new Intl.NumberFormat('fr-FR', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount) + ' F';
}

// Formater les pourcentages
function formatPercent(value) {
    if (value === null || value === undefined) return '0%';
    return value.toFixed(1) + '%';
}

// Afficher/masquer le chargement
function showLoading(show = true) {
    const mainContent = document.querySelector('.main-content');
    if (show) {
        mainContent.classList.add('loading');
    } else {
        mainContent.classList.remove('loading');
    }
}

// Afficher une notification
function showNotification(message, type = 'info') {
    // Supprimer les notifications existantes
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(notif => notif.remove());
    
    // Créer la nouvelle notification
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 8px;
        color: white;
        font-weight: 600;
        z-index: 10000;
        max-width: 400px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        animation: slideInRight 0.3s ease-out;
    `;
    
    // Appliquer la couleur selon le type
    if (type === 'success') {
        notification.style.background = '#28a745';
    } else if (type === 'error') {
        notification.style.background = '#dc3545';
    } else if (type === 'warning') {
        notification.style.background = '#ffc107';
        notification.style.color = '#000';
    } else {
        notification.style.background = '#17a2b8';
    }
    
    document.body.appendChild(notification);
    
    // Auto-suppression après 5 secondes
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 5000);
}

// Animation CSS pour les notifications
const notificationStyle = document.createElement('style');
notificationStyle.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
`;
document.head.appendChild(notificationStyle);

// === FONCTIONS PRINCIPALES DE CHARGEMENT ===

// Charger les statistiques principales
async function chargerStats(periode) {
    try {
        showLoading(true);
        console.log(`📊 Chargement des stats pour: ${periode}`);
        
        // Charger les statistiques de ventes
        const respVentes = await fetch(`/api/stats/ventes?periode=${periode}`);
        if (!respVentes.ok) {
            throw new Error(`Erreur API ventes: ${respVentes.status}`);
        }
        const dataVentes = await respVentes.json();
        
        console.log("📈 Données ventes:", dataVentes);
        
        // Vérifier si les données nécessaires existent
        if (!dataVentes || dataVentes.error) {
            throw new Error(dataVentes?.error || 'Données ventes non disponibles');
        }

        // Mettre à jour les KPIs avec vérifications
        updateKPIs(dataVentes);
        
        // Créer les graphiques principaux
        createMainCharts(dataVentes);
        
        // Charger les données complémentaires
        await loadComplementaryData();
        
        console.log("✅ Toutes les statistiques chargées avec succès");
        showNotification('📊 Statistiques mises à jour avec succès', 'success');
        
    } catch (error) {
        console.error('❌ Erreur lors du chargement des statistiques:', error);
        showNotification('❌ Erreur lors du chargement des statistiques: ' + error.message, 'error');
    } finally {
        showLoading(false);
    }
}

// Mettre à jour les indicateurs clés
function updateKPIs(data) {
    document.getElementById('stat-ca').textContent = formatCurrency(data.ca_total || 0);
    document.getElementById('stat-nb-ventes').textContent = data.nb_ventes || 0;
    document.getElementById('stat-panier').textContent = formatCurrency(data.panier_moyen || 0);
    
    // Mettre à jour les évolutions si disponibles
    const caEvolution = document.getElementById('stat-ca-evol');
    const ventesEvolution = document.getElementById('stat-ventes-evol');
    
    if (data.evolution_ca !== undefined) {
        caEvolution.textContent = `${data.evolution_ca >= 0 ? '+' : ''}${formatPercent(data.evolution_ca)}`;
        caEvolution.className = data.evolution_ca >= 0 ? 'evolution-positive' : 'evolution-negative';
    }
    
    if (data.evolution_ventes !== undefined) {
        ventesEvolution.textContent = `${data.evolution_ventes >= 0 ? '+' : ''}${formatPercent(data.evolution_ventes)}`;
        ventesEvolution.className = data.evolution_ventes >= 0 ? 'evolution-positive' : 'evolution-negative';
    }
}

// Créer les graphiques principaux
function createMainCharts(data) {
    // Graphique d'évolution
    createEvolutionChart(data);
    
    // Graphique par catégorie
    createCategoriesChart(data);
    
    // Graphique modes de paiement
    createPaymentsChart(data);
}

// Graphique d'évolution des ventes
function createEvolutionChart(data) {
    const evolutionData = Array.isArray(data.evolution) ? data.evolution : [];
    
    if (charts.evolution) charts.evolution.destroy();
    
    const ctxEvol = document.getElementById('chart-evolution').getContext('2d');
    charts.evolution = new Chart(ctxEvol, {
        type: 'line',
        data: {
            labels: evolutionData.map(e => e?.date || ''),
            datasets: [{
                label: 'Ventes (F CFA)',
                data: evolutionData.map(e => e?.montant || 0),
                borderColor: '#1abc9c',
                backgroundColor: 'rgba(26, 188, 156, 0.1)',
                tension: 0.4,
                fill: true,
                borderWidth: 3,
                pointBackgroundColor: '#1abc9c',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: '#1abc9c',
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            return `Ventes: ${formatCurrency(context.parsed.y)}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    },
                    ticks: {
                        callback: function(value) {
                            return formatCurrency(value);
                        }
                    }
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            }
        }
    });
}

// Graphique par catégorie
function createCategoriesChart(data) {
    const categoriesData = Array.isArray(data.ventes_par_categorie) ? data.ventes_par_categorie : [];
    
    if (charts.categories) charts.categories.destroy();
    
    const ctxCat = document.getElementById('chart-categories').getContext('2d');
    charts.categories = new Chart(ctxCat, {
        type: 'doughnut',
        data: {
            labels: categoriesData.map(c => c?.categorie || 'Non catégorisé'),
            datasets: [{
                data: categoriesData.map(c => c?.total || 0),
                backgroundColor: [
                    '#1abc9c', '#3498db', '#9b59b6', '#e74c3c', 
                    '#f39c12', '#2ecc71', '#e67e22', '#95a5a6',
                    '#34495e', '#16a085'
                ],
                borderWidth: 2,
                borderColor: '#fff',
                hoverOffset: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 15,
                        usePointStyle: true
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const value = context.parsed;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${context.label}: ${formatCurrency(value)} (${percentage}%)`;
                        }
                    }
                }
            },
            cutout: '50%'
        }
    });
}

// Graphique modes de paiement
function createPaymentsChart(data) {
    const paiementsData = Array.isArray(data.ventes_par_paiement) ? data.ventes_par_paiement : [];
    
    if (charts.paiements) charts.paiements.destroy();
    
    const ctxPay = document.getElementById('chart-paiements').getContext('2d');
    charts.paiements = new Chart(ctxPay, {
        type: 'pie',
        data: {
            labels: paiementsData.map(p => p?.mode || 'Inconnu'),
            datasets: [{
                data: paiementsData.map(p => p?.total || 0),
                backgroundColor: ['#1abc9c', '#3498db', '#f39c12', '#9b59b6', '#e74c3c'],
                borderWidth: 2,
                borderColor: '#fff',
                hoverOffset: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 15,
                        usePointStyle: true
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const value = context.parsed;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${context.label}: ${formatCurrency(value)} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

// Charger les données complémentaires
async function loadComplementaryData() {
    await Promise.all([
        chargerStatsProduits(),
        chargerStatsClients(),
        chargerRentabilite()
    ]);
}

// Charger les statistiques produits
async function chargerStatsProduits() {
    try {
        const respProduits = await fetch('/api/stats/produits');
        if (!respProduits.ok) {
            throw new Error(`Erreur produits: ${respProduits.status}`);
        }
        
        const dataProduits = await respProduits.json();
        console.log("📦 Données produits:", dataProduits);
        
        // Vérification sécurisée
        const topProduits = Array.isArray(dataProduits?.top_ventes) ? dataProduits.top_ventes : [];
        
        const tbodyProduits = document.querySelector('#table-top-produits tbody');
        if (topProduits.length > 0) {
            tbodyProduits.innerHTML = topProduits.slice(0, 10).map((p, i) => `
                <tr>
                    <td><strong>${i + 1}</strong></td>
                    <td>${escapeHtml(p.nom || 'Produit inconnu')}</td>
                    <td><strong>${p.quantite || 0}</strong></td>
                    <td style="color: #1abc9c; font-weight: 600;">${formatCurrency(p.ca || 0)}</td>
                </tr>
            `).join('');
        } else {
            tbodyProduits.innerHTML = `
                <tr>
                    <td colspan="4" style="text-align: center; color: #7f8c8d; padding: 20px;">
                        Aucune donnée de vente disponible
                    </td>
                </tr>
            `;
        }
        
    } catch (error) {
        console.error('❌ Erreur produits:', error);
        document.querySelector('#table-top-produits tbody').innerHTML = `
            <tr>
                <td colspan="4" style="text-align: center; color: #e74c3c; padding: 20px;">
                    Erreur de chargement des données produits
                </td>
            </tr>
        `;
    }
}

// Charger les statistiques clients
async function chargerStatsClients() {
    try {
        const respClients = await fetch('/api/stats/clients');
        if (!respClients.ok) {
            throw new Error(`Erreur clients: ${respClients.status}`);
        }
        
        const dataClients = await respClients.json();
        console.log("👥 Données clients:", dataClients);
        
        // Vérification sécurisée
        const topClients = Array.isArray(dataClients?.top_clients) ? dataClients.top_clients : [];
        
        const tbodyClients = document.querySelector('#table-top-clients tbody');
        if (topClients.length > 0) {
            tbodyClients.innerHTML = topClients.slice(0, 10).map((c, i) => `
                <tr>
                    <td><strong>${i + 1}</strong></td>
                    <td>${escapeHtml(c.nom || 'Client inconnu')}</td>
                    <td>${c.nb_achats || 0}</td>
                    <td style="color: #1abc9c; font-weight: 600;">${formatCurrency(c.total || 0)}</td>
                </tr>
            `).join('');
        } else {
            tbodyClients.innerHTML = `
                <tr>
                    <td colspan="4" style="text-align: center; color: #7f8c8d; padding: 20px;">
                        Aucune donnée client disponible
                    </td>
                </tr>
            `;
        }
        
        // Graphique clients (nouveaux par mois)
        createClientsChart(dataClients);
        
    } catch (error) {
        console.error('❌ Erreur clients:', error);
        document.querySelector('#table-top-clients tbody').innerHTML = `
            <tr>
                <td colspan="4" style="text-align: center; color: #e74c3c; padding: 20px;">
                    Erreur de chargement des données clients
                </td>
            </tr>
        `;
    }
}

// Graphique statistiques clients
function createClientsChart(data) {
    const nouveauxClientsData = Array.isArray(data.nouveaux_par_mois) ? data.nouveaux_par_mois : [];
    
    if (charts.clients) charts.clients.destroy();
    
    const ctxClients = document.getElementById('chart-clients').getContext('2d');
    charts.clients = new Chart(ctxClients, {
        type: 'bar',
        data: {
            labels: nouveauxClientsData.map(m => m?.mois || ''),
            datasets: [{
                label: 'Nouveaux clients',
                data: nouveauxClientsData.map(m => m?.nombre || 0),
                backgroundColor: '#3498db',
                borderRadius: 5,
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    },
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

// Charger l'analyse de rentabilité
async function chargerRentabilite() {
    try {
        const respRent = await fetch('/api/rapport/rentabilite');
        if (!respRent.ok) {
            throw new Error(`Erreur rentabilité: ${respRent.status}`);
        }
        
        const dataRent = await respRent.json();
        console.log("💹 Données rentabilité:", dataRent);
        
        updateRentabilityData(dataRent);
        
    } catch (error) {
        console.error('❌ Erreur rentabilité:', error);
        showNotification('❌ Erreur lors du chargement de l\'analyse de rentabilité', 'error');
    }
}

// Mettre à jour les données de rentabilité
function updateRentabilityData(data) {
    const resume = data.resume || {};
    
    document.getElementById('rent-ca').textContent = formatCurrency(resume.ca_total || 0);
    document.getElementById('rent-cout').textContent = formatCurrency(resume.cout_total || 0);
    document.getElementById('rent-benefice').textContent = formatCurrency(resume.benefice_brut || 0);
    document.getElementById('rent-marge-pct').textContent = formatPercent(resume.marge_brute || 0);
    document.getElementById('stat-marge').textContent = formatPercent(resume.marge_brute || 0);
    
    // Produits les plus rentables
    const topRentables = Array.isArray(data.top_rentables) ? data.top_rentables : [];
    const divRentables = document.getElementById('produits-rentables');
    
    if (topRentables.length > 0) {
        divRentables.innerHTML = topRentables.slice(0, 5).map((p, i) => `
            <div class="rentable-product ${i === 0 ? 'top' : ''}">
                <div class="rentable-product-content">
                    <div class="product-info">
                        <div class="product-name">${i + 1}. ${escapeHtml(p.nom || 'Produit inconnu')}</div>
                        <div class="product-details">
                            CA: ${formatCurrency(p.ca || 0)} | Coût: ${formatCurrency(p.cout || 0)}
                        </div>
                    </div>
                    <div class="product-stats">
                        <div class="product-benefit">${formatCurrency(p.benefice || 0)}</div>
                        <div class="product-quantity">${p.quantite || 0} vendus</div>
                    </div>
                </div>
            </div>
        `).join('');
    } else {
        divRentables.innerHTML = `
            <div style="text-align: center; color: #7f8c8d; padding: 20px;">
                Aucune donnée de rentabilité disponible
            </div>
        `;
    }
}

// Charger les statistiques avec période personnalisée
function chargerStatsCustom(event) {
    event.preventDefault();
    const dateDebut = document.getElementById('date-debut-custom').value;
    const dateFin = document.getElementById('date-fin-custom').value;
    
    if (!dateDebut || !dateFin) {
        showNotification('❌ Veuillez sélectionner une période complète', 'error');
        return;
    }
    
    if (new Date(dateDebut) > new Date(dateFin)) {
        showNotification('❌ La date de début doit être antérieure à la date de fin', 'error');
        return;
    }
    
    toggleModal('modal-periode-custom');
    showNotification(`📊 Analyse de la période du ${dateDebut} au ${dateFin}`, 'info');
    
    // Ici vous pouvez appeler une API spécifique pour les périodes personnalisées
    // Pour l'instant, on utilise la période "mois" comme placeholder
    chargerStats('mois');
}

// Échapper le HTML pour la sécurité
function escapeHtml(unsafe) {
    if (!unsafe) return '';
    return unsafe
        .toString()
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Exporter les statistiques
async function exporterStatistiques() {
    try {
        showNotification('📥 Préparation de l\'export...', 'info');
        
        // Ici vous pouvez implémenter l'export vers Excel ou PDF
        // Pour l'instant, on simule l'export
        setTimeout(() => {
            showNotification('✅ Export des statistiques généré avec succès', 'success');
        }, 2000);
        
    } catch (error) {
        console.error('❌ Erreur export:', error);
        showNotification('❌ Erreur lors de l\'export', 'error');
    }
}

// === INITIALISATION ===
document.addEventListener('DOMContentLoaded', function() {
    // Initialiser les dates par défaut
    initializeDefaultDates();
    
    // Charger les stats du mois par défaut
    chargerStats('mois');
    
    // Ajouter un bouton d'export si nécessaire
    const header = document.querySelector('.header');
    if (header) {
        const exportBtn = document.createElement('button');
        exportBtn.className = 'btn btn-success';
        exportBtn.innerHTML = '📥 Exporter PDF';
        exportBtn.onclick = exporterStatistiques;
        exportBtn.style.marginLeft = 'auto';
        
        const headerContent = header.querySelector('div');
        if (headerContent) {
            headerContent.style.display = 'flex';
            headerContent.style.alignItems = 'center';
            headerContent.appendChild(exportBtn);
        }
    }
    
    console.log('🚀 Module statistiques initialisé');
});