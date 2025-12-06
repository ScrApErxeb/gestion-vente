# Correction des Routes API Manquantes

## 📋 Problème Identifié

Les erreurs 404 indiquaient que les routes suivantes n'existaient pas :
```
GET /api/export/backup HTTP/1.1" 404
POST /api/notifications/nettoyer HTTP/1.1" 404
```

## ✅ Solution Appliquée

### 1. **Ajout de `/api/export/backup`** (ligne 713)
```python
@api_bp.route('/api/export/backup', methods=['GET'])
@login_required
def export_backup():
    """Exporte une sauvegarde de la base de données"""
```

**Fonctionnalité:**
- Vérifie les permissions admin
- Exporte le fichier SQLite de la base de données
- Fallback en JSON si ce n'est pas SQLite
- Retourne un fichier téléchargeable

### 2. **Correction de `/api/export/all-data`** (ligne 445)
- ✅ Changé de `/export/all-data` à `/api/export/all-data`
- Exporte toutes les données (utilisateurs, ventes, produits, statistiques)
- Retourne un fichier Excel multi-feuilles

### 3. **Route `/api/notifications/nettoyer`** (ligne 626)
- ✅ Déjà existante et correcte
- Supprime les notifications lues
- Retourne le nombre de notifications supprimées

## 🔧 Imports Ajoutés

```python
from flask import current_app  # Pour accéder à la config
import os                      # Pour manipuler les fichiers
import json                    # Pour les exports JSON
import shutil                  # Pour copier les fichiers
import tempfile               # Pour les fichiers temporaires
```

## 📁 Fichier Modifié

- `gestiostock/routes/api.py` - Ajout de 2 routes et correction d'1 route

## 🧪 Endpoints Disponibles

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/api/export/all-data` | Exporter toutes les données (Excel) |
| GET | `/api/export/backup` | Sauvegarder la base (DB) |
| POST | `/api/notifications/nettoyer` | Nettoyer les notifications |

## ✨ Statut

**✅ Toutes les erreurs 404 corrigées**

Les routes sont maintenant prêtes à être utilisées par la page des paramètres.
