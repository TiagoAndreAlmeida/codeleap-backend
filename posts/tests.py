from unittest.mock import patch
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Post, Like, Comment

class FirebaseAuthTestCase(APITestCase):
    def setUp(self):
        self.firebase_uid = "firebase-uid-123"
        self.firebase_email = "test@example.com"
        self.firebase_name = "Test User"
        self.valid_token = "valid-mock-token"
        
        self.mock_decoded_token = {
            'uid': self.firebase_uid,
            'email': self.firebase_email,
            'name': self.firebase_name,
        }

    @patch('firebase_admin.auth.verify_id_token')
    def test_authentication_creates_user(self, mock_verify):
        mock_verify.return_value = self.mock_decoded_token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.valid_token}')
        response = self.client.get('/api/v1/careers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(User.objects.filter(username=self.firebase_uid).exists())

    def test_authentication_unauthorized_without_token(self):
        response = self.client.get('/api/v1/careers/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch('firebase_admin.auth.verify_id_token')
    def test_post_ownership_protection(self, mock_verify):
        user_a = User.objects.create(username="user-a", first_name="Owner")
        post = Post.objects.create(author=user_a, title="Original", content="Text")
        
        mock_verify.return_value = {'uid': 'user-b', 'email': 'b@ex.com', 'name': 'Attacker'}
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.valid_token}')
        
        response = self.client.patch(f'/api/v1/careers/{post.id}/', {"title": "Hacked"}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        post.refresh_from_db()
        self.assertEqual(post.title, "Original")

    @patch('firebase_admin.auth.verify_id_token')
    def test_soft_delete_behavior(self, mock_verify):
        user = User.objects.create(username="user-a", first_name="Owner")
        post = Post.objects.create(author=user, title="Post to Delete")
        
        mock_verify.return_value = {'uid': 'user-a', 'email': 'a@ex.com', 'name': 'Owner'}
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.valid_token}')
        
        response = self.client.delete(f'/api/v1/careers/{post.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        self.assertTrue(Post.objects.filter(id=post.id).exists())
        self.assertTrue(Post.objects.get(id=post.id).deleted)
        
        response_list = self.client.get('/api/v1/careers/')
        self.assertEqual(response_list.data['count'], 0)

    @patch('firebase_admin.auth.verify_id_token')
    def test_like_atomic_toggle(self, mock_verify):
        user = User.objects.create(username="user-a", first_name="Owner")
        post = Post.objects.create(author=user, title="Cool Post")
        
        mock_verify.return_value = {'uid': 'user-a', 'email': 'a@ex.com', 'name': 'Owner'}
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.valid_token}')
        
        response = self.client.post(f'/api/v1/careers/{post.id}/like/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['liked'], True)
        self.assertEqual(response.data['likes_count'], 1)
        
        response = self.client.post(f'/api/v1/careers/{post.id}/like/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['liked'], False)
        self.assertEqual(response.data['likes_count'], 0)

    @patch('firebase_admin.auth.verify_id_token')
    def test_comment_creation_and_counter(self, mock_verify):
        user = User.objects.create(username="user-a", first_name="Owner")
        post = Post.objects.create(author=user, title="Post for Comments")
        
        mock_verify.return_value = {'uid': 'user-a', 'email': 'a@ex.com', 'name': 'Owner'}
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.valid_token}')
        
        data = {"content": "First Comment"}
        response = self.client.post(f'/api/v1/careers/{post.id}/comments/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        post.refresh_from_db()
        self.assertEqual(post.comments_count, 1)

    @patch('firebase_admin.auth.verify_id_token')
    def test_comment_deletion_and_counter(self, mock_verify):
        user = User.objects.create(username="user-a", first_name="Owner")
        post = Post.objects.create(author=user, title="Post", comments_count=1)
        comment = Comment.objects.create(author=user, post=post, content="To be deleted")
        
        mock_verify.return_value = {'uid': 'user-a', 'email': 'a@ex.com', 'name': 'Owner'}
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.valid_token}')
        
        response = self.client.delete(f'/api/v1/comments/{comment.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        post.refresh_from_db()
        self.assertEqual(post.comments_count, 0)
        self.assertTrue(Comment.objects.get(id=comment.id).deleted)

    @patch('firebase_admin.auth.verify_id_token')
    def test_comment_pagination(self, mock_verify):
        user = User.objects.create(username="user-a", first_name="Owner")
        post = Post.objects.create(author=user, title="Post for Pagination")
        
        for i in range(15):
            Comment.objects.create(author=user, post=post, content=f"Comment {i}")
        
        mock_verify.return_value = {'uid': 'user-a', 'email': 'a@ex.com', 'name': 'Owner'}
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.valid_token}')
        
        response = self.client.get(f'/api/v1/careers/{post.id}/comments/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)
        self.assertIsNotNone(response.data['next'])

    @patch('firebase_admin.auth.verify_id_token')
    def test_comment_ownership_protection(self, mock_verify):
        user_a = User.objects.create(username="user-a", first_name="Owner")
        post = Post.objects.create(author=user_a, title="Post")
        comment = Comment.objects.create(author=user_a, post=post, content="User A Comment")
        
        mock_verify.return_value = {'uid': 'user-b', 'email': 'b@ex.com', 'name': 'Attacker'}
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.valid_token}')
        
        response = self.client.delete(f'/api/v1/comments/{comment.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        comment.refresh_from_db()
        self.assertFalse(comment.deleted)
