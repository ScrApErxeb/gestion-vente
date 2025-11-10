# 🚀 GestioStock PRO - Documentation Complète

## 📋 Table des matières
- [Installation](#installation)
- [Structure du projet](#structure)
- [Fonctionnalités](#fonctionnalites)
- [API REST](#api)
- [Configuration](#configuration)
- [Templates HTML](#templates)

## 🔧 Installation {#installation}

### Prérequis
- Python 3.8+
- pip (gestionnaire de paquets Python)

### Étape 1: Créer l'environnement virtuel
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### Étape 2: Installer les dépendances
Créez `requirements.txt`:
```txt
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Login==0.6.3
reportlab==4.0.7
openpyxl==3.1.2
Werkzeug==3.0.1
```

```bash
pip install -r requirements.txt
```

### Étape 3: Lancer l'application
```bash
python app.py
```

### Étape 4: Accéder à l'application
- **URL:** http://localhost:5000
- **Admin:** admin / admin123
- **Vendeur:** vendeur / vendeur123

## 📁 Structure du projet {#structure}

```
gestiostock_pro/
│
├── app.py                      # Application Flask principale
├── requirements.txt            # Dépendances
├── gestiostock_pro.db         # Base de données SQLite
│
├── templates/
│   ├── base.html              # Template de base
│   ├── login.html             # Page de connexion
│   ├── dashboard.html         # Tableau de bord
│   ├── produits.html          # Gestion produits
│   ├── ventes.html            # Gestion ventes
│   ├── clients.html           # Gestion clients
│   ├── fournisseurs.html      # Gestion fournisseurs
│   ├── commandes.html         # Commandes fournisseurs
│   ├── statistiques.html      # Statistiques avancées
│   └── parametres.html        # Paramètres système
│
└── static/
    ├── css/
    │   └── style.css
    ├── js/
    │   └── app.js
    └── images/
        └── logo.png
```

## ✨ Fonctionnalités {#fonctionnalites}

### 🔐 Authentification
- ✅ Système de connexion sécurisé
- ✅ Gestion des rôles (Admin, Manager, User)
- ✅ Session utilisateur
- ✅ Mot de passe hashé

### 📦 Gestion des Produits
- ✅ CRUD complet
- ✅ Code-barres
- ✅ Catégories hiérarchiques
- ✅ Multi-fournisseurs
- ✅ Alertes stock faible
- ✅ Historique des mouvements
- ✅ Images produits
- ✅ Prix d'achat/vente avec TVA

### 🛒 Gestion des Ventes
- ✅ Création rapide de vente
- ✅ Numérotation automatique des factures
- ✅ Gestion des remises
- ✅ Multi-modes de paiement (espèces, carte, mobile money)
- ✅ Statuts de paiement
- ✅ Export PDF factures
- ✅ Historique complet

### 👥 Gestion des Clients
- ✅ Fiches clients complètes
- ✅ Particuliers / Professionnels
- ✅ Remise par défaut
- ✅ Plafond de crédit
- ✅ Historique d'achats
- ✅ Statistiques client

### 🏭 Gestion des Fournisseurs
- ✅ Informations complètes
- ✅ Conditions de paiement
- ✅ Délais de livraison
- ✅ Historique des commandes

### 📋 Commandes Fournisseurs
- ✅ Création de commandes
- ✅ Suivi des livraisons
- ✅ Réception partielle/totale
- ✅ Mise à jour automatique des stocks
- ✅ Alertes de retard

### 💱 Multi-devises
- ✅ Support XOF, EUR, USD, GBP
- ✅ Conversion automatique
- ✅ Taux de change configurables
- ✅ Rapports multi-devises

### 📊 Statistiques & Rapports
- ✅ Dashboard en temps réel
- ✅ Graphiques de ventes
- ✅ Top produits vendus
- ✅ Analyse de rentabilité
- ✅ Rotation des stocks
- ✅ Produits obsolètes
- ✅ Performance par catégorie
- ✅ Segmentation clients

### 📄 Export de données
- ✅ Export PDF (factures, rapports)
- ✅ Export Excel (produits, ventes, stocks)
- ✅ Mise en forme professionnelle
- ✅ Filtres personnalisables

### 🔔 Notifications
- ✅ Notifications en temps réel
- ✅ Alertes stock faible
- ✅ Commandes en retard
- ✅ Nouvelles ventes
- ✅ Email/SMS (configurable)

### 🎨 Interface
- ✅ Design moderne et professionnel
- ✅ Responsive (mobile-friendly)
- ✅ Navigation intuitive
- ✅ Thème vert (#1abc9c)
- ✅ Indicateurs visuels

## 🔌 API REST Complète {#api}

### Authentification

#### POST /login
**Connexion utilisateur**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

#### POST /register
**Créer un utilisateur**
```json
{
  "username": "nouveau_user",
  "email": "user@example.com",
  "password": "password123",
  "nom": "Nom",
  "prenom": "Prénom",
  "role": "user"
}
```

### Produits

#### GET /api/produits
**Liste des produits**  
*Query params:* `search`, `categorie_id`, `stock_faible`

#### POST /api/produits
**Créer un produit**
```json
{
  "nom": "Nom produit",
  "reference": "REF-001",
  "prix_achat": 10000,
  "prix_vente": 15000,
  "stock_actuel": 50,
  "categorie_id": 1
}
```

#### PUT /api/produits/{id}
**Mettre à jour un produit**

#### DELETE /api/produits/{id}
**Supprimer (désactiver) un produit**

### Ventes

#### GET /api/ventes
**Liste des ventes**  
*Query params:* `date_debut`, `date_fin`, `client_id`, `statut`

#### POST /api/ventes
**Créer une vente**
```json
{
  "produit_id": 1,
  "client_id": 2,
  "quantite": 5,
  "mode_paiement": "espèces",
  "devise": "XOF"
}
```

### Commandes

#### GET /api/commandes
**Liste des commandes fournisseurs**

#### POST /api/commandes
**Créer une commande**
```json
{
  "fournisseur_id": 1,
  "date_livraison_prevue": "2024-12-31",
  "items": [
    {
      "produit_id": 1,
      "quantite": 100,
      "prix_unitaire": 9000
    }
  ]
}
```

#### POST /api/commandes/{id}/recevoir
**Réceptionner une commande**

### Statistiques

#### GET /api/dashboard
**Données du tableau de bord**

#### GET /api/stats/produits
**Statistiques produits**

#### GET /api/stats/ventes
**Statistiques ventes** (*query param:* `periode`)

#### GET /api/stats/clients
**Statistiques clients**

#### GET /api/rapport/stock
**Rapport état du stock**

#### GET /api/rapport/rentabilite
**Analyse de rentabilité**

### Export

#### GET /api/export/facture/{vente_id}
**Export PDF facture**

#### GET /api/export/produits/excel
**Export Excel produits**

#### GET /api/export/ventes/excel
**Export Excel ventes**

### Devise

#### POST /api/devise/convertir
**Convertir un montant**
```json
{
  "montant": 100000,
  "devise_source": "XOF",
  "devise_cible": "EUR"
}
```

## ⚙️ Configuration {#configuration}

### Devises
Dans `app.py`, ligne ~38:
```python
app.config['CURRENCIES'] = {
    'XOF': {'symbol': 'F CFA', 'rate': 1.0, 'name': 'Franc CFA'},
    'EUR': {'symbol': '€', 'rate': 656.0, 'name': 'Euro'},
    'USD': {'symbol': '$', 'rate': 610.0, 'name': 'Dollar US'},
    'GBP': {'symbol': '£', 'rate': 765.0, 'name': 'Livre Sterling'}
}
```

### Email (SMTP)
```python
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'votre-email@gmail.com'
app.config['MAIL_PASSWORD'] = 'votre-mot-de-passe-app'
```

### SMS
Intégrer votre fournisseur SMS (Orange, MTN, etc.)
```python
app.config['SMS_API_KEY'] = 'votre-cle-api'
app.config['SMS_API_URL'] = 'https://api-sms.com/send'
```

## 🎯 Templates HTML {#templates}

### Pages principales :
- **base.html** - Template principal avec sidebar et navigation
- **dashboard.html** - Tableau de bord avec statistiques
- **produits.html** - Gestion complète des produits
- **ventes.html** - Interface de vente et historique
- **clients.html** - Gestion de la clientèle
- **fournisseurs.html** - Gestion des fournisseurs
- **commandes.html** - Commandes fournisseurs
- **statistiques.html** - Analyses et rapports détaillés
- **parametres.html** - Configuration système

### Caractéristiques des templates :
- ✅ Design responsive
- ✅ Interface moderne
- ✅ Navigation intuitive
- ✅ Formulaire de recherche
- ✅ Modales interactives
- ✅ Tableaux triables
- ✅ Alertes et notifications
- ✅ Export de données

---

## 🚀 Démarrage rapide

1. **Cloner le projet**
2. **Configurer l'environnement virtuel**
3. **Installer les dépendances**
4. **Lancer l'application**
5. **Accéder à http://localhost:5000**

## 📞 Support

Pour toute question ou problème :
1. Vérifier les logs de l'application
2. Consulter la documentation API
3. Vérifier la configuration

---

**GestioStock PRO** - *Votre solution complète de gestion de stock professionnelle* 🏪