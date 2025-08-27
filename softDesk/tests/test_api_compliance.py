"""
Complete test of the SoftDesk API according to the specifications
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import Contributor
from projects.models import Project, Issue, Comment

User = get_user_model()


class SoftDeskAPIComplianceTestCase(TestCase):
    """Complete compliance tests with SoftDesk requirements"""
    
    def setUp(self):
        """Initial setup"""
        self.client = APIClient()
        
        # Users
        self.author = User.objects.create_user(
            username='author', email='author@test.com', password='securepass123', age=25
        )
        self.contributor = User.objects.create_user(
            username='contributor', email='contrib@test.com', password='securepass123', age=30
        )
        self.outsider = User.objects.create_user(
            username='outsider', email='outsider@test.com', password='securepass123', age=28
        )
        
        # Project
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
        """Complete test of project workflow according to specifications"""
        
        # 1. Only contributors can see the project
        self.client.force_authenticate(user=self.outsider)
        response = self.client.get(f'/api/projects/{self.project.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # 2. Contributor can see the project
        self.client.force_authenticate(user=self.contributor)
        response = self.client.get(f'/api/projects/{self.project.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 3. Only the author can modify the project
        response = self.client.put(f'/api/projects/{self.project.id}/', {
            'name': 'Updated', 'description': 'Updated', 'type': 'FRONT_END'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # 4. The author can modify the project
        self.client.force_authenticate(user=self.author)
        response = self.client.put(f'/api/projects/{self.project.id}/', {
            'name': 'Updated Project', 'description': 'Updated', 'type': 'FRONT_END'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_issue_assignment_rules(self):
        """Test issue assignment rules according to requirements"""
        
        self.client.force_authenticate(user=self.contributor)
        
        # 1. Assignment to non-contributor should fail
        response = self.client.post(f'/api/projects/{self.project.id}/issues/', {
            'title': 'New Issue', 'description': 'Test', 'tag': 'FEATURE', 
            'priority': 'HIGH', 'assignee': self.outsider.id
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # 2. Assignment to a contributor should succeed
        response = self.client.post(f'/api/projects/{self.project.id}/issues/', {
            'title': 'New Issue', 'description': 'Test', 'tag': 'FEATURE', 
            'priority': 'HIGH', 'assignee': self.contributor.id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_resource_author_permissions(self):
        """Test of author permissions according to specifications"""
        
        # 1. Only the author of a comment can modify it
        self.client.force_authenticate(user=self.contributor)  # Auteur du commentaire
        response = self.client.put(
            f'/api/projects/{self.project.id}/issues/{self.issue.id}/comments/{self.comment.id}/',
            {'description': 'Updated comment'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 2. Another user cannot modify the comment
        self.client.force_authenticate(user=self.author)
        response = self.client.put(
            f'/api/projects/{self.project.id}/issues/{self.issue.id}/comments/{self.comment.id}/',
            {'description': 'Should not work'}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_pagination_implementation(self):
        """Test that pagination is correctly implemented"""
        
        self.client.force_authenticate(user=self.author)
        
        # Create multiple projects to test pagination
        for i in range(25):  # Plus que PAGE_SIZE (20)
            Project.objects.create(
                name=f'Project {i}', description=f'Desc {i}', 
                type='BACK_END', author=self.author
            )
        
        response = self.client.get('/api/projects/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify pagination structure
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertEqual(len(response.data['results']), 20)  # PAGE_SIZE
    
    def test_rgpd_age_validation(self):
        """Test GDPR age validation"""
        
        # Attempt to create a user who is too young
        response = self.client.post('/api/auth/register/', {
            'username': 'young', 'email': 'young@test.com', 'password': 'securepass123',
            'age': 14, 'can_be_contacted': True, 'can_data_be_shared': False
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('15 years', str(response.content))
        
        # Creation of a user with the required age
        response = self.client.post('/api/auth/register/', {
            'username': 'adult', 'email': 'adult@test.com', 'password': 'securepass123',
            'age': 16, 'can_be_contacted': True, 'can_data_be_shared': False
        })
        
        # Debug: display error if creation fails
        if response.status_code != status.HTTP_201_CREATED:
            print(f"Registration failed with status {response.status_code}: {response.content}")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_contributor_management_authorization(self):
        """Test contributor management according to specifications"""
        
        # 1. Only the project author can add contributors
        self.client.force_authenticate(user=self.author)
        response = self.client.post(f'/api/projects/{self.project.id}/users/', {
            'user_id': self.outsider.id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 2. A contributor cannot add other contributors
        self.client.force_authenticate(user=self.contributor)
        new_user = User.objects.create_user(
            username='newuser', email='new@test.com', password='pass123', age=25
        )
        response = self.client.post(f'/api/projects/{self.project.id}/users/', {
            'user_id': new_user.id
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
