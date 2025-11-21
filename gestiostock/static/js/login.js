// ===== GESTION DE LA CONNEXION =====


class LoginManager {
    constructor() {
        this.form = document.getElementById('login-form');
        this.errorDiv = document.getElementById('error-message');
        this.init();
    }

    init() {
        this.bindEvents();
        this.autoFocus();
        this.checkForLogout();
    }

    bindEvents() {
        // Soumission du formulaire
        this.form.addEventListener('submit', (e) => this.handleLogin(e));
        
        // Réinitialisation des erreurs lors de la saisie
        const inputs = this.form.querySelectorAll('input');
        inputs.forEach(input => {
            input.addEventListener('input', () => this.hideError());
        });
    }

async handleLogin(event) {
    event.preventDefault();
    
    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username: document.getElementById('username').value,
                password: document.getElementById('password').value
            }),
            credentials: 'include'
        });

        const data = await response.json();

        if (data.success) {
            // Redirection simple et efficace
            window.location.href = data.redirect || '/';
        } else {
            this.showError(data.message || 'Échec de connexion');
        }
    } catch (error) {
        this.showError('Erreur réseau');
    }
}

    showError(message) {
        this.errorDiv.textContent = message;
        this.errorDiv.style.display = 'block';
        this.errorDiv.className = 'error-message';
        
        // Focus sur le champ mot de passe en cas d'erreur
        document.getElementById('password').focus();
    }

    showMessage(message, type = 'error') {
        const className = type === 'success' ? 'success-message' : 'error-message';
        this.errorDiv.textContent = message;
        this.errorDiv.style.display = 'block';
        this.errorDiv.className = className;
    }

    hideError() {
        this.errorDiv.style.display = 'none';
    }

    setLoadingState(button, isLoading) {
        if (isLoading) {
            button.disabled = true;
            button.classList.add('loading');
            button.innerHTML = 'Connexion...';
        } else {
            button.disabled = false;
            button.classList.remove('loading');
            button.innerHTML = 'Se connecter';
        }
    }

    shakeForm() {
        this.form.style.animation = 'none';
        setTimeout(() => {
            this.form.style.animation = 'shake 0.5s ease-in-out';
        }, 10);
    }

    autoFocus() {
        const usernameInput = document.getElementById('username');
        if (usernameInput) {
            setTimeout(() => usernameInput.focus(), 100);
        }
    }

    checkForLogout() {
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.get('logout') === 'true') {
            this.showMessage('Vous avez été déconnecté avec succès.', 'success');
        }
    }
}

// ===== INITIALISATION =====

document.addEventListener('DOMContentLoaded', function() {
    const loginManager = new LoginManager();
    
    // Pour le débogage en développement
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        console.log('🔧 Mode développement activé');
        
        // Décommentez la ligne suivante pour pré-remplir les identifiants
        // loginManager.prefillCredentials('admin', 'admin123');
    }
});