# SoftDesk Support API

API RESTful moderne pour la gestion de projets, issues et commentaires développée avec Django REST Framework et authentification JWT.

## Description

SoftDesk Support est une API de suivi des problèmes permettant aux utilisateurs de :
- Créer et gérer des projets collaboratifs
- Ajouter des contributeurs avec système de rôles (AUTHOR/CONTRIBUTOR)
- Créer et suivre des issues (bugs, tâches, améliorations)
- Commenter les issues pour faciliter la collaboration
- Authentification sécurisée par tokens JWT

## Architecture

### 🏗️ Structure modulaire
- **`accounts/`** : Gestion des utilisateurs, authentification JWT, contributeurs
- **`projects/`** : Gestion des projets, issues et commentaires
- Architecture RESTful avec ViewSets dédiés

### 🔐 Gestion des utilisateurs et authentification
- Inscription avec validation d'âge (RGPD - 15 ans minimum)
- **Authentification JWT** avec tokens d'accès et de refresh
- Système de blacklist pour la déconnexion sécurisée
- Gestion des consentements de confidentialité
- Profil utilisateur personnalisé avec modèle User étendu

### 📁 Gestion des projets
- Création de projets (Back-end, Front-end, iOS, Android)
- **Système auteur/contributeur avec rôles** (AUTHOR automatique, CONTRIBUTOR ajouté)
- Accès restreint aux contributeurs uniquement
- Assignation automatique de l'auteur comme contributeur

### 🐛 Gestion des issues
- Création d'issues avec priorité (LOW, MEDIUM, HIGH)
- Tags personnalisables (BUG, FEATURE, TASK)
- Statuts de progression (To Do, In Progress, Finished)
- Assignation aux contributeurs du projet
- Système de permissions par rôle

### 💬 Système de commentaires
- Commentaires liés aux issues
- Identifiants UUID pour une meilleure traçabilité
- Horodatage automatique
- Permissions basées sur l'appartenance au projet

## Installation et configuration

### Prérequis
- Python 3.8+
- Django 5.2+
- Django REST Framework 3.16+
- djangorestframework-simplejwt

### Installation
```bash
# Cloner le projet
git clone https://github.com/xavierjeanne/OC_Project_10
cd OC_Project_10

# Créer et activer l'environnement virtuel
python -m venv env
# Windows:
env\Scripts\activate
# Linux/Mac:
source env/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Configurer la base de données
cd softDesk
python manage.py makemigrations accounts
python manage.py makemigrations projects
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Lancer le serveur
python manage.py runserver
```

## Endpoints API

### 🔑 Authentification JWT
```
POST   /api/auth/register/      # Inscription utilisateur (retourne tokens JWT)
POST   /api/auth/login/         # Connexion (retourne access + refresh tokens)
POST   /api/auth/refresh/       # Renouvellement du token d'accès
POST   /api/auth/logout/        # Déconnexion (blacklist du refresh token)
```

### 👥 Users (app accounts)
```
GET    /api/users/              # Liste des utilisateurs (auth requise)
GET    /api/users/{id}/         # Détail utilisateur (auth requise)
PUT    /api/users/{id}/         # Modification utilisateur (auth requise)
DELETE /api/users/{id}/         # Suppression utilisateur (auth requise)
```

### 👤 Contributors (app accounts)
```
GET    /api/contributors/       # Liste des contributeurs (auth requise)
GET    /api/contributors/{id}/  # Détail d'un contributeur (auth requise)
```

### 📁 Projects (app projects)
```
GET    /api/projects/           # Liste des projets de l'utilisateur
POST   /api/projects/           # Création d'un projet
GET    /api/projects/{id}/      # Détail d'un projet
PUT    /api/projects/{id}/      # Modification d'un projet (auteur uniquement)
DELETE /api/projects/{id}/      # Suppression d'un projet (auteur uniquement)
```

### 🐛 Issues (app projects)
```
GET    /api/issues/             # Liste des issues des projets de l'utilisateur
POST   /api/issues/             # Création d'une issue
GET    /api/issues/{id}/        # Détail d'une issue
PUT    /api/issues/{id}/        # Modification d'une issue
DELETE /api/issues/{id}/        # Suppression d'une issue
```

### 💬 Comments (app projects)
```
GET    /api/comments/           # Liste des commentaires accessibles
POST   /api/comments/           # Création d'un commentaire
GET    /api/comments/{id}/      # Détail d'un commentaire
PUT    /api/comments/{id}/      # Modification d'un commentaire (auteur uniquement)
DELETE /api/comments/{id}/      # Suppression d'un commentaire (auteur uniquement)
```

## Tests avec Postman

### 🔑 Inscription et authentification
```json
# 1. Inscription (retourne automatiquement les tokens JWT)
POST /api/auth/register/
{
    "username": "testuser",
    "email": "test@example.com",
    "password": "motdepasse123",
    "first_name": "Test",
    "last_name": "User",
    "age": 25,
    "can_be_contacted": true,
    "can_data_be_shared": false
}

# 2. Connexion
POST /api/auth/login/
{
    "username": "testuser",
    "password": "motdepasse123"
}

# Réponse JWT :
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com"
    }
}
```

### 📁 Utilisation des endpoints protégés
```json
# Ajouter le token d'accès dans les headers :
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...

# Créer un projet
POST /api/projects/
{
    "name": "Mon Projet API",
    "description": "Projet avec architecture modulaire",
    "type": "BACK_END"
}

# Créer une issue
POST /api/issues/
{
    "title": "Nouvelle fonctionnalité",
    "description": "Description de l'issue",
    "tag": "FEATURE",
    "priority": "MEDIUM",
    "project": 1,
    "assigned_to": 1
}
```

## Modèles de données

### 👤 User (app accounts)
- Hérite d'AbstractUser
- Champs supplémentaires : age, can_be_contacted, can_data_be_shared
- Validation d'âge minimum (15 ans) pour conformité RGPD

### 🤝 Contributor (app accounts)
- Rôles : AUTHOR (créateur du projet), CONTRIBUTOR (collaborateur)
- Relations : user (User), project (Project)
- Création automatique de l'AUTHOR lors de la création d'un projet

### 📁 Project (app projects)
- Types : BACK_END, FRONT_END, IOS, ANDROID
- Relations : author (User), contributors (Many-to-Many via Contributor)
- Assignation automatique de l'auteur comme contributeur AUTHOR

### 🐛 Issue (app projects)
- Tags : BUG, FEATURE, TASK
- Priorités : LOW, MEDIUM, HIGH
- Statuts : TO_DO, IN_PROGRESS, FINISHED
- Relations : project (Project), author (User), assigned_to (User)

### 💬 Comment (app projects)
- ID UUID pour une meilleure traçabilité
- Relations : issue (Issue), author (User)
- Horodatage automatique (created_time)

## Configuration JWT

### 🔑 Paramètres de sécurité
- **Access Token** : 60 minutes de validité
- **Refresh Token** : 7 jours de validité
- **Rotation** : Nouveaux tokens à chaque refresh
- **Blacklist** : Déconnexion sécurisée avec invalidation des tokens
- **Algorithme** : HS256

### 🛡️ Headers d'authentification
```
Authorization: Bearer <access_token>
```

## Conformité RGPD

- Validation d'âge minimum (15 ans)
- Gestion des consentements utilisateur
- Champs can_be_contacted et can_data_be_shared
- Modèle User étendu pour la conformité légale

## Technologies utilisées

- **Backend :** Django 5.2, Django REST Framework 3.16
- **Authentification :** JWT avec djangorestframework-simplejwt
- **Base de données :** SQLite (développement)
- **Architecture :** Apps modulaires (accounts, projects)
- **Documentation :** Browsable API de DRF + JWT endpoints

## Interface d'administration

Accédez à l'interface d'admin Django : `http://127.0.0.1:8000/admin/`

## Endpoints de développement

- **API Root** : `http://127.0.0.1:8000/api/`
- **JWT Auth** : `http://127.0.0.1:8000/api/auth/`
- **Admin Interface** : `http://127.0.0.1:8000/admin/`
- **Browsable API** : Interface DRF pour tester les endpoints

## Exemples de workflow

### 🚀 Démarrage rapide
1. **Inscription** → POST `/api/auth/register/` (reçoit tokens JWT)
2. **Créer projet** → POST `/api/projects/` (devient AUTHOR automatiquement)
3. **Ajouter contributeur** → Créer un Contributor avec role="CONTRIBUTOR"
4. **Créer issues** → POST `/api/issues/` liées au projet
5. **Commenter** → POST `/api/comments/` sur les issues

### 🔄 Renouvellement de session
- Utiliser le refresh token : POST `/api/auth/refresh/`
- En cas d'expiration, se reconnecter : POST `/api/auth/login/`
- Déconnexion propre : POST `/api/auth/logout/`

## Support

Pour toute question ou problème :
- Consultez la documentation Django REST Framework
- Vérifiez la configuration JWT dans `settings.py`
- Testez les endpoints avec la Browsable API

