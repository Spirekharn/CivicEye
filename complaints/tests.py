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
