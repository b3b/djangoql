import json

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase


class DjangoQLAdminTest(TestCase):
    def setUp(self):
        self.credentials = {'username': 'test', 'password': 'lol'}
        User.objects.create_superuser(email='herp@derp.rr', **self.credentials)

    def test_introspections(self):
        url = reverse('admin:core_book_djangoql_introspect')
        # unauthorized request should be redirected
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)
        self.assertTrue(self.client.login(**self.credentials))
        # authorized request should be served
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        introspections = json.loads(response.content.decode('utf8'))
        self.assertEqual('core.book', introspections['current_model'])
        for model in ('core.book', 'auth.user', 'auth.group'):
            self.assertIn(model, introspections['models'])

    def test_save_djangoql_query(self):
        url = reverse('admin:core_book_djangoql_save_query')
        url += '?text=test'
        # unauthorized request should be redirected to login page
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)
        self.assertIn('/admin/login/?next=', response.url)
        self.assertTrue(self.client.login(**self.credentials))
        # authorized request should be redirected to query creation page
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)
        self.assertIn('/admin/djangoql/query/add/', response.url)
        parameters = response.url.split('?')[1]
        # passed parameters should be preserved
        self.assertIn('text=', parameters)
        # _popup and model parameters should be added
        self.assertIn('_popup=', parameters)
        self.assertIn('model=', parameters)
