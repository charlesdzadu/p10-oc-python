# SoftDesk Support API

API RESTful pour la gestion de projets et de suivi de problèmes, développée avec Django REST Framework.

## 🚀 Fonctionnalités

### Gestion des utilisateurs (RGPD)
- ✅ Authentification JWT
- ✅ Validation de l'âge (minimum 15 ans selon RGPD)
- ✅ Gestion du consentement (contact et partage de données)
- ✅ Droit à l'oubli (suppression de compte)

### Gestion des projets
- ✅ Création de projets avec types (back-end, front-end, iOS, Android)
- ✅ Système de contributeurs
- ✅ Permissions basées sur les rôles

### Gestion des problèmes (Issues)
- ✅ Création de problèmes avec priorité, statut et tags
- ✅ Attribution à des contributeurs
- ✅ Suivi de progression (To Do, In Progress, Finished)

### Gestion des commentaires
- ✅ Commentaires sur les problèmes
- ✅ Identifiants UUID uniques
- ✅ Horodatage automatique

### Sécurité OWASP
- ✅ Authentification JWT
- ✅ Autorisation basée sur les rôles
- ✅ Protection contre les injections
- ✅ Validation des données

### Green Code
- ✅ Pagination optimisée
- ✅ Requêtes optimisées
- ✅ Gestion intelligente des ressources

### 📚 Documentation Interactive
- ✅ **Swagger UI** : Interface interactive pour tester l'API
- ✅ **ReDoc** : Documentation alternative plus détaillée
- ✅ **OpenAPI Schema** : Spécification complète de l'API
- ✅ **Exemples intégrés** : Exemples de requêtes pour chaque endpoint

## 🛠️ Installation

### Prérequis
- Python 3.12+
- Poetry

### Installation
```bash
# Cloner le projet
git clone <repository-url>
cd p10-oc-python

# Installer les dépendances
poetry install --no-root

# Créer les migrations
poetry run python manage.py makemigrations

# Appliquer les migrations
poetry run python manage.py migrate

# Créer un superutilisateur
poetry run python manage.py createsuperuser

# Lancer le serveur
poetry run python manage.py runserver
```

## 📖 Documentation Interactive

### Swagger UI
Accédez à l'interface interactive Swagger pour tester l'API :
```
http://localhost:8000/api/docs/
```

### ReDoc
Documentation alternative plus détaillée :
```
http://localhost:8000/api/redoc/
```

### OpenAPI Schema
Spécification complète de l'API au format JSON :
```
http://localhost:8000/api/schema/
```

### Fonctionnalités de la documentation
- 🔍 **Recherche** : Trouvez rapidement les endpoints
- 🧪 **Test interactif** : Testez les endpoints directement depuis l'interface
- 🔐 **Authentification** : Gestion automatique des tokens JWT
- 📝 **Exemples** : Exemples de requêtes pour chaque endpoint
- 🏷️ **Tags organisés** : Endpoints groupés par fonctionnalité
- 📊 **Responses** : Documentation complète des réponses

## 🔐 Authentification

L'API utilise JWT (JSON Web Tokens) pour l'authentification.

### Obtenir un token
```bash
POST /auth/token/
{
    "username": "votre_username",
    "password": "votre_password"
}
```

### Rafraîchir un token
```bash
POST /auth/token/refresh/
{
    "refresh": "votre_refresh_token"
}
```

### Utiliser le token
```bash
Authorization: Bearer <votre_access_token>
```

## 📚 Endpoints API

### Utilisateurs

#### Créer un utilisateur
```bash
POST /api/users/
{
    "username": "nouveau_utilisateur",
    "email": "user@example.com",
    "password": "mot_de_passe_securise",
    "password_confirm": "mot_de_passe_securise",
    "age": 25,
    "can_be_contacted": true,
    "can_data_be_shared": false
}
```

#### Lister les utilisateurs
```bash
GET /api/users/
Authorization: Bearer <token>
```

#### Modifier le profil
```bash
PUT /api/users/{id}/profile/
Authorization: Bearer <token>
{
    "age": 26,
    "can_be_contacted": false
}
```

#### Supprimer le compte (RGPD)
```bash
DELETE /api/users/{id}/delete_account/
Authorization: Bearer <token>
```

### Projets

#### Créer un projet
```bash
POST /api/projects/
Authorization: Bearer <token>
{
    "title": "Mon Projet",
    "description": "Description du projet",
    "type": "back-end"
}
```

#### Lister les projets
```bash
GET /api/projects/
Authorization: Bearer <token>
```

#### Ajouter un contributeur
```bash
POST /api/projects/{id}/add_contributor/
Authorization: Bearer <token>
{
    "user_id": 2
}
```

#### Lister les contributeurs
```bash
GET /api/projects/{id}/contributors/
Authorization: Bearer <token>
```

### Problèmes (Issues)

#### Créer un problème
```bash
POST /api/issues/
Authorization: Bearer <token>
{
    "title": "Bug critique",
    "description": "Description du problème",
    "priority": "HIGH",
    "status": "To Do",
    "tag": "BUG",
    "project": 1,
    "assigned_to_id": 2
}
```

#### Lister les problèmes
```bash
GET /api/issues/
Authorization: Bearer <token>
```

#### Lister les commentaires d'un problème
```bash
GET /api/issues/{id}/comments/
Authorization: Bearer <token>
```

### Commentaires

#### Créer un commentaire
```bash
POST /api/comments/
Authorization: Bearer <token>
{
    "description": "Commentaire sur le problème",
    "issue": 1
}
```

#### Récupérer un commentaire par UUID
```bash
GET /api/comments/{uuid}/
Authorization: Bearer <token>
```

## 🔒 Permissions

### Modèles de permissions
- **IsProjectContributor** : Accès aux ressources du projet
- **IsAuthorOrReadOnly** : Lecture pour tous, modification pour l'auteur
- **IsProjectAuthorOrReadOnly** : Permissions spéciales pour les projets
- **IsIssueAuthorOrReadOnly** : Permissions spéciales pour les issues
- **IsCommentAuthorOrReadOnly** : Permissions spéciales pour les commentaires

### Règles d'accès
1. **Authentification requise** pour toutes les opérations
2. **Seuls les contributeurs** peuvent accéder aux projets
3. **Seuls les auteurs** peuvent modifier/supprimer leurs ressources
4. **Lecture autorisée** pour tous les contributeurs du projet

## 📊 Pagination

L'API utilise une pagination optimisée pour les performances :

```json
{
    "count": 100,
    "next": "http://localhost:8000/api/projects/?page=2",
    "previous": null,
    "results": [...]
}
```

## 🛡️ Sécurité OWASP

### A1:2021 – Broken Access Control
- ✅ Authentification JWT obligatoire
- ✅ Autorisation basée sur les rôles
- ✅ Validation des permissions par ressource

### A2:2021 – Cryptographic Failures
- ✅ Tokens JWT sécurisés
- ✅ Validation des mots de passe
- ✅ Chiffrement des données sensibles

### A3:2021 – Injection
- ✅ Validation des données avec Pydantic
- ✅ Protection contre les injections SQL
- ✅ Échappement des caractères spéciaux

## 📋 RGPD

### Droits des utilisateurs
- ✅ **Droit d'accès** : Consultation des données personnelles
- ✅ **Droit de rectification** : Modification du profil
- ✅ **Droit à l'oubli** : Suppression complète du compte
- ✅ **Consentement** : Gestion des préférences de contact

### Validation de l'âge
- ✅ Vérification de l'âge minimum (15 ans)
- ✅ Validation lors de l'inscription
- ✅ Respect des normes RGPD

## 🌱 Green Code

### Optimisations implémentées
- ✅ **Pagination** : Limitation du nombre de résultats
- ✅ **Requêtes optimisées** : Utilisation de `select_related` et `prefetch_related`
- ✅ **Cache intelligent** : Mise en cache des données fréquemment consultées
- ✅ **Gestion des ressources** : Optimisation de la consommation mémoire

### Bonnes pratiques
- ✅ Code modulaire et réutilisable
- ✅ Validation des données côté serveur
- ✅ Gestion d'erreurs optimisée
- ✅ Documentation claire

## 🧪 Tests

### Lancer les tests
```bash
poetry run python manage.py test
```

### Tests couverts
- ✅ Modèles et validations
- ✅ Sérialiseurs
- ✅ Permissions
- ✅ Vues et endpoints
- ✅ Authentification JWT

## 📝 Exemples d'utilisation

### Workflow complet
1. **Créer un utilisateur**
2. **Obtenir un token JWT**
3. **Créer un projet**
4. **Ajouter des contributeurs**
5. **Créer des problèmes**
6. **Ajouter des commentaires**

### Exemple avec curl
```bash
# Authentification
TOKEN=$(curl -X POST http://localhost:8000/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"password"}' | jq -r '.access')

# Créer un projet
curl -X POST http://localhost:8000/api/projects/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Mon Projet","description":"Description","type":"back-end"}'
```

### Test avec Swagger UI
1. Ouvrez `http://localhost:8000/api/docs/`
2. Cliquez sur "Authorize" en haut à droite
3. Entrez votre token JWT : `Bearer <votre_token>`
4. Testez les endpoints directement depuis l'interface

## 🚀 Déploiement

### Variables d'environnement
```bash
SECRET_KEY=votre_clé_secrète
DEBUG=False
ALLOWED_HOSTS=votre-domaine.com
```

### Production
```bash
# Collecter les fichiers statiques
poetry run python manage.py collectstatic

# Configurer le serveur web (nginx + gunicorn)
# Configurer la base de données PostgreSQL
# Configurer les variables d'environnement
```

## 📞 Support

Pour toute question ou problème :
- Créer une issue sur GitHub
- Contacter l'équipe de développement
- Consulter la documentation Django REST Framework
- Utiliser l'interface Swagger pour tester l'API

---

**Développé avec ❤️ pour OpenClassrooms** 