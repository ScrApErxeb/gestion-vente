# ✅ Checklist de Vérification - GestioStock Révision

## 📋 Tests À Effectuer

### 1. Page Paramètres
- [ ] Accéder à `/parametres`
- [ ] Page se charge sans erreur
- [ ] Onglets sont visibles
- [ ] Navigation entre onglets fonctionne

### 2. Onglet Général
- [ ] Formes entreprise et paramètres présentes
- [ ] Remplissage du formulaire
- [ ] Clic "Enregistrer" fonctionne
- [ ] Notification de succès s'affiche

### 3. Onglet Catégories
- [ ] Liste des catégories s'affiche
- [ ] Bouton "Ajouter Catégorie" fonctionne
- [ ] Modal s'ouvre
- [ ] Création d'une catégorie OK
- [ ] Édition d'une catégorie OK
- [ ] Suppression protégée (si produits) OK

### 4. Onglet Utilisateurs
- [ ] Liste des utilisateurs s'affiche
- [ ] Utilisateur courant en évidence
- [ ] Bouton "Ajouter Utilisateur" fonctionne
- [ ] Création d'utilisateur OK
- [ ] Activation/désactivation OK

### 5. Onglet Actions
- [ ] ✅ Exporter toutes les données → Excel téléchargé
- [ ] ✅ Sauvegarder la base → Fichier téléchargé
- [ ] ✅ Nettoyer notifications → Notification de succès
- [ ] Section dangereuse visible
- [ ] Réinitialisation avec confirmations multiples

### 6. Statistiques
- [ ] Page `/statistiques` se charge
- [ ] Total dépenses s'affiche ✅
- [ ] Bénéfice net s'affiche ✅
- [ ] Données correctes

### 7. API Routes (Logs)
- [ ] ✅ GET `/api/export/backup` - 200 OK (avant: 404)
- [ ] ✅ GET `/api/export/all-data` - 200 OK (avant: 404)
- [ ] ✅ POST `/api/notifications/nettoyer` - 200 OK (avant: 404)

---

## 🧪 Test Rapide en Curl

```bash
# Test export backup
curl -X GET http://localhost:5000/api/export/backup \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o backup_test.db

# Test export all-data
curl -X GET http://localhost:5000/api/export/all-data \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o export_test.xlsx

# Test nettoyer notifications
curl -X POST http://localhost:5000/api/notifications/nettoyer \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📊 Résultats Avant/Après

### Avant
```
❌ Route /api/export/backup → 404 Not Found
❌ Route /api/export/all-data → 404 Not Found  
❌ Route /api/notifications/nettoyer → 404 Not Found
❌ Dépenses non affichées dans statistiques
❌ Bénéfice net non calculé
❌ Page paramètres désorganisée
```

### Après
```
✅ Route /api/export/backup → 200 OK (Sauvegarde BD)
✅ Route /api/export/all-data → 200 OK (Export Excel)
✅ Route /api/notifications/nettoyer → 200 OK
✅ Dépenses affichées correctement
✅ Bénéfice net calculé (Brut - Dépenses)
✅ Page paramètres organisée en onglets
```

---

## 🎯 Points Clés À Vérifier

1. **Console du Navigateur**
   - [ ] Pas d'erreurs JavaScript
   - [ ] Pas de warnings

2. **Logs du Serveur**
   - [ ] Pas d'erreurs 500
   - [ ] Routes accessibles (200 OK)
   - [ ] Pas de 404 pour `/api/export/backup` et `/api/export/all-data`

3. **Base de Données**
   - [ ] Données intègres après export
   - [ ] Pas de corruption

4. **Fichiers Téléchargés**
   - [ ] Excel valide et exploitable
   - [ ] Backup DB utilisable
   - [ ] JSON bien formaté

---

## 🚨 Dépannage

### Si erreur 404 persiste
```bash
# Vérifier les routes enregistrées
python -c "from gestiostock.routes.api import api_bp; print([r.rule for r in api_bp.url_map.iter_rules()])"
```

### Si Excel vide
```bash
# Vérifier les données dans la BD
python -c "from models import User; print(User.query.count())"
```

### Si modal ne s'ouvre pas
```javascript
// Vérifier dans la console
toggleModal('modal-categorie');
// Devrait afficher la modal
```

---

## ✨ Performances Attendues

| Action | Temps Attendu |
|--------|---------------|
| Chargement page paramètres | < 500ms |
| Export 100 ventes | < 2s |
| Backup DB (< 10MB) | < 1s |
| Nettoyage notifications | < 500ms |

---

## 📞 Support

Si des problèmes persistent:
1. Vérifier les logs du serveur
2. Vérifier la console du navigateur
3. Vérifier les permissions utilisateur (admin required)
4. Vérifier la connexion à la BD

---

**Date**: 6 décembre 2025
**Status**: ✅ Prêt pour testing
