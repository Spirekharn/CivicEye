from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class UserTest(TestCase):

    def test_create_user(self):
        user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='citizen'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.role, 'citizen')