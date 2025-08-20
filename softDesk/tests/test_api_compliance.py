"""
Test complet de l'API SoftDesk selon le cahier des charges
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import Contributor
from projects.models import Project, Issue, Comment

User = get_user_model()


class SoftDeskAPIComplianceTestCase(TestCase):
    """Tests de conformité complète avec le cahier des charges SoftDesk"""
    
    def setUp(self):
        """Configuration initiale"""
        self.client = APIClient()
        
        # Utilisateurs
        self.author = User.objects.create_user(
            username='author', email='author@test.com', password='pass123', age=25
        )
        self.contributor = User.objects.create_user(
            username='contributor', email='contrib@test.com', password='pass123', age=30
        )
        self.outsider = User.objects.create_user(
            username='outsider', email='outsider@test.com', password='pass123', age=28
        )
        
        # Projet
        self.project = Project.objects.create(
            name='Test Project', description='Test', type='BACK_END', author=self.author
        )
        Contributor.objects.create(user=self.contributor, project=self.project, role='CONTRIBUTOR')
        
        # Issue
        self.issue = Issue.objects.create(
            title='Test Issue', description='Test', tag='BUG', priority='MEDIUM',
            project=self.project, author=self.author, assignee=self.contributor
        )
        
        # Comment
        self.comment = Comment.objects.create(
            description='Test comment', issue=self.issue, author=self.contributor
        )
    
    def test_complete_project_workflow(self):
        """Test complet du workflow d'un projet selon le cahier des charges"""
        
        # 1. Seuls les contributeurs peuvent voir le projet
        self.client.force_authenticate(user=self.outsider)
        response = self.client.get(f'/api/projects/{self.project.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # 2. Contributeur peut voir le projet
        self.client.force_authenticate(user=self.contributor)
        response = self.client.get(f'/api/projects/{self.project.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 3. Seul l'auteur peut modifier le projet
        response = self.client.put(f'/api/projects/{self.project.id}/', {
            'name': 'Updated', 'description': 'Updated', 'type': 'FRONT_END'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # 4. L'auteur peut modifier le projet
        self.client.force_authenticate(user=self.author)
        response = self.client.put(f'/api/projects/{self.project.id}/', {
            'name': 'Updated Project', 'description': 'Updated', 'type': 'FRONT_END'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_issue_assignment_rules(self):
        """Test des règles d'assignation des issues selon le cahier des charges"""
        
        self.client.force_authenticate(user=self.contributor)
        
        # 1. Assignation à un non-contributeur doit échouer
        response = self.client.post(f'/api/projects/{self.project.id}/issues/', {
            'title': 'New Issue', 'description': 'Test', 'tag': 'FEATURE', 
            'priority': 'HIGH', 'assignee': self.outsider.id
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # 2. Assignation à un contributeur doit réussir
        response = self.client.post(f'/api/projects/{self.project.id}/issues/', {
            'title': 'New Issue', 'description': 'Test', 'tag': 'FEATURE', 
            'priority': 'HIGH', 'assignee': self.contributor.id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_resource_author_permissions(self):
        """Test des permissions d'auteur selon le cahier des charges"""
        
        # 1. Seul l'auteur d'un commentaire peut le modifier
        self.client.force_authenticate(user=self.contributor)  # Auteur du commentaire
        response = self.client.put(
            f'/api/projects/{self.project.id}/issues/{self.issue.id}/comments/{self.comment.id}/',
            {'description': 'Updated comment'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 2. Un autre utilisateur ne peut pas modifier le commentaire
        self.client.force_authenticate(user=self.author)
        response = self.client.put(
            f'/api/projects/{self.project.id}/issues/{self.issue.id}/comments/{self.comment.id}/',
            {'description': 'Should not work'}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_pagination_implementation(self):
        """Test que la pagination est bien implémentée"""
        
        self.client.force_authenticate(user=self.author)
        
        # Créer plusieurs projets pour tester la pagination
        for i in range(25):  # Plus que PAGE_SIZE (20)
            Project.objects.create(
                name=f'Project {i}', description=f'Desc {i}', 
                type='BACK_END', author=self.author
            )
        
        response = self.client.get('/api/projects/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier la structure de pagination
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertEqual(len(response.data['results']), 20)  # PAGE_SIZE
    
    def test_rgpd_age_validation(self):
        """Test de validation d'âge RGPD"""
        
        # Tentative de création d'un utilisateur trop jeune
        response = self.client.post('/api/auth/register/', {
            'username': 'young', 'email': 'young@test.com', 'password': 'pass123',
            'age': 14, 'can_be_contacted': True, 'can_data_be_shared': False
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('15 years', str(response.content))
        
        # Création d'un utilisateur avec l'âge requis
        response = self.client.post('/api/auth/register/', {
            'username': 'adult', 'email': 'adult@test.com', 'password': 'pass123',
            'age': 16, 'can_be_contacted': True, 'can_data_be_shared': False
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_contributor_management_authorization(self):
        """Test de gestion des contributeurs selon le cahier des charges"""
        
        # 1. Seul l'auteur du projet peut ajouter des contributeurs
        self.client.force_authenticate(user=self.author)
        response = self.client.post(f'/api/projects/{self.project.id}/users/', {
            'user_id': self.outsider.id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 2. Un contributeur ne peut pas ajouter d'autres contributeurs
        self.client.force_authenticate(user=self.contributor)
        new_user = User.objects.create_user(
            username='newuser', email='new@test.com', password='pass123', age=25
        )
        response = self.client.post(f'/api/projects/{self.project.id}/users/', {
            'user_id': new_user.id
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
