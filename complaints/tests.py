from django.test import TestCase

# Create your tests here.
from django.test import TestCase

class ComplaintListTest(TestCase):

    def test_list_view(self):
        response = self.client.get('/complaints/')
        self.assertEqual(response.status_code, 200)

class ComplaintDetailTest(TestCase):

    def test_detail_view(self):
        response = self.client.get('/complaints/1/')
        self.assertEqual(response.status_code, 200)

class ComplaintSearchTest(TestCase):

    def test_search(self):
        response = self.client.get('/complaints/?q=test')
        self.assertEqual(response.status_code, 200)

class ComplaintSuccessMessageTest(TestCase):

    def test_success_message(self):
        response = self.client.post('/complaints/create/', {
            'title': 'Test',
            'description': 'Test desc'
        }, follow=True)

        self.assertContains(response, "successfully")