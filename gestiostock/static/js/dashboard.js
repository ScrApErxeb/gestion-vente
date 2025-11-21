// gestiostock/static/js/dashboard.js
console.log('🚀 dashboard.js chargé !');

let chartVentes;

async function loadDashboard() {
    try {
        console.log('🔄 Chargement des données du dashboard...');
        
        const response = await fetch('/api/dashboard');
        
        if (!response.ok) {
            throw new Error(`Erreur HTTP: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('📊 Données reçues:', data);
        
        // Mettre à jour l'interface
        updateDashboard(data);
        
    } catch (error) {
        console.error('❌ Erreur:', error);
        showError('Impossible de charger les données: ' + error.message);
    }
}

function updateDashboard(data) {
    console.log('🔄 Mise à jour de l\'interface...');
    
    // Ventes
    updateElement('ventes-jour', formatCurrency(data.ventes.jour, data.devise));
    updateElement('ventes-mois', formatCurrency(data.ventes.mois, data.devise));
    updateElement('ventes-annee', formatCurrency(data.ventes.annee, data.devise));
    
    // Statistiques
    updateElement('nb-categories', data.stats_globales.categories);
    updateElement('nb-produits', data.produits.total);
    updateElement('nb-clients', data.clients.total);
    updateElement('stock-faible', data.produits.stock_faible);
    updateElement('nouveaux-clients', data.clients.nouveaux);
    updateElement('nb-fournisseurs', data.stats_globales.fournisseurs);
    
    // Commandes
    updateElement('commandes-en-cours', data.commandes.en_cours);
    updateElement('montant-commandes', formatCurrency(data.commandes.montant_en_cours, data.devise));
    
    // Top produits
    updateTopProduits(data.produits.top_ventes, data.devise);
    
    // Graphique
    updateChart(data.ventes.mensuelles, data.devise);
    
    console.log('✅ Interface mise à jour !');
}

function updateElement(id, value) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = value;
        console.log(`✅ ${id} = ${value}`);
    } else {
        console.warn(`❌ Élément #${id} non trouvé`);
    }
}

function updateTopProduits(topProduits, devise) {
    const container = document.getElementById('top-produits-list');
    if (!container) {
        console.warn('❌ Conteneur top-produits-list non trouvé');
        return;
    }

    const produits = topProduits.slice(0, 5);
    
    if (produits.length === 0) {
        container.innerHTML = '<div style="padding: 20px; text-align: center; color: #7f8c8d;">Aucun produit vendu</div>';
        console.log('ℹ️ Aucun top produit à afficher');
        return;
    }

    container.innerHTML = produits.map((p, i) => `
        <div style="padding: 12px; margin-bottom: 10px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #1abc9c;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div style="font-weight: 600; color: #2c3e50;">${i + 1}. ${p.nom}</div>
                    <div style="font-size: 12px; color: #7f8c8d;">Quantité: ${p.quantite}</div>
                </div>
                <div style="font-weight: 600; color: #1abc9c;">${formatCurrency(p.ca, devise)}</div>
            </div>
        </div>
    `).join('');
    
    console.log(`✅ ${produits.length} top produits affichés`);
}

function updateChart(ventesMensuelles, devise) {
    const ctx = document.getElementById('chart-ventes-mensuelles');
    if (!ctx) {
        console.warn('❌ Canvas chart-ventes-mensuelles non trouvé');
        return;
    }

    if (chartVentes) {
        chartVentes.destroy();
    }

    chartVentes = new Chart(ctx.getContext('2d'), {
        type: 'line',
        data: {
            labels: ventesMensuelles.map(v => v.mois),
            datasets: [{
                label: 'Ventes',
                data: ventesMensuelles.map(v => v.montant),
                borderColor: '#1abc9c',
                backgroundColor: 'rgba(26, 188, 156, 0.1)',
                tension: 0.4,
                fill: true,
                borderWidth: 3
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return formatCurrency(value, devise);
                        }
                    }
                }
            }
        }
    });
    
    console.log('✅ Graphique des ventes créé');
}

function formatCurrency(amount, currency = 'F CFA') {
    if (!amount) amount = 0;
    return new Intl.NumberFormat('fr-FR').format(amount) + ' ' + currency;
}

function showError(message) {
    console.error('❌ Erreur dashboard:', message);
    // Créer une alerte visible
    const alert = document.createElement('div');
    alert.style.cssText = `
        background: #f8d7da;
        color: #721c24;
        padding: 15px;
        border-radius: 8px;
        margin: 15px 0;
        border: 1px solid #f5c6cb;
    `;
    alert.innerHTML = `<strong>Erreur:</strong> ${message}`;
    document.querySelector('.header').after(alert);
}

// Initialisation
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Dashboard initialisé - DOM prêt');
    loadDashboard();
    setInterval(loadDashboard, 30000);
});

console.log('📝 dashboard.js entièrement chargé');