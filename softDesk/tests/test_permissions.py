"""
Tests pour vérifier les permissions selon le cahier des charges SoftDesk
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import Contributor
from projects.models import Project, Issue, Comment

User = get_user_model()


class PermissionTestCase(TestCase):
    """Tests pour les permissions selon le cahier des charges"""
    
    def setUp(self):
        """Configuration initiale pour les tests"""
        self.client = APIClient()
        
        # Create test users
        self.author_user = User.objects.create_user(
            username='author',
            email='author@test.com',
            password='testpass123',
            age=25,
            can_be_contacted=True,
            can_data_be_shared=False
        )
        
        self.contributor_user = User.objects.create_user(
            username='contributor', 
            email='contributor@test.com',
            password='testpass123',
            age=30,
            can_be_contacted=True,
            can_data_be_shared=True
        )
        
        self.other_user = User.objects.create_user(
            username='other',
            email='other@test.com', 
            password='testpass123',
            age=28,
            can_be_contacted=False,
            can_data_be_shared=False
        )
        
        # Create a test project
        self.project = Project.objects.create(
            name='Test Project',
            description='A test project',
            type='BACK_END',
            author=self.author_user
        )
        # Note: The AUTHOR contributor is automatically created by Project.save()
        
        # Create additional contributor
        Contributor.objects.create(
            user=self.contributor_user,
            project=self.project,
            role='CONTRIBUTOR'
        )
        
        # Create a test issue
        self.issue = Issue.objects.create(
            title='Test Issue',
            description='A test issue',
            tag='BUG',
            priority='MEDIUM',
            status='TO_DO',
            project=self.project,
            author=self.author_user,
            assignee=self.contributor_user
        )
        
        # Create a test comment
        self.comment = Comment.objects.create(
            description='Test comment',
            issue=self.issue,
            author=self.contributor_user
        )
    
    def test_age_validation_rgpd(self):
        """Test: GDPR age validation (minimum 15 years)"""
        data = {
            'username': 'young_user',
            'email': 'young@test.com',
            'password': 'testpass123',
            'age': 14,  # Trop jeune
            'can_be_contacted': True,
            'can_data_be_shared': False
        }
        
        response = self.client.post('/api/auth/register/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('15 years', str(response.content))
    
    def test_project_author_permissions(self):
        """Test : Seul l'auteur peut modifier/supprimer un projet"""
        # L'auteur peut modifier
        self.client.force_authenticate(user=self.author_user)
        response = self.client.put(f'/api/projects/{self.project.id}/', {
            'name': 'Updated Project',
            'description': 'Updated description',
            'type': 'FRONT_END'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Un contributeur ne peut pas modifier
        self.client.force_authenticate(user=self.contributor_user)
        response = self.client.put(f'/api/projects/{self.project.id}/', {
            'name': 'Should not update',
            'description': 'Should not update',
            'type': 'IOS'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_only_contributors_can_access_project(self):
        """Test: Only contributors can access projects"""
        # Contributeur peut voir
        self.client.force_authenticate(user=self.contributor_user)
        response = self.client.get(f'/api/projects/{self.project.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Utilisateur non-contributeur ne peut pas voir
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(f'/api/projects/{self.project.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_only_project_author_can_manage_contributors(self):
        """Test: Only project author can manage contributors"""
        # L'auteur peut ajouter un contributeur
        self.client.force_authenticate(user=self.author_user)
        response = self.client.post(f'/api/projects/{self.project.id}/users/', {
            'user_id': self.other_user.id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Un contributeur ne peut pas ajouter d'autres contributeurs
        self.client.force_authenticate(user=self.contributor_user)
        new_user = User.objects.create_user(
            username='new_user',
            email='new@test.com',
            password='testpass123',
            age=25
        )
        response = self.client.post(f'/api/projects/{self.project.id}/users/', {
            'user_id': new_user.id
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_assigned_to_must_be_contributor(self):
        """Test: assignee must be a project contributor"""
        self.client.force_authenticate(user=self.contributor_user)
        
        # Assigning to a non-contributor should fail
        response = self.client.post(f'/api/projects/{self.project.id}/issues/', {
            'title': 'New Issue',
            'description': 'A new issue',
            'tag': 'BUG',
            'priority': 'MEDIUM',
            'assignee': self.other_user.id  # other_user is not a contributor
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # The serializer automatically filters out non-contributors,
        # and returns an error message that the user is not a contributor
        self.assertIn('is not a contributor to project', str(response.content))
        
        # Check that we can assign to a valid contributor
        response = self.client.post(f'/api/projects/{self.project.id}/issues/', {
            'title': 'Valid Issue',
            'description': 'A valid issue',
            'tag': 'FEATURE',
            'priority': 'LOW',
            'assignee': self.contributor_user.id  # valid contributor
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_comment_author_permissions(self):
        """Test : Seul l'auteur peut modifier/supprimer ses commentaires"""
        # L'auteur du commentaire peut le modifier
        self.client.force_authenticate(user=self.contributor_user)
        response = self.client.put(f'/api/projects/{self.project.id}/issues/{self.issue.id}/comments/{self.comment.id}/', {
            'description': 'Updated comment',
            'issue': self.issue.id
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Un autre utilisateur ne peut pas modifier
        self.client.force_authenticate(user=self.author_user)
        response = self.client.put(f'/api/projects/{self.project.id}/issues/{self.issue.id}/comments/{self.comment.id}/', {
            'description': 'Should not update',
            'issue': self.issue.id
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_user_profile_permissions(self):
        """Test : Un utilisateur ne peut modifier que son propre profil"""
        # L'utilisateur peut modifier son profil
        self.client.force_authenticate(user=self.author_user)
        response = self.client.put(f'/api/users/{self.author_user.id}/', {
            'username': 'updated_author',
            'email': 'updated@test.com',
            'first_name': 'Updated',
            'last_name': 'Author',
            'age': 26,
            'can_be_contacted': False,
            'can_data_be_shared': True
        })
        if response.status_code != status.HTTP_200_OK:
            print(f"Update failed: {response.content}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Un autre utilisateur ne peut pas modifier ce profil
        self.client.force_authenticate(user=self.contributor_user)
        response = self.client.put(f'/api/users/{self.author_user.id}/', {
            'username': 'should_not_update',
            'email': 'should_not_update@test.com',
            'first_name': 'Should',
            'last_name': 'Not',
            'age': 25,
            'can_be_contacted': True,
            'can_data_be_shared': False
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
