from django.contrib.auth.models import Group, User
from django.test import TestCase

from .factories import create_saved_query, Query


class QueryTest(TestCase):

    def test_created(self):
        self.assertFalse(Query.objects.exists())
        create_saved_query()
        self.assertTrue(Query.objects.exists())

    def test_blank_label(self):
        create_saved_query(text='q')
        self.assertEqual(Query.objects.get().label, 'q')

    def test_long_label_truncated(self):
        create_saved_query(text='q' * 200)
        self.assertEqual(Query.objects.get().label, 'q' * 47 + '...')

    def test_deleted_with_user(self):
        create_saved_query()
        self.assertTrue(Query.objects.exists())
        User.objects.all().delete()
        self.assertFalse(Query.objects.exists())


class QueryForModelTest(TestCase):

    def test_query_returned(self):
        self.assertFalse(Query.objects.for_model(User).exists())
        create_saved_query()
        self.assertEqual(Query.objects.for_model(User).count(), 1)

    def test_other_model_object(self):
        create_saved_query(model=Group)
        self.assertEqual(Query.objects.for_model(User).count(), 0)

    def test_private_returned(self):
        user = User.objects.create(username='user1')
        create_saved_query(is_private=True, username='user1')
        self.assertEqual(Query.objects.for_model(User,
                                                 user=user).count(), 1)

    def test_private_anonymous(self):
        create_saved_query(is_private=True)
        self.assertEqual(Query.objects.for_model(User).count(), 0)

    def test_private_other_user(self):
        user = User.objects.create(username='user1')
        create_saved_query(is_private=True, username='user2')
        self.assertEqual(Query.objects.for_model(User,
                                                 user=user).count(), 0)
