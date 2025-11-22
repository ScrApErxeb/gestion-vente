// static/js/fournisseurs.js
class FournisseursManager {
    constructor() {
        this.fournisseurs = [];
        this.init();
    }

    async init() {
        console.log('🚀 Initialisation gestion fournisseurs...');
        await this.loadFournisseurs();
        this.bindEvents();
    }

    bindEvents() {
        // Recherche en temps réel
        document.getElementById('search-fournisseur')?.addEventListener('input', (e) => {
            clearTimeout(this.searchTimeout);
            this.searchTimeout = setTimeout(() => this.loadFournisseurs(), 500);
        });

        // Formulaire fournisseur
        document.getElementById('form-fournisseur').addEventListener('submit', (e) => this.saveFournisseur(e));
    }

    async loadFournisseurs() {
        try {
            this.showLoading(true);
            
            const search = document.getElementById('search-fournisseur')?.value;
            
            let url = '/api/fournisseurs?';
            if (search) url += `search=${encodeURIComponent(search)}&`;
            
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`Erreur HTTP: ${response.status}`);
            }
            
            this.fournisseurs = await response.json();
            this.afficherFournisseurs(this.fournisseurs);
            
        } catch (error) {
            console.error('❌ Erreur chargement fournisseurs:', error);
            this.showError('Impossible de charger les fournisseurs: ' + error.message);
        } finally {
            this.showLoading(false);
        }
    }

    afficherFournisseurs(fournisseurs) {
    const tbody = document.querySelector('#fournisseurs-table tbody');

    if (!fournisseurs || fournisseurs.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" style="text-align: center; padding: 40px; color: #7f8c8d;">
                    🏭 Aucun fournisseur trouvé
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = fournisseurs.map(f => `
        <tr>
            <td>
                <div style="font-weight: 600; color: #2c3e50;">${f.nom}</div>
                ${f.site_web ? `<div style="font-size: 11px; color: #7f8c8d;">🌐 ${f.site_web}</div>` : ''}
            </td>
            <td>
                ${f.contact ? `<div style="font-weight: 500;">${f.contact}</div>` : ''}
                <div style="font-size: 12px; color: #7f8c8d;">👤 Contact</div>
            </td>
            <td>
                <div style="display: flex; flex-direction: column; gap: 2px;">
                    ${f.telephone ? `<div style="display: flex; align-items: center; gap: 5px;">📞 ${f.telephone}</div>` : ''}
                    ${f.email ? `<div style="display: flex; align-items: center; gap: 5px;">📧 ${f.email}</div>` : ''}
                    ${f.adresse ? `<div style="display: flex; align-items: center; gap: 5px; font-size: 11px; color: #7f8c8d;">📍 ${f.adresse}</div>` : ''}
                </div>
            </td>
            
            
            <td>
                <div style="display: flex; gap: 5px;">
                    <button class="btn btn-secondary btn-sm" onclick="fournisseursManager.editFournisseur(${f.id})" title="Modifier">
                        ✏️
                    </button>
                    <button class="btn btn-primary btn-sm" onclick="fournisseursManager.voirCommandes(${f.id})" title="Commandes">
                        📋
                    </button>
                    <button class="btn btn-info btn-sm" onclick="fournisseursManager.voirDetails(${f.id})" title="Détails">
                        👁️
                    </button>
                    ${f.actif ? `
                    <button class="btn btn-danger btn-sm" onclick="fournisseursManager.desactiverFournisseur(${f.id})" title="Désactiver">
                        🚫
                    </button>
                    ` : `
                    <button class="btn btn-success btn-sm" onclick="fournisseursManager.activerFournisseur(${f.id})" title="Activer">
                        ✅
                    </button>
                    `}
                </div>
            </td>
        </tr>
    `).join('');

    console.log(`✅ ${fournisseurs.length} fournisseurs affichés`);
}


    async saveFournisseur(event) {
        event.preventDefault();
        
        const form = event.target;
        const formData = new FormData(form);
        const data = Object.fromEntries(formData);
        
        // Validation
        if (!data.nom || !data.telephone) {
            this.showError('Veuillez remplir les champs obligatoires (Nom et Téléphone)');
            return;
        }

        // Conversion des types
        if (data.delai_livraison) {
            data.delai_livraison = parseInt(data.delai_livraison);
        }

        // Nettoyage des données
        Object.keys(data).forEach(key => {
            if (data[key] === '' || data[key] === null) {
                delete data[key];
            }
        });

        const id = document.getElementById('fournisseur-id').value;
        const method = id ? 'PUT' : 'POST';
        const url = id ? `/api/fournisseurs/${id}` : '/api/fournisseurs';

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
                this.toggleModal('modal-fournisseur');
                form.reset();
                document.getElementById('fournisseur-id').value = '';
                await this.loadFournisseurs();
                this.showSuccess(id ? '✅ Fournisseur modifié avec succès!' : '✅ Fournisseur créé avec succès!');
            } else {
                throw new Error(result.error || result.message || 'Erreur inconnue');
            }
            
        } catch (error) {
            console.error('❌ Erreur sauvegarde fournisseur:', error);
            this.showError('Erreur: ' + error.message);
        } finally {
            this.showLoading(false);
        }
    }

    editFournisseur(id) {
        const fournisseur = this.fournisseurs.find(f => f.id === id);
        if (!fournisseur) {
            this.showError('Fournisseur non trouvé');
            return;
        }

        document.getElementById('modal-fournisseur-title').textContent = 'Modifier le fournisseur';
        document.getElementById('fournisseur-id').value = fournisseur.id;
        document.getElementById('fournisseur-nom').value = fournisseur.nom;
        document.getElementById('fournisseur-contact').value = fournisseur.contact || '';
        document.getElementById('fournisseur-telephone').value = fournisseur.telephone;
        document.getElementById('fournisseur-email').value = fournisseur.email || '';
        document.getElementById('fournisseur-site').value = fournisseur.site_web || '';
        document.getElementById('fournisseur-adresse').value = fournisseur.adresse || '';
        document.getElementById('fournisseur-ville').value = fournisseur.ville || 'Ouagadougou';
        document.getElementById('fournisseur-pays').value = fournisseur.pays || 'Burkina Faso';
        document.getElementById('fournisseur-conditions').value = fournisseur.conditions_paiement || '';
        document.getElementById('fournisseur-delai').value = fournisseur.delai_livraison || '';
        document.getElementById('fournisseur-notes').value = fournisseur.notes || '';

        this.toggleModal('modal-fournisseur');
    }

    async desactiverFournisseur(id) {
        const fournisseur = this.fournisseurs.find(f => f.id === id);
        if (!fournisseur) return;

        if (!confirm(`Voulez-vous vraiment désactiver le fournisseur "${fournisseur.nom}" ?\nIl n'apparaîtra plus dans les listes.`)) {
            return;
        }

        try {
            const response = await fetch(`/api/fournisseurs/${id}/desactiver`, {
                method: 'PUT'
            });

            if (response.ok) {
                await this.loadFournisseurs();
                this.showSuccess('✅ Fournisseur désactivé avec succès');
            } else {
                const error = await response.json();
                throw new Error(error.error || error.message);
            }
        } catch (error) {
            console.error('❌ Erreur désactivation:', error);
            this.showError('Erreur lors de la désactivation: ' + error.message);
        }
    }

    async activerFournisseur(id) {
        const fournisseur = this.fournisseurs.find(f => f.id === id);
        if (!fournisseur) return;

        try {
            const response = await fetch(`/api/fournisseurs/${id}/activer`, {
                method: 'PUT'
            });

            if (response.ok) {
                await this.loadFournisseurs();
                this.showSuccess('✅ Fournisseur activé avec succès');
            } else {
                const error = await response.json();
                throw new Error(error.error || error.message);
            }
        } catch (error) {
            console.error('❌ Erreur activation:', error);
            this.showError('Erreur lors de l\'activation: ' + error.message);
        }
    }

    voirCommandes(fournisseurId) {
        window.location.href = `/commandes?fournisseur_id=${fournisseurId}`;
    }

    voirDetails(fournisseurId) {
        const fournisseur = this.fournisseurs.find(f => f.id === fournisseurId);
        if (!fournisseur) return;

        const details = `
🏭 ${fournisseur.nom}
${fournisseur.contact ? `👤 Contact: ${fournisseur.contact}` : ''}
📞 Téléphone: ${fournisseur.telephone}
${fournisseur.email ? `📧 Email: ${fournisseur.email}` : ''}
${fournisseur.site_web ? `🌐 Site web: ${fournisseur.site_web}` : ''}
${fournisseur.adresse ? `📍 Adresse: ${fournisseur.adresse}` : ''}
${fournisseur.ville ? `🏙️ Ville: ${fournisseur.ville}` : ''}
${fournisseur.pays ? `🇧🇫 Pays: ${fournisseur.pays}` : ''}
${fournisseur.conditions_paiement ? `💳 Conditions: ${fournisseur.conditions_paiement}` : ''}
${fournisseur.delai_livraison ? `🚚 Délai: ${fournisseur.delai_livraison} jours` : ''}
${fournisseur.notes ? `📝 Notes: ${fournisseur.notes}` : ''}
        `.trim();

        alert(details);
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
}

// Initialisation globale
let fournisseursManager;

document.addEventListener('DOMContentLoaded', function() {
    fournisseursManager = new FournisseursManager();
});

// Fonctions globales pour les onclick
function toggleModal(modalId) {
    if (fournisseursManager) {
        fournisseursManager.toggleModal(modalId);
    }
}