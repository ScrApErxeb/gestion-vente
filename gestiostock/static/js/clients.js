// ===== GESTION DES CLIENTS =====

class ClientsManager {
    constructor() {
        this.clients = [];
        this.searchTimeout = null;
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadClients();
    }

    bindEvents() {
        // Recherche avec debounce
        document.getElementById('search-client').addEventListener('input', (e) => {
            clearTimeout(this.searchTimeout);
            this.searchTimeout = setTimeout(() => {
                this.loadClients();
            }, 500);
        });

        // Réinitialisation du formulaire à la fermeture du modal
        document.getElementById('modal-client').addEventListener('click', (e) => {
            if (e.target.id === 'modal-client') {
                this.resetForm();
            }
        });

        // Changement de type de client
        document.getElementById('client-type').addEventListener('change', (e) => {
            this.toggleEntrepriseField(e.target.value === 'professionnel');
        });
    }

    // Charger la liste des clients
    async loadClients() {
        try {
            this.showLoading();
            
            const search = document.getElementById('search-client').value;
            const type = document.getElementById('filter-type-client').value;
            
            let url = '/api/clients?';
            if (search) url += `search=${encodeURIComponent(search)}&`;
            if (type) url += `type=${type}&`;
            
            const response = await fetch(url);
            if (!response.ok) throw new Error('Erreur de chargement');
            
            this.clients = await response.json();
            this.displayClients();
            this.calculateStats();
            
        } catch (error) {
            console.error('Erreur:', error);
            this.showError('Erreur lors du chargement des clients');
        }
    }

    // Afficher les clients dans le tableau
    displayClients() {
        const tbody = document.querySelector('#clients-table tbody');
        
        if (this.clients.length === 0) {
            tbody.innerHTML = this.getEmptyState();
            return;
        }

        tbody.innerHTML = this.clients.map(client => this.getClientRow(client)).join('');
    }

    // Générer une ligne de client
    getClientRow(client) {
        const typeClass = client.type_client === 'professionnel' ? 'client-type-professionnel' : 'client-type-particulier';
        const typeText = client.type_client === 'professionnel' ? '🏢 Pro' : '👤 Particulier';
        
        return `
            <tr>
                <td>
                    <div class="client-info">
                        <span class="client-name">${this.escapeHtml(client.nom)} ${this.escapeHtml(client.prenom || '')}</span>
                        ${client.entreprise ? `<span class="client-entreprise">${this.escapeHtml(client.entreprise)}</span>` : ''}
                    </div>
                </td>
                <td>
                    <div class="client-contact">
                        ${client.email ? `<span class="client-contact-email">📧 ${this.escapeHtml(client.email)}</span>` : '<span style="color: #95a5a6;">📧 -</span>'}
                        <span class="client-contact-phone">📞 ${this.escapeHtml(client.telephone)}</span>
                    </div>
                </td>
                <td>
                    <span class="client-type-badge ${typeClass}">
                        ${typeText}
                    </span>
                </td>
                <td>${this.escapeHtml(client.ville || '-')}</td>
                <td><strong>${formatCurrency(client.total_achats || 0)}</strong></td>
                <td>${client.nombre_achats || 0}</td>
                <td>
                    <div class="client-actions">
                        <button class="btn btn-secondary btn-sm" onclick="clientsManager.editClient(${client.id})" title="Modifier">
                            ✏️
                        </button>
                        <button class="btn btn-primary btn-sm" onclick="clientsManager.viewHistory(${client.id})" title="Historique">
                            📊
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }

    // État vide
    getEmptyState() {
        return `
            <tr>
                <td colspan="7">
                    <div class="clients-empty">
                        <div class="clients-empty-icon">👥</div>
                        <div class="clients-empty-text">Aucun client trouvé</div>
                        <div class="clients-empty-subtext">
                            ${document.getElementById('search-client').value ? 
                              'Essayez de modifier vos critères de recherche' : 
                              'Commencez par ajouter votre premier client'}
                        </div>
                        ${!document.getElementById('search-client').value ? `
                            <button class="btn btn-primary" onclick="toggleModal('modal-client')" style="margin-top: 15px;">
                                ➕ Ajouter un client
                            </button>
                        ` : ''}
                    </div>
                </td>
            </tr>
        `;
    }

    // Calculer les statistiques
    calculateStats() {
        const total = this.clients.length;
        const particuliers = this.clients.filter(c => c.type_client === 'particulier').length;
        const professionnels = this.clients.filter(c => c.type_client === 'professionnel').length;

        document.getElementById('total-clients').textContent = total;
        document.getElementById('clients-particuliers').textContent = particuliers;
        document.getElementById('clients-pro').textContent = professionnels;
    }

    // Sauvegarder un client
    async saveClient(event) {
        event.preventDefault();
        
        const form = event.target;
        const formData = new FormData(form);
        const data = Object.fromEntries(formData);
        
        // Conversion des nombres
        ['remise_defaut', 'plafond_credit'].forEach(key => {
            if (data[key]) data[key] = parseFloat(data[key]);
        });

        const id = document.getElementById('client-id').value;
        const method = id ? 'PUT' : 'POST';
        const url = id ? `/api/clients/${id}` : '/api/clients';
        
        try {
            const response = await fetch(url, {
                method: method,
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            
            if (response.ok) {
                toggleModal('modal-client');
                this.resetForm();
                this.loadClients();
                showAlert('✅ Client enregistré avec succès!', 'success');
            } else {
                const error = await response.json();
                throw new Error(error.error || 'Erreur inconnue');
            }
        } catch (error) {
            console.error('Erreur:', error);
            showAlert(`❌ Erreur: ${error.message}`, 'error');
        }
    }

    // Éditer un client
    editClient(id) {
        const client = this.clients.find(c => c.id === id);
        if (!client) return;

        document.getElementById('modal-client-title').textContent = 'Modifier le client';
        document.getElementById('client-id').value = client.id;
        document.getElementById('client-nom').value = client.nom;
        document.getElementById('client-prenom').value = client.prenom || '';
        document.getElementById('client-entreprise').value = client.entreprise || '';
        document.getElementById('client-email').value = client.email || '';
        document.getElementById('client-telephone').value = client.telephone;
        document.getElementById('client-adresse').value = client.adresse || '';
        document.getElementById('client-ville').value = client.ville || '';
        document.getElementById('client-pays').value = client.pays || 'Burkina Faso';
        document.getElementById('client-type').value = client.type_client;
        document.getElementById('client-remise').value = client.remise_defaut || 0;
        document.getElementById('client-plafond').value = client.plafond_credit || 0;
        document.getElementById('client-notes').value = client.notes || '';

        this.toggleEntrepriseField(client.type_client === 'professionnel');
        toggleModal('modal-client');
    }

    // Voir l'historique
    viewHistory(clientId) {
        // Implémenter l'affichage de l'historique
        showAlert(`Historique du client #${clientId} - Fonctionnalité à implémenter`, 'info');
    }

    // Filtrer les clients
    filtrerClients() {
        this.loadClients();
    }

    // Réinitialiser le formulaire
    resetForm() {
        document.getElementById('form-client').reset();
        document.getElementById('modal-client-title').textContent = 'Nouveau Client';
        document.getElementById('client-id').value = '';
        document.getElementById('client-ville').value = 'Ouagadougou';
        document.getElementById('client-pays').value = 'Burkina Faso';
        this.toggleEntrepriseField(false);
    }

    // Afficher/masquer le champ entreprise
    toggleEntrepriseField(show) {
        const entrepriseField = document.getElementById('client-entreprise').closest('.form-group');
        entrepriseField.style.display = show ? 'block' : 'none';
    }

    // Échapper le HTML pour la sécurité
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // État de chargement
    showLoading() {
        const tbody = document.querySelector('#clients-table tbody');
        tbody.innerHTML = `
            <tr>
                <td colspan="7">
                    <div class="clients-loading">Chargement des clients...</div>
                </td>
            </tr>
        `;
    }

    // Afficher une erreur
    showError(message) {
        const tbody = document.querySelector('#clients-table tbody');
        tbody.innerHTML = `
            <tr>
                <td colspan="7">
                    <div class="alert alert-error">
                        ❌ ${message}
                        <button class="btn btn-primary btn-sm" onclick="clientsManager.loadClients()" style="margin-left: 10px;">
                            Réessayer
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }
}

// ===== INITIALISATION =====

let clientsManager;

document.addEventListener('DOMContentLoaded', function() {
    clientsManager = new ClientsManager();
});

// Exposer les fonctions globales
window.filtrerClients = () => clientsManager.filtrerClients();
window.saveClient = (e) => clientsManager.saveClient(e);
window.editClient = (id) => clientsManager.editClient(id);
window.voirHistorique = (id) => clientsManager.viewHistory(id);