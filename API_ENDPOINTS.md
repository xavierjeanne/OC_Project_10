# API SoftDesk - Endpoints Conformes au Cahier des Charges

## 🔐 Authentification JWT

### Inscription
```http
POST /api/auth/register/
Content-Type: application/json

{
    "username": "string",
    "email": "email",
    "password": "string",
    "first_name": "string",
    "last_name": "string",
    "age": 15+,  // RGPD: minimum 15 ans
    "can_be_contacted": boolean,
    "can_data_be_shared": boolean
}
```

### Connexion
```http
POST /api/auth/login/
Content-Type: application/json

{
    "username": "string",
    "password": "string"
}

Response:
{
    "access": "jwt_token",
    "refresh": "jwt_refresh_token",
    "user": { user_info }
}
```

## 👥 Gestion des Utilisateurs

### Profil utilisateur
```http
GET /api/users/{id}/
Authorization: Bearer {jwt_token}

PUT /api/users/{id}/  // Seulement son propre profil
Authorization: Bearer {jwt_token}
```

## 📁 Gestion des Projets

### Règles selon le cahier des charges :
- **Auteur** : Peut modifier/supprimer le projet, gérer les contributeurs
- **Contributeur** : Peut seulement voir le projet et ses ressources
- **Non-contributeur** : Aucun accès

```http
GET /api/projects/                    // Liste projets de l'utilisateur
POST /api/projects/                   // Créer projet (devient auteur)
GET /api/projects/{id}/               // Détail (contributeurs seulement)
PUT /api/projects/{id}/               // Modifier (auteur seulement)
DELETE /api/projects/{id}/            // Supprimer (auteur seulement)
```

### Gestion des contributeurs
```http
GET /api/projects/{id}/users/         // Liste contributeurs (contributeurs seulement)
POST /api/projects/{id}/users/        // Ajouter contributeur (auteur seulement)
DELETE /api/projects/{id}/users/{id}/ // Supprimer contributeur (auteur seulement)
```

## 🐛 Gestion des Issues

### Règles selon le cahier des charges :
- **Créateur** : Contributeur du projet
- **Assignee** : DOIT être contributeur du projet
- **Priorité** : LOW, MEDIUM, HIGH
- **Tag** : BUG, FEATURE, TASK
- **Statut** : TO_DO (défaut), IN_PROGRESS, FINISHED

```http
GET /api/projects/{id}/issues/        // Liste issues du projet
POST /api/projects/{id}/issues/       // Créer issue
GET /api/projects/{id}/issues/{id}/   // Détail issue
PUT /api/projects/{id}/issues/{id}/   // Modifier tous les champs (contributeurs)
PATCH /api/projects/{id}/issues/{id}/ // Modifier partiellement (contributeurs)
DELETE /api/projects/{id}/issues/{id}/ // Supprimer (auteur de l'issue)
```

### Exemple création issue
```json
{
    "title": "string",
    "description": "string",
    "tag": "BUG|FEATURE|TASK",
    "priority": "LOW|MEDIUM|HIGH",
    "status": "TO_DO|IN_PROGRESS|FINISHED",
    "assignee": contributor_user_id  // DOIT être contributeur
}
```

### Modification d'issue
```http
// Modification complète (tous les champs requis)
PUT /api/projects/{id}/issues/{id}/
{
    "title": "string",
    "description": "string", 
    "tag": "BUG|FEATURE|TASK",
    "priority": "LOW|MEDIUM|HIGH",
    "status": "TO_DO|IN_PROGRESS|FINISHED",
    "assignee": contributor_user_id
}

// Modification partielle (seulement les champs à modifier)
PATCH /api/projects/{id}/issues/{id}/
{
    "assignee": contributor_user_id  // Seulement l'assignee
}
```

## 💬 Gestion des Commentaires

### Règles selon le cahier des charges :
- **Auteur** : Peut modifier/supprimer ses commentaires
- **Autres** : Lecture seulement
- **UUID** : Identifiant unique automatique

```http
GET /api/projects/{p_id}/issues/{i_id}/comments/           // Liste commentaires
POST /api/projects/{p_id}/issues/{i_id}/comments/          // Créer commentaire
GET /api/projects/{p_id}/issues/{i_id}/comments/{uuid}/    // Détail
PUT /api/projects/{p_id}/issues/{i_id}/comments/{uuid}/    // Modifier (auteur seulement)
DELETE /api/projects/{p_id}/issues/{i_id}/comments/{uuid}/ // Supprimer (auteur seulement)
```

## 📊 Pagination

Toutes les listes utilisent la pagination (PAGE_SIZE: 20) :

```json
{
    "count": 45,
    "next": "http://api/endpoint/?page=3",
    "previous": "http://api/endpoint/?page=1",
    "results": [...]
}
```

## ⚡ Horodatage

Toutes les ressources possèdent `created_time` (automatique) selon le cahier des charges.

## 🛡️ Permissions Résumé

| Action | Projet | Issue | Commentaire | Contributeur |
|--------|---------|-------|-------------|--------------|
| **Voir** | Contributeur | Contributeur | Contributeur | Contributeur |
| **Créer** | Tous auth. | Contributeur | Contributeur | Auteur projet |
| **Modifier** | Auteur | Contributeur | Auteur ressource | Auteur projet |
| **Supprimer** | Auteur | Auteur ressource | Auteur ressource | Auteur projet |

## 🔒 Conformité RGPD

- Âge minimum : 15 ans
- Consentements : `can_be_contacted`, `can_data_be_shared`
- Validation automatique lors de l'inscription
