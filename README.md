# SoftDesk Support API

API RESTful pour la gestion de projets, issues et commentaires développée avec Django REST Framework.

## Description

SoftDesk Support est une API de suivi des problèmes permettant aux utilisateurs de :
- Créer et gérer des projets
- Ajouter des contributeurs aux projets
- Créer et suivre des issues (bugs, tâches, améliorations)
- Commenter les issues pour faciliter la collaboration

## Fonctionnalités

### 🔐 Gestion des utilisateurs
- Inscription avec validation d'âge (RGPD - 15 ans minimum)
- Authentification par session et Basic Auth
- Gestion des consentements de confidentialité
- Profil utilisateur personnalisé

### 📁 Gestion des projets
- Création de projets (Back-end, Front-end, iOS, Android)
- Système auteur/contributeur
- Accès restreint aux contributeurs uniquement

### 🐛 Gestion des issues
- Création d'issues avec priorité (LOW, MEDIUM, HIGH)
- Tags personnalisables (BUG, FEATURE, TASK)
- Statuts de progression (To Do, In Progress, Finished)
- Assignation aux contributeurs du projet

### 💬 Système de commentaires
- Commentaires liés aux issues
- Identifiants UUID pour une meilleure traçabilité
- Horodatage automatique

## Installation et configuration

### Prérequis
- Python 3.8+
- Django 5.2+
- Django REST Framework

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
python manage.py makemigrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Lancer le serveur
python manage.py runserver
```

## Endpoints API

### Authentification
- Authentification Basic Auth ou Session
- Création de compte libre, autres actions protégées

### Users
```
POST   /api/users/              # Création d'utilisateur
GET    /api/users/              # Liste des utilisateurs (auth requise)
GET    /api/users/{id}/         # Détail utilisateur (auth requise)
PUT    /api/users/{id}/         # Modification utilisateur (auth requise)
DELETE /api/users/{id}/         # Suppression utilisateur (auth requise)
GET    /api/users/profile/      # Profil utilisateur connecté
```

### Projects
```
GET    /api/projects/           # Liste des projets de l'utilisateur
POST   /api/projects/           # Création d'un projet
GET    /api/projects/{id}/      # Détail d'un projet
PUT    /api/projects/{id}/      # Modification d'un projet
DELETE /api/projects/{id}/      # Suppression d'un projet
```

### Contributors
```
GET    /api/projects/{id}/users/          # Liste des contributeurs
POST   /api/projects/{id}/users/          # Ajout d'un contributeur
DELETE /api/projects/{id}/users/{id}/     # Suppression d'un contributeur
```

### Issues
```
GET    /api/projects/{id}/issues/         # Liste des issues d'un projet
POST   /api/projects/{id}/issues/         # Création d'une issue
GET    /api/projects/{id}/issues/{id}/    # Détail d'une issue
PUT    /api/projects/{id}/issues/{id}/    # Modification d'une issue
DELETE /api/projects/{id}/issues/{id}/    # Suppression d'une issue
```

### Comments
```
GET    /api/projects/{p_id}/issues/{i_id}/comments/          # Liste des commentaires
POST   /api/projects/{p_id}/issues/{i_id}/comments/          # Création d'un commentaire
GET    /api/projects/{p_id}/issues/{i_id}/comments/{c_id}/   # Détail d'un commentaire
PUT    /api/projects/{p_id}/issues/{i_id}/comments/{c_id}/   # Modification d'un commentaire
DELETE /api/projects/{p_id}/issues/{i_id}/comments/{c_id}/   # Suppression d'un commentaire
```

## Tests avec Postman

### Créer un utilisateur
```json
POST /api/users/
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
```

### Créer un projet
```json
POST /api/projects/
Authorization: Basic Auth
{
    "name": "Mon Projet",
    "description": "Description du projet",
    "type": "BACK_END"
}
```

## Modèles de données

### User
- Hérite d'AbstractUser
- Champs supplémentaires : age, can_be_contacted, can_data_be_shared

### Project
- Types : BACK_END, FRONT_END, IOS, ANDROID
- Relations : author (User), contributors (Many-to-Many via Contributor)

### Issue
- Tags : BUG, FEATURE, TASK
- Priorités : LOW, MEDIUM, HIGH
- Statuts : TO_DO, IN_PROGRESS, FINISHED

### Comment
- ID UUID pour une meilleure traçabilité
- Lié à une issue spécifique

## Conformité RGPD

- Validation d'âge minimum (15 ans)
- Gestion des consentements utilisateur
- Champs can_be_contacted et can_data_be_shared

## Technologies utilisées

- **Backend :** Django 5.2, Django REST Framework
- **Base de données :** SQLite (développement)
- **Authentification :** Session + Basic Auth
- **Documentation :** Browsable API de DRF

## Interface d'administration

Accédez à l'interface d'admin Django : `http://127.0.0.1:8000/admin/`

## Support

Pour toute question ou problème, consultez la documentation Django REST Framework ou créez une issue dans le projet.
