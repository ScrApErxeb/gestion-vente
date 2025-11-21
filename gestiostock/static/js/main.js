// ===== GESTION DU SIDEBAR =====

// Toggle sidebar sur mobile
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('mobile-open');
}

// Fermer le sidebar si on clique en dehors sur mobile
document.addEventListener('click', function(event) {
    const sidebar = document.getElementById('sidebar');
    const toggleBtn = document.querySelector('.toggle-sidebar');
    
    if (window.innerWidth <= 768 && 
        !sidebar.contains(event.target) && 
        !toggleBtn.contains(event.target) &&
        sidebar.classList.contains('mobile-open')) {
        sidebar.classList.remove('mobile-open');
    }
});

// ===== FONCTIONS UTILITAIRES =====

// Formater les montants
function formatCurrency(amount, devise = 'XOF') {
    const symbols = {
        'XOF': 'F CFA',
        'EUR': '€',
        'USD': '$',
        'GBP': '£'
    };
    
    return new Intl.NumberFormat('fr-FR', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount) + ' ' + (symbols[devise] || devise);
}

// Formater les dates
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// ===== GESTION DES MODAUX =====

// Fonction pour afficher/masquer les modaux
function toggleModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal.style.display === 'block') {
        modal.style.display = 'none';
    } else {
        modal.style.display = 'block';
    }
}

// Fermer le modal en cliquant à l'extérieur
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = 'none';
    }
}

// Fermer le modal avec la touche Échap
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            modal.style.display = 'none';
        });
    }
});

// ===== GESTION DES NOTIFICATIONS =====

// Afficher les notifications

// Afficher le modal des notifications
function afficherModalNotifications(notifications) {
    // Créer le contenu du modal
    const modalContent = `
        <div class="modal-header">
            <h2>Notifications (${notifications.length})</h2>
            <span class="modal-close" onclick="toggleModal('notifications-modal')">&times;</span>
        </div>
        <div class="notifications-list">
            ${notifications.map(notif => `
                <div class="notification-item ${notif.lue ? 'lue' : 'non-lue'}" onclick="marquerNotificationLue(${notif.id})">
                    <div class="notification-icon">${getNotificationIcon(notif.type)}</div>
                    <div class="notification-content">
                        <div class="notification-title">${notif.titre}</div>
                        <div class="notification-message">${notif.message}</div>
                        <div class="notification-date">${formatDate(notif.date)}</div>
                    </div>
                    ${!notif.lue ? '<div class="notification-dot"></div>' : ''}
                </div>
            `).join('')}
            ${notifications.length === 0 ? '<div class="no-notifications">Aucune notification</div>' : ''}
        </div>
        ${notifications.length > 0 ? `
            <div class="modal-footer">
                <button class="btn btn-secondary" onclick="marquerToutesLues()">Marquer toutes comme lues</button>
                <button class="btn btn-danger" onclick="nettoyerNotifications()">Nettoyer les notifications</button>
            </div>
        ` : ''}
    `;
    
    // Créer ou mettre à jour le modal
    let modal = document.getElementById('notifications-modal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'notifications-modal';
        modal.className = 'modal';
        modal.innerHTML = `<div class="modal-content">${modalContent}</div>`;
        document.body.appendChild(modal);
    } else {
        modal.querySelector('.modal-content').innerHTML = modalContent;
    }
    
    toggleModal('notifications-modal');
}

// Obtenir l'icône selon le type de notification
function getNotificationIcon(type) {
    const icons = {
        'stock_faible': '⚠️',
        'vente': '🛒',
        'commande': '📋',
        'system': '⚙️',
        'default': '🔔'
    };
    return icons[type] || icons.default;
}

// Marquer une notification comme lue
async function marquerNotificationLue(notificationId) {
    try {
        const response = await fetch(`/api/notifications/${notificationId}/lire`, {
            method: 'POST'
        });
        
        if (response.ok) {
            // Recharger les notifications
            afficherNotifications();
        }
    } catch (error) {
        console.error('Erreur:', error);
    }
}

// Marquer toutes les notifications comme lues
async function marquerToutesLues() {
    try {
        const response = await fetch('/api/notifications/marquer-toutes-lues', {
            method: 'POST'
        });
        
        if (response.ok) {
            afficherNotifications();
            showAlert('Toutes les notifications ont été marquées comme lues', 'success');
        }
    } catch (error) {
        console.error('Erreur:', error);
        showAlert('Erreur lors du marquage des notifications', 'error');
    }
}

// Nettoyer les notifications
async function nettoyerNotifications() {
    try {
        const response = await fetch('/api/notifications/nettoyer', {
            method: 'POST'
        });
        
        if (response.ok) {
            afficherNotifications();
            showAlert('Notifications nettoyées avec succès', 'success');
        }
    } catch (error) {
        console.error('Erreur:', error);
        showAlert('Erreur lors du nettoyage des notifications', 'error');
    }
}

// ===== RECHERCHE GLOBALE =====

// Recherche globale
document.getElementById('global-search').addEventListener('input', function(e) {
    const searchTerm = e.target.value.toLowerCase().trim();
    
    if (searchTerm.length >= 2) {
        effectuerRecherche(searchTerm);
    }
});

// Effectuer la recherche
async function effectuerRecherche(term) {
    try {
        // Implémenter la logique de recherche selon la page actuelle
        const currentPage = window.location.pathname;
        
        // Exemple de recherche multi-pages
        const endpoints = {
            '/produits': '/api/produits',
            '/clients': '/api/clients',
            '/ventes': '/api/ventes',
            '/fournisseurs': '/api/fournisseurs'
        };
        
        const endpoint = endpoints[currentPage];
        if (endpoint) {
            const response = await fetch(`${endpoint}?search=${encodeURIComponent(term)}`);
            const results = await response.json();
            
            // Afficher les résultats (à adapter selon la page)
            console.log('Résultats de recherche:', results);
        }
        
    } catch (error) {
        console.error('Erreur recherche:', error);
    }
}

// ===== GESTION DES ALERTES =====

// Afficher une alerte

// function showAlert(message, type = 'info', duration = 5000) {
//     const alert = document.createElement('div');
//     alert.className = `alert alert-${type}`;
//     alert.innerHTML = `
//         <span class="alert-icon">${getAlertIcon(type)}</span>
//         <span class="alert-message">${message}</span>
//         <button class="alert-close" onclick="this.parentElement.remove()">&times;</button>
//     `;
    
//     // Styles pour l'alerte
//     alert.style.cssText = `
//         position: fixed;
//         top: 20px;
//         right: 20px;
//         z-index: 3000;
//         min-width: 300px;
//         max-width: 500px;
//         animation: slideInRight 0.3s;
//     `;
    
//     document.body.appendChild(alert);
    
//     // Auto-suppression après la durée
//     if (duration > 0) {
//         setTimeout(() => {
//             if (alert.parentElement) {
//                 alert.remove();
//             }
//         }, duration);
//     }
    
//     return alert;
// }

// Obtenir l'icône d'alerte
function getAlertIcon(type) {
    const icons = {
        'success': '✅',
        'error': '❌',
        'warning': '⚠️',
        'info': 'ℹ️'
    };
    return icons[type] || icons.info;
}

// ===== CHARGEMENT DES DONNÉES =====

// Fonction utilitaire pour les requêtes API
async function apiCall(endpoint, options = {}) {
    try {
        const response = await fetch(endpoint, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`Erreur ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Erreur API:', error);
        showAlert('Erreur de connexion au serveur', 'error');
        throw error;
    }
}

// ===== INITIALISATION =====

// Charger le nombre de notifications au chargement


// Exposer les fonctions globales
window.toggleSidebar = toggleSidebar;
window.toggleModal = toggleModal;
// window.afficherNotifications = afficherNotifications;
window.marquerNotificationLue = marquerNotificationLue;
window.marquerToutesLues = marquerToutesLues;
window.nettoyerNotifications = nettoyerNotifications;
window.formatCurrency = formatCurrency;
window.formatDate = formatDate;
// window.showAlert = showAlert;
window.apiCall = apiCall;