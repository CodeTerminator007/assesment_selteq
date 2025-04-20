from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Task
from datetime import timedelta


class TaskAPITestCase(APITestCase):
    """Test suite for Task Management API endpoints.
    
    Tests authentication, CRUD operations, and raw SQL operations.
    Ensures proper user isolation and data integrity.
    """

    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(
            username='testuser1',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            password='testpass123'
        )

        # Create some tasks for user1
        self.task1 = Task.objects.create(
            title='Test Task 1',
            duration=timedelta(hours=1),
            user=self.user1
        )
        self.task2 = Task.objects.create(
            title='Test Task 2',
            duration=timedelta(hours=2),
            user=self.user1
        )

        # Create a task for user2
        self.task3 = Task.objects.create(
            title='Test Task 3',
            duration=timedelta(hours=1),
            user=self.user2
        )

        # Get tokens for authentication
        refresh = RefreshToken.for_user(self.user1)
        self.token = str(refresh.access_token)

    def api_authenticate(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_jwt_authentication(self):
        """Test JWT authentication flow including token generation and refresh.
        Verifies that valid credentials return access and refresh tokens."""

        url = reverse('token_obtain_pair')
        response = self.client.post(url, {
            'username': 'testuser1',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

        url = reverse('token_refresh')
        response = self.client.post(url, {
            'refresh': response.data['refresh']
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_list_tasks(self):
        """Test task listing endpoint.
        Verifies that:
        - Unauthenticated users cannot access the list
        - Authenticated users can see their tasks
        - List is limited to 4 most recent tasks"""

        url = reverse('task-list')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.api_authenticate()
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(response.data), 4)  # Should return max 4 tasks

    def test_create_task(self):
        """Test task creation endpoint.
        Verifies that an authenticated user can create a task
        and the response contains correct task details including user association."""

        url = reverse('task-list')
        self.api_authenticate()
        data = {
            'title': 'New Test Task',
            'duration': '01:00:00'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Test Task')
        self.assertEqual(response.data['user'], self.user1.id)

    def test_raw_retrieve(self):
        """Test raw SQL task retrieval endpoint.
        Verifies that:
        - Users can retrieve their own tasks
        - Users cannot access other users' tasks
        - Response contains correct task details"""

        url = reverse('task-raw-retrieve', kwargs={'pk': self.task1.id})
        self.api_authenticate()
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Task 1')

        url = reverse('task-raw-retrieve', kwargs={'pk': self.task3.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_raw_update_title(self):
        """Test raw SQL task title update endpoint.
        Verifies that:
        - Users can update their own tasks' titles
        - Empty title updates are rejected
        - Users cannot update other users' tasks
        - Updates are correctly persisted"""

        url = reverse('task-raw-update-title', kwargs={'pk': self.task1.id})
        self.api_authenticate()
        
        data = {'title': 'Updated Title'}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.task1.refresh_from_db()
        self.assertEqual(self.task1.title, 'Updated Title')

        response = self.client.put(url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        url = reverse('task-raw-update-title', kwargs={'pk': self.task3.id})
        response = self.client.put(url, {'title': 'Hack'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_task(self):
        """Test task deletion endpoint.
        Verifies that:
        - Users can delete their own tasks
        - Users cannot delete other users' tasks
        - Task is properly removed from database"""

        url = reverse('task-detail', kwargs={'pk': self.task1.id})
        self.api_authenticate()
        
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        self.assertFalse(Task.objects.filter(id=self.task1.id).exists())

        url = reverse('task-detail', kwargs={'pk': self.task3.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Task.objects.filter(id=self.task3.id).exists())
