from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from djangoql.models import Query


def content_type(model):
    return ContentType.objects.get_for_model(model)


def create_saved_query(text='qtest', model=None, username='user1',
                       is_private=False, **kwargs):
    user, created = User.objects.get_or_create(username=username)
    return Query.objects.create(
        text=text,
        model=content_type(model or User),
        user=user,
        is_private=is_private,
        **kwargs
    )
