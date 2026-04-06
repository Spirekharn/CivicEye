from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class AuthTests(TestCase):

    def test_register_user(self):
        response = self.client.post(reverse('register'), {
            'username': 'testuser',
            'password': '12345'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_login_user(self):
        User.objects.create_user(username='testuser', password='12345')

        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': '12345'
        })

        self.assertEqual(response.status_code, 302)

    def test_dashboard_access(self):
        user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)