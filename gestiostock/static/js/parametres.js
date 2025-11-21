// Fonctions spécifiques pour la gestion des paramètres

let categories = [];
let users = [];

// Gestion des modals
function toggleModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal.style.display === 'block') {
        modal.style.display = 'none';
        resetForm(modalId);
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
            resetForm(modal.id);
        }
    });
}

// Réinitialiser les formulaires
function resetForm(modalId) {
    const forms = {
        'modal-categorie': 'form-categorie',
        'modal-utilisateur': 'form-utilisateur'
    };
    
    const formId = forms[modalId];
    if (formId) {
        const form = document.getElementById(formId);
        if (form) {
            form.reset();
            // Réinitialiser les titres des modals
            if (modalId === 'modal-categorie') {
                document.querySelector('#modal-categorie .modal-header h2').textContent = 'Nouvelle Catégorie';
            } else if (modalId === 'modal-utilisateur') {
                document.querySelector('#modal-utilisateur .modal-header h2').textContent = 'Nouvel Utilisateur';
            }
        }
    }
}

// === GESTION DES CATÉGORIES ===

// Charger les catégories
async function loadCategories() {
    try {
        showLoading('categories-list', true);
        
        const response = await fetch('/api/categories');
        if (!response.ok) {
            throw new Error('Erreur lors du chargement des catégories');
        }
        
        categories = await response.json();
        afficherCategories(categories);
    } catch (error) {
        console.error('Erreur:', error);
        showNotification('❌ Erreur lors du chargement des catégories', 'error');
    } finally {
        showLoading('categories-list', false);
    }
}

// Afficher les catégories
function afficherCategories(data) {
    const container = document.getElementById('categories-list');
    
    if (data.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="icon">📂</div>
                <h3>Aucune catégorie</h3>
                <p>Créez votre première catégorie pour organiser vos produits</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = data.map(cat => `
        <div class="list-item">
            <div class="list-item-content">
                <strong>${escapeHtml(cat.nom)}</strong>
                <div style="font-size: 12px; color: #7f8c8d;">
                    ${cat.description || 'Aucune description'}
                    <span style="margin-left: 10px;">(${cat.nb_produits || 0} produits)</span>
                </div>
            </div>
            <div class="list-item-actions">
                <button class="btn btn-secondary btn-sm" onclick="editCategorie(${cat.id})" title="Modifier">
                    ✏️
                </button>
                <button class="btn btn-danger btn-sm" onclick="deleteCategorie(${cat.id})" title="Supprimer">
                    🗑️
                </button>
            </div>
        </div>
    `).join('');
}

// Sauvegarder une catégorie
async function saveCategorie(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);
    
    // Validation
    if (!data.nom) {
        showNotification('❌ Le nom de la catégorie est obligatoire', 'error');
        return;
    }
    
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = 'Enregistrement...';
    submitBtn.disabled = true;
    
    try {
        const response = await fetch('/api/categories', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            toggleModal('modal-categorie');
            loadCategories();
            showNotification('✅ Catégorie enregistrée avec succès!', 'success');
        } else {
            const error = await response.json();
            throw new Error(error.error || 'Erreur lors de l\'enregistrement');
        }
    } catch (error) {
        console.error('Erreur:', error);
        showNotification('❌ ' + error.message, 'error');
    } finally {
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    }
}

// Éditer une catégorie
async function editCategorie(id) {
    const categorie = categories.find(c => c.id === id);
    if (!categorie) return;
    
    document.querySelector('#modal-categorie .modal-header h2').textContent = 'Modifier la catégorie';
    document.getElementById('cat-nom').value = categorie.nom || '';
    document.getElementById('cat-description').value = categorie.description || '';
    
    // Stocker l'ID pour la mise à jour
    const form = document.getElementById('form-categorie');
    form.dataset.editId = id;
    
    toggleModal('modal-categorie');
}

// Supprimer une catégorie
async function deleteCategorie(id) {
    const categorie = categories.find(c => c.id === id);
    if (!categorie) return;
    
    if (categorie.nb_produits > 0) {
        showNotification(`❌ Impossible de supprimer: ${categorie.nb_produits} produits utilisent cette catégorie`, 'error');
        return;
    }
    
    if (!confirm(`Êtes-vous sûr de vouloir supprimer la catégorie "${categorie.nom}" ?`)) {
        return;
    }
    
    try {
        const response = await fetch(`/api/categories/${id}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            loadCategories();
            showNotification('✅ Catégorie supprimée avec succès!', 'success');
        } else {
            throw new Error('Erreur lors de la suppression');
        }
    } catch (error) {
        console.error('Erreur:', error);
        showNotification('❌ Erreur lors de la suppression', 'error');
    }
}

// === GESTION DES UTILISATEURS ===

// Charger les utilisateurs
async function loadUsers() {
    try {
        const response = await fetch('/api/users');
        if (response.ok) {
            users = await response.json();
            afficherUsers(users);
        }
    } catch (error) {
        console.error('Erreur:', error);
        showNotification('❌ Erreur lors du chargement des utilisateurs', 'error');
    }
}

// Afficher les utilisateurs
function afficherUsers(data) {
    const container = document.getElementById('other-users');
    
    if (data.length === 0) {
        container.innerHTML = `
            <div class="empty-state" style="padding: 20px;">
                <div class="icon">👥</div>
                <p>Aucun autre utilisateur</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = data.map(user => `
        <div class="list-item">
            <div class="list-item-content">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <strong>${escapeHtml(user.prenom)} ${escapeHtml(user.nom)}</strong>
                    <span class="badge badge-${getRoleBadgeClass(user.role)}">${user.role.toUpperCase()}</span>
                    ${!user.actif ? '<span class="badge badge-danger">INACTIF</span>' : ''}
                </div>
                <div style="font-size: 12px; color: #7f8c8d;">
                    ${escapeHtml(user.email)} • ${user.telephone || 'Aucun téléphone'}
                </div>
            </div>
            <div class="list-item-actions">
                <button class="btn btn-secondary btn-sm" onclick="editUser(${user.id})" title="Modifier">
                    ✏️
                </button>
                <button class="btn btn-${user.actif ? 'warning' : 'success'} btn-sm" 
                        onclick="toggleUserStatus(${user.id}, ${user.actif})" 
                        title="${user.actif ? 'Désactiver' : 'Activer'}">
                    ${user.actif ? '🚫' : '✅'}
                </button>
            </div>
        </div>
    `).join('');
}

// Obtenir la classe du badge selon le rôle
function getRoleBadgeClass(role) {
    const classes = {
        'admin': 'danger',
        'manager': 'warning',
        'user': 'info'
    };
    return classes[role] || 'info';
}

// Basculer le statut d'un utilisateur
async function toggleUserStatus(userId, currentStatus) {
    const user = users.find(u => u.id === userId);
    if (!user) return;
    
    const action = currentStatus ? 'désactiver' : 'activer';
    
    if (!confirm(`Êtes-vous sûr de vouloir ${action} l'utilisateur "${user.prenom} ${user.nom}" ?`)) {
        return;
    }
    
    try {
        const response = await fetch(`/api/users/${userId}/toggle-status`, {
            method: 'POST'
        });
        
        if (response.ok) {
            loadUsers();
            showNotification(`✅ Utilisateur ${action} avec succès!`, 'success');
        } else {
            throw new Error('Erreur lors du changement de statut');
        }
    } catch (error) {
        console.error('Erreur:', error);
        showNotification('❌ Erreur lors du changement de statut', 'error');
    }
}

// === ACTIONS SYSTÈME ===

// Initialiser les actions système
function initializeSystemActions() {
    // Exporter toutes les données
    const exportBtn = document.getElementById('btn-export-all');
    if (exportBtn) {
        exportBtn.addEventListener('click', exporterToutesDonnees);
    }
    
    // Nettoyer les notifications
    const cleanNotificationsBtn = document.getElementById('btn-clean-notifications');
    if (cleanNotificationsBtn) {
        cleanNotificationsBtn.addEventListener('click', nettoyerNotifications);
    }
    
    // Réinitialiser la base de données
    const resetDbBtn = document.getElementById('btn-reset-db');
    if (resetDbBtn) {
        resetDbBtn.addEventListener('click', reinitialiserBaseDeDonnees);
    }
}

// Exporter toutes les données
async function exporterToutesDonnees() {
    const btn = document.getElementById('btn-export-all');
    
    try {
        const originalText = btn.innerHTML;
        btn.innerHTML = '⏳ Export en cours...';
        btn.disabled = true;
        
        addLog('🔄 Début de l\'export complet des données...');
        
        const response = await fetch('/api/export/all-data', {
            method: 'GET',
            headers: {'Content-Type': 'application/json'}
        });
        
        if (response.ok) {
            // Télécharger le fichier
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            
            // Récupérer le nom du fichier
            const contentDisposition = response.headers.get('Content-Disposition');
            let filename = 'export_complet.xlsx';
            if (contentDisposition) {
                const filenameMatch = contentDisposition.match(/filename="(.+)"/);
                if (filenameMatch) {
                    filename = filenameMatch[1];
                }
            }
            
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            addLog('✅ Export terminé: ' + filename);
            showNotification('✅ Export terminé avec succès!', 'success');
        } else {
            const error = await response.json();
            throw new Error(error.error || 'Erreur lors de l\'export');
        }
    } catch (error) {
        console.error('❌ Erreur:', error);
        addLog('❌ Erreur export: ' + error.message);
        showNotification('❌ Erreur lors de l\'export: ' + error.message, 'error');
    } finally {
        btn.innerHTML = '📥 Exporter toutes les données';
        btn.disabled = false;
    }
}

// Nettoyer les notifications
async function nettoyerNotifications() {
    if (!confirm('Supprimer toutes les notifications lues?')) return;
    
    const btn = document.getElementById('btn-clean-notifications');
    
    try {
        btn.disabled = true;
        const originalText = btn.innerHTML;
        btn.innerHTML = '⏳ Nettoyage...';
        
        addLog('🗑️ Nettoyage des notifications...');
        
        const response = await fetch('/api/notifications/nettoyer', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });
        
        if (response.ok) {
            const result = await response.json();
            addLog('✅ Notifications nettoyées: ' + result.message);
            showNotification(`🗑️ ${result.message}`, 'success');
        } else {
            const error = await response.json();
            throw new Error(error.error || 'Erreur lors du nettoyage');
        }
    } catch (error) {
        console.error('❌ Erreur:', error);
        addLog('❌ Erreur nettoyage: ' + error.message);
        showNotification('❌ Erreur: ' + error.message, 'error');
    } finally {
        btn.innerHTML = '🗑️ Nettoyer les notifications';
        btn.disabled = false;
    }
}

// Réinitialiser la base de données
async function reinitialiserBaseDeDonnees() {
    if (!confirm('⚠️ DANGER! Êtes-vous ABSOLUMENT sûr?\n\nCette action supprimera TOUTES les données et ne peut pas être annulée!')) {
        return;
    }
    
    if (!confirm('❌ CONFIRMATION FINALE: Toutes les données seront PERDUES!')) {
        return;
    }
    
    const btn = document.getElementById('btn-reset-db');
    
    try {
        btn.disabled = true;
        const originalText = btn.innerHTML;
        btn.innerHTML = '⏳ Réinitialisation...';
        
        addLog('⚠️ Début de la réinitialisation de la base de données...');
        
        const response = await fetch('/api/system/reset-database', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });
        
        if (response.ok) {
            const result = await response.json();
            addLog('✅ Base de données réinitialisée: ' + result.message);
            showNotification('✅ Base de données réinitialisée avec succès!', 'success');
            
            // Rediriger après réinitialisation
            setTimeout(() => {
                window.location.href = '/';
            }, 3000);
        } else {
            const error = await response.json();
            throw new Error(error.error || 'Erreur lors de la réinitialisation');
        }
    } catch (error) {
        console.error('❌ Erreur:', error);
        addLog('❌ Erreur réinitialisation: ' + error.message);
        showNotification('❌ Erreur: ' + error.message, 'error');
    } finally {
        btn.innerHTML = '⚠️ Réinitialiser la base de données';
        btn.disabled = false;
    }
}

// === CONTRÔLE SYSTÈME ===

// Mettre à jour le statut du système
async function refreshSystemStatus() {
    try {
        const response = await fetch('/api/system/status');
        const data = await response.json();
        
        const statusElement = document.getElementById('system-status');
        const infoElement = document.getElementById('system-info');
        
        if (data.status === 'running') {
            statusElement.innerHTML = '🟢 EN MARCHE';
            statusElement.className = 'status-indicator status-running';
        } else {
            statusElement.innerHTML = '🔴 ARRÊTÉ';
            statusElement.className = 'status-indicator status-stopped';
        }
        
        infoElement.innerHTML = `Version ${data.version} | Démarrage: ${data.started_at}`;
        
        addLog(`🔍 Statut système: ${data.status}`, 'info');
        
    } catch (error) {
        document.getElementById('system-status').innerHTML = '❌ HORS LIGNE';
        document.getElementById('system-status').className = 'status-indicator status-unknown';
        addLog('❌ Impossible de contacter le serveur', 'error');
    }
}

// Contrôler le système
async function controlSystem(action) {
    const actions = {
        'start': { text: 'démarrage', emoji: '▶️' },
        'stop': { text: 'arrêt', emoji: '⏹️' }, 
        'restart': { text: 'redémarrage', emoji: '🔄' }
    };
    
    addLog(`${actions[action].emoji} Tentative de ${actions[action].text} du système...`, 'info');
    
    // Désactiver les boutons temporairement
    const buttons = ['btn-start', 'btn-stop', 'btn-restart'];
    buttons.forEach(btnId => {
        const btn = document.getElementById(btnId);
        if (btn) btn.disabled = true;
    });
    
    try {
        const response = await fetch('/api/system/control', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ action: action })
        });
        
        const data = await response.json();
        
        if (data.success) {
            addLog(`✅ ${data.message}`, 'success');
            showNotification(data.message, 'success');
            
            // Mettre à jour le statut après un délai
            setTimeout(refreshSystemStatus, 2000);
        } else {
            addLog(`❌ Erreur: ${data.message}`, 'error');
            showNotification(data.message, 'error');
        }
        
    } catch (error) {
        addLog(`❌ Erreur réseau: ${error.message}`, 'error');
        showNotification('Erreur de communication avec le serveur', 'error');
    } finally {
        // Réactiver les boutons
        setTimeout(() => {
            buttons.forEach(btnId => {
                const btn = document.getElementById(btnId);
                if (btn) btn.disabled = false;
            });
        }, 3000);
    }
}

// Gestion des logs
function addLog(message, type = 'info') {
    const logsDiv = document.getElementById('system-logs');
    const timestamp = new Date().toLocaleTimeString();
    const logEntry = document.createElement('div');
    
    const typeClass = `log-${type}`;
    logEntry.innerHTML = `<span class="log-timestamp">[${timestamp}]</span> <span class="${typeClass}">${message}</span>`;
    
    logsDiv.appendChild(logEntry);
    logsDiv.scrollTop = logsDiv.scrollHeight;
}

function clearLogs() {
    document.getElementById('system-logs').innerHTML = '<div class="log-info">> Journal effacé...</div>';
    addLog('🗑️ Journal effacé par l\'utilisateur', 'info');
}

function exportLogs() {
    const logs = document.getElementById('system-logs').innerText;
    const blob = new Blob([logs], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `system-logs-${new Date().toISOString().split('T')[0]}.txt`;
    a.click();
    window.URL.revokeObjectURL(url);
    addLog('📥 Journal exporté', 'info');
}

// === FONCTIONS UTILITAIRES ===

// Afficher une notification
function showNotification(message, type = 'info') {
    // Supprimer les notifications existantes
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(notif => notif.remove());
    
    // Créer la nouvelle notification
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Auto-suppression après 5 secondes
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 5000);
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

// Afficher/masquer le chargement
function showLoading(elementId, show) {
    const element = document.getElementById(elementId);
    if (show) {
        element.classList.add('loading');
    } else {
        element.classList.remove('loading');
    }
}

// === INITIALISATION ===
document.addEventListener('DOMContentLoaded', function() {
    // Initialiser les données
    loadCategories();
    loadUsers();
    initializeSystemActions();
    
    // Initialiser le contrôle système
    refreshSystemStatus();
    
    // Actualiser le statut toutes les 30 secondes
    setInterval(refreshSystemStatus, 30000);
    
    // Premier log
    addLog('🚀 Module de contrôle système initialisé', 'info');
    
    // Gestion des formulaires de paramètres
    document.getElementById('form-entreprise').addEventListener('submit', (e) => {
        e.preventDefault();
        showNotification('✅ Informations entreprise enregistrées!', 'success');
    });
    
    document.getElementById('form-parametres').addEventListener('submit', (e) => {
        e.preventDefault();
        showNotification('✅ Paramètres généraux enregistrés!', 'success');
    });
});